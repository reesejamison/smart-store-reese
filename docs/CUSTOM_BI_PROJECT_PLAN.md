# Custom BI Project Plan: Customer Loyalty & Revenue Optimization

## Your name:
Reese Jamison

## Your business goal:
**Optimize product mix and pricing strategy by analyzing discount effectiveness across product categories and store locations to maximize profit margins while maintaining sales velocity.**

## Why did you choose this goal:
This goal was selected because:
1. **Profitability Focus**: Rather than focusing solely on revenue, this analyzes the balance between discounts, sales volume, and margin preservation - directly impacting bottom-line profitability
2. **Operational Excellence**: Understanding which products sell well at different discount levels helps merchandising teams make data-driven pricing decisions and avoid over-discounting
3. **Store-Level Insights**: By analyzing performance by store location, we can identify best practices and replicate successful strategies across underperforming locations
4. **Inventory Turnover**: Connects discount strategy to stock movement, helping reduce dead inventory costs and improve cash flow
5. **Unique Analysis Angle**: While previous work analyzed campaign effectiveness, this focuses on product-level profitability and operational efficiency - a complementary but distinct business question that addresses "how to sell" rather than "who to target"

---

## Descriptive Dimensions - List the dimensions you will analyze and why they matter:

1. **Product Category** (Electronics/Clothing/Office/Home)
   - *Why it matters*: Different categories have different margin structures and price elasticity - Electronics may tolerate lower discounts while Clothing may require steeper promotions to move inventory

2. **Store Location** (StoreID 401-405+)
   - *Why it matters*: Store performance varies by location demographics, competition, and management practices - identifying top performers reveals replicable best practices

3. **Discount Tier** (0-10%, 10-20%, 20-30%, 30%+)
   - *Why it matters*: Critical for understanding price elasticity - at what discount level do sales spike without unnecessarily sacrificing margin?

4. **Stock Quantity Level** (Low: 0-250, Medium: 251-500, High: 501+)
   - *Why it matters*: Connects inventory levels to discounting behavior - are we over-discounting products with healthy stock levels?

5. **Supplier** (GlobalTech, SupplyCo, Unknown/Others)
   - *Why it matters*: Different suppliers may have different cost structures affecting optimal pricing strategies and margin potential

6. **Time Period** (Month, Quarter, Holiday vs. Non-Holiday)
   - *Why it matters*: Seasonal patterns inform when aggressive discounting is necessary versus when products sell without promotions

---

## Numeric Metrics - List the metrics you will calculate and why they are important:

1. **Gross Margin by Category**
   - *Importance*: Shows profitability after accounting for discounts - reveals which categories maintain healthy margins vs. those eroded by promotions
   - *Calculation*: `(SaleAmount - (SaleAmount * DiscountPercent/100)) / SaleAmount * 100`

2. **Sales Velocity (Units per Day)**
   - *Importance*: Measures how quickly inventory moves - fast movers may not need deep discounts
   - *Calculation*: `COUNT(TransactionID) / Number of Days in Period` per product/category

3. **Discount Efficiency Ratio**
   - *Importance*: Determines if discounts are driving incremental volume or just giving away margin
   - *Calculation*: `% Change in Volume / % Increase in Discount Depth` - ratios >1 indicate efficient discounting

4. **Average Discount Depth by Category**
   - *Importance*: Identifies over-discounting patterns that may be habitual rather than strategic
   - *Calculation*: `AVG(DiscountPercent)` grouped by product category and store

5. **Revenue per Square Foot (Proxy: Revenue per Store)**
   - *Importance*: Store-level efficiency metric showing which locations generate the most value
   - *Calculation*: `SUM(SaleAmount)` per StoreID divided by store count

6. **Stock Turn Rate**
   - *Importance*: How many times inventory is sold and replaced - slow movers tie up capital
   - *Calculation*: `Total Units Sold / Average Stock Quantity` over time period

7. **Net Revenue (After Discount)**
   - *Importance*: True revenue realization after promotional costs - more accurate than gross sales
   - *Calculation*: `SUM(SaleAmount * (1 - DiscountPercent/100))`

---

## Aggregations - What aggregations will you perform:

1. **SUM Aggregations**:
   - Total gross revenue by category and store
   - Total net revenue (after discounts) by category
   - Total units sold by discount tier
   - Total discount dollars given away by category

