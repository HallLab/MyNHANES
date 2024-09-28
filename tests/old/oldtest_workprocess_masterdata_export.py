# import pytest
# import pandas as pd

# from mynhanes.nhanes.workprocess.masterdata_export import masterdata_export


# @pytest.mark.django_db
# def test_workprocess_masterdata_export(setup_test_data, tmpdir):
#     """Test the export_masterdata function."""

#     # Use temporary directory for output
#     export_dir = tmpdir.mkdir("masterdata")

#     # Call the function to export data
#     result = masterdata_export(folder=export_dir)

#     # Assert the function returned True
#     assert result is True

#     # Check that CSV files are created
#     expected_files = [
#         'cycles.csv',
#         'groups.csv',
#         'datasets.csv',
#         'variables.csv',
#         'variable_cycles.csv',
#         'dataset_cycles.csv',
#         'fields.csv',
#         'normalization_rules.csv',
#         'system_config.csv',
#         'work_process_master_data.csv',
#         # 'tags.csv',
#     ]

#     for file_name in expected_files:
#         file_path = export_dir / file_name
#         assert file_path.exists(), f"{file_name} was not created."

#     # Check the content of one of the files (e.g., cycles.csv)
#     df = pd.read_csv(export_dir / 'cycles.csv')
#     assert len(df) == 2
#     assert df['cycle'].iloc[0] == '2017-2018'
#     assert df['year_code'].iloc[0] == 'A'

#     # Remove the temporary directory after the test
#     tmpdir.remove(ignore_errors=True)


# def test_dummy():
#     assert True
