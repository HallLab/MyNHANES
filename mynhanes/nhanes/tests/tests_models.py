from django.test import TestCase
import pytest
import json
# from django.utils import timezone
from ..models import NHANESCycle, NHANESDataset, NHANESField, FieldMetadata, \
    NHANESData, DatasetMetadata


# TESTS FOR NHANESCycle MODEL
@pytest.mark.django_db
class TestNHANESCycle(TestCase):
    def setUp(self):
        self.cycle = NHANESCycle.objects.create(
            cycle_name="2017-2018",
            base_dir="/path/to/data",
            year_code="J",
            base_url='https://wwwn.cdc.gov/Nchs/Nhanes',
            dataset_url_pattern='%s/%s/%s_%s.XPT'
        )

    def test_cycle_creation(self):
        """
        Test that the NHANESCycle was created correctly.
        """
        assert NHANESCycle.objects.count() == 1
        assert self.cycle.cycle_name == "2017-2018"
        assert self.cycle.base_dir == "/path/to/data"
        assert self.cycle.year_code == "J"
        assert self.cycle.base_url == 'https://wwwn.cdc.gov/Nchs/Nhanes'
        assert self.cycle.dataset_url_pattern == '%s/%s/%s_%s.XPT'

        # Test the __str__ method
        assert str(self.cycle) == '2017-2018'

        # # Test the get_dataset_url method
        dataset_url = self.cycle.get_dataset_url('DEMO')
        expected_url = 'https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.XPT'
        assert dataset_url == expected_url

        # Test the ordering Meta option
        assert NHANESCycle.objects.all().order_by('cycle_name').first() == self.cycle  # noqa E501

    def test_cycle_update(self):
        """
        Test that the NHANESCycle can be updated correctly.
        """
        self.cycle.cycle_name = "2019-2020"
        self.cycle.save()
        assert self.cycle.cycle_name == "2019-2020"

    def test_cycle_delete(self):
        """
        Test that the NHANESCycle can be deleted correctly.
        """
        self.cycle.delete()
        assert NHANESCycle.objects.count() == 0


# TESTS FOR NHANESDataset MODEL
@pytest.mark.django_db
class TestNHANESDataset(TestCase):
    def setUp(self):
        self.dataset = NHANESDataset.objects.create(
            name="DEMO",
            description="Demographic Variables and Sample Weights",
            is_download=True,
        )

    def test_dataset_creation(self):
        """
        Test that the NHANESDataset was created correctly.
        """
        assert NHANESDataset.objects.count() == 1
        assert self.dataset.name == "DEMO"
        assert self.dataset.description == "Demographic Variables and Sample Weights"   # noqa E501
        assert self.dataset.is_download is True

    def test_dataset_update(self):
        """
        Test that the NHANESDataset can be updated correctly.
        """
        self.dataset.name = "DEMO_ALT"
        self.dataset.save()
        assert self.dataset.name == "DEMO_ALT"

    def test_dataset_delete(self):
        """
        Test that the NHANESDataset can be deleted correctly.
        """
        self.dataset.delete()
        assert NHANESDataset.objects.count() == 0


# TESTS FOR DatasetMetadata MODEL
@pytest.mark.django_db
class TestDatasetMetadata(TestCase):
    def setUp(self):
        self.cycle = NHANESCycle.objects.create(
            cycle_name="2017-2018",
            base_dir="/path/to/data",
            year_code="J",
            base_url='https://wwwn.cdc.gov/Nchs/Nhanes',
            dataset_url_pattern='%s/%s/%s_%s.XPT'
        )
        self.dataset = NHANESDataset.objects.create(
            name="DEMO",
            description="Demographic Variables and Sample Weights",
            is_download=True,
        )
        self.metadata = DatasetMetadata.objects.create(
            dataset=self.dataset,
            cycle=self.cycle,
            metadata_url="https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.htm",   # noqa E501
            description="This is a test metadata",
            status="complete",
        )

    def test_metadata_creation(self):
        """
        Test that the DatasetMetadata was created correctly.
        """
        assert DatasetMetadata.objects.count() == 1
        assert self.metadata.dataset == self.dataset
        assert self.metadata.cycle == self.cycle
        assert self.metadata.metadata_url == "https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.htm"   # noqa E501
        assert self.metadata.description == "This is a test metadata"
        assert self.metadata.status == "complete"

    def test_metadata_update(self):
        """
        Test that the DatasetMetadata can be updated correctly.
        """
        self.metadata.description = "Updated description"
        self.metadata.save()
        assert self.metadata.description == "Updated description"

    def test_metadata_delete(self):
        """
        Test that the DatasetMetadata can be deleted correctly.
        """
        self.metadata.delete()
        assert DatasetMetadata.objects.count() == 0


# TESTS FOR NHANESField MODEL
@pytest.mark.django_db
class TestNHANESField(TestCase):
    def setUp(self):
        self.dataset = NHANESDataset.objects.create(
            name="DEMO",
            description="Demographic Variables and Sample Weights",
            is_download=True,
        )
        self.field = NHANESField.objects.create(
            dataset=self.dataset,
            name="RIAGENDR",
            internal_id="Gender",
            description="Gender of the participant."
        )

    def test_field_creation(self):
        """
        Test that the NHANESField was created correctly.
        """
        assert NHANESField.objects.count() == 1
        assert self.field.dataset == self.dataset
        assert self.field.name == "RIAGENDR"
        assert self.field.internal_id == "Gender"
        assert self.field.description == "Gender of the participant."

    def test_field_update(self):
        """
        Test that the NHANESField can be updated correctly.
        """
        self.field.name = "Field 2"
        self.field.save()
        assert self.field.name == "Field 2"

    def test_field_delete(self):
        """
        Test that the NHANESField can be deleted correctly.
        """
        self.field.delete()
        assert NHANESField.objects.count() == 0


