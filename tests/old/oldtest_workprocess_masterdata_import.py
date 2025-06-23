# import pytest
# from nhanes.models import (
#     Cycle,
#     Group,
#     Dataset,
#     Variable,
#     VariableCycle,
#     DatasetCycle,
#     Field,
#     NormalizationRule,
#     SystemConfig,
#     WorkProcessMasterData
# )
# from mynhanes.nhanes.workprocess.masterdata_import import masterdata_import


# @pytest.mark.django_db
# def test_workprocess_masterdata_import():
#     """Test the download_and_insert_data function with real CSV data from GitHub."""

#     # Call the function to download and insert data from GitHub
#     masterdata_import()

#     # Assertions to ensure data has been inserted
#     assert Cycle.objects.count() > 0
#     assert Group.objects.count() > 0
#     assert Dataset.objects.count() > 0
#     assert Variable.objects.count() > 0
#     assert VariableCycle.objects.count() > 0
#     assert DatasetCycle.objects.count() > 0
#     assert Field.objects.count() > 0
#     assert NormalizationRule.objects.count() > 0
#     assert SystemConfig.objects.count() > 0
#     assert WorkProcessMasterData.objects.count() > 0

#     # Additional assertions to check specific data values
#     assert Cycle.objects.filter(cycle="2017-2018").exists()
#     assert Group.objects.filter(group="Demographics").exists()
#     assert Dataset.objects.filter(dataset="DEMO").exists()
#     assert Variable.objects.filter(variable="RIDAGEYR").exists()
#     assert Field.objects.filter(field="Age").exists()
#     assert NormalizationRule.objects.filter(
#         rule="AgeNormalization",
#         version="1.0"
#         ).exists()
