# import pytest
# import django
# django.setup()
# # from django.conf import settings

# from nhanes.models import (  # noqa E402
#     Cycle,
#     Group,
#     Dataset,
#     Variable,
#     VariableCycle,
#     DatasetCycle,
#     Field,
#     NormalizationRule,
#     SystemConfig,
#     WorkProcessMasterData,
#     Tag,
# )


# @pytest.fixture
# def setup_test_data(db):
#     """Fixture to set up test data for models."""

#     # Create SystemConfig
#     SystemConfig.objects.create(
#         config_key="ALLOW_NORMALIZATION",
#         config_value=True
#         )

#     # Create WorkProcessMasterData
#     WorkProcessMasterData.objects.create(
#         component_type="rule",
#         source_file_version="v1.0",
#         status="complete"
#     )

#     # create a cycle
#     cycle_1 = Cycle.objects.create(cycle="2017-2018", year_code="A")
#     cycle_2 = Cycle.objects.create(cycle="2019-2020", year_code="B")  # noqa F481

#     # create a group
#     group_1 = Group.objects.create(
#         group="Demographics",
#         description="Demographic Data"
#         )

#     # create a dataset
#     dataset_1 = Dataset.objects.create(
#         dataset="DEMO",
#         description="Demographic Dataset",
#         group=group_1)

#     # Create a variable
#     variable_1 = Variable.objects.create(
#         variable="RIDAGEYR",
#         description="Age in Years at Screening"
#         )

#     # Create VariableCycle
#     VariableCycle.objects.create(
#         variable=variable_1,
#         cycle=cycle_1,
#         variable_name="RIDAGEYR",
#         sas_label="Age",
#         english_text="Age at screening",
#         target="Person",
#         type="Numeric",
#         value_table={"1": "18-29", "2": "30-39"}
#         )

#     # Create DatasetCycle
#     DatasetCycle.objects.create(
#         dataset=dataset_1,
#         cycle=cycle_1,
#         metadata_url="http://example.com",
#         has_special_year_code=False
#         )

#     # Create Tags
#     tag_1 = Tag.objects.create(
#         tag="demographic",
#         description="Demographic data"
#         )

#     # Create Fields
#     field_1 = Field.objects.create(
#         field="Age",
#         description="Age at screening",
#         field_type="num"
#         )
#     field_1.tags.add(tag_1)  # Adicionando a Tag ao Field

#     # Create NormalizationRule
#     normalization_rule_1 = NormalizationRule.objects.create(
#         rule="AgeNormalization",
#         version="1.0",
#         folder_path="/path/to/rules",
#         file_name="age_normalization.py"
#     )
#     normalization_rule_1.source_variables.add(variable_1)
#     normalization_rule_1.destination_fields.add(field_1)
