"""
data_preparation/prepare_sales_data.py

This script reads sales data from the data/raw folder, cleans the data,
and writes the cleaned version to the data/prepared folder.

Tasks:
- Remove duplicates
- Handle missing values
- Remove outliers (unrealistic amounts/discounts)
- Ensure consistent formatting

To run this script from the project root:
    python -m src.analytics_project.data_preparation.prepare_sales_data

Or navigate to this directory and run:
    python prepare_sales_data.py
"""

#####################################
# Import Modules at the Top
#####################################

# Import from Python Standard Library
import pathlib
import sys

# Import from external packages (requires a virtual environment)
import pandas as pd

# Ensure project root is in sys.path for local imports
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import local modules
from src.analytics_project.utils.logger import logger, configure_logger
from src.analytics_project.utils.data_scrubber import DataScrubber

# Configure logger for this script
configure_logger("prepare_sales")

# Constants
SCRIPTS_DATA_PREP_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR: pathlib.Path = SCRIPTS_DATA_PREP_DIR.parent
DATA_DIR: pathlib.Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: pathlib.Path = DATA_DIR / "raw"
PREPARED_DATA_DIR: pathlib.Path = DATA_DIR / "prepared"

# Ensure the directories exist or create them
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)

#####################################
# Define Functions - Reusable blocks of code / instructions
#####################################

def read_raw_data(file_name: str) -> pd.DataFrame:
    """Read raw data from CSV."""
    file_path: pathlib.Path = RAW_DATA_DIR.joinpath(file_name)
    try:
        logger.info(f"READING: {file_path}")
        return pd.read_csv(file_path)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    """
    Save cleaned data to CSV.

    Args:
        df (pd.DataFrame): Cleaned DataFrame.
        file_name (str): Name of the output file.
    """
    logger.info(f"FUNCTION START: save_prepared_data with file_name={file_name}, dataframe shape={df.shape}")
    file_path = PREPARED_DATA_DIR.joinpath(file_name)
    df.to_csv(file_path, index=False)
    logger.info(f"Data saved to {file_path}")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from the DataFrame.

    For sales, we consider duplicates based on TransactionID.
    If there are duplicate TransactionIDs, we keep the first occurrence.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicates removed.
    """
    logger.info(f"FUNCTION START: remove_duplicates with dataframe shape={df.shape}")

    # Create an instance of the DataScrubber class
    df_scrubber = DataScrubber(df)

    # Remove duplicates based on TransactionID
    df_deduped = df_scrubber.remove_duplicate_records(subset=['TransactionID'], keep='first')

    logger.info(f"Original dataframe shape: {df.shape}")
    logger.info(f"Deduped  dataframe shape: {df_deduped.shape}")
    return df_deduped


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values by filling or dropping.

    Business Rules for Sales:
    - TransactionID: Required, drop rows without it
    - SaleDate: Required, drop rows without it
    - CustomerID: Required, drop rows without it
    - ProductID: Required, drop rows without it
    - StoreID: Required, drop rows without it
    - CampaignID: Fill with 0 (no campaign)
    - SaleAmount: Required, drop rows without it
    - DiscountPercent: Fill with 0 (no discount)
    - PaymentType: Fill with 'Unknown'

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
    """
    logger.info(f"FUNCTION START: handle_missing_values with dataframe shape={df.shape}")

    # Log missing values count before handling
    missing_before = df.isna().sum()
    logger.info(f"Missing values before handling:\n{missing_before[missing_before > 0]}")

    # Replace common placeholders with NaN
    scrubber = DataScrubber(df)
    df = scrubber.replace_placeholders()

    # Convert DiscountPercent to numeric, coercing errors to NaN
    df['DiscountPercent'] = pd.to_numeric(df['DiscountPercent'], errors='coerce')

    # Drop rows missing critical fields
    initial_count = len(df)
    critical_fields = ['TransactionID', 'SaleDate', 'CustomerID', 'ProductID', 'StoreID', 'SaleAmount']
    df.dropna(subset=critical_fields, inplace=True)
    dropped = initial_count - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with missing critical fields")

    # Fill non-critical missing values
    df = df.fillna({
        'CampaignID': 0,
        'DiscountPercent': 0,
        'PaymentType': 'Unknown'
    })

    # Log missing values count after handling
    missing_after = df.isna().sum()
    if missing_after.sum() > 0:
        logger.warning(f"Missing values after handling:\n{missing_after[missing_after > 0]}")
    else:
        logger.info("All missing values handled successfully")

    logger.info(f"{len(df)} records remaining after handling missing values")
    return df


