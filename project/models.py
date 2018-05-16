import datetime

from django.conf import settings
from django.db import models

from institution.models import Institution
from system.models import System


class ProjectCategory(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.TextField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Project Categories'
        ordering = ('name', )


class ProjectFundingSource(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.CharField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Project Funding Sources'
        ordering = ('name', )


class Project(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name='Project Title',
    )
    description = models.TextField(
        max_length=1024,
        verbose_name='Project Description',
    )
    legacy_hpcw_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Legacy HPC Wales ID',
        help_text='Project legacy ID from HPC Wales',
    )
    legacy_arcca_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Legacy ARCCA ID',
        help_text='Project legacy ID ARCCA',
    )
    code = models.CharField(
        max_length=20,
        verbose_name='Project code assigned by SCW',
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text='Institution project is based',
    )
    institution_reference = models.CharField(
        max_length=128,
        verbose_name='Owning institution project reference',
    )
    department = models.CharField(
        max_length=128,
        blank=True,
    )
    pi = models.CharField(
        max_length=256,
        verbose_name='Principal Investigator',
    )
    tech_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='project_as_tech_lead',
        on_delete=models.CASCADE,
        verbose_name='Technical Lead',
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.CASCADE,
        null=True,
    )
    funding_source = models.ForeignKey(
        ProjectFundingSource,
        on_delete=models.CASCADE,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    economic_user = models.BooleanField(default=False)
    requirements_software = models.TextField(
        max_length=512,
        help_text='Software name and versions',
    )
    requirements_gateways = models.TextField(
        max_length=512,
        help_text='Web gateway or portal name and versions',
    )
    requirements_training = models.TextField(max_length=512)
    requirements_onboarding = models.TextField(max_length=512)
    allocation_rse = models.BooleanField(
        default=False,
        verbose_name='RSE available to?',
    )
    allocation_cputime = models.PositiveIntegerField(verbose_name='CPU time allocation in hours')
    allocation_memory = models.PositiveIntegerField(verbose_name='RAM allocation in GB')
    allocation_storage_home = models.PositiveIntegerField(verbose_name='Home storage in GB')
    allocation_storage_scartch = models.PositiveIntegerField(verbose_name='Scratch storage in GB')
    allocation_systems = models.ManyToManyField(
        System,
        through='ProjectSystemAllocation',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectUserMembership',
    )
    AWAITING_APPROVAL = 1
    APPROVED = 2
    DECLINED = 3
    REVOKED = 4
    SUSPENDED = 5
    CLOSED = 6
    STATUS_CHOICES = (
        (AWAITING_APPROVAL, 'Awaiting Approval'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
        (REVOKED, 'Revoked'),
        (SUSPENDED, 'Suspended'),
        (CLOSED, 'Closed'),
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_APPROVAL,
    )
    reason_decision = models.TextField(
        max_length=256,
        blank=True,
        verbose_name='Reason for the project status decision:',
        help_text='The reason will be emailed to the project\'s technical lead upon project status update.',
    )
    notes = models.TextField(max_length=512, blank=True, help_text='Internal project notes')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def awaiting_approval(self):
        return True if self.status == Project.AWAITING_APPROVAL else False

    def __str__(self):
        data = {
            'code': self.code,
            'title': self.title,
        }
        return '{code} - {title}'.format(**data)

    class Meta:
        verbose_name_plural = 'Projects'


class ProjectSystemAllocation(models.Model):
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

    def __str__(self):
        data = {
            'project': self.project,
            'system': self.system,
            'date_allocated': self.date_allocated,
            'date_unallocated': self.date_unallocated
        }
        return '{project} on {system} from {date_allocated} to {date_unallocated}'.format(**data)

    class Meta:
        verbose_name_plural = 'Project System Allocations'


class ProjectUserMembershipManager(models.Manager):

    def awaiting_authorisation(self, user):
        projects = Project.objects.filter(tech_lead=user)
        project_user_memberships = ProjectUserMembership.objects.filter(
            project__in=projects,
            status=ProjectUserMembership.AWAITING_AUTHORISATION,
        )
        return project_user_memberships


class ProjectUserMembership(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    AWAITING_AUTHORISATION = 1
    AUTHORISED = 2
    DECLINED = 3
    REVOKED = 4
    SUSPENDED = 5
    STATUS_CHOICES = (
        (AWAITING_AUTHORISATION, 'Awaiting Authorisation'),
        (AUTHORISED, 'Authorised'),
        (DECLINED, 'Declined'),
        (REVOKED, 'Revoked'),
        (SUSPENDED, 'Suspended'),
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_AUTHORISATION,
    )
    date_joined = models.DateField()
    date_left = models.DateField(default=datetime.date.max)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    objects = ProjectUserMembershipManager()

    def awaiting_authorisation(self):
        return True if self.status == ProjectUserMembership.AWAITING_AUTHORISATION else False

    def authorised(self):
        return True if self.status == ProjectUserMembership.AUTHORISED else False

    def unauthorised(self):
        revoked_states = [
            ProjectUserMembership.REVOKED,
            ProjectUserMembership.SUSPENDED,
            ProjectUserMembership.DECLINED,
        ]
        return True if self.status in revoked_states else False

    def __str__(self):
        data = {
            'user': self.user,
            'project': self.project,
            'date_joined': self.date_joined,
            'date_left': self.date_left
        }
        return '{user} on {project} from {date_joined} to {date_left}'.format(**data)

    class Meta:
        verbose_name_plural = 'Project User Memberships'
        unique_together = ('project', 'user')
