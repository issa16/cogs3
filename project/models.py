import datetime
import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from openldap.api import project_membership_api
from system.models import System
from funding.models import Attribution

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

    history = HistoricalRecords()

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
    pi_legacy = models.CharField(
        max_length=256,
        verbose_name=_("[Deprecated]Principal Investigator's name, position and email"),
    )
    supervisor_name = models.CharField(
        max_length=256,
        verbose_name=_("Project Leader's name"),
        blank=True,
    )
    supervisor_position = models.CharField(
        max_length=256,
        verbose_name=_("Project Leader's position"),
        blank=True,
    )
    supervisor_email = models.CharField(
        max_length=256,
        verbose_name=_("Project Leader's email"),
        blank=True,
    )
    attributions = models.ManyToManyField(
        Attribution,
        blank=True,
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
    economic_user = models.BooleanField(
        default=False,
        verbose_name=_('Economic user'),
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

    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Created time'))
    modified_time = models.DateTimeField(auto_now=True, verbose_name=_('Modified time'))

    def get_allocation_requests(self):
        return SystemAllocationRequest.objects.filter(project=self.id).order_by('-start_date')

    # objects = ProjectManager()

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

    def _remove_from_project_owner(self, old_techlead):
        try:
            # If the old tech lead no longer has any projects,
            # remove them from the project_owner group
            techlead_projects = Project.objects.filter(
                tech_lead=old_techlead,
            )
            if techlead_projects.count() == 1:
                group = Group.objects.get(name='project_owner')
                old_techlead.groups.remove(group)
        except Exception:
            logger.exception('Failed assign project owner membership to the project\'s technical lead.')

    def _generate_project_code(self):
        prefix = 'scw'
        last_project = Project.objects.order_by('id').last()
        if not last_project:
            if self.legacy_arcca_id or self.legacy_hpcw_id:
                return prefix + '0000'
            else:
                return prefix + '1000'
        else:
            code = last_project.code.split(prefix)[1]
            return prefix + str(int(code) + 1).zfill(4)

    def save(self, *args, **kwargs):
        if self.code is '':
            self.code = self._generate_project_code()

        self._assign_project_owner_project_membership()

        # If the project already exists check for changes
        if(Project.objects.filter(pk=self.id).exists()):
            current = Project.objects.get(pk=self.id)
            if self.tech_lead != current.tech_lead:
                self._remove_from_project_owner(current.tech_lead)

        super(Project, self).save(*args, **kwargs)

    history = HistoricalRecords()

    def __str__(self):
        return self.code


class SystemAllocationRequest(models.Model):

    class Meta:
        verbose_name_plural = _('System Allocation Requests')

    information = models.TextField(
        max_length=1024,
        blank=True,
        verbose_name=_('Additional details of the allocation request not present in the project description'),
    )
    project = models.ForeignKey(
        Project,
        related_name='system_allocation_as_project',
        on_delete=models.CASCADE,
        verbose_name=_('Project'),
    )
    start_date = models.DateField(verbose_name=_('Start date'))
    end_date = models.DateField(verbose_name=_('End date'))

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

    requirements_software = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Software name and versions'),
        verbose_name=_('Software Requirements'),
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

    document = models.FileField(
        verbose_name=_('Upload Supporting Documents'),
        upload_to="documents/%Y/%m/%d/%M/",
        blank=True,
        null=True,
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
        verbose_name=_('Reason for the system allocation status decision:'),
        help_text=_('The reason will be emailed to the project\'s technical lead upon project status update.'),
    )
    notes = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Internal notes'),
        verbose_name=_('Notes'),
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Created time'))
    modified_time = models.DateTimeField(auto_now=True, verbose_name=_('Modified time'))

    history = HistoricalRecords()

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


class ProjectSystemAllocation(models.Model):

    class Meta:
        verbose_name_plural = _('Project System Allocations')
        unique_together = (('project', 'system'), )

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

    history = HistoricalRecords()

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
    initiated_by_user = models.BooleanField(
        default=True,
        verbose_name=_('Initiated by User'),
        help_text=_('Determines who needs to approve the membership. The initating user is assumend to have approved it.'),
    )
    date_joined = models.DateField()
    date_left = models.DateField(default=datetime.date.max)
    created_time = models.DateTimeField(auto_now_add=True)
    approved_time = models.DateField(default=datetime.date.max)
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

    def is_user_editable(self):
        ''' Check if the user is allowed to edit current state '''
        allowed_states = [
            ProjectUserMembership.AWAITING_AUTHORISATION,
            ProjectUserMembership.AUTHORISED,
            ProjectUserMembership.DECLINED,
        ]
        condition = not self.initiated_by_user and self.status in allowed_states
        return condition

    def is_owner_editable(self):
        ''' Check if the tech lead is allowed to edit current state '''
        forbidden_states = [
            ProjectUserMembership.AWAITING_AUTHORISATION,
            ProjectUserMembership.DECLINED,
        ]
        condition = self.initiated_by_user or self.status not in forbidden_states
        return condition

    def reset_status(self):
        """
        Reset the current status to the previous status.
        """
        self.status = self.previous_status
        self.save()

    history = HistoricalRecords()

    def __str__(self):
        data = {
            'user': self.user,
            'project': self.project,
            'date_joined': self.date_joined,
            'date_left': self.date_left
        }
        return _('{user} on {project} from {date_joined} to {date_left}').format(**data)
