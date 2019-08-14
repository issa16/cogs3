from collections import namedtuple
from datetime import date, timedelta
import os
import tempfile
import shutil
import filecmp

from pandas import to_numeric
from django.test import TestCase
from django.conf import settings

import numpy as np

from funding.models import FundingSource
from priority.management.commands.calculate_priority import (
    update_SlurmPriority_and_Project_tables,
    get_priority_attribution_data,
    read_raw_sacct_dump,
    read_and_aggregate_sacct_dump,
    calculate_priority,
    Command
)
from priority.models import SlurmPriority
from project.models import Project
from users.models import CustomUser

Pandas = namedtuple(
    'Pandas',
    [
        'account',
        'attribution_points',
        'quality_of_service',
        'cpu_hours_to_date',
        'gpu_hours_to_date',
        'prioritised_cpu_hours',
        'prioritised_gpu_hours'
    ]
)


class PriorityCommandTests(TestCase):
    dump_file = os.path.join(
            settings.BASE_DIR, 'priority/tests/test_dump.dat'
    )

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]


class ReadSacctDumpTests(PriorityCommandTests, TestCase):
    def test_read_raw_sacct_dump(self):
        '''
        Test that sacct dumps are correctly read into Pandas DataFrames.
        '''
        expected_columns = {
            'JobName', 'TotalCPU', 'CPUTimeHours', 'CPUTimeRAW',
            'JobID', 'Account', 'Partition'
        }
        data = read_raw_sacct_dump(self.dump_file)

        self.assertEqual(len(data), 51)
        self.assertGreaterEqual(set(data.columns), expected_columns)
        try:
            to_numeric(data.JobID)
        except ValueError:
            self.fail("Jobs don't appear to be filtered to allocations only.")

    def test_read_and_aggregate_sacct_dump(self):
        '''
        Test that sacct dumps correctly read in are then correctly
        aggregated into per-account CPU and GPU totals.
        '''
        expected_cpu_data = (
            ('scw0000', 229),
            ('scw0001', 80865),
            ('scw0002', 48544),
            ('scw1000', 67)
        )
        expected_gpu_data = (('scw0001', 20438), ('scw0002', 1985))

        cpu_data, gpu_data = read_and_aggregate_sacct_dump(self.dump_file)
        self.assertEqual(tuple(cpu_data.itertuples()), expected_cpu_data)
        self.assertEqual(tuple(gpu_data.itertuples()), expected_gpu_data)


class PriorityCalculationTests(PriorityCommandTests, TestCase):
    def test_calculate_priority(self):
        expected_priorities = (
            (0, 1050000, 4, 'scw0000'),
            (1, 50000, 3, 'scw0001'),
            (2, 50000, 3, 'scw0002'),
            (3, 50000, 3, 'scw1000')
        )
        test_columns = ['attribution_points',
                        'quality_of_service',
                        'account']
        expected_columns = {'attribution_points',
                            'quality_of_service',
                            'account',
                            'cpu_hours_to_date',
                            'gpu_hours_to_date',
                            'prioritised_cpu_hours',
                            'prioritised_gpu_hours'}

        # Generate enough disparity to see more than one QoS
        FundingSource.objects.filter(title='Test funding source').update(
            amount=1000000
        )
        priority_attribution_data = get_priority_attribution_data()
        sacct_data = read_and_aggregate_sacct_dump(self.dump_file)
        calculated_priority = calculate_priority(priority_attribution_data,
                                                 sacct_data)

        self.assertGreaterEqual(set(calculated_priority.columns),
                                expected_columns)
        self.assertEqual(tuple(calculated_priority[test_columns].itertuples()),
                         expected_priorities)