# TESTS FOR FieldMetadata MODEL
@pytest.mark.django_db
class TestFieldMetadata(TestCase):
    def setUp(self):
        self.cycle = NHANESCycle.objects.create(
            cycle_name="2017-2018",
            base_dir="/path/to/data",
            year_code="J",
            base_url='https://wwwn.cdc.gov/Nchs/Nhanes',
            dataset_url_pattern='%s/%s/%s_%s.XPT'
        )
        self.dataset = NHANESDataset.objects.create(
            name="DEMO",
            description="Demographic Variables and Sample Weights",
            is_download=True,
        )
        self.field = NHANESField.objects.create(
            dataset=self.dataset,
            name="RIAGENDR",
            internal_id="Gender",
            description="Gender of the participant."
        )
        data = {
            "Variable Name": "RIAGENDR",
            "SAS Label": "Gender",
            "English Text": "Gender of the participant.",
            "Target": "Both males and females 0 YEARS - 150 YEARS",
            "Values": [
                {"Code": "1", "Value Description": "Male", "Count": 4557, "Cumulative": 4557, "Skip to Item": ""},  # noqa E501
                {"Code": "2", "Value Description": "Female", "Count": 4697, "Cumulative": 9254, "Skip to Item": ""},  # noqa E501
                {"Code": ".", "Value Description": "Missing", "Count": 0, "Cumulative": 9254, "Skip to Item": ""}  # noqa E501
            ]
        }
        self.json_string = json.dumps(data, indent=4)
        self.metadata = FieldMetadata.objects.create(
            field=self.field,
            cycle=self.cycle,
            variable_name="RIAGENDR",
            sas_label="Gender",
            english_text="Gender of the participant.",
            target="Both males and females 0 YEARS - 150 YEARS",
            type="Binary",
            value_table=self.json_string,
        )

    def test_metadata_creation(self):
        """
        Test that the FieldMetadata was created correctly.
        """
        assert FieldMetadata.objects.count() == 1
        assert self.metadata.field == self.field
        assert self.metadata.cycle == self.cycle
        assert self.metadata.variable_name == "RIAGENDR"
        assert self.metadata.sas_label == "Gender"
        assert self.metadata.english_text == "Gender of the participant."
        assert self.metadata.target == "Both males and females 0 YEARS - 150 YEARS"  # noqa E501
        assert self.metadata.type == "Binary"
        data = {
            "Variable Name": "RIAGENDR",
            "SAS Label": "Gender",
            "English Text": "Gender of the participant.",
            "Target": "Both males and females 0 YEARS - 150 YEARS",
            "Values": [
                {"Code": "1", "Value Description": "Male", "Count": 4557, "Cumulative": 4557, "Skip to Item": ""}, # noqa E501
                {"Code": "2", "Value Description": "Female", "Count": 4697, "Cumulative": 9254, "Skip to Item": ""}, # noqa E501
                {"Code": ".", "Value Description": "Missing", "Count": 0, "Cumulative": 9254, "Skip to Item": ""} # noqa E501
            ]
        }
        self.json_string = json.dumps(data, indent=4)
        assert self.metadata.value_table == self.json_string

    def test_metadata_update(self):
        """
        Test that the FieldMetadata can be updated correctly.
        """
        self.metadata.variable_name = "Var2"
        self.metadata.save()
        assert self.metadata.variable_name == "Var2"

    def test_metadata_delete(self):
        """
        Test that the FieldMetadata can be deleted correctly.
        """
        self.metadata.delete()
        assert FieldMetadata.objects.count() == 0


# TESTS FOR NHANESData MODEL
@pytest.mark.django_db
class TestNHANESData(TestCase):
    def setUp(self):
        self.cycle = NHANESCycle.objects.create(
            cycle_name="2017-2018",
            base_dir="/path/to/data",
            year_code="J",
            base_url='https://wwwn.cdc.gov/Nchs/Nhanes',
            dataset_url_pattern='%s/%s/%s_%s.XPT'
        )
        self.dataset = NHANESDataset.objects.create(
            name="DEMO",
            description="Demographic Variables and Sample Weights",
            is_download=True,
        )
        self.field = NHANESField.objects.create(
            dataset=self.dataset,
            name="RIAGENDR",
            internal_id="Gender",
            description="Gender of the participant."
        )
        self.data = NHANESData.objects.create(
            dataset=self.dataset,
            cycle=self.cycle,
            field=self.field,
            internal_id=self.field.internal_id,
            sample="1",
            value="1"
        )

    def test_data_creation(self):
        """
        Test that the NHANESData was created correctly.
        """
        assert NHANESData.objects.count() == 1
        assert self.data.dataset == self.dataset
        assert self.data.cycle == self.cycle
        assert self.data.field == self.field
        assert self.data.value == "1"

    def test_data_update(self):
        """
        Test that the NHANESData can be updated correctly.
        """
        self.data.value = "Value2"
        self.data.save()
        assert self.data.value == "Value2"

    def test_data_delete(self):
        """
        Test that the NHANESData can be deleted correctly.
        """
        self.data.delete()
        assert NHANESData.objects.count() == 0