def standardize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize data formats and values.

    - Standardize PaymentType values (title case)
    - Ensure date format is correct
    - Ensure numeric types are correct
    - Trim whitespace from string columns

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized data.
    """
    logger.info(f"FUNCTION START: standardize_data with dataframe shape={df.shape}")

    # Standardize PaymentType values
    payment_mapping = {
        'cash': 'Cash',
        'CASH': 'Cash',
        'credit card': 'Credit Card',
        'CREDIT CARD': 'Credit Card',
        'debit card': 'Debit Card',
        'DEBIT CARD': 'Debit Card',
        'check': 'Check',
        'CHECK': 'Check',
        'paypal': 'PayPal',
        'PAYPAL': 'PayPal',
        'gift card': 'Gift Card',
        'GIFT CARD': 'Gift Card'
    }
    df['PaymentType'] = df['PaymentType'].str.strip().replace(payment_mapping)
    logger.info(f"Standardized PaymentType values: {df['PaymentType'].unique()}")

    # Convert SaleDate to datetime
    df['SaleDate'] = pd.to_datetime(df['SaleDate'], errors='coerce')

    # Ensure numeric columns are correct type (using to_numeric with coerce for safety)
    df['TransactionID'] = pd.to_numeric(df['TransactionID'], errors='coerce').astype(int)
    df['CustomerID'] = pd.to_numeric(df['CustomerID'], errors='coerce').astype(int)
    df['ProductID'] = pd.to_numeric(df['ProductID'], errors='coerce').astype(int)
    df['StoreID'] = pd.to_numeric(df['StoreID'], errors='coerce').astype(int)
    df['CampaignID'] = pd.to_numeric(df['CampaignID'], errors='coerce').astype(int)
    df['SaleAmount'] = pd.to_numeric(df['SaleAmount'], errors='coerce')
    df['DiscountPercent'] = pd.to_numeric(df['DiscountPercent'], errors='coerce')

    # Drop rows where SaleAmount conversion failed (critical field)
    initial_count = len(df)
    df.dropna(subset=['SaleAmount'], inplace=True)
    dropped = initial_count - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with invalid SaleAmount values")

    # Fill missing DiscountPercent with 0 (already done in handle_missing_values, but just in case)
    df['DiscountPercent'] = df['DiscountPercent'].fillna(0)

    logger.info("Data standardization complete")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers based on business rules.

    Business Rules for Sales:
    - SaleAmount should be >= 0 and <= 50,000 (reasonable transaction)
    - DiscountPercent should be >= 0 and <= 100 (valid percentage)
    - SaleDate should be between 2020-01-01 and today

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with outliers removed.
    """
    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)

    # Remove negative sale amounts
    before = len(df)
    df = df[df['SaleAmount'] >= 0]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with negative SaleAmount")

    # Remove unreasonably high sale amounts (> 50,000)
    before = len(df)
    df = df[df['SaleAmount'] <= 50000]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with SaleAmount > 50,000")

    # Remove invalid discount percentages (< 0 or > 100)
    before = len(df)
    df = df[(df['DiscountPercent'] >= 0) & (df['DiscountPercent'] <= 100)]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with invalid DiscountPercent")

    # Remove sale dates before 2020 or in the future
    before = len(df)
    df = df[df['SaleDate'] >= '2020-01-01']
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with SaleDate before 2020")

    before = len(df)
    df = df[df['SaleDate'] <= pd.Timestamp.now()]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with SaleDate in the future")

    total_removed = initial_count - len(df)
    logger.info(f"Removed {total_removed} outlier rows total")
    logger.info(f"{len(df)} records remaining after removing outliers")
    return df


#####################################
# Define Main Function - The main entry point of the script
#####################################

def main() -> None:
    """
    Main function for processing sales data.
    """
    logger.info("=" * 50)
    logger.info("STARTING prepare_sales_data.py")
    logger.info("=" * 50)

    logger.info(f"Project Root : {PROJECT_ROOT}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")

    input_file = "sales_data.csv"
    output_file = "sales_prepared.csv"

    # Read raw data
    df = read_raw_data(input_file)

    if df.empty:
        logger.error("No data to process. Exiting.")
        return

    # Record original shape
    original_shape = df.shape

    # Log initial dataframe information
    logger.info(f"Initial dataframe columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Initial dataframe shape: {df.shape}")

    # Clean column names
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip()

    # Log if any column names changed
    changed_columns = [f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new]
    if changed_columns:
        logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

    # Remove duplicates
    df = remove_duplicates(df)

    # Handle missing values
    df = handle_missing_values(df)

    # Standardize data
    df = standardize_data(df)

    # Remove outliers
    df = remove_outliers(df)

    # Save prepared data
    save_prepared_data(df, output_file)

    logger.info("=" * 50)
    logger.info(f"Original shape: {original_shape}")
    logger.info(f"Cleaned shape:  {df.shape}")
    logger.info(f"Records removed: {original_shape[0] - df.shape[0]}")
    logger.info("=" * 50)
    logger.info("FINISHED prepare_sales_data.py")
    logger.info("=" * 50)

#####################################
# Conditional Execution Block
# Ensures the script runs only when executed directly
# This is a common Python convention.
#####################################

if __name__ == "__main__":
    main()
