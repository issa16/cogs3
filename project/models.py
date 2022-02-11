import datetime
import logging
import re

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from system.models import System

from openldap.api import project_membership_api
from project.notifications import project_created_notification

logger = logging.getLogger('apps')


class ProjectCategory(models.Model):

    class Meta:
        verbose_name_plural = _('Project Categories')
        ordering = ('name',)

    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.TextField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProjectFundingSource(models.Model):

    class Meta:
        verbose_name_plural = _('Project Funding Sources')
        ordering = ('name',)

    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.CharField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProjectManager(models.Manager):

    def awaiting_approval(self, user):
        return Project.objects.filter(
            tech_lead=user,
            status=Project.AWAITING_APPROVAL,
        )


class Project(models.Model):

    class Meta:
        verbose_name_plural = _('Projects')
        get_latest_by = 'created_time'

    title = models.CharField(
        max_length=256,
        help_text="A descriptive title that aims to cover the aims and objectives of the project and the work that will be undertaken as part of the project",
        verbose_name=_('Project Title'),
    )
    description = models.TextField(
        max_length=1024,
        help_text="A meaningful description of the scientific goals and objectives of the project, and the methods and objectives to be pursued.",
        verbose_name=_('Project Description'),
    )
    legacy_hpcw_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Legacy HPC Wales ID'),
        help_text=_('Project legacy ID from HPC Wales'),
    )
    legacy_arcca_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Legacy ARCCA ID'),
        help_text=_('Project legacy ID ARCCA'),
    )
    code = models.CharField(
        max_length=20,
        verbose_name=_('Project code assigned by SCW'),
    )
    gid_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('OpenLDAP GID Number'),
    )
    institution_reference = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_('Owning institution project reference'),
        help_text=_('If your project is externally funded (see below), please enter the reference number provided by the sponsors, e.g., EPSRC (EP/S016376/1), BBSRC (BB/T006188/1)'),
    )
    department = models.CharField(
        max_length=128,
        blank=False,
        verbose_name=_('Department'),
        help_text=_('Your School, Institute and/or Department. If the project is under the auspices of an Institute, please also specify your School.'),
    )
    pi = models.CharField(
        max_length=256,
        blank=False,
        verbose_name=_("(obsolete) Principal Investigator's name, position and email"),
    )
    pi_name = models.CharField(
        max_length=128,
        blank=False,
        verbose_name=_("Principal Investigator's name"),
        help_text=_('By default, we request that Principal Investigators for Projects on the system be permanent staff members who are ultimately responsible for the research being undertaken. If you are a PhD student, Research Associate or Research Assistant, this would naturally be your supervisor or line manager. As the person requesting the project, you will be listed as Technical Lead, the person we will contact in first instance on all matters related with this project and who will receive project membership requests and can approve/deny them'),
    )
    pi_position = models.CharField(
        max_length=128,
        blank=False,
        verbose_name=_("Principal Investigator's position"),
    )
    pi_email = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("Principal Investigator's email"),
    )
    tech_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='project_as_tech_lead',
        on_delete=models.CASCADE,
        verbose_name=_('Technical Lead'),
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('Category'),
    )
    funding_source = models.ForeignKey(
        ProjectFundingSource,
        on_delete=models.CASCADE,
        verbose_name=_('Funding source'),
        help_text=_('If the research study, of which this project is part, has received funding (internal or external), please let us know by selecting the appropriate category.'),
    )
    start_date = models.DateField(
        verbose_name=_('Start date'),
        help_text=_('Project start date. If there is likely to be a delay in starting the project, please let us know here. We will use this date as reference to contact you in case we notice the project remains inactive.'),
    )
    end_date = models.DateField(
        verbose_name=_('End date'),
        help_text=_('Project end date. The project will be suspended on this date preventing you from submitting further jobs to the system. Please contact us ahead of this date if you wish to renew the project.'),
    )
    economic_user = models.BooleanField(
        default=False,
        verbose_name=_('Economic user'),
    )
    requirements_software = models.TextField(
        max_length=512,
        blank=False,
        verbose_name=_('Software Requirements'),
        help_text=_('Enter details of any software you require to be installed on the system to be able to use it for your research. Examples include compilers (Intel and GNU C, C++, and Fortran compilers are available already), interpreters (Python and R are available already), open-source libraries, and commercial software (e.g. Stata, Matlab, Molpro). In addition, if you require a specific version of the software then please specify this.'),
    )
    requirements_gateways = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Web gateway or portal name and versions'),
        verbose_name=_('Gateway Requirements'),
    )
    requirements_training = models.TextField(
        max_length=512,
        blank=False,
        verbose_name=_('Training Requirements'),
        help_text=_('Do you require training to make use of the system (e.g. Linux, Bash, General HPC concepts, containers)? If so, write details of this here.'),
    )
    requirements_onboarding = models.TextField(
        max_length=512,
        blank=False,
        verbose_name=_('Onboarding Requirements'),
        help_text=_('Do you require any assistance in adapting your software to be able to make use of the system? Would a virtual session explaining the use of the Scheduler be helpful, if so, write details of these here.'),
    )
    allocation_rse = models.BooleanField(
        default=False,
        verbose_name=_('RSE available to?'),
    )
    allocation_gpus = models.BooleanField(
        default=False,
        verbose_name=_('Does the project requires access to GPUs?'),
    )
    allocation_cputime = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Required compute time (in hours) for the entire project'),
        help_text=_('How many “core-hours” do you anticipate this project needing? For example, if you have a program that only uses one CPU on your laptop, and runs for 48 hours, and you need to run it 1,000 times, then this number would be 48,000; if instead it used four cores on your laptop for the same amount of time, it would be 192,000. Thus one useful way to quantify the overall project requirements is to first define the requirements of a typical job, then have a stab at estimating the likely number of jobs to be run over the lifetime of the project. We realise this can be tough providing even a ballpark estimate given the dynamics of any research project, but it doesn’t have to be too quantitative, just a qualitative estimate will be fine.'),
    )
    allocation_memory = models.PositiveIntegerField(
        null=True,
        blank=False,
        verbose_name=_('Required memory (in Gigabytes) for a typical program run'),
        help_text=_('How much memory will your program need at once per node? If you don’t know this number, but know that the program runs on your computer, then enter the amount of RAM on your computer.'),
    )
    allocation_storage_home = models.PositiveIntegerField(
        null=True,
        blank=False,
        verbose_name=_('Home (resilient) storage in Gigabytes'),
        help_text=_('Home storage is long-term (although not backed up) file storage used for data you need to keep on the system for months at a time. This is subject to a quota. Enter the amount of storage you need for the longer term; 50 GBytes is the default allocation on Hawk and 100 GBytes on Sunbird.'),
    )
    allocation_storage_scratch = models.PositiveIntegerField(
        null=True,
        blank=False,
        verbose_name=_('High performance transient (scratch) storage in Gigabytes'),
        help_text=_('Scratch storage is short-term, high-performance parallel file storage used for intermediary data you need temporarily but will either delete or move off the system once it is no longer needed. There is a 5 TBytes user quota on Hawk and 20 TBytes on Sunbird. When the scratch filesystem approaches full capacity, old unused files will be deleted.'),
    )
    document = models.FileField(
        verbose_name=_('Upload Supporting Documents'),
        upload_to="documents/%Y/%m/%d/%M/",
        blank=True,
        null=True,
        help_text=_('Any other documentation relevant for the project application. This could include relevant publications from previous work, a case for greater allocations than the defaults (storage etc), detailed software requirements etc.'),
    )
    allocation_systems = models.ManyToManyField(
        System,
        through='ProjectSystemAllocation',
        verbose_name=_('Allocation systems'),
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectUserMembership',
        verbose_name=_('Members'),
    )
    AWAITING_APPROVAL = 0
    APPROVED = 1
    DECLINED = 2
    REVOKED = 3
    SUSPENDED = 4
    CLOSED = 5
    STATUS_CHOICES = (
        (AWAITING_APPROVAL, _('Awaiting Approval')),
        (APPROVED, _('Approved')),
        (DECLINED, _('Declined')),
        (REVOKED, _('Revoked')),
        (SUSPENDED, _('Suspended')),
        (CLOSED, _('Closed')),
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_APPROVAL,
        verbose_name=_('Current Status'),
    )
    previous_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_APPROVAL,
        verbose_name=_('Previous Status'),
    )
    reason_decision = models.TextField(
        max_length=256,
        blank=True,
        verbose_name=_('Reason for the project status decision:'),
        help_text=_('The reason will be emailed to the project\'s technical lead upon project status update.'),
    )
    notes = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Internal project notes'),
        verbose_name=_('Notes'),
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Created time'))
    modified_time = models.DateTimeField(auto_now=True, verbose_name=_('Modified time'))

    objects = ProjectManager()

    def is_awaiting_approval(self):
        return True if self.status == Project.AWAITING_APPROVAL else False

    def is_approved(self):
        return True if self.status == Project.APPROVED else False

    def is_declined(self):
        return True if self.status == Project.DECLINED else False

    def is_revoked(self):
        return True if self.status == Project.REVOKED else False

    def is_suspended(self):
        return True if self.status == Project.SUSPENDED else False

    def is_closed(self):
        return True if self.status == Project.CLOSED else False

    def reset_status(self):
        """
        Reset the current status to the previous status.
        """
        self.status = self.previous_status
        self.save()

    def _assign_project_owner_project_membership(self):
        try:
            project_membership, created = ProjectUserMembership.objects.get_or_create(
                project=self,
                user=self.tech_lead,
                date_joined=datetime.date.today(),
                status=ProjectUserMembership.AUTHORISED,
                previous_status=ProjectUserMembership.AUTHORISED,
            )
            # Assign the 'project_owner' group to the project's technical lead.
            group = Group.objects.get(name='project_owner')
            self.tech_lead.groups.add(group)

            # Propagate the changes to LDAP
            if created:
                project_membership_api.create_project_membership(project_membership=project_membership)
        except Exception:
            logger.exception('Failed assign project owner membership to the project\'s technical lead.')

    def _generate_project_code(self):
        prefix = 'scw'
        last_project = Project.objects.exclude(code="scw0001").exclude(code="scw0002").order_by('id').last()
        if not last_project:
            if self.legacy_arcca_id or self.legacy_hpcw_id:
                return prefix + '0000'
            else:
                return prefix + '1000'
        else:
            code = last_project.code.split(prefix)[1]
            return prefix + str(int(code) + 1).zfill(4)

    def save(self, *args, **kwargs):
        if self.code == '':
            self.code = self._generate_project_code()
            project_created_notification.delay(self)
        if self.status == Project.APPROVED:
            self._assign_project_owner_project_membership()
        super(Project, self).save(*args, **kwargs)

    @classmethod
    def latest_project(cls, tech_lead):
        '''
        Return the tech lead's latest project.
        '''
        return cls.objects.filter(tech_lead=tech_lead).latest()

    def __str__(self):
        return self.code


