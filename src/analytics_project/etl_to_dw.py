"""ETL Script: Load data from prepared CSV files into Data Warehouse (SQLite)."""

import pandas as pd
import sqlite3
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

DW_DIR = pathlib.Path("data").joinpath("dw")
DB_PATH = DW_DIR.joinpath("smart_sales.db")
PREPARED_DATA_DIR = pathlib.Path("data").joinpath("prepared")

DW_DIR.mkdir(parents=True, exist_ok=True)


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create dimension and fact tables in the data warehouse."""

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            join_date TEXT NOT NULL,
            loyalty_points INTEGER,
            preferred_contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            supplier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            store_id TEXT PRIMARY KEY,
            store_name TEXT,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id TEXT PRIMARY KEY,
            campaign_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id TEXT PRIMARY KEY,
            transaction_date TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            store_id TEXT NOT NULL,
            campaign_id TEXT,
            sale_amount REAL NOT NULL,
            discount_percent REAL DEFAULT 0.0,
            net_sale_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (store_id) REFERENCES stores(store_id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
        )
    """)

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_sales_transaction_date ON sales(transaction_date)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_store_id ON sales(store_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_campaign_id ON sales(campaign_id)")


def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from all tables."""
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM stores")
    cursor.execute("DELETE FROM campaigns")


def insert_customers(customers_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert customer data into the customer dimension table."""
    customers_df_mapped = customers_df.rename(
        columns={
            "CustomerID": "customer_id",
            "Name": "name",
            "Region": "region",
            "JoinDate": "join_date",
            "LoyaltyPoints": "loyalty_points",
            "PreferredContact": "preferred_contact",
        }
    )

    columns = ["customer_id", "name", "region", "join_date", "loyalty_points", "preferred_contact"]
    customers_df_mapped = customers_df_mapped[columns]
    customers_df_mapped["customer_id"] = customers_df_mapped["customer_id"].astype(str)

    customers_df_mapped.to_sql("customers", cursor.connection, if_exists="append", index=False)
    print(f"[OK] Inserted {len(customers_df_mapped)} customer records")


def insert_products(products_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert product data into the product dimension table."""
    products_df_mapped = products_df.rename(
        columns={
            "ProductID": "product_id",
            "ProductName": "product_name",
            "Category": "category",
            "UnitPrice": "unit_price",
            "StockQuantity": "stock_quantity",
            "Supplier": "supplier",
        }
    )

    columns = ["product_id", "product_name", "category", "unit_price", "stock_quantity", "supplier"]
    products_df_mapped = products_df_mapped[columns]
    products_df_mapped["product_id"] = products_df_mapped["product_id"].astype(str)

    products_df_mapped.to_sql("products", cursor.connection, if_exists="append", index=False)
    print(f"[OK] Inserted {len(products_df_mapped)} product records")


def extract_stores(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Extract unique stores from sales data."""
    stores_df = sales_df[["StoreID"]].drop_duplicates()
    stores_df = stores_df.rename(columns={"StoreID": "store_id"})
    stores_df["store_id"] = stores_df["store_id"].astype(str)
    stores_df["store_name"] = "Store-" + stores_df["store_id"]
    stores_df["region"] = None

    stores_df = stores_df[["store_id", "store_name", "region"]]
    stores_df.to_sql("stores", cursor.connection, if_exists="append", index=False)
    print(f"[OK] Inserted {len(stores_df)} store records")


def extract_campaigns(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Extract unique campaigns from sales data."""
    campaigns_df = sales_df[["CampaignID"]].drop_duplicates()
    campaigns_df = campaigns_df.rename(columns={"CampaignID": "campaign_id"})
    campaigns_df["campaign_id"] = campaigns_df["campaign_id"].astype(str)
    campaigns_df["campaign_name"] = "Campaign-" + campaigns_df["campaign_id"]

    campaigns_df = campaigns_df[["campaign_id", "campaign_name"]]
    campaigns_df.to_sql("campaigns", cursor.connection, if_exists="append", index=False)
    print(f"[OK] Inserted {len(campaigns_df)} campaign records")


def create_missing_customers(
    sales_df: pd.DataFrame, customers_df: pd.DataFrame, cursor: sqlite3.Cursor
) -> None:
    """Create placeholder records for orphaned customer IDs."""
    sales_customer_ids = set(sales_df["CustomerID"].astype(str).unique())
    customer_ids = set(customers_df["CustomerID"].astype(str).unique())

    orphaned = sales_customer_ids - customer_ids

    if orphaned:
        orphaned_list = sorted(orphaned)
        print(f"\n[WARN] Found {len(orphaned)} orphaned customer IDs: {orphaned_list}")
        print("[INFO] Creating placeholder customer records...")

        placeholder_customers = pd.DataFrame(
            {
                "customer_id": orphaned_list,
                "name": [f"Unknown Customer {cid}" for cid in orphaned_list],
                "region": ["Unknown"] * len(orphaned_list),
                "join_date": ["2024-01-01"] * len(orphaned_list),
                "loyalty_points": [0] * len(orphaned_list),
                "preferred_contact": ["Unknown"] * len(orphaned_list),
            }
        )

        placeholder_customers.to_sql(
            "customers", cursor.connection, if_exists="append", index=False
        )
        print(f"[OK] Created {len(placeholder_customers)} placeholder customer records")


def insert_sales(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert sales data into the sales fact table."""
    sales_df_mapped = sales_df.rename(
        columns={
            "TransactionID": "sale_id",
            "SaleDate": "transaction_date",
            "CustomerID": "customer_id",
            "ProductID": "product_id",
            "StoreID": "store_id",
            "CampaignID": "campaign_id",
            "SaleAmount": "sale_amount",
            "DiscountPercent": "discount_percent",
            "PaymentType": "payment_method",
        }
    )

    sales_df_mapped["sale_id"] = sales_df_mapped["sale_id"].astype(str)
    sales_df_mapped["customer_id"] = sales_df_mapped["customer_id"].astype(str)
    sales_df_mapped["product_id"] = sales_df_mapped["product_id"].astype(str)
    sales_df_mapped["store_id"] = sales_df_mapped["store_id"].astype(str)
    sales_df_mapped["campaign_id"] = sales_df_mapped["campaign_id"].astype(str)

    sales_df_mapped["net_sale_amount"] = sales_df_mapped["sale_amount"] * (
        1 - sales_df_mapped["discount_percent"] / 100
    )

    columns = [
        "sale_id",
        "transaction_date",
        "customer_id",
        "product_id",
        "store_id",
        "campaign_id",
        "sale_amount",
        "discount_percent",
        "net_sale_amount",
        "payment_method",
    ]
    sales_df_mapped = sales_df_mapped[columns]

    sales_df_mapped.to_sql("sales", cursor.connection, if_exists="append", index=False)
    print(f"[OK] Inserted {len(sales_df_mapped)} sales records")


def verify_warehouse(cursor: sqlite3.Cursor) -> None:
    """Verify the data warehouse was populated correctly."""
    print("\n" + "=" * 60)
    print("DATA WAREHOUSE VERIFICATION")
    print("=" * 60)

    tables = ["customers", "products", "stores", "campaigns", "sales"]
    for table in tables:
        count = cursor.fetchone()[0]
        print(f"[OK] {table.capitalize():10s}: {count:6d} records")

    cursor.execute("""
        SELECT COUNT(*) FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """)
    orphaned_customers = cursor.fetchone()[0]
    if orphaned_customers == 0:
        print("\n[OK] Referential Integrity: All sales have valid customer references")
    else:
        print(f"\n[WARN] {orphaned_customers} sales have invalid customer references")

    print("\n" + "-" * 60)
    print("SAMPLE DATA FROM EACH TABLE:")
    print("-" * 60)

    cursor.execute("SELECT * FROM customers LIMIT 3")
    print("\nCustomers (sample):")
    for row in cursor.fetchall():
        print(f"  {row}")

    cursor.execute("SELECT * FROM products LIMIT 3")
    print("\nProducts (sample):")
    for row in cursor.fetchall():
        print(f"  {row}")

    cursor.execute("SELECT * FROM stores LIMIT 3")
    print("\nStores (sample):")
    for row in cursor.fetchall():
        print(f"  {row}")

    cursor.execute("""
        SELECT s.sale_id, s.transaction_date, s.customer_id, s.product_id,
               s.sale_amount, s.net_sale_amount FROM sales s LIMIT 3
    """)
    print("\nSales (sample):")
    for row in cursor.fetchall():
        print(f"  {row}")

    print("\n" + "=" * 60)


def load_data_to_db() -> None:
    """Create schema and load all data into warehouse."""
    conn: sqlite3.Connection | None = None

    try:
        print("=" * 60)
        print("STARTING DATA WAREHOUSE ETL PROCESS")
        print("=" * 60)
        print(f"Database path: {DB_PATH}\n")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Step 1: Creating data warehouse schema...")
        create_schema(cursor)
        print("[OK] Schema created successfully\n")

        print("Step 2: Clearing existing records...")
        delete_existing_records(cursor)
        print("[OK] Existing records deleted\n")

        print("Step 3: Loading prepared data from CSV files...")
        customers_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("customers_data_prepared.csv"))
        products_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("products_data_prepared.csv"))
        sales_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("sales_data_prepared.csv"))
        print(f"[OK] Loaded customers: {len(customers_df)} rows")
        print(f"[OK] Loaded products: {len(products_df)} rows")
        print(f"[OK] Loaded sales: {len(sales_df)} rows\n")

        print("Step 4: Loading dimension tables...")
        insert_customers(customers_df, cursor)
        insert_products(products_df, cursor)
        extract_stores(sales_df, cursor)
        extract_campaigns(sales_df, cursor)
        print()

        print("Step 5: Handling data quality issues...")
        create_missing_customers(sales_df, customers_df, cursor)
        print()

        print("Step 6: Loading fact table...")
        insert_sales(sales_df, cursor)
        print()

        print("Step 7: Committing changes to database...")
        conn.commit()
        print("[OK] All changes committed\n")

        verify_warehouse(cursor)

        print("\n" + "=" * 60)
        print("ETL PROCESS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    load_data_to_db()
