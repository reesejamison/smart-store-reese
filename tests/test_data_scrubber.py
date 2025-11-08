"""Test suite for the DataScrubber class.

This module contains unit tests for all DataScrubber methods to ensure
proper data cleaning functionality.
"""

import sys
import pathlib
import unittest
import pandas as pd
import numpy as np

# Add the project root to the path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analytics_project.utils.data_scrubber import DataScrubber


class TestDataScrubber(unittest.TestCase):
    """Test cases for DataScrubber class methods."""

    def setUp(self):
        """Set up test data before each test method."""
        self.sample_data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'Alice', 'David'],
            'Age': [25, 30, 35, 25, 40],
            'City': ['New York', 'Los Angeles', 'Chicago', 'New York', 'Houston'],
            'Salary': [50000, 60000, 70000, 50000, 80000]
        }
        self.df = pd.DataFrame(self.sample_data)

    def test_init(self):
        """Test DataScrubber initialization."""
        scrubber = DataScrubber(self.df)
        self.assertIsInstance(scrubber.df, pd.DataFrame)
        self.assertEqual(len(scrubber.df), 5)

    def test_remove_duplicate_records(self):
        """Test removing duplicate records."""
        scrubber = DataScrubber(self.df)
        result = scrubber.remove_duplicate_records()
        self.assertEqual(len(result), 4)  # Should remove 1 duplicate (Alice)

    def test_remove_duplicate_records_with_subset(self):
        """Test removing duplicates based on specific columns."""
        scrubber = DataScrubber(self.df)
        result = scrubber.remove_duplicate_records(subset=['Name'])
        self.assertEqual(len(result), 4)  # Should remove duplicate based on Name only

    def test_standardize_column_names(self):
        """Test standardizing column names."""
        df_with_caps = pd.DataFrame({'First Name': [1], 'LAST NAME': [2], '  Age  ': [3]})
        scrubber = DataScrubber(df_with_caps)
        result = scrubber.standardize_column_names()
        expected_columns = ['first name', 'last name', 'age']
        self.assertListEqual(list(result.columns), expected_columns)

    def test_replace_placeholders(self):
        """Test replacing placeholder values with NaN."""
        df_with_placeholders = pd.DataFrame({
            'Col1': ['value', 'N/A', 'data'],
            'Col2': ['NULL', 'value', 'none']
        })
        scrubber = DataScrubber(df_with_placeholders)
        result = scrubber.replace_placeholders()
        self.assertTrue(pd.isna(result.loc[1, 'Col1']))
        self.assertTrue(pd.isna(result.loc[0, 'Col2']))

    def test_replace_placeholders_custom(self):
        """Test replacing custom placeholder values."""
        df_custom = pd.DataFrame({'Col1': ['value', 'MISSING', 'data']})
        scrubber = DataScrubber(df_custom)
        result = scrubber.replace_placeholders(replacements={'MISSING': pd.NA})
        self.assertTrue(pd.isna(result.loc[1, 'Col1']))

    def test_standardize_text_column_lower(self):
        """Test standardizing text to lowercase."""
        df_text = pd.DataFrame({'Name': ['ALICE', 'BOB', 'CHARLIE']})
        scrubber = DataScrubber(df_text)
        result = scrubber.standardize_text_column('Name', case='lower')
        self.assertEqual(result.loc[0, 'Name'], 'alice')

    def test_standardize_text_column_upper(self):
        """Test standardizing text to uppercase."""
        df_text = pd.DataFrame({'Name': ['alice', 'bob', 'charlie']})
        scrubber = DataScrubber(df_text)
        result = scrubber.standardize_text_column('Name', case='upper')
        self.assertEqual(result.loc[0, 'Name'], 'ALICE')

    def test_standardize_text_column_title(self):
        """Test standardizing text to title case."""
        df_text = pd.DataFrame({'Name': ['alice smith', 'bob jones']})
        scrubber = DataScrubber(df_text)
        result = scrubber.standardize_text_column('Name', case='title')
        self.assertEqual(result.loc[0, 'Name'], 'Alice Smith')

    def test_check_data_consistency_before_cleaning(self):
        """Test checking data consistency before cleaning."""
        df_with_issues = pd.DataFrame({
            'Col1': [1, 2, np.nan, 2],
            'Col2': [4, 5, 6, 5]
        })
        scrubber = DataScrubber(df_with_issues)
        result = scrubber.check_data_consistency_before_cleaning()
        self.assertIn('null_counts', result)
        self.assertIn('duplicate_count', result)
        self.assertEqual(result['duplicate_count'], 1)

    def test_convert_column_to_new_data_type(self):
        """Test converting column data type."""
        df_convert = pd.DataFrame({'Age': ['25', '30', '35']})
        scrubber = DataScrubber(df_convert)
        result = scrubber.convert_column_to_new_data_type('Age', int)
        self.assertEqual(result['Age'].dtype, np.int64)

    def test_convert_column_invalid_raises_error(self):
        """Test that converting non-existent column raises ValueError."""
        scrubber = DataScrubber(self.df)
        with self.assertRaises(ValueError):
            scrubber.convert_column_to_new_data_type('NonExistent', int)

    def test_drop_columns(self):
        """Test dropping columns."""
        scrubber = DataScrubber(self.df)
        result = scrubber.drop_columns(['City', 'Salary'])
        self.assertEqual(len(result.columns), 2)
        self.assertNotIn('City', result.columns)
        self.assertNotIn('Salary', result.columns)

    def test_drop_columns_invalid_raises_error(self):
        """Test that dropping non-existent column raises ValueError."""
        scrubber = DataScrubber(self.df)
        with self.assertRaises(ValueError):
            scrubber.drop_columns(['NonExistent'])

    def test_filter_column_outliers(self):
        """Test filtering outliers."""
        df_outliers = pd.DataFrame({'Value': [1, 2, 3, 100, 4, 5]})
        scrubber = DataScrubber(df_outliers)
        result = scrubber.filter_column_outliers('Value', 1, 10)
        self.assertEqual(len(result), 5)  # Should remove the outlier (100)

    def test_filter_column_outliers_invalid_raises_error(self):
        """Test that filtering non-existent column raises ValueError."""
        scrubber = DataScrubber(self.df)
        with self.assertRaises(ValueError):
            scrubber.filter_column_outliers('NonExistent', 0, 100)

    def test_format_column_strings_to_lower_and_trim(self):
        """Test formatting strings to lowercase and trimming."""
        df_format = pd.DataFrame({'Name': ['  ALICE  ', '  BOB  ']})
        scrubber = DataScrubber(df_format)
        result = scrubber.format_column_strings_to_lower_and_trim('Name')
        self.assertEqual(result.loc[0, 'Name'], 'alice')

    def test_format_column_strings_to_upper_and_trim(self):
        """Test formatting strings to uppercase and trimming."""
        df_format = pd.DataFrame({'Name': ['  alice  ', '  bob  ']})
        scrubber = DataScrubber(df_format)
        result = scrubber.format_column_strings_to_upper_and_trim('Name')
        self.assertEqual(result.loc[0, 'Name'], 'ALICE')

    def test_handle_missing_data_drop(self):
        """Test handling missing data by dropping rows."""
        df_missing = pd.DataFrame({'Col1': [1, np.nan, 3], 'Col2': [4, 5, np.nan]})
        scrubber = DataScrubber(df_missing)
        result = scrubber.handle_missing_data(drop=True)
        self.assertEqual(len(result), 1)  # Only one complete row

    def test_handle_missing_data_fill(self):
        """Test handling missing data by filling with value."""
        df_missing = pd.DataFrame({'Col1': [1, np.nan, 3], 'Col2': [4, 5, np.nan]})
        scrubber = DataScrubber(df_missing)
        result = scrubber.handle_missing_data(fill_value=0)
        self.assertEqual(result.loc[1, 'Col1'], 0)
        self.assertEqual(result.loc[2, 'Col2'], 0)

    def test_inspect_data(self):
        """Test data inspection."""
        scrubber = DataScrubber(self.df)
        info_str, describe_str = scrubber.inspect_data()
        self.assertIsInstance(info_str, str)
        self.assertIsInstance(describe_str, str)
        self.assertIn('Name', info_str)

    def test_parse_dates_to_add_standard_datetime(self):
        """Test parsing dates to StandardDateTime."""
        df_dates = pd.DataFrame({'Date': ['2023-01-01', '2023-01-02', '2023-01-03']})
        scrubber = DataScrubber(df_dates)
        result = scrubber.parse_dates_to_add_standard_datetime('Date')
        self.assertIn('StandardDateTime', result.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['StandardDateTime']))

    def test_parse_dates_invalid_raises_error(self):
        """Test that parsing non-existent column raises ValueError."""
        scrubber = DataScrubber(self.df)
        with self.assertRaises(ValueError):
            scrubber.parse_dates_to_add_standard_datetime('NonExistent')

    def test_rename_columns(self):
        """Test renaming columns."""
        scrubber = DataScrubber(self.df)
        result = scrubber.rename_columns({'Name': 'FullName', 'Age': 'Years'})
        self.assertIn('FullName', result.columns)
        self.assertIn('Years', result.columns)
        self.assertNotIn('Name', result.columns)
        self.assertNotIn('Age', result.columns)

    def test_rename_columns_invalid_raises_error(self):
        """Test that renaming non-existent column raises ValueError."""
        scrubber = DataScrubber(self.df)
        with self.assertRaises(ValueError):
            scrubber.rename_columns({'NonExistent': 'NewName'})

    def test_reorder_columns(self):
        """Test reordering columns."""
        scrubber = DataScrubber(self.df)
        new_order = ['Salary', 'City', 'Age', 'Name']
        result = scrubber.reorder_columns(new_order)
        self.assertListEqual(list(result.columns), new_order)

    def test_reorder_columns_invalid_raises_error(self):
        """Test that reordering with non-existent column raises ValueError."""
        scrubber = DataScrubber(self.df)
        with self.assertRaises(ValueError):
            scrubber.reorder_columns(['Name', 'NonExistent'])

    def test_get_dataframe(self):
        """Test getting the dataframe."""
        scrubber = DataScrubber(self.df)
        result = scrubber.get_dataframe()
        self.assertIsInstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, self.df)

    def test_method_chaining(self):
        """Test that methods can be chained."""
        df_chain = pd.DataFrame({
            'Name': ['ALICE', 'BOB', 'ALICE'],
            'Age': [25, 30, 25]
        })
        scrubber = DataScrubber(df_chain)
        scrubber.remove_duplicate_records()
        result = scrubber.standardize_text_column('Name', case='lower')
        self.assertEqual(len(result), 2)
        self.assertEqual(result.loc[0, 'Name'], 'alice')


if __name__ == '__main__':
    unittest.main()
