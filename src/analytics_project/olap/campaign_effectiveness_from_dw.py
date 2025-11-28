"""
OLAP Analysis: Campaign Effectiveness by State (from Data Warehouse).

This version queries the smart_sales.db data warehouse (Project 5)
instead of prepared CSV files, demonstrating full project integration.

Business Goal:
    Identify which campaigns are most effective by region to optimize marketing spend.

Techniques:
    - Slicing: Filter by specific campaign
    - Dicing: Campaign × Region cross-tabulation
    - Drill-down: Campaign → Region → Product Category
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DW_PATH = PROJECT_ROOT / "data" / "dw" / "smart_sales.db"
OLAP_OUTPUT = PROJECT_ROOT / "src" / "analytics_project" / "olap" / "output"

# Create output directory
OLAP_OUTPUT.mkdir(exist_ok=True)


def load_data_from_dw():
    """Load data from data warehouse (Project 5)."""
    conn = sqlite3.connect(DW_PATH)

    # Query to combine sales, customers, and products
    query = """
    SELECT
        s.sale_id,
        s.transaction_date,
        s.customer_id,
        s.product_id,
        s.campaign_id,
        s.net_sale_amount,
        s.discount_percent,
        c.region,
        p.category,
        p.product_name
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    JOIN products p ON s.product_id = p.product_id
    WHERE c.region IS NOT NULL
    """

    sales_df = pd.read_sql_query(query, conn)
    conn.close()

    # Convert date
    sales_df["transaction_date"] = pd.to_datetime(sales_df["transaction_date"])

    return sales_df


def slice_analysis(sales_df):
    """Filter data by single dimension."""
    print("\n" + "=" * 70)
    print("SLICING: Campaign 1 Performance (Single Dimension Filter)")
    print("=" * 70)

    campaign_1 = sales_df[sales_df["campaign_id"] == 1]

    slice_result = (
        campaign_1.groupby("region")
        .agg(
            {
                "net_sale_amount": ["sum", "mean", "count"],
                "discount_percent": "mean",
            }
        )
        .round(2)
    )

    slice_result.columns = [
        "Total Sales",
        "Avg Sale",
        "Transactions",
        "Avg Discount %",
    ]
    print(slice_result)

    # Save to CSV
    slice_result.to_csv(OLAP_OUTPUT / "slice_campaign_1_by_region_dw.csv")
    print(f"\n✓ Saved to: slice_campaign_1_by_region_dw.csv")

    return slice_result


def dice_analysis(sales_df):
    """Break down data by multiple dimensions."""
    print("\n" + "=" * 70)
    print("DICING: Campaign × Region Cross-Tabulation")
    print("=" * 70)

    # Create pivot table: Campaigns × Regions (Revenue)
    dice_result = (
        sales_df.pivot_table(
            values="net_sale_amount", index="campaign_id", columns="region", aggfunc="sum"
        )
    ).round(2)

    print("\nRevenue by Campaign and Region:")
    print(dice_result)

    # Add totals
    dice_result["Total"] = dice_result.sum(axis=1)
    dice_result.loc["Total"] = dice_result.sum()

    print("\nWith Totals:")
    print(dice_result)

    # Save to CSV
    dice_result.to_csv(OLAP_OUTPUT / "dice_campaign_by_region_dw.csv")
    print(f"\n✓ Saved to: dice_campaign_by_region_dw.csv")

    return dice_result


def drilldown_analysis(sales_df):
    """Explore data through hierarchical levels."""
    print("\n" + "=" * 70)
    print("DRILL-DOWN: Campaign → Region → Product Category Hierarchy")
    print("=" * 70)

    # Level 1: Campaign totals
    level_1 = (
        sales_df.groupby("campaign_id")
        .agg({"net_sale_amount": "sum", "discount_percent": "mean"})
        .round(2)
    )
    level_1.columns = ["Total Sales", "Avg Discount %"]
    print("\nLevel 1 - Campaign Totals:")
    print(level_1)

    # Level 2: Campaign × Region
    level_2 = (
        sales_df.groupby(["campaign_id", "region"])
        .agg({"net_sale_amount": "sum", "discount_percent": "mean"})
        .round(2)
    )
    level_2.columns = ["Total Sales", "Avg Discount %"]
    print("\nLevel 2 - Campaign × Region (Top 10):")
    print(level_2.sort_values("Total Sales", ascending=False).head(10))

    # Level 3: Campaign × Region × Category
    level_3 = (
        sales_df.groupby(["campaign_id", "region", "category"])
        .agg({"net_sale_amount": "sum", "discount_percent": "mean"})
        .round(2)
    )
    level_3.columns = ["Total Sales", "Avg Discount %"]
    print("\nLevel 3 - Campaign × Region × Category (Top 10):")
    top_10 = level_3.sort_values("Total Sales", ascending=False).head(10)
    print(top_10)

    # Save to CSV
    level_3.to_csv(OLAP_OUTPUT / "drilldown_campaign_region_category_dw.csv")
    print(f"\n✓ Saved to: drilldown_campaign_region_category_dw.csv")

    return level_1, level_2, level_3


def create_visualizations(sales_df):
    """Create basic charts for insights."""
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Campaign Effectiveness Analysis (from Data Warehouse)", fontsize=16, fontweight="bold"
    )

    # Chart 1: Total Revenue by Campaign
    campaign_revenue = (
        sales_df.groupby("campaign_id")["net_sale_amount"].sum().sort_values(ascending=False)
    )
    axes[0, 0].bar(campaign_revenue.index.astype(str), campaign_revenue.values, color="steelblue")
    axes[0, 0].set_title("Total Revenue by Campaign")
    axes[0, 0].set_xlabel("Campaign ID")
    axes[0, 0].set_ylabel("Revenue ($)")
    axes[0, 0].grid(axis="y", alpha=0.3)

    # Chart 2: Transaction Count by Region
    region_count = sales_df.groupby("region").size().sort_values(ascending=False)
    axes[0, 1].bar(region_count.index, region_count.values, color="coral")
    axes[0, 1].set_title("Transaction Count by Region")
    axes[0, 1].set_xlabel("Region")
    axes[0, 1].set_ylabel("Count")
    axes[0, 1].grid(axis="y", alpha=0.3)

    # Chart 3: Average Discount by Campaign
    avg_discount = (
        sales_df.groupby("campaign_id")["discount_percent"].mean().sort_values(ascending=False)
    )
    axes[1, 0].bar(avg_discount.index.astype(str), avg_discount.values, color="mediumseagreen")
    axes[1, 0].set_title("Average Discount Percent by Campaign")
    axes[1, 0].set_xlabel("Campaign ID")
    axes[1, 0].set_ylabel("Discount %")
    axes[1, 0].grid(axis="y", alpha=0.3)

    # Chart 4: Revenue by Region
    region_revenue = (
        sales_df.groupby("region")["net_sale_amount"].sum().sort_values(ascending=False)
    )
    axes[1, 1].bar(region_revenue.index, region_revenue.values, color="mediumpurple")
    axes[1, 1].set_title("Total Revenue by Region")
    axes[1, 1].set_xlabel("Region")
    axes[1, 1].set_ylabel("Revenue ($)")
    axes[1, 1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    chart_path = OLAP_OUTPUT / "campaign_effectiveness_charts_dw.png"
    plt.savefig(chart_path, dpi=100, bbox_inches="tight")
    print(f"✓ Charts saved to: campaign_effectiveness_charts_dw.png")
    plt.close()


def summary_statistics(sales_df):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS (from Data Warehouse)")
    print("=" * 70)

    print(f"\nTotal Transactions: {len(sales_df)}")
    print(f"Total Revenue: ${sales_df['net_sale_amount'].sum():,.2f}")
    print(f"Average Transaction: ${sales_df['net_sale_amount'].mean():,.2f}")
    print(f"Number of Campaigns: {sales_df['campaign_id'].nunique()}")
    print(f"Number of Regions: {sales_df['region'].nunique()}")
    regions = sorted(sales_df["region"].unique())
    print(f"Regions: {regions}")
    print(f"Average Discount: {sales_df['discount_percent'].mean():.2f}%")


def main():
    """Run full OLAP analysis from data warehouse."""
    print("\n" + "=" * 70)
    print("OLAP ANALYSIS: CAMPAIGN EFFECTIVENESS (from Data Warehouse)")
    print("=" * 70)
    print(f"\nDatabase: {DW_PATH}")

    # Load data from warehouse
    sales_df = load_data_from_dw()
    print(f"\n✓ Loaded {len(sales_df)} transactions from smart_sales.db")

    # Summary
    summary_statistics(sales_df)

    # Run OLAP analyses
    slice_analysis(sales_df)
    dice_analysis(sales_df)
    drilldown_analysis(sales_df)

    # Visualizations
    create_visualizations(sales_df)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print(f"Output files saved to: {OLAP_OUTPUT}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