class CalculatePriorityCommandTests(PriorityCommandTests, TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_command(self):
        # Generate enough disparity to see more than one QoS
        FundingSource.objects.filter(title='Test funding source').update(
            amount=1000000
        )

        # Specify output location and check file is not present
        out_file = os.path.join(self.test_dir, 'test_priority_data.psv')
        self.assertFalse(os.path.exists(out_file))

        # Run command and check output file is created
        Command.handle(None, input_file=self.dump_file, output_file=out_file)
        self.assertTrue(os.path.exists(out_file))
        self.assertTrue(os.path.join(settings.BASE_DIR,
                                     'priority/tests/test_priority_data.psv'),
                        out_file)


class TableUpdateTests(PriorityCommandTests, TestCase):
    def test_update_new_record(self):
        '''
        Test that the method correctly creates new entries in the SlurmPriority
        table and updates the Project table.
        '''
        accounts = [
            {
                'record': Pandas('scw0000', 62000, 2, 1000, 10, 500, 0),
                'project': Project.objects.get(code='scw0000')
            },
            {
                'record': Pandas('invalid', 50000, 1, 100000, 1000, 0, 0),
                'project': None
            }
        ]
        for account in accounts:
            # Check no objects already exist
            self.assertFalse(
                SlurmPriority.objects.filter(account=account['record'].account)
                .exists()
            )

            update_SlurmPriority_and_Project_tables(account['record'])

            new_priority = SlurmPriority.objects.get(
                account=account['record'].account
            )
            self.assertEqual(new_priority.project, account['project'])
            for key, expected_value in account['record']._asdict().items():
                if key == 'code':
                    continue
                self.assertEqual(getattr(new_priority, key),
                                 expected_value)

            if account['project']:
                account['project'].refresh_from_db()
                self.assertEqual(account['project'].active_attribution_points,
                                 account['record'].attribution_points)
                self.assertEqual(account['project'].quality_of_service,
                                 account['record'].quality_of_service)

    def test_update_existing_record(self):
        '''
        Test that the method correctly updates existing entries for today
        in the SlurmPriority table and updates the Project table.
        '''
        old_record = Pandas('scw0000', 62000, 2, 1000, 10, 500, 0)
        new_record = Pandas('scw0000', 80000, 3, 1500, 11, 1000, 1)

        # Create initial state with old record present; check it's there
        update_SlurmPriority_and_Project_tables(old_record)
        self.assertTrue(
            SlurmPriority.objects.filter(account='scw0000').exists()
        )

        # Update the record with new information
        update_SlurmPriority_and_Project_tables(new_record)

        # Check it's correct
        new_priority = SlurmPriority.objects.get(account='scw0000')

        project = Project.objects.get(code='scw0000')
        self.assertEqual(new_priority.project, project)
        for key, expected_value in new_record._asdict().items():
            if key == 'code':
                continue
            self.assertEqual(getattr(new_priority, key), expected_value)

        self.assertEqual(project.active_attribution_points, 80000)
        self.assertEqual(project.quality_of_service, 3)


class PriorityAttributionDataTests(PriorityCommandTests, TestCase):
    def test_get_priority_attribution_data_empty_db(self):
        expected_data = [
            (0, 'scw0000', 62000, 0.0, 0.0, 0.0, 0.0, 0.0, 1, 40),
            (1, 'scw0001', 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0),
            (2, 'scw0002', 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0)
        ]
        actual_data = get_priority_attribution_data()
        for expected_datum, actual_datum in zip(expected_data,
                                                actual_data.itertuples()):
            self.assertEqual(expected_datum, actual_datum)

    def test_get_priority_attribution_data_with_existing_data(self):
        # Construct some plausible data
        original_data = get_priority_attribution_data()
        for field, lower_bound, upper_bound in (
                ('cpu_hours_to_date', 1000, 1500),
                ('gpu_hours_to_date', 1000, 1500),
                ('prioritised_cpu_hours', 0, 500),
                ('prioritised_gpu_hours', 0, 500),
                ('QOS', 1, 5)
        ):
            original_data[field] = np.random.randint(
                low=lower_bound,
                high=upper_bound,
                size=len(original_data)
            )

        # Save this data in the database for yesterday
        for project_record in original_data.itertuples():
            update_SlurmPriority_and_Project_tables(
                project_record,
                override_date=date.today() - timedelta(1)
            )

        # Check that it reads back correctly
        actual_data = get_priority_attribution_data()
        for original_record in original_data.itertuples():
            # Check data from SlurmPriority table
            for field in (
                    'cpu_hours_to_date',
                    'gpu_hours_to_date',
                    'prioritised_cpu_hours',
                    'prioritised_gpu_hours',
                    'quality_of_service',
                    'attribution_points'
            ):
                self.assertEqual(
                    actual_data[
                        actual_data.account == original_record.account
                    ][field].values,
                    getattr(original_record, field)
                )

            # Check joined Institution data matches the database
            self.assertEqual(
                Project.objects.get(code=original_record.account)
                .tech_lead.profile.institution.AP_per_CPU_hour,
                actual_data[
                    actual_data.account == original_record.account
                ].AP_per_CPU_hour.values
            )
            self.assertEqual(
                Project.objects.get(code=original_record.account)
                .tech_lead.profile.institution.AP_per_GPU_hour,
                actual_data[
                    actual_data.account == original_record.account
                ].AP_per_GPU_hour.values
            )

    def test_get_priority_attribution_data_with_new_project(self):
        '''
        Checks that correct and complete information are returned when
        a project has just been created; i.e. is in the Project table but
        not in the SlurmPriority table.
        '''

        # Get a starting point
        original_data = get_priority_attribution_data()

        # Make sure that the tech lead of a project is from an institution
        # with defined AP_per_CPU_hour, AP_per_GPU_hour, and then remove
        # the project
        account = original_data.at[2, 'account']
        project = Project.objects.get(code=account)
        project.tech_lead = CustomUser.objects.get(
            email='shibboleth.user@example.ac.uk'
        )
        project.save()
        original_data = original_data.drop(2)

        # Now construct some plausible data
        for field, lower_bound, upper_bound in (
                ('cpu_hours_to_date', 1000, 1500),
                ('gpu_hours_to_date', 1000, 1500),
                ('prioritised_cpu_hours', 0, 500),
                ('prioritised_gpu_hours', 0, 500),
                ('quality_of_service', 1, 5)
        ):
            original_data[field] = np.random.randint(
                low=lower_bound,
                high=upper_bound,
                size=len(original_data)
            )

        # Save this data in the database for yesterday
        for project_record in original_data.itertuples():
            update_SlurmPriority_and_Project_tables(
                project_record,
                override_date=date.today() - timedelta(1)
            )

        # Check that it reads back correctly
        actual_data = get_priority_attribution_data()
        project_record = actual_data[actual_data.account == account]

        for key in (
                'cpu_hours_to_date',
                'gpu_hours_to_date',
                'prioritised_cpu_hours',
                'prioritised_gpu_hours',
                'quality_of_service'
        ):
            self.assertEqual(project_record[key].values, 0)

        self.assertEqual(
            project_record.AP_per_CPU_hour.values,
            project.tech_lead.profile.institution.AP_per_CPU_hour
        )
        self.assertEqual(
            project_record.AP_per_GPU_hour.values,
            project.tech_lead.profile.institution.AP_per_GPU_hour
        )
