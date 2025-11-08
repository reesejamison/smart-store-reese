# Pro Analytics 02 - Business Intelligence with Python

> A professional Python project for reading and analyzing business data using pandas DataFrames.

## Project Overview

This project demonstrates how to:
- Set up a professional Python development environment
- Read raw CSV data files into pandas DataFrames for analysis
- Use logging to track data processing steps
- Implement reusable data processing functions
- Follow professional Git workflow practices

Key files:
- `src/analytics_project/data_prep.py`: Main data preparation module
- `data/raw/*.csv`: Raw data files (customers, products, sales)
- Additional information: <https://github.com/denisecase/pro-analytics-02>
- Project organization: [STRUCTURE](./STRUCTURE.md)
- Build professional skills:
  - **Environment Management**: Every project in isolation
  - **Code Quality**: Automated checks for fewer bugs
  - **Documentation**: Use modern project documentation tools
  - **Testing**: Prove your code works
  - **Version Control**: Collaborate professionally

---

## WORKFLOW 1. Set Up Your Machine

Proper setup is critical.
Complete each step in the following guide and verify carefully.

- [SET UP MACHINE](./SET_UP_MACHINE.md)

---

## WORKFLOW 2. Set Up Your Project

After verifying your machine is set up, set up a new Python project by copying this template.
Complete each step in the following guide.

- [SET UP PROJECT](./SET_UP_PROJECT.md)

It includes the critical commands to set up your local environment (and activate it):

```shell
uv venv
uv python pin 3.12
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
uv run python --version
```

**Windows (PowerShell):**

```shell
.\.venv\Scripts\activate
```

**macOS / Linux / WSL:**

```shell
source .venv/bin/activate
```

---

## WORKFLOW 3. Daily Workflow

Please ensure that the prior steps have been verified before continuing.
When working on a project, we open just that project in VS Code.

### 3.1 Git Pull from GitHub

Always start with `git pull` to check for any changes made to the GitHub repo.

```shell
git pull
```

### 3.2 Run Checks as You Work

This mirrors real work where we typically:

1. Update dependencies (for security and compatibility).
2. Clean unused cached packages to free space.
3. Use `git add .` to stage all changes.
4. Run ruff and fix minor issues.
5. Update pre-commit periodically.
6. Run pre-commit quality checks on all code files (**twice if needed**, the first pass may fix things).
7. Run tests.

In VS Code, open your repository, then open a terminal (Terminal / New Terminal) and run the following commands one at a time to check the code.

```shell
uv sync --extra dev --extra docs --upgrade
uv cache clean
git add .
uvx ruff check --fix
uvx pre-commit autoupdate
uv run pre-commit run --all-files
git add .
uv run pytest
```

NOTE: The second `git add .` ensures any automatic fixes made by Ruff or pre-commit are included before testing or committing.

<details>
<summary>Click to see a note on best practices</summary>

`uvx` runs the latest version of a tool in an isolated cache, outside the virtual environment.
This keeps the project light and simple, but behavior can change when the tool updates.
For fully reproducible results, or when you need to use the local `.venv`, use `uv run` instead.

</details>

### 3.3 Build Project Documentation

Make sure you have current doc dependencies, then build your docs, fix any errors, and serve them locally to test.

```shell
uv run mkdocs build --strict
uv run mkdocs serve
```

- After running the serve command, the local URL of the docs will be provided. To open the site, press **CTRL and click** the provided link (at the same time) to view the documentation. On a Mac, use **CMD and click**.
- Press **CTRL c** (at the same time) to stop the hosting process.

### 3.4 Execute

This project includes demo code.
Run the demo Python modules to confirm everything is working.

In VS Code terminal, run:

```shell
uv run python -m analytics_project.demo_module_basics
uv run python -m analytics_project.demo_module_languages
uv run python -m analytics_project.demo_module_stats
uv run python -m analytics_project.demo_module_viz
```

You should see:

- Log messages in the terminal
- Greetings in several languages
- Simple statistics
- A chart window open (close the chart window to continue).

If this works, your project is ready! If not, check:

- Are you in the right folder? (All terminal commands are to be run from the root project folder.)
- Did you run the full `uv sync --extra dev --extra docs --upgrade` command?
- Are there any error messages? (ask for help with the exact error)

---

### 3.5 Local Commands I Ran

Here are the specific commands I used to set up and run this project:

```shell
# 1. Create & activate a local venv
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies (if using project tooling)
uv sync --extra dev --extra docs --upgrade

# 3. Create and run the data prep module
# Created src/analytics_project/data_prep.py in VS Code
# Then ran:
python -m analytics_project.data_prep

# 4. Git workflow - initial commit
git add .
git commit -m "add starter files"
git push -u origin main

# 5. Git workflow - README updates
git add .
git commit -m "Update README with commands"
git push
```

Notes:
- The module `main` calls `read_and_log` to load CSVs under `data/raw`
- Three DataFrames are created: customers, products, and sales
- Logging is initialized via `init_logger`; check both:
  - Terminal output for immediate feedback
  - Log file for detailed processing records
- Always run Python modules from the project root folder
- Use descriptive commit messages in present tense

---

### 3.6 Git add-commit-push to GitHub

Anytime we make working changes to code is a good time to git add-commit-push to GitHub.

1. Stage your changes with git add.
2. Commit your changes with a useful message in quotes.
3. Push your work to GitHub.

