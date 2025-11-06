"""
utils/data_scrubber.py

Utility class for common data cleaning tasks.
Provides reusable methods for removing duplicates, handling missing values,
and standardizing data formats.
"""

import pandas as pd
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

        changed = [f"{old} -> {new}" for old, new in zip(original_columns, self.df.columns) if old != new]
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
                'UNKNOWN': pd.NA
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
