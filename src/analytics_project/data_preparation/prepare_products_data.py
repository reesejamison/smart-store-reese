"""
data_preparation/prepare_products_data.py

This script reads product data from the data/raw folder, cleans the data,
and writes the cleaned version to the data/prepared folder.

Tasks:
- Remove duplicates
- Handle missing values
- Remove outliers (unrealistic prices/quantities)
- Ensure consistent formatting

To run this script from the project root:
    python -m src.analytics_project.data_preparation.prepare_products_data

Or navigate to this directory and run:
    python prepare_products_data.py
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
configure_logger("prepare_products")

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

    For products, we consider duplicates based on ProductID.
    If there are duplicate ProductIDs, we keep the first occurrence.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicates removed.
    """
    logger.info(f"FUNCTION START: remove_duplicates with dataframe shape={df.shape}")

    # Create an instance of the DataScrubber class
    df_scrubber = DataScrubber(df)

    # Remove duplicates based on ProductID
    df_deduped = df_scrubber.remove_duplicate_records(subset=['ProductID'], keep='first')

    logger.info(f"Original dataframe shape: {df.shape}")
    logger.info(f"Deduped  dataframe shape: {df_deduped.shape}")
    return df_deduped


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values by filling or dropping.

    Business Rules for Products:
    - ProductID: Required, drop rows without it
    - ProductName: Required, drop rows without it
    - Category: Fill with 'Uncategorized'
    - UnitPrice: Required, drop rows without it
    - StockQuantity: Fill with 0 (out of stock)
    - Supplier: Fill with 'Unknown'

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

    # Convert StockQuantity to numeric, coercing errors to NaN
    df['StockQuantity'] = pd.to_numeric(df['StockQuantity'], errors='coerce')

    # Drop rows missing critical fields
    initial_count = len(df)
    df.dropna(subset=['ProductID', 'ProductName', 'UnitPrice'], inplace=True)
    dropped = initial_count - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with missing critical fields (ProductID, ProductName, or UnitPrice)")

    # Fill non-critical missing values
    df = df.fillna({
        'Category': 'Uncategorized',
        'StockQuantity': 0,
        'Supplier': 'Unknown'
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

    - Standardize Category values (title case)
    - Standardize Supplier values (title case)
    - Ensure numeric types are correct
    - Trim whitespace from string columns

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized data.
    """
    logger.info(f"FUNCTION START: standardize_data with dataframe shape={df.shape}")

    # Standardize Category values
    df['Category'] = df['Category'].str.strip().str.title()
    logger.info(f"Standardized Category values: {df['Category'].unique()}")

    # Standardize Supplier values
    supplier_mapping = {
        'globaltech': 'GlobalTech',
        'GLOBALTECH': 'GlobalTech',
        'GlobalTech': 'GlobalTech',
        'megacorp': 'MegaCorp',
        'MEGACORP': 'MegaCorp',
        'MegaCorp': 'MegaCorp',
        'bestsource': 'BestSource',
        'BESTSOURCE': 'BestSource',
        'BestSource': 'BestSource',
        'supplypro': 'SupplyPro',
        'SUPPLYPRO': 'SupplyPro',
        'SupplyPro': 'SupplyPro'
    }
    df['Supplier'] = df['Supplier'].str.strip().replace(supplier_mapping)
    logger.info(f"Standardized Supplier values: {df['Supplier'].unique()}")

    # Trim whitespace from ProductName column
    df['ProductName'] = df['ProductName'].str.strip()

    # Ensure numeric columns are correct type
    df['ProductID'] = df['ProductID'].astype(int)
    df['UnitPrice'] = df['UnitPrice'].astype(float)
    df['StockQuantity'] = df['StockQuantity'].astype(int)

    logger.info("Data standardization complete")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers based on business rules.

    Business Rules for Products:
    - UnitPrice should be > 0 and <= 10,000 (reasonable range)
    - StockQuantity should be >= 0 and <= 2,000 (reasonable inventory)

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with outliers removed.
    """
    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)

    # Remove zero or negative prices
    before = len(df)
    df = df[df['UnitPrice'] > 0]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with UnitPrice <= 0")

    # Remove unreasonably high prices (> 10,000)
    before = len(df)
    df = df[df['UnitPrice'] <= 10000]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with UnitPrice > 10,000")

    # Remove negative stock quantities
    before = len(df)
    df = df[df['StockQuantity'] >= 0]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with negative StockQuantity")

    # Remove unreasonably high stock quantities (> 2,000)
    before = len(df)
    df = df[df['StockQuantity'] <= 2000]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} rows with StockQuantity > 2,000")

    total_removed = initial_count - len(df)
    logger.info(f"Removed {total_removed} outlier rows total")
    logger.info(f"{len(df)} records remaining after removing outliers")
    return df


#####################################
# Define Main Function - The main entry point of the script
#####################################

def main() -> None:
    """
    Main function for processing product data.
    """
    logger.info("=" * 50)
    logger.info("STARTING prepare_products_data.py")
    logger.info("=" * 50)

    logger.info(f"Project Root : {PROJECT_ROOT}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")

    input_file = "products_data.csv"
    output_file = "products_prepared.csv"

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
    logger.info("FINISHED prepare_products_data.py")
    logger.info("=" * 50)

#####################################
# Conditional Execution Block
# Ensures the script runs only when executed directly
# This is a common Python convention.
#####################################

if __name__ == "__main__":
    main()