```shell
git add .
git commit -m "describe your change in quotes"
git push -u origin main
```

This will trigger the GitHub Actions workflow and publish your documentation via GitHub Pages.

### 3.6 Modify and Debug

With a working version safe in GitHub, start making changes to the code.

Before starting a new session, remember to do a `git pull` and keep your tools updated.

Each time forward progress is made, remember to git add-commit-push.

---

## WORKFLOW 4. Project 3 - Data Preparation with DataScrubber

### 4.1 Overview

Project 3 focuses on preparing data for Extract-Transform-Load (ETL) processes using a reusable `DataScrubber` class. This class provides standardized methods for common data cleaning tasks such as:

- Removing duplicate records
- Handling missing values
- Standardizing column names and text data
- Filtering outliers
- Converting data types
- Renaming and reordering columns
- Parsing dates

### 4.2 DataScrubber Class

The `DataScrubber` class is located at `src/analytics_project/utils/data_scrubber.py` and provides a modular, reusable approach to data cleaning.

**Key Methods:**
- `remove_duplicate_records()` - Remove duplicate rows
- `standardize_column_names()` - Standardize column names to lowercase
- `replace_placeholders()` - Replace common placeholder values with NaN
- `standardize_text_column()` - Standardize text to lower/upper/title case
- `handle_missing_data()` - Drop or fill missing values
- `check_data_consistency_before_cleaning()` - Check for nulls and duplicates
- `check_data_consistency_after_cleaning()` - Verify data is clean
- `convert_column_to_new_data_type()` - Convert column data types
- `drop_columns()` - Remove specified columns
- `filter_column_outliers()` - Filter outliers based on bounds
- `rename_columns()` - Rename columns based on mapping
- `reorder_columns()` - Reorder columns
- `parse_dates_to_add_standard_datetime()` - Parse dates to datetime format
- `inspect_data()` - Get DataFrame info and statistics

### 4.3 Data Preparation Scripts

Three specialized data preparation scripts use the DataScrubber class:

1. **prepare_customers_data.py** - Cleans customer data
   - Removes duplicates based on CustomerID
   - Handles missing values (fills Region, LoyaltyPoints, PreferredContact)
   - Standardizes Region and PreferredContact values
   - Removes outliers in LoyaltyPoints (< 0 or > 10,000)
   - Parses JoinDate to datetime format

2. **prepare_products_data.py** - Cleans product data
   - Removes duplicates based on ProductID
   - Handles missing values (fills Supplier with 'Unknown')
   - Standardizes Category and Supplier values
   - Removes outliers in StockQuantity (< 0 or > 2,000)
   - Validates UnitPrice is positive

3. **prepare_sales_data.py** - Cleans sales data
   - Removes duplicates based on TransactionID
   - Handles missing values (fills CampaignID, DiscountPercent, PaymentType)
   - Standardizes PaymentType values
   - Removes outliers in DiscountPercent (< 0 or > 100)
   - Validates SaleDate is after 2020
   - Parses SaleDate to datetime format

### 4.4 Running Data Preparation

To clean and prepare all three data files, run these commands from the project root:

```shell
# Prepare customers data
python -m src.analytics_project.data_preparation.prepare_customers_data

# Prepare products data
python -m src.analytics_project.data_preparation.prepare_products_data

# Prepare sales data
python -m src.analytics_project.data_preparation.prepare_sales_data
```

**Results:**
- Cleaned data is saved to `data/prepared/` folder
- Original data: `data/raw/customers_data.csv` (201 rows) → Cleaned: `customers_prepared.csv` (193 rows)
- Original data: `data/raw/products_data.csv` (100 rows) → Cleaned: `products_prepared.csv` (98 rows)
- Original data: `data/raw/sales_data.csv` (2001 rows) → Cleaned: `sales_prepared.csv` (1978 rows)

### 4.5 Testing DataScrubber

A comprehensive test suite verifies all DataScrubber methods work correctly.

**Run tests:**

```shell
# Run all DataScrubber tests with unittest
python -m unittest tests.test_data_scrubber -v

# Run all tests with pytest (if available)
uv run pytest tests/test_data_scrubber.py -v
```

**Test Results:**
- ✅ All 29 tests pass successfully
- Tests cover all DataScrubber methods
- Tests verify error handling for invalid inputs
- Tests confirm method chaining works properly

### 4.6 Project 3 Summary

**What Was Accomplished:**
1. ✅ Enhanced DataScrubber class with all required methods
2. ✅ Created comprehensive test suite (29 tests, all passing)
3. ✅ Implemented data preparation scripts using DataScrubber
4. ✅ Successfully cleaned all 3 data files (customers, products, sales)
5. ✅ Generated prepared data files in `data/prepared/` folder
6. ✅ Documented all processes and commands

**Key Skills Learned:**
- Creating reusable, object-oriented data cleaning classes
- Using Python pandas for data manipulation
- Writing unit tests with unittest
- Implementing standardized data preparation pipelines
- Handling missing values and outliers
- Logging data processing steps

**Files Created/Modified:**
- `src/analytics_project/utils/data_scrubber.py` - Main DataScrubber class (enhanced)
- `tests/test_data_scrubber.py` - Comprehensive test suite (new)
- `data/prepared/customers_prepared.csv` - Cleaned customer data
- `data/prepared/products_prepared.csv` - Cleaned product data
- `data/prepared/sales_prepared.csv` - Cleaned sales data


