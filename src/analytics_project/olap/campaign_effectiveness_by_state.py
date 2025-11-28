"""
OLAP Analysis: Campaign Effectiveness by State/Region

Business Goal:
Identify which campaigns are most effective by region to optimize marketing spend.

Techniques:
- Slicing: Filter by specific campaign
- Dicing: Campaign × Region cross-tabulation
- Drill-down: Campaign → Region → Transaction details
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PREPARED = PROJECT_ROOT / "data" / "prepared"
OLAP_OUTPUT = PROJECT_ROOT / "src" / "analytics_project" / "olap" / "output"

# Create output directory
OLAP_OUTPUT.mkdir(exist_ok=True)


def load_data():
    """Load prepared CSV data."""
    sales_df = pd.read_csv(DATA_PREPARED / "sales_data_prepared.csv")
    customers_df = pd.read_csv(DATA_PREPARED / "customers_data_prepared.csv")
    products_df = pd.read_csv(DATA_PREPARED / "products_data_prepared.csv")

    # Merge to get region info
    sales_df = sales_df.merge(customers_df[["CustomerID", "Region"]], on="CustomerID", how="left")
    sales_df = sales_df.merge(products_df[["ProductID", "Category"]], on="ProductID", how="left")

    # Convert date
    sales_df["SaleDate"] = pd.to_datetime(sales_df["SaleDate"])

    # Drop rows with missing Region (data quality)
    sales_df = sales_df.dropna(subset=["Region"])

    return sales_df


def slice_analysis(sales_df):
    """
    SLICING: Filter by single dimension (e.g., Campaign 1)
    Shows campaign 1 performance across all regions.
    """
    print("\n" + "=" * 70)
    print("SLICING: Campaign 1 Performance (Single Dimension Filter)")
    print("=" * 70)

    campaign_1 = sales_df[sales_df["CampaignID"] == 1]

    slice_result = (
        campaign_1.groupby("Region")
        .agg({"SaleAmount": ["sum", "mean", "count"], "DiscountPercent": "mean"})
        .round(2)
    )

    slice_result.columns = ["Total Sales", "Avg Sale", "Transactions", "Avg Discount %"]
    print(slice_result)

    # Save to CSV
    slice_result.to_csv(OLAP_OUTPUT / "slice_campaign_1_by_region.csv")
    print(f"\n✓ Saved to: slice_campaign_1_by_region.csv")

    return slice_result


def dice_analysis(sales_df):
    """
    DICING: Multi-dimensional breakdown (Campaign × Region)
    Shows campaign effectiveness across multiple dimensions simultaneously.
    """
    print("\n" + "=" * 70)
    print("DICING: Campaign × Region Cross-Tabulation")
    print("=" * 70)

    # Create pivot table: Campaigns × Regions (Revenue)
    dice_result = sales_df.pivot_table(
        values="SaleAmount", index="CampaignID", columns="Region", aggfunc="sum"
    ).round(2)

    print("\nRevenue by Campaign and Region:")
    print(dice_result)

    # Add totals
    dice_result["Total"] = dice_result.sum(axis=1)
    dice_result.loc["Total"] = dice_result.sum()

    print("\nWith Totals:")
    print(dice_result)

    # Save to CSV
    dice_result.to_csv(OLAP_OUTPUT / "dice_campaign_by_region.csv")
    print(f"\n✓ Saved to: dice_campaign_by_region.csv")

    return dice_result


def drilldown_analysis(sales_df):
    """
    DRILL-DOWN: Progressive detail (Campaign → Region → Product Category)
    Shows hierarchical exploration from aggregate to detail.
    """
    print("\n" + "=" * 70)
    print("DRILL-DOWN: Campaign → Region → Product Category Hierarchy")
    print("=" * 70)

    # Level 1: Campaign totals
    level_1 = (
        sales_df.groupby("CampaignID")
        .agg({"SaleAmount": "sum", "DiscountPercent": "mean"})
        .round(2)
    )
    level_1.columns = ["Total Sales", "Avg Discount %"]
    print("\nLevel 1 - Campaign Totals:")
    print(level_1)

    # Level 2: Campaign × Region
    level_2 = (
        sales_df.groupby(["CampaignID", "Region"])
        .agg({"SaleAmount": "sum", "DiscountPercent": "mean"})
        .round(2)
    )
    level_2.columns = ["Total Sales", "Avg Discount %"]
    print("\nLevel 2 - Campaign × Region (Top 10):")
    print(level_2.sort_values("Total Sales", ascending=False).head(10))

    # Level 3: Campaign × Region × Category
    level_3 = (
        sales_df.groupby(["CampaignID", "Region", "Category"])
        .agg({"SaleAmount": "sum", "DiscountPercent": "mean"})
        .round(2)
    )
    level_3.columns = ["Total Sales", "Avg Discount %"]
    print("\nLevel 3 - Campaign × Region × Category (Top 10):")
    top_10 = level_3.sort_values("Total Sales", ascending=False).head(10)
    print(top_10)

    # Save to CSV
    level_3.to_csv(OLAP_OUTPUT / "drilldown_campaign_region_category.csv")
    print(f"\n✓ Saved to: drilldown_campaign_region_category.csv")

    return level_1, level_2, level_3


def create_visualizations(sales_df):
    """Create basic charts for insights."""
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Campaign Effectiveness Analysis", fontsize=16, fontweight="bold")

    # Chart 1: Total Revenue by Campaign
    campaign_revenue = (
        sales_df.groupby("CampaignID")["SaleAmount"].sum().sort_values(ascending=False)
    )
    axes[0, 0].bar(campaign_revenue.index.astype(str), campaign_revenue.values, color="steelblue")
    axes[0, 0].set_title("Total Revenue by Campaign")
    axes[0, 0].set_xlabel("Campaign ID")
    axes[0, 0].set_ylabel("Revenue ($)")
    axes[0, 0].grid(axis="y", alpha=0.3)

    # Chart 2: Transaction Count by Region
    region_count = sales_df.groupby("Region").size().sort_values(ascending=False)
    axes[0, 1].bar(region_count.index, region_count.values, color="coral")
    axes[0, 1].set_title("Transaction Count by Region")
    axes[0, 1].set_xlabel("Region")
    axes[0, 1].set_ylabel("Count")
    axes[0, 1].grid(axis="y", alpha=0.3)

    # Chart 3: Average Discount by Campaign
    avg_discount = (
        sales_df.groupby("CampaignID")["DiscountPercent"].mean().sort_values(ascending=False)
    )
    axes[1, 0].bar(avg_discount.index.astype(str), avg_discount.values, color="mediumseagreen")
    axes[1, 0].set_title("Average Discount Percent by Campaign")
    axes[1, 0].set_xlabel("Campaign ID")
    axes[1, 0].set_ylabel("Discount %")
    axes[1, 0].grid(axis="y", alpha=0.3)

    # Chart 4: Revenue by Region
    region_revenue = sales_df.groupby("Region")["SaleAmount"].sum().sort_values(ascending=False)
    axes[1, 1].bar(region_revenue.index, region_revenue.values, color="mediumpurple")
    axes[1, 1].set_title("Total Revenue by Region")
    axes[1, 1].set_xlabel("Region")
    axes[1, 1].set_ylabel("Revenue ($)")
    axes[1, 1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    chart_path = OLAP_OUTPUT / "campaign_effectiveness_charts.png"
    plt.savefig(chart_path, dpi=100, bbox_inches="tight")
    print(f"✓ Charts saved to: campaign_effectiveness_charts.png")
    plt.close()


def summary_statistics(sales_df):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    print(f"\nTotal Transactions: {len(sales_df)}")
    print(f"Total Revenue: ${sales_df['SaleAmount'].sum():,.2f}")
    print(f"Average Transaction: ${sales_df['SaleAmount'].mean():,.2f}")
    print(f"Number of Campaigns: {sales_df['CampaignID'].nunique()}")
    print(f"Number of Regions: {sales_df['Region'].nunique()}")
    regions = sorted([r for r in sales_df['Region'].unique() if pd.notna(r)])
    print(f"Regions: {regions}")
    print(f"Average Discount: {sales_df['DiscountPercent'].mean():.2f}%")


def main():
    """Run full OLAP analysis."""
    print("\n" + "=" * 70)
    print("OLAP ANALYSIS: CAMPAIGN EFFECTIVENESS BY STATE/REGION")
    print("=" * 70)

    # Load data
    sales_df = load_data()
    print(f"\n✓ Loaded {len(sales_df)} transactions")

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
