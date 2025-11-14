"""Utility class for common data cleaning tasks.

Provides reusable methods for removing duplicates, handling missing values,
and standardizing data formats.

This class provides methods for:
- Checking data consistency
- Removing duplicates
- Handling missing values
- Filtering outliers
- Renaming and reordering columns
- Formatting strings
- Parsing date fields

Use this class to perform similar cleaning operations across multiple files.

Example:
    from analytics_project.utils.data_scrubber import DataScrubber

    scrubber = DataScrubber(df)
    df = scrubber.remove_duplicate_records().handle_missing_data(fill_value="N/A")
"""

import io
import pandas as pd
from typing import Dict, Tuple, Union, List
from loguru import logger


class DataScrubber:
    """
    A utility class for cleaning and scrubbing pandas DataFrames.

    This class provides methods for common data cleaning tasks such as
    removing duplicates, handling missing values, and standardizing data.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataScrubber with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to clean.
        """
        self.df = df.copy()  # Work with a copy to avoid modifying the original

    def remove_duplicate_records(self, subset=None, keep='first') -> pd.DataFrame:
        """
        Remove duplicate rows from the DataFrame.

        Args:
            subset (list, optional): Column labels to consider for identifying duplicates.
                                    If None, all columns are used.
            keep (str): Determines which duplicates to keep.
                       'first': Keep first occurrence (default)
                       'last': Keep last occurrence
                       False: Drop all duplicates

        Returns:
            pd.DataFrame: DataFrame with duplicates removed.
        """
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_count - len(self.df)

        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate records")
        else:
            logger.info("No duplicate records found")

        return self.df

    def standardize_column_names(self) -> pd.DataFrame:
        """
        Standardize column names by stripping whitespace and converting to lowercase.

        Returns:
            pd.DataFrame: DataFrame with standardized column names.
        """
        original_columns = self.df.columns.tolist()
        self.df.columns = self.df.columns.str.strip().str.lower()

        changed = [
            f"{old} -> {new}"
            for old, new in zip(original_columns, self.df.columns, strict=True)
            if old != new
        ]
        if changed:
            logger.info(f"Standardized column names: {', '.join(changed)}")

        return self.df

    def replace_placeholders(self, replacements: dict = None) -> pd.DataFrame:
        """
        Replace common placeholder values with NaN.

        Args:
            replacements (dict, optional): Dictionary of values to replace with NaN.
                                          If None, uses default placeholders.

        Returns:
            pd.DataFrame: DataFrame with placeholders replaced.
        """
        if replacements is None:
            # Default common placeholders
            replacements = {
                'N/A': pd.NA,
                'n/a': pd.NA,
                'NA': pd.NA,
                'null': pd.NA,
                'NULL': pd.NA,
                'None': pd.NA,
                'none': pd.NA,
                '': pd.NA,
                ' ': pd.NA,
                'unknown': pd.NA,
                'Unknown': pd.NA,
                'UNKNOWN': pd.NA,
            }

        self.df.replace(replacements, inplace=True)
        logger.info(f"Replaced placeholder values with NaN")

        return self.df

    def standardize_text_column(self, column: str, case: str = 'title') -> pd.DataFrame:
        """
        Standardize text in a specific column.

        Args:
            column (str): Name of the column to standardize.
            case (str): Case to convert to ('lower', 'upper', 'title').

        Returns:
            pd.DataFrame: DataFrame with standardized text column.
        """
        if column not in self.df.columns:
            logger.warning(f"Column '{column}' not found in DataFrame")
            return self.df

        # Strip whitespace first
        self.df[column] = self.df[column].astype(str).str.strip()

        # Apply case transformation
        if case == 'lower':
            self.df[column] = self.df[column].str.lower()
        elif case == 'upper':
            self.df[column] = self.df[column].str.upper()
        elif case == 'title':
            self.df[column] = self.df[column].str.title()

        logger.info(f"Standardized text in column '{column}' to {case} case")

        return self.df

    def check_data_consistency_before_cleaning(self) -> Dict[str, Union[pd.Series, int]]:
        """
        Check data consistency before cleaning by calculating counts of null and duplicate entries.

        Returns:
            dict: Dictionary with counts of null values and duplicate rows.
        """
        null_counts = self.df.isnull().sum()
        duplicate_count = self.df.duplicated().sum()
        logger.info(
            f"Before cleaning - Null values: {null_counts.sum()}, Duplicates: {duplicate_count}"
        )
        return {'null_counts': null_counts, 'duplicate_count': duplicate_count}

    def check_data_consistency_after_cleaning(self) -> Dict[str, Union[pd.Series, int]]:
        """
        Check data consistency after cleaning to ensure there are no null or duplicate entries.

        Returns:
            dict: Dictionary with counts of null values and duplicate rows,
                  expected to be zero for each.
        """
        null_counts = self.df.isnull().sum()
        duplicate_count = self.df.duplicated().sum()
        assert null_counts.sum() == 0, "Data still contains null values after cleaning."
        assert duplicate_count == 0, "Data still contains duplicate records after cleaning."
        logger.info("After cleaning - Data is clean (no nulls or duplicates)")
        return {'null_counts': null_counts, 'duplicate_count': duplicate_count}

    def convert_column_to_new_data_type(self, column: str, new_type: type) -> pd.DataFrame:
        """
        Convert a specified column to a new data type.

        Args:
            column (str): Name of the column to convert.
            new_type (type): The target data type (e.g., 'int', 'float', 'str').

        Returns:
            pd.DataFrame: Updated DataFrame with the column type converted.

        Raises:
            ValueError: If the specified column not found in the DataFrame.
        """
        try:
            self.df[column] = self.df[column].astype(new_type)
            logger.info(f"Converted column '{column}' to {new_type}")
            return self.df
        except KeyError:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from None

    def drop_columns(self, columns: List[str]) -> pd.DataFrame:
        """
        Drop specified columns from the DataFrame.

        Args:
            columns (list): List of column names to drop.

        Returns:
            pd.DataFrame: Updated DataFrame with specified columns removed.

        Raises:
            ValueError: If a specified column is not found in the DataFrame.
        """
        for column in columns:
            if column not in self.df.columns:
                raise ValueError(f"Column name '{column}' not found in the DataFrame.")
        self.df = self.df.drop(columns=columns)
        logger.info(f"Dropped columns: {', '.join(columns)}")
        return self.df

    def filter_column_outliers(
        self, column: str, lower_bound: Union[float, int], upper_bound: Union[float, int]
    ) -> pd.DataFrame:
        """
        Filter outliers in a specified column based on lower and upper bounds.

        Args:
            column (str): Name of the column to filter for outliers.
            lower_bound (float or int): Lower threshold for outlier filtering.
            upper_bound (float or int): Upper threshold for outlier filtering.

        Returns:
            pd.DataFrame: Updated DataFrame with outliers filtered out.

        Raises:
            ValueError: If the specified column not found in the DataFrame.
        """
        try:
            initial_count = len(self.df)
            self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]
            removed_count = initial_count - len(self.df)
            logger.info(f"Filtered {removed_count} outliers from column '{column}'")
            return self.df
        except KeyError:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from None

    def format_column_strings_to_lower_and_trim(self, column: str) -> pd.DataFrame:
        """
        Format strings in a specified column by converting to lowercase and trimming whitespace.

        Args:
            column (str): Name of the column to format.

        Returns:
            pd.DataFrame: Updated DataFrame with formatted string column.

        Raises:
            ValueError: If the specified column not found in the DataFrame.
        """
        try:
            self.df[column] = self.df[column].str.lower().str.strip()
            logger.info(f"Formatted column '{column}' to lowercase and trimmed")
            return self.df
        except KeyError:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from None

    def format_column_strings_to_upper_and_trim(self, column: str) -> pd.DataFrame:
        """
        Format strings in a specified column by converting to uppercase and trimming whitespace.

        Args:
            column (str): Name of the column to format.

        Returns:
            pd.DataFrame: Updated DataFrame with formatted string column.

        Raises:
            ValueError: If the specified column not found in the DataFrame.
        """
        try:
            self.df[column] = self.df[column].str.upper().str.strip()
            logger.info(f"Formatted column '{column}' to uppercase and trimmed")
            return self.df
        except KeyError:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from None

    def handle_missing_data(
        self, drop: bool = False, fill_value: Union[None, float, int, str] = None
    ) -> pd.DataFrame:
        """
        Handle missing data in the DataFrame.

        Args:
            drop (bool, optional): If True, drop rows with missing values. Default is False.
            fill_value (any, optional): Value to fill in for missing entries if drop is False.

        Returns:
            pd.DataFrame: Updated DataFrame with missing data handled.
        """
        if drop:
            initial_count = len(self.df)
            self.df = self.df.dropna()
            removed_count = initial_count - len(self.df)
            logger.info(f"Dropped {removed_count} rows with missing values")
        elif fill_value is not None:
            self.df = self.df.fillna(fill_value)
            logger.info(f"Filled missing values with: {fill_value}")
        return self.df

    def inspect_data(self) -> Tuple[str, str]:
        """
        Inspect the data by providing DataFrame information and summary statistics.

        Returns:
            tuple: (info_str, describe_str), where `info_str` is a string representation
                   of DataFrame.info() and `describe_str` is a string representation of
                   DataFrame.describe().
        """
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()
        describe_str = self.df.describe().to_string()
        logger.info("Data inspection completed")
        return info_str, describe_str

    def parse_dates_to_add_standard_datetime(self, column: str) -> pd.DataFrame:
        """
        Parse a specified column as datetime format and add it as a new column named 'StandardDateTime'.

        Args:
            column (str): Name of the column to parse as datetime.

        Returns:
            pd.DataFrame: Updated DataFrame with a new 'StandardDateTime' column
                         containing parsed datetime values.

        Raises:
            ValueError: If the specified column not found in the DataFrame.
        """
        try:
            self.df['StandardDateTime'] = pd.to_datetime(self.df[column])
            logger.info(f"Parsed column '{column}' to StandardDateTime")
            return self.df
        except KeyError:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from None

    def rename_columns(self, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Rename columns in the DataFrame based on a provided mapping.

        Args:
            column_mapping (dict): Dictionary where keys are old column names and values are new names.

        Returns:
            pd.DataFrame: Updated DataFrame with renamed columns.

        Raises:
            ValueError: If a specified column is not found in the DataFrame.
        """
        for old_name in column_mapping:
            if old_name not in self.df.columns:
                raise ValueError(f"Column '{old_name}' not found in the DataFrame.")
        self.df = self.df.rename(columns=column_mapping)
        logger.info(f"Renamed columns: {column_mapping}")
        return self.df

    def reorder_columns(self, columns: List[str]) -> pd.DataFrame:
        """
        Reorder columns in the DataFrame based on the specified order.

        Args:
            columns (list): List of column names in the desired order.

        Returns:
            pd.DataFrame: Updated DataFrame with reordered columns.

        Raises:
            ValueError: If a specified column is not found in the DataFrame.
        """
        for column in columns:
            if column not in self.df.columns:
                raise ValueError(f"Column name '{column}' not found in the DataFrame.")
        self.df = self.df[columns]
        logger.info(f"Reordered columns to: {', '.join(columns)}")
        return self.df

    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the current state of the DataFrame.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        return self.df
