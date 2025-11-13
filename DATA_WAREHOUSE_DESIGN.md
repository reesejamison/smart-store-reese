## What fact tables will you use in your DW:

**Fact Table: `sales`**

The central fact table containing quantitative data representing business transactions. This table captures every sale event with measurable metrics and foreign key references to dimension tables.

---

## What dimension tables will you use in your DW:

1. **`customers`** - Dimension table containing customer attributes and characteristics
2. **`products`** - Dimension table containing product details and specifications
3. **`stores`** - Dimension table containing store information (derived from StoreID in raw data)
4. **`campaigns`** - Dimension table containing campaign information (derived from CampaignID in raw data)

---

## What additional columns did you add to Sales & what type is each column:

**Additional columns beyond the base example:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| quantity | INTEGER | Number of units sold (derived from SaleAmount / avg unit price analysis) |
| net_sale_amount | REAL | Sale amount after discount applied |
| payment_method | TEXT | Type of payment used (normalized from PaymentType) |
| transaction_date | DATE | Date of transaction (ISO 8601 format) |

**Rationale:** These columns provide additional analytical dimensions such as volume metrics, net revenue (accounting for discounts), payment tracking, and date standardization for time-based analysis.

---

## What additional columns did you add to Products & what type is each column:

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| supplier_normalized | TEXT | Standardized supplier name (handles missing/N/A values) |
| is_active | BOOLEAN | Whether product is currently in inventory |
| last_restock_date | DATE | Date when product was last restocked |
| category_normalized | TEXT | Standardized product category (lowercase, consistent naming) |

**Rationale:** Enhanced data quality with normalized fields, inventory status tracking, and restock information for supply chain analysis.

---

## What additional columns did you add to Customers & what type is each column:

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| loyalty_tier | TEXT | Classification based on LoyaltyPoints (Bronze/Silver/Gold/Platinum) |
| customer_lifetime_value | REAL | Total value of all purchases by customer |
| region_normalized | TEXT | Standardized region name (consistent format) |
| contact_preference_normalized | TEXT | Standardized contact method (Email/Phone/Mail/SMS) |
| days_as_customer | INTEGER | Number of days since join_date |

**Rationale:** These columns support customer segmentation, lifetime value analysis, personalization, and engagement metrics for CRM-focused analytics.

---

## Show your schema for your dimension tables:

### Dimension Table: `customers`

```sql
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    region_normalized TEXT,
    join_date DATE NOT NULL,
    loyalty_points INTEGER,
    loyalty_tier TEXT,
    preferred_contact TEXT,
    contact_preference_normalized TEXT,
    customer_lifetime_value REAL,
    days_as_customer INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Dimension Table: `products`

```sql
CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    category_normalized TEXT,
    unit_price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    supplier TEXT,
    supplier_normalized TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_restock_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Dimension Table: `stores`

```sql
CREATE TABLE stores (
    store_id TEXT PRIMARY KEY,
    store_name TEXT,
    region TEXT,
    manager_name TEXT,
    opening_date DATE,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Dimension Table: `campaigns`

```sql
CREATE TABLE campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT,
    start_date DATE,
    end_date DATE,
    budget REAL,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Show your schema for your fact table:

### Fact Table: `sales`

```sql
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    transaction_date DATE NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    campaign_id TEXT,
    quantity INTEGER,
    unit_price REAL,
    sale_amount REAL NOT NULL,
    discount_percent REAL DEFAULT 0.0,
    net_sale_amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraints
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),

    -- Indexes for query performance
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_customer_id (customer_id),
    INDEX idx_product_id (product_id),
    INDEX idx_store_id (store_id),
    INDEX idx_campaign_id (campaign_id)
);
```

---

## Does each table have exactly one PRIMARY KEY:

✅ **Yes, each table has exactly one PRIMARY KEY:**

- **`customers`** → PRIMARY KEY: `customer_id` (TEXT)
- **`products`** → PRIMARY KEY: `product_id` (TEXT)
- **`stores`** → PRIMARY KEY: `store_id` (TEXT)
- **`campaigns`** → PRIMARY KEY: `campaign_id` (TEXT)
- **`sales`** (Fact Table) → PRIMARY KEY: `sale_id` (INTEGER)