2. **COUNT Aggregations**:
   - Number of transactions by discount tier
   - Number of products by stock quantity level
   - Number of sales per store per category
   - Transaction count by supplier

3. **AVERAGE (AVG) Aggregations**:
   - Average discount percentage by category and store
   - Average sale amount by discount tier
   - Average stock quantity by category
   - Average gross margin percentage by store

4. **MIN/MAX Aggregations**:
   - Highest and lowest margin products per category
   - Peak and minimum sales by store location
   - Minimum discount required to move slow inventory
   - Maximum discount offered by category (identify outliers)

5. **RATIO/EFFICIENCY Calculations**:
   - Discount efficiency ratio (volume lift vs. margin sacrifice)
   - Stock turn rate by category
   - Revenue per store (efficiency metric)
   - Margin preservation rate = Net Revenue / Gross Revenue
   - Sales concentration (% of revenue from top 20% of products)

---

## Slicing and Dicing - How will you break down the data:

**Slicing** (filtering by one dimension):
- Slice by Category: Show only "Electronics" to analyze their discount patterns
- Slice by Store: Filter to Store 401 to see what makes it successful
- Slice by Discount Tier: Look only at 30%+ discounts to find over-discounting

**Dicing** (filtering multiple dimensions simultaneously):
- Electronics + High Discount (30%+) + Low Stock = identify clearance opportunities
- Clothing + Store 402 + Q4 = understand seasonal performance at specific location
- Office supplies + 0-10% discount + High Sales = products that don't need promotions

---

## Drilldown - What deeper insights will you explore:

**Level 1**: Total revenue by category (Electronics = $X, Clothing = $Y)

**Level 2**: Drill into Electronics → break down by store location
- Discover which stores are best at selling Electronics

**Level 3**: Drill into best Electronics store → break down by discount tier
- See if they use less discounting or just have better location

**Level 4**: Drill into specific discount tier → individual products
- Identify which specific products drive the results

---

## What type of chart/graph will you use and why:

**Bar Chart**: Compare average discount % across categories
- Shows which categories are over-discounted at a glance

**Heatmap**: Store (rows) × Category (columns) with revenue as color intensity
- Quickly spot high/low performing store-category combinations

**Scatter Plot**: Discount % (x-axis) vs. Sales Volume (y-axis)
- Shows if higher discounts actually drive more sales (discount efficiency)

**Line Chart**: Net margin % over time by category
- Track if profitability is improving or declining

---

## What might be difficult about implementing this:

1. **Calculating net margin accurately** - Need to account for discount impact on profitability, requires math: `SaleAmount * (1 - DiscountPercent/100)`

2. **Joining multiple tables** - Sales data needs to connect with Products (for category, stock) and possibly Stores

3. **Discount tier binning** - Need to categorize discounts into ranges (0-10%, 10-20%, etc.) using conditional logic

4. **Limited store data** - Only have StoreID numbers, no geographic or demographic context about locations

5. **Seasonality complexity** - Hard to know if discount patterns are strategic or just seasonal without multi-year data

---

## What actions might the business take based on your insights:

1. **Reduce unnecessary discounting** - If Electronics sells well with 15% discounts, stop offering 30%+ discounts on those items to preserve margin

2. **Replicate best store practices** - If Store 401 achieves high sales with lower discounts, train other store managers on their approach

3. **Clear slow inventory strategically** - Items with high stock + low sales velocity get targeted discounts, while fast movers need minimal promotion

4. **Category-specific pricing rules** - Set maximum discount guidelines by category (e.g., Electronics max 20%, Clothing max 35%)

5. **Seasonal discount planning** - Use historical data to plan when discounts are truly needed vs. when products sell at full price

6. **Optimize store inventory allocation** - Send more high-margin products to stores that can sell them without heavy discounting

---

## Resources & References

**1. Pandas Pivot Tables Documentation**
- **Link**: [https://pandas.pydata.org/docs/user_guide/reshaping.html](https://pandas.pydata.org/docs/user_guide/reshaping.html)
- **Why**: Essential for slicing, dicing, and creating cross-tabulations in Python

**2. Matplotlib Bar Charts and Heatmaps**
- **Link**: [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html)
- **Why**: Shows code examples for all the chart types needed in this analysis
