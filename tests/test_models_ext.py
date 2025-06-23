from django.test import TestCase
from nhanes.models import Version, Cycle, Group, Dataset, Tag


class VersionTest(TestCase):
    fixtures = ['tests/fixtures/version_fixture.json']

    def test_version_loade_ext(self):
        version = Version.objects.get(pk=1)
        self.assertEqual(version.version, "nhanes")


class CycleTest(TestCase):
    fixtures = ['tests/fixtures/cycle_fixture.json']

    def test_cycle_loade_ext(self):
        cycle = Cycle.objects.get(pk=10)
        self.assertEqual(cycle.cycle, "2017-2018")
        self.assertEqual(cycle.year_code, "J")
        self.assertEqual(cycle.base_url, "https://wwwn.cdc.gov/Nchs/Nhanes")
        self.assertEqual(cycle.dataset_url_pattern, "%s/%s/%s")


class GroupTest(TestCase):
    fixtures = ['tests/fixtures/group_fixture.json']

    def test_group_loade_ext(self):
        group = Group.objects.get(pk=1)
        self.assertEqual(group.group, "Demographics")


class TagTest(TestCase):
    fixtures = ['tests/fixtures/tag_fixture.json']

    def test_tag_loade_ext(self):
        tag = Tag.objects.get(pk=1)
        self.assertEqual(tag.tag, "Demographics")


class DatasetTest(TestCase):
    fixtures = [
        'tests/fixtures/group_fixture.json',
        'tests/fixtures/dataset_fixture.json'
    ]

    def test_dataset_loade_ext(self):
        dataset = Dataset.objects.get(pk=1)
        self.assertEqual(dataset.dataset, "DEMO")

# TODO: Create other tests for the remaining models.
