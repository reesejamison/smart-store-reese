# Data Preparation Scripts

This folder contains Python scripts for cleaning and preparing raw data for ETL processes.

## Structure

```
src/analytics_project/
├── data_preparation/
│   ├── __init__.py
│   ├── prepare_customers_data.py
│   ├── prepare_products_data.py
│   └── prepare_sales_data.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── data_scrubber.py
```

## Scripts Overview

### 1. `prepare_customers_data.py`
Cleans customer data including:
- Remove duplicates based on CustomerID
- Handle missing values (drop critical fields, fill others)
- Standardize Region and PreferredContact values
- Remove outliers (invalid loyalty points, dates)

### 2. `prepare_products_data.py`
Cleans product data including:
- Remove duplicates based on ProductID
- Handle missing values (drop critical fields, fill others)
- Standardize Category and Supplier values
- Remove outliers (invalid prices, stock quantities)

### 3. `prepare_sales_data.py`
Cleans sales data including:
- Remove duplicates based on TransactionID
- Handle missing values (drop critical fields, fill others)
- Standardize PaymentType values
- Remove outliers (invalid amounts, discounts, dates)

## Utility Modules

### `utils/logger.py`
Centralized logging configuration using Loguru. Creates log files in `logs/` directory.

### `utils/data_scrubber.py`
Reusable data cleaning class with methods for:
- Removing duplicates
- Replacing placeholder values (N/A, null, unknown, etc.)
- Standardizing text columns
- Standardizing column names

## How to Run

### From Project Root:
```bash
# Activate virtual environment first
source venv/Scripts/activate  # On Windows with Git Bash
# or
venv\Scripts\activate  # On Windows CMD

# Run individual scripts
python src/analytics_project/data_preparation/prepare_customers_data.py
python src/analytics_project/data_preparation/prepare_products_data.py
python src/analytics_project/data_preparation/prepare_sales_data.py
```

### From the data_preparation directory:
```bash
cd src/analytics_project/data_preparation
python prepare_customers_data.py
python prepare_products_data.py
python prepare_sales_data.py
```

## Input/Output

- **Input**: Raw CSV files from `data/raw/`
  - `customers_data.csv`
  - `products_data.csv`
  - `sales_data.csv`

- **Output**: Cleaned CSV files to `data/prepared/`
  - `customers_prepared.csv`
  - `products_prepared.csv`
  - `sales_prepared.csv`

- **Logs**: Detailed logs in `logs/`
  - `prepare_customers.log`
  - `prepare_products.log`
  - `prepare_sales.log`

## Data Quality Rules

### Customers
- **Required fields**: CustomerID, Name, JoinDate
- **Filled defaults**: Region (Unknown), LoyaltyPoints (0), PreferredContact (Email)
- **Outlier rules**:
  - LoyaltyPoints: 0 to 10,000
  - JoinDate: 2010-01-01 to today

### Products
- **Required fields**: ProductID, ProductName, UnitPrice
- **Filled defaults**: Category (Uncategorized), StockQuantity (0), Supplier (Unknown)
- **Outlier rules**:
  - UnitPrice: > 0 and <= 10,000
  - StockQuantity: 0 to 2,000

### Sales
- **Required fields**: TransactionID, SaleDate, CustomerID, ProductID, StoreID, SaleAmount
- **Filled defaults**: CampaignID (0), DiscountPercent (0), PaymentType (Unknown)
- **Outlier rules**:
  - SaleAmount: 0 to 50,000
  - DiscountPercent: 0 to 100
  - SaleDate: 2020-01-01 to today

## Dependencies

Required Python packages (install via `pip install -r requirements.txt`):
- pandas
- loguru
