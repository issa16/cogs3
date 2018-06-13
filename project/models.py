import datetime
import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from institution.models import Institution
from system.models import System

logger = logging.getLogger('apps')


class ProjectCategory(models.Model):

    class Meta:
        verbose_name_plural = _('Project Categories')
        ordering = ('name', )

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
        ordering = ('name', )

    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.CharField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Project(models.Model):

    class Meta:
        verbose_name_plural = _('Projects')

    title = models.CharField(
        max_length=256,
        verbose_name=_('Project Title'),
    )
    description = models.TextField(
        max_length=1024,
        blank=True,
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
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text=_('Institution project is based'),
        verbose_name=_('Institution'),
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
        verbose_name=_('Principal Investigator'),
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
        verbose_name=_('Requirements software'),
    )
    requirements_gateways = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Web gateway or portal name and versions'),
        verbose_name=_('Requirements gateways'),
    )
    requirements_training = models.TextField(
        max_length=512,
        blank=True,
        verbose_name=_('Requirements training'),
    )
    requirements_onboarding = models.TextField(
        max_length=512,
        blank=True,
        verbose_name=_('Requirements onboarding'),
    )
    allocation_rse = models.BooleanField(
        default=False,
        verbose_name=_('RSE available to?'),
    )
    allocation_cputime = models.PositiveIntegerField(verbose_name=_('CPU time allocation in hours'))
    allocation_memory = models.PositiveIntegerField(verbose_name=_('RAM allocation in GB'))
    allocation_storage_home = models.PositiveIntegerField(verbose_name=_('Home storage in GB'))
    allocation_storage_scratch = models.PositiveIntegerField(verbose_name=_('Scratch storage in GB'))
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
    AWAITING_APPROVAL = 1
    APPROVED = 2
    DECLINED = 3
    REVOKED = 4
    SUSPENDED = 5
    CLOSED = 6
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
        verbose_name=_('Status'),
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

    def _assign_project_owner_project_membership(self):
        try:
            ProjectUserMembership.objects.get_or_create(
                project=self,
                user=self.tech_lead,
                date_joined=datetime.date.today(),
                status=ProjectUserMembership.AUTHORISED,
            )
            # Assign the 'project_owner' group to the project's technical lead.
            group = Group.objects.get(name='project_owner')
            self.tech_lead.groups.add(group)
        except Exception as e:
            logger.exception('Failed assign project owner membership to the project\'s technical lead.')

    def save(self, *args, **kwargs):
        updated = self.pk
        if self.code is '':
            last_project = Project.objects.order_by('id').last()
            if not last_project:
                if self.legacy_arcca_id or self.legacy_hpcw_id:
                    self.code = 'SCW-0000'
                else:
                    self.code = 'SCW-1000'
            else:
                prefix, code = last_project.code.split('-')
                self.code = 'SCW-' + str(int(code) + 1).zfill(4)

        super(Project, self).save(*args, **kwargs)

        if self.status == Project.APPROVED:
            self._assign_project_owner_project_membership()

    def __str__(self):
        data = {
            'code': self.code,
            'title': self.title,
        }
        return '{code} - {title}'.format(**data)


class ProjectSystemAllocation(models.Model):

    class Meta:
        verbose_name_plural = _('Project System Allocations')

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

    class Meta:
        verbose_name_plural = _('Project System Allocations')
        unique_together = (('project', 'system'), )


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
    AWAITING_AUTHORISATION = 1
    AUTHORISED = 2
    DECLINED = 3
    REVOKED = 4
    SUSPENDED = 5
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

    def __str__(self):
        data = {
            'user': self.user,
            'project': self.project,
            'date_joined': self.date_joined,
            'date_left': self.date_left
        }
        return _('{user} on {project} from {date_joined} to {date_left}').format(**data)
