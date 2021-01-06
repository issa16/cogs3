import datetime
import logging

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
        verbose_name=_('Project Title'),
    )
    description = models.TextField(
        max_length=1024,
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
    )
    department = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_('Department'),
    )
    pi = models.CharField(
        max_length=256,
        verbose_name=_("Principal Investigator's name, position and email"),
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
    )
    start_date = models.DateField(verbose_name=_('Start date'))
    end_date = models.DateField(verbose_name=_('End date'))
    economic_user = models.BooleanField(
        default=False,
        verbose_name=_('Economic user'),
    )
    requirements_software = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Software name and versions'),
        verbose_name=_('Software Requirements'),
    )
    requirements_gateways = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Web gateway or portal name and versions'),
        verbose_name=_('Gateway Requirements'),
    )
    requirements_training = models.TextField(
        max_length=512,
        blank=True,
        verbose_name=_('Training Requirements'),
    )
    requirements_onboarding = models.TextField(
        max_length=512,
        blank=True,
        verbose_name=_('Onboarding Requirements'),
    )
    allocation_rse = models.BooleanField(
        default=False,
        verbose_name=_('RSE available to?'),
    )
    allocation_cputime = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('CPU time allocation in hours'),
    )
    allocation_memory = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('RAM allocation in GB'),
    )
    allocation_storage_home = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Home storage in GB'),
    )
    allocation_storage_scratch = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Scratch storage in GB'),
    )
    document = models.FileField(
        verbose_name=_('Upload Supporting Documents'),
        upload_to="documents/%Y/%m/%d/%M/",
        blank=True,
        null=True,
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

    @classmethod
    def project_codes_for_tech_lead(cls, tech_lead):
        '''
        Return a list of project codes for a tech lead.
        '''
        return cls.objects.filter(tech_lead=tech_lead,).order_by('-created_time').values_list('code', flat=True)

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
