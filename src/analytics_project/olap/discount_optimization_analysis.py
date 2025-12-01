"""
OLAP Analysis: Product Pricing & Discount Optimization
Business Goal: Optimize product mix and pricing strategy by analyzing discount
effectiveness across product categories and store locations to maximize profit
margins while maintaining sales velocity.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Create output directories
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
VIZ_DIR = os.path.join(os.path.dirname(__file__), 'visualizations')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

def load_data():
    """Load and prepare data from CSV files."""
    print("Loading data...")

    # Load prepared data
    sales_df = pd.read_csv('data/prepared/sales_data_prepared.csv')
    products_df = pd.read_csv('data/prepared/products_data_prepared.csv')
    customers_df = pd.read_csv('data/prepared/customers_data_prepared.csv')

    # Merge datasets
    merged_df = sales_df.merge(products_df, on='ProductID', how='left')
    merged_df = merged_df.merge(customers_df, on='CustomerID', how='left')

    # Convert date column
    merged_df['SaleDate'] = pd.to_datetime(merged_df['SaleDate'])
    merged_df['Month'] = merged_df['SaleDate'].dt.to_period('M').astype(str)
    merged_df['Quarter'] = merged_df['SaleDate'].dt.to_period('Q').astype(str)

    print(f"Loaded {len(merged_df)} transactions")
    return merged_df

def calculate_metrics(df):
    """Calculate key business metrics."""
    print("\nCalculating metrics...")

    # 1. Gross Margin by Category
    df['NetSaleAmount'] = df['SaleAmount'] * (1 - df['DiscountPercent'] / 100)
    df['GrossMargin'] = (df['NetSaleAmount'] / df['SaleAmount']) * 100

    # 2. Discount Tier
    df['DiscountTier'] = pd.cut(df['DiscountPercent'],
                                  bins=[0, 10, 20, 30, 100],
                                  labels=['0-10%', '10-20%', '20-30%', '30%+'])

    # 3. Stock Level Categories
    df['StockLevel'] = pd.cut(df['StockQuantity'],
                               bins=[0, 250, 500, float('inf')],
                               labels=['Low', 'Medium', 'High'])

    return df

def slice_analysis(df):
    """OLAP Slicing: Filter by single dimension."""
    print("\n=== SLICING ANALYSIS ===")

    # Slice 1: Electronics only
    electronics = df[df['Category'] == 'Electronics'].copy()
    electronics_summary = electronics.groupby('DiscountTier').agg({
        'SaleAmount': 'sum',
        'NetSaleAmount': 'sum',
        'TransactionID': 'count',
        'DiscountPercent': 'mean'
    }).round(2)
    print("\nSlice 1: Electronics by Discount Tier")
    print(electronics_summary)
    electronics_summary.to_csv(os.path.join(OUTPUT_DIR, 'slice_electronics_discount.csv'))

    # Slice 2: Store 401 only
    store_401 = df[df['StoreID'] == 401].copy()
    store_summary = store_401.groupby('Category').agg({
        'SaleAmount': 'sum',
        'NetSaleAmount': 'sum',
        'DiscountPercent': 'mean',
        'GrossMargin': 'mean'
    }).round(2)
    print("\nSlice 2: Store 401 by Category")
    print(store_summary)
    store_summary.to_csv(os.path.join(OUTPUT_DIR, 'slice_store401_category.csv'))

    # Slice 3: High discounts (30%+)
    high_discount = df[df['DiscountPercent'] >= 30].copy()
    high_discount_summary = high_discount.groupby('Category').agg({
        'SaleAmount': 'sum',
        'TransactionID': 'count',
        'GrossMargin': 'mean'
    }).round(2)
    print("\nSlice 3: High Discount (30%+) by Category")
    print(high_discount_summary)
    high_discount_summary.to_csv(os.path.join(OUTPUT_DIR, 'slice_high_discount.csv'))

def dice_analysis(df):
    """OLAP Dicing: Multi-dimensional filtering."""
    print("\n=== DICING ANALYSIS ===")

    # Dice 1: Electronics + High Discount + Low Stock
    dice1 = df[(df['Category'] == 'Electronics') &
               (df['DiscountPercent'] >= 30) &
               (df['StockLevel'] == 'Low')].copy()
    print(f"\nDice 1: Electronics + High Discount + Low Stock: {len(dice1)} transactions")
    if len(dice1) > 0:
        dice1_summary = dice1.groupby('ProductName').agg({
            'SaleAmount': 'sum',
            'StockQuantity': 'mean',
            'DiscountPercent': 'mean'
        }).round(2).head(10)
        print(dice1_summary)
        dice1_summary.to_csv(os.path.join(OUTPUT_DIR, 'dice_electronics_clearance.csv'))

    # Dice 2: Clothing + Store 402 + Q4
    dice2 = df[(df['Category'] == 'Clothing') &
               (df['StoreID'] == 402) &
               (df['Quarter'].str.contains('Q4', na=False))].copy()
    print(f"\nDice 2: Clothing + Store 402 + Q4: {len(dice2)} transactions")
    if len(dice2) > 0:
        dice2_summary = dice2.agg({
            'SaleAmount': 'sum',
            'NetSaleAmount': 'sum',
            'DiscountPercent': 'mean',
            'TransactionID': 'count'
        }).round(2)
        print(dice2_summary)

    # Dice 3: Office + Low Discount + High Sales
    dice3 = df[(df['Category'] == 'Office') &
               (df['DiscountPercent'] < 10)].copy()
    dice3_summary = dice3.groupby('StoreID').agg({
        'SaleAmount': 'sum',
        'TransactionID': 'count',
        'GrossMargin': 'mean'
    }).round(2).sort_values('SaleAmount', ascending=False)
    print(f"\nDice 3: Office + Low Discount by Store")
    print(dice3_summary)
    dice3_summary.to_csv(os.path.join(OUTPUT_DIR, 'dice_office_low_discount.csv'))

def drilldown_analysis(df):
    """OLAP Drilldown: Progressive detail levels."""
    print("\n=== DRILLDOWN ANALYSIS ===")

    # Level 1: Total revenue by category
    level1 = df.groupby('Category').agg({
        'SaleAmount': 'sum',
        'NetSaleAmount': 'sum',
        'TransactionID': 'count'
    }).round(2).sort_values('SaleAmount', ascending=False)
    print("\nLevel 1: Revenue by Category")
    print(level1)
    level1.to_csv(os.path.join(OUTPUT_DIR, 'drilldown_level1_category.csv'))

    # Level 2: Drill into top category by store
    top_category = level1.index[0]
    level2 = df[df['Category'] == top_category].groupby('StoreID').agg({
        'SaleAmount': 'sum',
        'NetSaleAmount': 'sum',
        'DiscountPercent': 'mean',
        'TransactionID': 'count'
    }).round(2).sort_values('SaleAmount', ascending=False)
    print(f"\nLevel 2: {top_category} by Store")
    print(level2)
    level2.to_csv(os.path.join(OUTPUT_DIR, 'drilldown_level2_store.csv'))

    # Level 3: Drill into best store by discount tier
    top_store = level2.index[0]
    level3 = df[(df['Category'] == top_category) &
                (df['StoreID'] == top_store)].groupby('DiscountTier').agg({
        'SaleAmount': 'sum',
        'NetSaleAmount': 'sum',
        'TransactionID': 'count',
        'GrossMargin': 'mean'
    }).round(2)
    print(f"\nLevel 3: {top_category} at Store {top_store} by Discount Tier")
    print(level3)
    level3.to_csv(os.path.join(OUTPUT_DIR, 'drilldown_level3_discount.csv'))

    # Level 4: Top products in best discount tier
    best_tier = level3['SaleAmount'].idxmax()
    level4 = df[(df['Category'] == top_category) &
                (df['StoreID'] == top_store) &
                (df['DiscountTier'] == best_tier)].groupby('ProductName').agg({
        'SaleAmount': 'sum',
        'TransactionID': 'count',
        'DiscountPercent': 'mean'
    }).round(2).sort_values('SaleAmount', ascending=False).head(10)
    print(f"\nLevel 4: Top Products in {best_tier} tier")
    print(level4)
    level4.to_csv(os.path.join(OUTPUT_DIR, 'drilldown_level4_products.csv'))

def create_visualizations(df):
    """Create key visualizations for the analysis."""
    print("\n=== CREATING VISUALIZATIONS ===")

    # Visualization 1: Bar Chart - Average Discount by Category
    plt.figure(figsize=(10, 6))
    category_discount = df.groupby('Category')['DiscountPercent'].mean().sort_values(ascending=False)
    ax = category_discount.plot(kind='bar', color='steelblue')
    plt.title('Average Discount Percentage by Product Category', fontsize=14, fontweight='bold')
    plt.xlabel('Product Category', fontsize=12)
    plt.ylabel('Average Discount (%)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add value labels on bars
    for i, v in enumerate(category_discount.values):
        ax.text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom')

    plt.savefig(os.path.join(VIZ_DIR, '1_bar_discount_by_category.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: 1_bar_discount_by_category.png")
    plt.close()

    # Visualization 2: Heatmap - Store x Category Revenue
    plt.figure(figsize=(12, 8))
    pivot_revenue = df.pivot_table(values='NetSaleAmount',
                                     index='StoreID',
                                     columns='Category',
                                     aggfunc='sum',
                                     fill_value=0)
    sns.heatmap(pivot_revenue, annot=True, fmt='.0f', cmap='YlOrRd', cbar_kws={'label': 'Net Revenue ($)'})
    plt.title('Net Revenue Heatmap: Store × Category', fontsize=14, fontweight='bold')
    plt.xlabel('Product Category', fontsize=12)
    plt.ylabel('Store ID', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, '2_heatmap_store_category.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: 2_heatmap_store_category.png")
    plt.close()

    # Visualization 3: Scatter Plot - Discount Efficiency
    plt.figure(figsize=(10, 6))

    # Calculate sales volume by discount tier
    discount_analysis = df.groupby('DiscountTier').agg({
        'TransactionID': 'count',
        'DiscountPercent': 'mean'
    }).reset_index()

    plt.scatter(discount_analysis['DiscountPercent'],
                discount_analysis['TransactionID'],
                s=200, alpha=0.6, c=['green', 'blue', 'orange', 'red'])

    # Add labels
    for idx, row in discount_analysis.iterrows():
        plt.annotate(row['DiscountTier'],
                    (row['DiscountPercent'], row['TransactionID']),
                    xytext=(5, 5), textcoords='offset points')

    plt.title('Discount Efficiency: Discount % vs Sales Volume', fontsize=14, fontweight='bold')
    plt.xlabel('Average Discount Percentage (%)', fontsize=12)
    plt.ylabel('Number of Transactions', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, '3_scatter_discount_efficiency.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: 3_scatter_discount_efficiency.png")
    plt.close()

    # Visualization 4: Line Chart - Margin Trends Over Time
    plt.figure(figsize=(12, 6))

    # Calculate average margin by month and category
    monthly_margin = df.groupby(['Month', 'Category'])['GrossMargin'].mean().reset_index()

    for category in monthly_margin['Category'].unique():
        cat_data = monthly_margin[monthly_margin['Category'] == category]
        plt.plot(cat_data['Month'], cat_data['GrossMargin'],
                marker='o', label=category, linewidth=2)

    plt.title('Gross Margin Trends by Category Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Average Gross Margin (%)', fontsize=12)
    plt.legend(title='Category', loc='best')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, '4_line_margin_trends.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: 4_line_margin_trends.png")
    plt.close()

def generate_summary_report(df):
    """Generate comprehensive summary statistics."""
    print("\n=== GENERATING SUMMARY REPORT ===")

    summary = {
        'Total Transactions': len(df),
        'Total Gross Revenue': f"${df['SaleAmount'].sum():,.2f}",
        'Total Net Revenue': f"${df['NetSaleAmount'].sum():,.2f}",
        'Average Discount': f"{df['DiscountPercent'].mean():.2f}%",
        'Average Gross Margin': f"{df['GrossMargin'].mean():.2f}%",
        'Date Range': f"{df['SaleDate'].min().date()} to {df['SaleDate'].max().date()}",
        'Number of Products': df['ProductID'].nunique(),
        'Number of Stores': df['StoreID'].nunique(),
        'Number of Categories': df['Category'].nunique()
    }

    print("\nSummary Statistics:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Save summary
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(os.path.join(OUTPUT_DIR, 'summary_statistics.csv'), index=False)
    print("\n✓ Saved: summary_statistics.csv")

def main():
    """Main execution function."""
    print("="*70)
    print("  DISCOUNT OPTIMIZATION ANALYSIS")
    print("  Business Goal: Maximize profit margins through strategic pricing")
    print("="*70)

    # Load and prepare data
    df = load_data()

    # Calculate metrics
    df = calculate_metrics(df)

    # Perform OLAP operations
    slice_analysis(df)
    dice_analysis(df)
    drilldown_analysis(df)

    # Create visualizations
    create_visualizations(df)

    # Generate summary
    generate_summary_report(df)

    print("\n" + "="*70)
    print("  ANALYSIS COMPLETE!")
    print(f"  Output files saved to: {OUTPUT_DIR}")
    print(f"  Visualizations saved to: {VIZ_DIR}")
    print("="*70)

if __name__ == "__main__":
    main()
