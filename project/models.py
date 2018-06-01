import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

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
        verbose_name_plural = _('Project Categories')
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
        verbose_name_plural = _('Project Funding Sources')
        ordering = ('name', )


class Project(models.Model):
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
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text=_('Institution project is based'),
        verbose_name=_('Institution'),
    )
    institution_reference = models.CharField(
        max_length=128,
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
    start_date = models.DateField(verbose_name=_('Start date'), )
    end_date = models.DateField(verbose_name=_('End date'), )
    economic_user = models.BooleanField(
        default=False,
        verbose_name=_('Economic user'),
    )
    requirements_software = models.TextField(
        max_length=512,
        help_text=_('Software name and versions'),
        verbose_name=_('Requirements software'),
    )
    requirements_gateways = models.TextField(
        max_length=512,
        help_text=_('Web gateway or portal name and versions'),
        verbose_name=_('Requirements gateways'),
    )
    requirements_training = models.TextField(max_length=512, verbose_name=_('Requirements training'))
    requirements_onboarding = models.TextField(max_length=512, verbose_name=_('Requirements onboarding'))
    allocation_rse = models.BooleanField(
        default=False,
        verbose_name=_('RSE available to?'),
    )
    allocation_cputime = models.PositiveIntegerField(verbose_name=_('CPU time allocation in hours'))
    allocation_memory = models.PositiveIntegerField(verbose_name=_('RAM allocation in GB'))
    allocation_storage_home = models.PositiveIntegerField(verbose_name=_('Home storage in GB'))
    allocation_storage_scratch = models.PositiveIntegerField(verbose_name=_('Scratch storage in GB'))
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
    notes = models.TextField(max_length=512, blank=True, help_text=_('Internal project notes'), verbose_name=_('Notes'))
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

    def notify_status_change(self, status, reason=''):
        """ Generate an email to inform the user about a status change """
        status = self.STATUS_CHOICES[status-1][1]
        title = 'Supercomputing Wales Project %s' % status

        message = 'Your project request "%s" has been %s.' % (self.title, status.lower())
        if reason != '':
            message += '\n\n%s' % reason
        self.tech_lead.notify(title, message)


    def __str__(self):
        data = {
            'code': self.code,
            'title': self.title,
        }
        return '{code} - {title}'.format(**data)

    def save(self):
        if self.id:
            current = Project.objects.get(pk=self.id)
            status_changed = self.status != current.status
            if self.reason_decision == current.reason_decision:
                self.reason_decision = ''
            if status_changed:
                self.notify_status_change(self.status, self.reason_decision)
        super(Project, self).save()

    class Meta:
        verbose_name_plural = _('Projects')


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
    CREATE = 1
    CREATED = 2
    DEACTIVATE = 3
    DEACTIVATED = 4
    STATUS_CHOICES = (
        (CREATE, 'Create System Resources'),
        (CREATED, 'Created System Resources'),
        (DEACTIVATE, 'Deactivate System Resources'),
        (DEACTIVATED, 'Deactivated System Resources'),
    )
    openldap_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=CREATE,
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


    def notify_status_change(self, status):
        """ Notify the user about a status change """
        status_text = self.STATUS_CHOICES[status-1][1]
        title = 'Supercomputing Wales Project Membership'

        message = 'Your membership status in the project titled "%s" has been set to %s.' % (self.project.title, status_text.lower())
        self.user.notify(title, message)

    def __str__(self):
        data = {
            'user': self.user,
            'project': self.project,
            'date_joined': self.date_joined,
            'date_left': self.date_left
        }
        return _('{user} on {project} from {date_joined} to {date_left}').format(**data)

    class Meta:
        verbose_name_plural = _('Project User Memberships')
        unique_together = ('project', 'user')

    def save(self, *args, **kwargs):
        if self.id:
            current = ProjectUserMembership.objects.get(pk=self.id)
            status_changed = self.status != current.status
            if status_changed:
                self.notify_status_change(self.status)
        super(ProjectUserMembership, self).save(*args, **kwargs)
