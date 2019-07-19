from django.core.management.base import BaseCommand, CommandError
from sqlalchemy import create_engine, Table
import numpy as np
import pandas as pd
from datetime import date, timedelta
from project.models import Project
from funding.models import Attribution
from priority.models import slurm_priority
class Command(BaseCommand):
    def handle(self, *args, **options):
        #number of QOS levels
        QOS_levels=4.0
        Today=date.today()
        #engine for reading/writing sql files
        # sqlite://<nohostname>/<pathtofile>
        engine = create_engine('sqlite:///db.sqlite3', echo=False)
        #df = pd.read_csv ('~/Documents/full_sacct_dump.csv',sep='|')
        df = pd.read_csv ('~/Documents/Cogs3/cogs3/priority/fixtures/TEST_dump.csv',sep='|')
        #remove NANs
        df=df.dropna(how='any')
        #convert cpu time from core seconds to core hours
        cpuhours=df['CPUTimeRAW']/3600
        df['CPU-HOURS']=cpuhours.astype(int)
        #seperate into gpu and not gpu
        gpu=df[df.Partition=="gpu"]
        compute=df[df.Partition!="gpu"]
        
        #calculate the total raw cpu time used for each project
        cpu_sum=compute.groupby('Account')['CPU-HOURS'].sum().astype(int).to_frame(name='cpu_sum')
        gpu_sum=gpu.groupby('Account')['CPU-HOURS'].sum().astype(int).to_frame(name='gpu_sum')
        
        #generate random ap values for testing
        #Ap=list(np.random.randint(50000,250000,len(combi_sum.index)))
        SCW=caculate_AP()
        #combine the three data frames into one
        SCW = pd.merge(SCW,cpu_sum, on='Account', how='outer').fillna(0)
        SCW = pd.merge(SCW,gpu_sum, on='Account', how='outer').fillna(0)
        SCW['Cpu_New']=SCW['cpu_sum'].subtract(SCW['CPU_hours'])
        SCW['Gpu_New']=SCW['gpu_sum'].subtract(SCW['GPU_hours'])
        
        
        #calculate parameter such that K*log(Ap) has a max defined by QOS_levels
        Max_Ap=SCW['Ap'].max()
        k=QOS_levels/np.log10(Max_Ap)
        #check if previous run was prioritezed and if so add the time since last sactdump to total priortized time
        P=SCW['Qos']>0
        Prioritsed=SCW[P]
        Prioritsed['P_CPU']=Prioritsed['P_CPU']+Prioritsed['Cpu_New']
        Prioritsed['P_GPU']=Prioritsed['P_GPU']+Prioritsed['Gpu_New']
        
        SCW.update(Prioritsed)
        SCW['CPU_hours']=SCW['CPU_hours']+SCW['Cpu_New']
        SCW['GPU_hours']=SCW['GPU_hours']+SCW['Gpu_New']
        print(SCW['CPU_hours'])
        #calculate Priority
        Priority =(SCW['Ap']-(SCW['P_CPU'] + SCW['P_GPU']*40)).to_frame(name='Priority_Sum').astype(int)
        Priority['QOS']=SCW['Ap'].map(lambda a : k*np.log10(a))
        Priority['QOS']= Priority['QOS'].where(Priority['Priority_Sum']>=0,0)
        Priority['Account']=SCW['Account']
        
        
        #create datframe for output to django
        COGS_DB = pd.DataFrame(Priority['Account'], columns=['Account'])
        #COGS_DB['Account']=Priority['Account']
        COGS_DB['QOS']=Priority['QOS'].astype(int)
        COGS_DB['CPU_hours']=SCW['CPU_hours']
        COGS_DB['GPU_hours']=SCW['GPU_hours']
        COGS_DB['P_CPU']=SCW['P_CPU']
        COGS_DB['P_GPU']=SCW['P_GPU']
        COGS_DB['Ap']=SCW['Ap']
        COGS_DB['Date']=pd.date_range(start=Today, end=Today,periods=len(SCW.index))
        #output Acoount and QOS to pipe seperated csv file 
        Priority.to_csv(path_or_buf='~/Documents/Cogs3/cogs3/priority/fixtures/QOS_output.csv',sep='|',columns=['Account','QOS'],index=False)
  #chack put in place to prevent writing data twice on the same day
        assert (not slurm_priority.objects.filter(Date__year=Today.year, Date__month=Today.month, Date__day=Today.day).exists()),'Data for today already exists in django database'
        # Write data to django database
        COGS_DB.to_sql('priority_slurm_priority',index=False,con=engine,if_exists='append')
        engine.execute("SELECT * FROM priority_slurm_priority").fetchall()
        
def caculate_AP():
    from django.core.management.base import BaseCommand, CommandError
    from django.conf import settings
    from django.db import models
    from project.models import Project, ProjectSystemAllocation
    from funding.models import Attribution
    from priority.models import slurm_priority
#list all projects that are on sunbird
    on_sunbird=[]
    Sunbird=ProjectSystemAllocation.objects.exclude(system=1)
    for I in Sunbird:
        on_sunbird.append(I.project)
    A = Project.objects.filter(code__in=on_sunbird)
    priorities={}
#query the Database for attributions associted to each project and calculate Ap based type of attribution
    for B in A:
        Ap=50000
        if B.attributions==None:
            priorities.update({B.code:Ap})
        else:
            for C in B.attributions.all():
                    
                if C.is_fundingsource:
                    Ap=Ap+C.fundingsource.amount
                else:
                    Ap=Ap+10000
                priorities.update({B.code:Ap})
    Attpoints=pd.DataFrame(list(priorities.items()),columns=['Account','Ap'])
#query the priorities datbase and merge in the Ap values 
    Priority_DB = pd.DataFrame(list(slurm_priority.objects.all().values('Account','CPU_hours','GPU_hours','P_CPU','P_GPU','Qos')))
    SCW=pd.merge(Priority_DB,Attpoints, on='Account', how='outer').fillna(50000)
    return SCW
