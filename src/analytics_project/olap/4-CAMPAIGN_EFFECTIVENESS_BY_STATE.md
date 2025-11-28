# OLAP Analysis: Campaign Effectiveness by State

## 1. Business Goal

**Question:** Which marketing campaigns are most effective by region to optimize future spend?

**Why it matters:** Understanding campaign performance across regions enables data-driven marketing budget allocation and identifies geographic strengths/weaknesses.

---

## 2. Data Source

**Source:** Prepared CSV data
- `sales_data_prepared.csv` (1,978 transactions → 1,902 after cleaning)
- `customers_data_prepared.csv` (193 records)
- `products_data_prepared.csv` (98 records)

**Key Columns Used:**
| Table | Column | Purpose |
|-------|--------|---------|
| sales | CampaignID, SaleAmount, DiscountPercent | Campaign metrics |
| sales | SaleDate | Time context |
| customers | Region | Geographic dimension |
| products | Category | Product classification |

---

## 3. Tools

**Python with pandas, matplotlib**
- Simple, repeatable, and easy to integrate with existing workflow
- Enables automation for regular reporting
- Clear code documentation for reproducibility

---

## 4. Workflow & Logic

### OLAP Techniques Applied

#### Slicing
Filter by single dimension to isolate one campaign's performance.
- **Example:** Campaign 1 revenue across all regions
- **Result:** Identified East region as strongest ($127K), South weakest ($47K) for Campaign 1

#### Dicing
Multi-dimensional cross-tabulation showing campaign × region interaction.
- **Result:** Campaign 3 is highest revenue ($602K), Campaign 2 lowest ($383K)
- **Key Finding:** East region dominates for all campaigns (30% of total revenue)

#### Drill-down
Progressive detail from aggregate (campaign) → intermediate (region) → specific (product category).
- **Level 1:** Campaign totals (4 records)
- **Level 2:** Campaign × Region (24 combinations)
- **Level 3:** Campaign × Region × Category (96+ combinations)
- **Key Finding:** Electronics in East region for Campaign 3 generates highest revenue ($55.6K)

### Aggregations

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| Total Sales | SUM(SaleAmount) | Revenue by dimension |
| Transaction Count | COUNT(*) | Volume metrics |
| Average Sale | MEAN(SaleAmount) | Transaction size |
| Avg Discount | MEAN(DiscountPercent) | Promotional intensity |

---

## 5. Results

### Summary Statistics
- **Total Transactions:** 1,902 (after removing 76 rows with missing regions)
- **Total Revenue:** $1,922,459
- **Avg Transaction:** $1,011
- **Campaigns:** 4 (IDs: 0, 1, 2, 3)
- **Regions:** 6 (Central, East, North, South, Southwest, West)

### Key Insights

**1. Campaign Performance Ranking**
| Campaign | Total Revenue | Transactions | Avg Sale |
|----------|---------------|--------------|----------|
| Campaign 3 | $601,941 | 595 | $1,011 |
| Campaign 0 | $526,668 | 521 | $1,010 |
| Campaign 1 | $411,160 | 407 | $1,010 |
| Campaign 2 | $382,689 | 379 | $1,010 |

**→ Campaign 3 generates 57% more revenue than Campaign 2**

**2. Regional Performance**
| Region | Total Revenue | % of Total | Transactions |
|--------|---------------|-----------|--------------|
| East | $624,887 | 32.5% | 618 |
| North | $377,646 | 19.6% | 374 |
| West | $337,057 | 17.5% | 334 |
| Central | $195,181 | 10.2% | 193 |
| Southwest | $196,147 | 10.2% | 194 |
| South | $191,541 | 10.0% | 189 |

**→ East region is 3x higher than Central/South (geographic concentration)**

**3. Campaign × Region Performance**
- **Highest:** Campaign 3 × East = $201,103
- **Lowest:** Campaign 2 × South = $37,406
- **Variance:** 5.4x difference between best and worst combination

### Visualizations

Four charts generated (`campaign_effectiveness_charts.png`):
1. **Revenue by Campaign** - Shows Campaign 3 dominance
2. **Transaction Count by Region** - East leads significantly
3. **Avg Discount by Campaign** - Relatively consistent (24-25%)
4. **Revenue by Region** - Clear geographic concentration

---

## 6. Suggested Business Actions

1. **Increase Campaign 3 Investment** - Highest ROI; allocate additional budget to replicate success
2. **Investigate East Region** - Disproportionate success; analyze market characteristics for replication in other regions
3. **Enhance Campaign 2** - Lowest performer; review messaging/targeting or consider reallocation to Campaign 3
4. **Geographic Expansion** - South/Central/Southwest underperform; test localized campaigns or market analysis needed
5. **Discount Strategy** - Average discounts stable at 25%; evaluate if reduction is possible without affecting volume

---

## 7. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Missing Region data (76 rows) | Dropped rows with NaN regions; documented data loss |
| Campaign/Store dimension limited | Used only sales-derived campaigns; sufficient for analysis goals |
| Region values inconsistent | Cleaned during merge; all 6 regions consistent after prep |

---

## Files Generated

- `campaign_effectiveness_by_state.py` - OLAP analysis script
- `slice_campaign_1_by_region.csv` - Slicing result
- `dice_campaign_by_region.csv` - Dicing result (pivot table)
- `drilldown_campaign_region_category.csv` - Drill-down detail
- `campaign_effectiveness_charts.png` - Visualizations (4 charts)

---

**Analysis Date:** November 28, 2025
**Data Period:** Sales from prepared data (2024-2025)
**Next Steps:** Schedule monthly refresh of analysis; monitor Campaign 3 sustainability