Each primary key uniquely identifies every record in its respective table, and foreign key constraints in the `sales` fact table maintain referential integrity with the dimension tables.

---

## What challenges did you encounter in the design process:

1. **Data Quality Issues:**
   - Missing supplier values and inconsistent null representations ("", "N/A") required normalization strategy
   - PreferredContact values had inconsistent formatting (e.g., "SMS" vs "Text", "Cash" vs "CASH")
   - Required mapping and standardization rules during ETL

2. **Derived Dimensions:**
   - StoreID and CampaignID existed in raw sales data but lacked corresponding dimension tables
   - Had to create new dimension tables with limited information from the fact table
   - Required assumptions about store and campaign attributes that might not exist in source systems

3. **Grain and Aggregation:**
   - Determining the appropriate grain of the fact table (each row = one transaction)
   - Calculating quantity from sales amount when quantity data wasn't directly available
   - Deciding which metrics should be in the fact table vs. calculated in views

4. **Type Conversions:**
   - Dates in CSV format needed standardization to ISO 8601 (YYYY-MM-DD) for consistency
   - Numeric fields with varying precision and potential outliers
   - Text fields with inconsistent capitalization and whitespace

5. **Schema Normalization vs. Performance:**
   - Balancing normalized design (reduce redundancy) with denormalized design (optimize query performance)
   - Adding calculated fields like `loyalty_tier`, `days_as_customer`, and `net_sale_amount` at dimension/fact level vs. calculated in queries

6. **Temporal Attributes:**
   - Adding timestamps (`created_at`, `updated_at`) for audit trails and tracking data lineage
   - Managing the trade-off between historical accuracy and storage efficiency
   - Determining when snapshots vs. incremental updates are appropriate

7. **Foreign Key Relationships:**
   - Ensuring every foreign key reference in the sales table could be satisfied by corresponding dimension records
   - Handling cases where dimension values might be missing or incomplete
   - Deciding whether to create placeholder records for unknown/missing dimensions

---

## Star Schema Diagram (Visual Representation):

```
                    ┌──────────────────┐
                    │  Dimension: Time │
                    │  (transaction_   │
                    │   date derived)  │
                    └──────────────────┘
                            ▲
                            │ FK
                            │
        ┌─────────────────┐  │  ┌──────────────────┐
        │ Dimension:      │  │  │ Dimension: Stores│
        │ Customers       │  │  └──────────────────┘
        │ ──────────────  │  │         ▲
        │ PK: customer_id │  │         │ FK
        │ - name          │  │         │
        │ - region        │  │    ┌────────────────┐
        │ - join_date     │  │    │   FACT TABLE   │
        │ - loyalty_*     │  │    │    sales       │
        └─────────────────┘  │    │ ──────────────ℹ│
                  ▲           │    │ PK: sale_id    │
                  │ FK        │    │ - customer_id  │
                  │          │    │ - product_id   │
                  └──────────┼────┤ - store_id     │
                             │    │ - campaign_id  │
        ┌─────────────────┐  │    │ - sale_amount  │
        │ Dimension:      │  │    │ - discount_%   │
        │ Products        │  │    │ - payment_*    │
        │ ──────────────  │  │    └────────────────┘
        │ PK: product_id  │  │         ▲
        │ - name          │  │         │ FK
        │ - category      │  │         │
        │ - unit_price    │  │    ┌──────────────────┐
        │ - supplier      │  │    │ Dimension: Camps │
        └─────────────────┘  │    │ (Campaigns)      │
                             │    └──────────────────┘
                             │
                             └─────────────────────
```

This star schema design provides:
- ✅ Centralized fact table for efficient aggregations
- ✅ Clear dimensional hierarchies for drill-down analysis
- ✅ Denormalized structure optimized for read operations
- ✅ Foreign key relationships maintaining data integrity
- ✅ Extensible design allowing additional dimensions as needed
