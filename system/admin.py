from django.contrib import admin

from system.models import Application
from system.models import AccessMethod
from system.models import OperatingSystem
from system.models import Partition
from system.models import System
from system.models import HardwareGroup


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'modified_time',
    )


@admin.register(AccessMethod)
class AccessMethodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'modified_time',
    )


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'number_of_cores',
        'modified_time',
    )


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'modified_time',
    )


@admin.register(HardwareGroup)
class HardwareGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'total_number_of_cores',
        'system',
        'modified_time',
    )


@admin.register(Partition)
class PartitionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'system',
        'os',
        'cores_per_node',
        'modified_time',
    )
