import datetime
import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from simple_history.models import HistoricalRecords

from funding.models import Attribution
from openldap.api import project_membership_api
from project.notifications import project_created_notification
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

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Project(models.Model):

    class Meta:
        verbose_name_plural = _('Projects')

    title = models.CharField(
        max_length=256,
        verbose_name=_('Project Title'),
        help_text=_("Write a one-line description of the work you will be doing in this project."),
    )
    description = models.TextField(
        max_length=1024,
        verbose_name=_('Project Description'),
        help_text=_("Write an abstract for the research that you will be doing in this project, including a description of what sort of computations will be done."),
    )
    legacy_hpcw_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Legacy HPC Wales ID'),
        help_text=_('If the project previously made use of the HPC Wales facilities, enter the ID here.'),
    )
    legacy_arcca_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Legacy ARCCA ID'),
        help_text=_('If the project has previously made use of ARCCA resources and has an ARCCA ID, enter it here'),
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
        help_text=_(' If your institution assigns identifiers to research projects, enter the identifier for this project here'),
    )
    department = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_('Department'),
        help_text= ('Enter the department or other division of the university that the project will be based in'),
    )
    pi_legacy = models.CharField(
        max_length=256,
        verbose_name=_("[Deprecated]Principal Investigator's name, position and email"),
    )
    supervisor_name = models.CharField(
        max_length=256,
        verbose_name=_("Project Leader's name"),
        help_text= ("Enter the name of the member of staff who is leading this research. This need not be you, but should be a permanent member of University staff. If this research is funded, this would typically be the local Principal Investigator on the grant."),
        blank=True,
    )
    supervisor_position = models.CharField(
        max_length=256,
        verbose_name=_("Project Leader's position"),
        help_text= (' What position does the Project Leader named above hold? (For example, Lecturer, Professor, Head of Department)'),
        blank=True,
    )
    supervisor_email = models.CharField(
        max_length=256,
        verbose_name=_("Project Leader's email"),
        help_text= ('Enter the email address of the Project Leader named above.'),
        blank=True,
    )
    approved_by_supervisor = models.BooleanField(
        default=False,
        verbose_name=_('Confirmed by Supervisor'),
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

    custom_user_cap = models.PositiveIntegerField(
        verbose_name=_('Custom user cap'),
        default=0,
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

    def can_have_more_users(self):
        if not self.custom_user_cap:
            if not self.tech_lead.profile.institution:
                return True
            elif not self.tech_lead.profile.institution.default_project_user_cap:
                return True
            elif (self.tech_lead.profile.institution.default_project_user_cap >=
                  ProjectUserMembership.objects.filter(
                      project=self,
                      status=ProjectUserMembership.AUTHORISED,
                  ).count() + 1):
                return True
            else:
                return False
        elif (self.custom_user_cap >= ProjectUserMembership.objects.filter(
                project=Project.objects.last(),
                status=ProjectUserMembership.AUTHORISED,
        ).count() + 1):
            return True
        else:
            return False

    def can_view_project(self, user):
        if ProjectUserMembership.objects.filter(
                project=self,
                status=ProjectUserMembership.AUTHORISED,
                user=user
        ).count() > 0:
            return True
        else:
            return False

    def is_approved(self):
        allocation_requests = self.get_allocation_requests()
        for allocation_request in allocation_requests:
            if allocation_request.is_approved():
                return True
        return False

    def has_allocation_request(self):
        return len(self.get_allocation_requests()) > 0

    def get_allocation_requests(self):
        return SystemAllocationRequest.objects.filter(project=self.id).order_by('-start_date')

    def get_rse_requests(self):
        return RSEAllocation.objects.filter(project=self.id).order_by('-created_time')

    # objects = ProjectManager()

    def _assign_project_owner_project_membership(self):
        try:
            project_membership, created = ProjectUserMembership.objects.get_or_create(
                project=self,
                user=self.tech_lead,
                defaults=dict(
                    date_joined=datetime.date.today(),
                    status=ProjectUserMembership.AUTHORISED,
                    previous_status=ProjectUserMembership.AUTHORISED,
                    initiated_by_user=False,
                )
            )

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

        super(Project, self).save(*args, **kwargs)

        self._assign_project_owner_project_membership()

        # Assign the 'project_owner' group to the project's technical lead
        # if it is not already assigned
        if self.tech_lead.groups.filter(name='project_owner').count() == 0:
            group = Group.objects.get(name='project_owner')
            self.tech_lead.groups.add(group)

        # If the project already exists check for changes
        if(Project.objects.filter(pk=self.id).exists()):
            current = Project.objects.get(pk=self.id)
            if self.tech_lead != current.tech_lead:
                self._remove_from_project_owner(current.tech_lead)

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
    start_date = models.DateField(verbose_name=_('Start date'), help_text= ('When do you like to start using the system for this project?'),)
    end_date = models.DateField(verbose_name=_('End date'), help_text= ('When do you anticipate being finished with the system for this project?'),)

    allocation_rse = models.BooleanField(
        default=False,
        verbose_name=_('RSE available to?'),
    )

    allocation_cputime = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('CPU time allocation in hours'),
        help_text=('How many "core-hours" do you anticipate this project needing? For example, if you have a program that only uses one CPU on your laptop, and runs for 48 hours, and you need to run it 1000 times, then this number would be 48,000; if instead it used four cores on your laptop for the same amount of time, it would be 192,000.'),
    )
    allocation_memory = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('RAM allocation in GB'),
        help_text=('How much memory will your program need at once per node? If you don\'t know this number, but know that the program runs on your computer, then enter the amount of RAM on your computer.'),
    )
    allocation_storage_home = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Home storage in GB'),
        help_text=('Home storage is long-term (although not backed up) file storage used for data you need to keep on the system for months at a time. This is subject to a quota. Enter the amount of storage you need for the longer term; 100GB is the default size.'),
        )
    allocation_storage_scratch = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Scratch storage in GB'),
        help_text=('Scratch storage is short-term file storage used for intermediary data you need temporarily, but will either delete or move off the system once it is no longer needed. There is no quota on scratch, but it is shared with other users, and when it is full, then old unused files will be deleted. Enter the amount of short-term intermediary storage you will need.'),
    )

    requirements_software = models.TextField(
        max_length=512,
        blank=True,
 #       help_text=_('Software name and versions'),
        verbose_name=_('Software Requirements'),
        help_text=('Enter details of any software you require to be installed on the system to be able to use it for your research. Examples include compilers (Intel and GNU C, C++, and Fortran compilers are available already), interpreters (Python and R are available already), open-source libraries, and commercial software (e.g. Stata, Matlab, Molpro). In addition if you require a specific version of the software then please specify this.'),
    )
    requirements_training = models.TextField(
        max_length=512,
        blank=True,
        verbose_name=_('Training Requirements'),
        help_text=('Do you require training in order to make use of the system? If so, write details of this here.'),
    )
    requirements_onboarding = models.TextField(
        max_length=512,
        blank=True,
        verbose_name=_('Onboarding Requirements'),
        help_text=('Do you require any assistance in adapting your software to be able to make use of the system? If so, write details of this here.'),
    )

    document = models.FileField(
        verbose_name=_('Upload Supporting Documents'),
        help_text=('If you have any documentation that you feel Supercomputing Wales would benefit from seeing with regards to this project, or have been asked to include some documentation in your request, please attach it here.'),
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}.{}'.format(self.project.code, self.id)


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