class ProjectSystemAllocation(models.Model):

    class Meta:
        verbose_name_plural = _('Project System Allocations')
        unique_together = (('project', 'system'),)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
    )
    date_allocated = models.DateField()
    date_unallocated = models.DateField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    ACTIVE = 1
    INACTIVE = 2
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )
    openldap_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name='OpenLDAP status',
    )

    def __str__(self):
        data = {
            'project': self.project,
            'system': self.system,
            'date_allocated': self.date_allocated,
            'date_unallocated': self.date_unallocated
        }
        return _('{project} on {system} from {date_allocated} to {date_unallocated}').format(**data)


class ProjectUserMembershipManager(models.Manager):

    def awaiting_authorisation(self, user):
        projects = Project.objects.filter(tech_lead=user)
        project_user_memberships = ProjectUserMembership.objects.filter(
            project__in=projects,
            status=ProjectUserMembership.AWAITING_AUTHORISATION,
        )
        return project_user_memberships


class ProjectUserMembership(models.Model):

    class Meta:
        verbose_name_plural = _('Project User Memberships')
        unique_together = ('project', 'user')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    AWAITING_AUTHORISATION = 0
    AUTHORISED = 1
    DECLINED = 2
    REVOKED = 3
    SUSPENDED = 4
    STATUS_CHOICES = (
        (AWAITING_AUTHORISATION, _('Awaiting Authorisation')),
        (AUTHORISED, _('Authorised')),
        (DECLINED, _('Declined')),
        (REVOKED, _('Revoked')),
        (SUSPENDED, _('Suspended')),
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_AUTHORISATION,
        verbose_name=_('Current Status'),
    )
    previous_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_AUTHORISATION,
        verbose_name=_('Previous Status'),
    )
    date_joined = models.DateField()
    date_left = models.DateField(default=datetime.date.max)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    objects = ProjectUserMembershipManager()

    def is_awaiting_authorisation(self):
        return True if self.status == ProjectUserMembership.AWAITING_AUTHORISATION else False

    def is_authorised(self):
        return True if self.status == ProjectUserMembership.AUTHORISED else False

    def is_unauthorised(self):
        revoked_states = [
            ProjectUserMembership.REVOKED,
            ProjectUserMembership.SUSPENDED,
            ProjectUserMembership.DECLINED,
        ]
        return True if self.status in revoked_states else False

    def reset_status(self):
        """
        Reset the current status to the previous status.
        """
        self.status = self.previous_status
        self.save()

    def __str__(self):
        data = {
            'user': self.user,
            'project': self.project,
            'date_joined': self.date_joined,
            'date_left': self.date_left
        }
        return _('{user} on {project} from {date_joined} to {date_left}').format(**data)
