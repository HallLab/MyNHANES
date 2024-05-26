import os
import tempfile
# from unittest.mock import patch
from django.test import TestCase
from nhanes.models import NHANESData, NHANESCycle, NHANESDataset, NHANESField, NHANESGroup  # noqa E501
from nhanes.services.consult import export_to_csv, extract_data
import pytest


@pytest.mark.django_db
class TestExportToCsv(TestCase):
    def setUp(self):
        self.cycle = NHANESCycle.objects.create(
            cycle_name="2017-2018",
            base_dir="/path/to/data",
            year_code="J",
            base_url='https://wwwn.cdc.gov/Nchs/Nhanes',
            dataset_url_pattern='%s/%s/%s_%s.XPT'
        )
        self.group = NHANESGroup.objects.create(
            name="Demographics",
            description="Group 1 description",
        )
        self.dataset = NHANESDataset.objects.create(
            name="DEMO",
            description="Demographic Variables and Sample Weights",
            is_download=True,
            group=self.group,
        )
        self.field_1 = NHANESField.objects.create(
            dataset=self.dataset,
            name="RIAGENDR",
            internal_id="Gender",
            description="Gender of the participant."
        )
        self.field_2 = NHANESField.objects.create(
            dataset=self.dataset,
            name="RIAGENDR_TEST",
            internal_id="TESTE",
            description="TESTE of the participant."
        )
        self.data = [
            NHANESData(cycle=self.cycle, dataset=self.dataset, field=self.field_1, sample="1", value="Value 1"),  # noqa E501
            NHANESData(cycle=self.cycle, dataset=self.dataset, field=self.field_1, sample="2", value="Value 2"),  # noqa E501
            NHANESData(cycle=self.cycle, dataset=self.dataset, field=self.field_1, sample="3", value="Value 3"),  # noqa E501
            NHANESData(cycle=self.cycle, dataset=self.dataset, field=self.field_2, sample="1", value="AAA"),  # noqa E501
            NHANESData(cycle=self.cycle, dataset=self.dataset, field=self.field_2, sample="2", value="BBB"),  # noqa E501
            NHANESData(cycle=self.cycle, dataset=self.dataset, field=self.field_2, sample="3", value="CCC"),  # noqa E501
        ]
        NHANESData.objects.bulk_create(self.data)

    def test_export_to_csv_with_filters(self):
        filters = [
            {
                'field': 'field__name',
                'operator': 'icontains',
                'value': 'RIAGENDR',
            },
        ]
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
            export_to_csv(filters, filename)
            with open(filename, 'r') as csv_file:
                lines = csv_file.readlines()
                self.assertEqual(len(lines), 4)  # Including the header
                self.assertIn("cycle,dataset,field,sample,value\n", lines)
                self.assertIn("2017-2018,DEMO,RIAGENDR,1,Value 1\n", lines)
                self.assertIn("2017-2018,DEMO,RIAGENDR,2,Value 2\n", lines)
                self.assertIn("2017-2018,DEMO,RIAGENDR,3,Value 3\n", lines)
        os.remove(filename)

    def test_export_to_csv_without_filters(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
            export_to_csv(None, filename)
            with open(filename, 'r') as csv_file:
                lines = csv_file.readlines()
                self.assertEqual(len(lines), 4)  # Including the header
                self.assertIn("cycle,dataset,field,sample,value\n", lines)
                self.assertIn("2017-2018,DEMO,RIAGENDR,1,Value 1\n", lines)
                self.assertIn("2017-2018,DEMO,RIAGENDR,2,Value 2\n", lines)
                self.assertIn("2017-2018,DEMO,RIAGENDR,3,Value 3\n", lines)
        os.remove(filename)

    # Meu Teste
    def test_extract_data(self):
        filters = [
            {
                'field': 'field__dataset__group__name',
                'operator': 'icontains',
                'value': 'Demographics',
            },
        ]
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
            extract_data(filters, filename)
            with open(filename, 'r') as csv_file:
                lines = csv_file.readlines()
                self.assertEqual(len(lines), 4)  # Including the header
                self.assertIn("cycle__cycle_name,dataset__name,sample,RIAGENDR,RIAGENDR_TEST\n", lines)
                self.assertIn("2017-2018,DEMO,1,Value 1,AAA\n", lines)
                self.assertIn("2017-2018,DEMO,2,Value 2,BBB\n", lines)
                self.assertIn("2017-2018,DEMO,3,Value 3,CCC\n", lines)
        os.remove(filename)