class RSEAllocation(models.Model):
    class meta:
        verbose_name_plural = _('Project RSE Allocations')

    title = models.CharField(
        max_length=256,
        verbose_name=_('Subproject title'),
        help_text=_(
            "A one-sentence summary of the work to be done by the RSE team."
        )
    )
    software = models.TextField(
        max_length=2000,
        verbose_name=_('Software description'),
        help_text=_(
            "The software currently in use to deliver the research outcomes. "
            "Questions to consider: Is it commercial, open-source, or in-house "
            "code? What language is it written in? What libraries does it "
            "depend on? Is it parallelised?"
        )
    )
    duration = models.DecimalField(
        decimal_places=1,
        max_digits=5,
        verbose_name=_('Estimated duration (in weeks)'),
        validators=[MinValueValidator(
            0.01,
            "Estimated duration must be a positive number of weeks."
        )]
    )
    goals = models.TextField(
        max_length=5000,
        verbose_name='Project goals',
        help_text=_(
            "Describe in as much detail as possible what you would like the "
            "RSE team to achieve. What steps are necessary to achieve this?"
        )
    )
    outcomes = models.TextField(
        max_length=2000,
        verbose_name='Project outcomes',
        help_text=_(
            "What effect will the completion of this work have on your "
            "research, e.g. in terms of publications or grants enabled? "
        )
    )
    confidentiality = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name=_('Confidentiality constraints'),
        help_text=_(
            "Is the research or code restricted from being published openly "
            "and presented at conferences and other events related to "
            "research software? If so, please describe the restrictions."
        )
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )

    AWAITING_APPROVAL = 0
    APPROVED = 1
    DECLINED = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    CLOSED = 5
    STATUS_CHOICES = (
        (AWAITING_APPROVAL, _('Awaiting Approval')),
        (APPROVED, _('Approved; awaiting RSE time')),
        (DECLINED, _('Declined')),
        (IN_PROGRESS, _('In progress')),
        (COMPLETED, _('Completed')),
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
        verbose_name=_('Reason for the RSE allocation status decision:'),
    )
    notes = models.TextField(
        max_length=512,
        blank=True,
        help_text=_('Internal notes'),
        verbose_name=_('Notes'),
    )

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    start_date = models.DateField(null=True)
    completed_date = models.DateField(null=True)

    history = HistoricalRecords()

    def __str__(self):
        data = {
            'title': self.title,
            'duration': self.duration
        }
        return _("Project to '{title}' in {duration} weeks").format(**data)


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
