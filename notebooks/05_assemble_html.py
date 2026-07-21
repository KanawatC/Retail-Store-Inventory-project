import json

with open('outputs/eda_summary.json') as f:
    D = json.load(f)
with open('outputs/charts_cache.json') as f:
    C = json.load(f)

ov = D['overview']
fa = D['forecast_accuracy']
pc = D['price_competitor']

def fmt_money(v, digits=1):
    v = float(v)
    if abs(v) >= 1_000_000_000:
        return f"${v/1_000_000_000:.{digits}f}B"
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.{digits}f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.{digits}f}K"
    return f"${v:.0f}"

def fmt_num(v, digits=1):
    v = float(v)
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.{digits}f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.{digits}f}K"
    return f"{v:.0f}"

kpis = [
    ("Total revenue", fmt_money(ov['total_revenue']), "Jan 2022 – Dec 2023, 5 stores"),
    ("Units sold", fmt_num(ov['total_units_sold']), "across 20 product slots"),
    ("Avg daily revenue", fmt_money(ov['avg_daily_revenue']), "per day, all stores combined"),
    ("Stockout rate", f"{ov['overall_stockout_rate']*100:.2f}%", "days sold ≥ on-hand inventory"),
    ("Forecast MAE", f"{fa['mae']:.1f} units", f"bias {fa['mean_bias']:+.1f} units/day"),
    ("Avg sell-through", f"{ov['avg_sell_through_rate']*100:.1f}%", "units sold ÷ inventory on hand"),
]

kpi_html = "\n".join(f'''
      <div class="kpi">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
      </div>''' for label, value, note in kpis)

html = f"""<!-- Retail Store Inventory: Cleaning & EDA Report -->
<div class="viz-root">
<style>
  .viz-root {{
    color-scheme: light;
    --page:            #f9f9f7;
    --surface:         #fffffe;
    --surface-sunken:  #f3f2ee;
    --text-primary:    #14171c;
    --text-secondary:  #52514e;
    --text-muted:      #898781;
    --grid:            #e6e5df;
    --axis:            #c3c2b7;
    --line:            #e2e1da;
    --accent:          #2a5fa5;
    --series-1: #2a78d6; --series-2: #eb6834; --series-3: #1baf7a; --series-4: #eda100;
    --series-5: #e87ba4; --series-6: #008300; --series-7: #4a3aa7; --series-8: #e34948;
    --div-pos: #2a78d6; --div-neg: #e34948; --div-mid: #f0efec;
    --shadow: 0 1px 2px rgba(20,23,28,0.04), 0 8px 24px -12px rgba(20,23,28,0.10);
  }}
  @media (prefers-color-scheme: dark) {{
    :root:where(:not([data-theme="light"])) .viz-root {{
      color-scheme: dark;
      --page:            #0d0d0d;
      --surface:         #17181a;
      --surface-sunken:  #1e1f21;
      --text-primary:    #f5f5f3;
      --text-secondary:  #c3c2b7;
      --text-muted:      #8f8d86;
      --grid:            #2c2c2a;
      --axis:            #3a3a37;
      --line:            #2a2a28;
      --accent:          #6ba3ea;
      --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500;
      --series-5: #d55181; --series-6: #35b135; --series-7: #9085e9; --series-8: #e66767;
      --div-pos: #3987e5; --div-neg: #e66767; --div-mid: #383835;
      --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
    }}
  }}
  :root[data-theme="dark"] .viz-root {{
    color-scheme: dark;
    --page:            #0d0d0d;
    --surface:         #17181a;
    --surface-sunken:  #1e1f21;
    --text-primary:    #f5f5f3;
    --text-secondary:  #c3c2b7;
    --text-muted:      #8f8d86;
    --grid:            #2c2c2a;
    --axis:            #3a3a37;
    --line:            #2a2a28;
    --accent:          #6ba3ea;
    --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500;
    --series-5: #d55181; --series-6: #35b135; --series-7: #9085e9; --series-8: #e66767;
    --div-pos: #3987e5; --div-neg: #e66767; --div-mid: #383835;
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
  }}
  :root[data-theme="light"] .viz-root {{
    color-scheme: light;
    --page: #f9f9f7; --surface: #fffffe; --surface-sunken: #f3f2ee;
    --text-primary: #14171c; --text-secondary: #52514e; --text-muted: #898781;
    --grid: #e6e5df; --axis: #c3c2b7; --line: #e2e1da; --accent: #2a5fa5;
  }}

  .viz-root {{
    background: var(--page);
    color: var(--text-primary);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  .viz-root * {{ box-sizing: border-box; }}
  .serif {{
    font-family: Georgia, "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
  }}
  .mono {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Consolas, monospace;
    font-variant-numeric: tabular-nums;
  }}

  .wrap {{ max-width: 960px; margin: 0 auto; padding: 0 24px 96px; }}

  /* ---- masthead ---- */
  .masthead {{
    border-bottom: 1px solid var(--line);
    padding: 56px 0 32px;
  }}
  .eyebrow {{
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    margin: 0 0 14px;
  }}
  .masthead h1 {{
    font-size: clamp(28px, 4.4vw, 42px);
    line-height: 1.12;
    margin: 0 0 12px;
    font-weight: 600;
    text-wrap: balance;
    letter-spacing: -0.01em;
  }}
  .masthead .dek {{
    font-size: 17px;
    color: var(--text-secondary);
    max-width: 62ch;
    margin: 0 0 22px;
  }}
  .meta-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    font-size: 13px;
    color: var(--text-muted);
    border-top: 1px solid var(--line);
    padding-top: 16px;
  }}
  .meta-row span b {{ color: var(--text-secondary); font-weight: 600; }}

  /* ---- sections ---- */
  section {{ padding: 44px 0; border-bottom: 1px solid var(--line); }}
  section:last-of-type {{ border-bottom: none; }}
  .section-head {{ margin-bottom: 20px; }}
  .section-head .eyebrow {{ margin-bottom: 8px; }}
  .section-head h2 {{
    font-size: 23px;
    font-weight: 600;
    margin: 0 0 6px;
    letter-spacing: -0.005em;
  }}
  .section-head p {{
    color: var(--text-secondary);
    font-size: 15px;
    max-width: 68ch;
    margin: 0;
  }}

  /* ---- KPI strip ---- */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
  }}
  .kpi {{ background: var(--surface); padding: 18px 18px 16px; }}
  .kpi-label {{ font-size: 12.5px; color: var(--text-muted); margin-bottom: 8px; }}
  .kpi-value {{
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 24px; font-weight: 600; letter-spacing: -0.01em;
    margin-bottom: 6px;
  }}
  .kpi-note {{ font-size: 12px; color: var(--text-muted); }}

  /* ---- panels ---- */
  .panel-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .panel-grid.thirds {{ grid-template-columns: repeat(3, 1fr); }}
  .panel-grid.quarters {{ grid-template-columns: repeat(4, 1fr); }}
  @media (max-width: 760px) {{
    .panel-grid, .panel-grid.thirds, .panel-grid.quarters {{ grid-template-columns: 1fr; }}
  }}
  .panel {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 18px 20px 16px;
    box-shadow: var(--shadow);
  }}
  .panel h3 {{
    font-size: 14px; font-weight: 600; margin: 0 0 2px;
  }}
  .panel .panel-sub {{ font-size: 12.5px; color: var(--text-muted); margin: 0 0 14px; }}
  .panel-wide {{ grid-column: 1 / -1; }}

  .chart-wrap {{ width: 100%; overflow-x: auto; }}
  .axis-label {{ font-size: 11.5px; fill: var(--text-muted); }}
  .value-label {{ font-size: 12px; fill: var(--text-secondary); font-variant-numeric: tabular-nums; }}
  .tick-label {{ font-size: 10.5px; fill: var(--text-muted); text-anchor: start; }}
  .grid-line {{ stroke: var(--grid); stroke-width: 1; }}
  .axis-line {{ stroke: var(--axis); stroke-width: 1; }}

  .legend {{ display: flex; gap: 16px; margin-bottom: 12px; font-size: 12.5px; color: var(--text-secondary); }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-swatch {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; }}

  /* ---- findings list ---- */
  .findings {{ display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }}
  .findings li {{
    display: grid; grid-template-columns: 22px 1fr; gap: 10px;
    font-size: 14.5px; color: var(--text-secondary); line-height: 1.55;
  }}
  .findings li::before {{ content: "—"; color: var(--accent); font-weight: 600; }}
  .findings b {{ color: var(--text-primary); font-weight: 600; }}

  /* ---- methodology ---- */
  .steps {{ display: grid; gap: 14px; }}
  .step {{ display: grid; grid-template-columns: 100px 1fr; gap: 16px; font-size: 14px; }}
  .step .tag {{
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--text-muted); padding-top: 2px;
  }}
  .step .body {{ color: var(--text-secondary); }}
  .step .body b {{ color: var(--text-primary); }}
  code {{
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    background: var(--surface-sunken); padding: 1px 5px; border-radius: 4px; font-size: 0.92em;
    color: var(--text-primary);
  }}

  table.dq {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  table.dq th {{
    text-align: left; font-weight: 600; color: var(--text-muted);
    font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.04em;
    padding: 8px 12px; border-bottom: 1px solid var(--line);
  }}
  table.dq td {{ padding: 9px 12px; border-bottom: 1px solid var(--line); color: var(--text-secondary); }}
  table.dq td:first-child, table.dq th:first-child {{ color: var(--text-primary); }}
  table.dq tr:last-child td {{ border-bottom: none; }}

  footer.colophon {{
    padding-top: 28px; font-size: 12.5px; color: var(--text-muted);
  }}
</style>

<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Data cleaning &amp; exploratory analysis</p>
    <h1 class="serif">Retail Store Inventory — two years of demand, pricing &amp; stock signals</h1>
    <p class="dek">A full clean-and-explore pass over the store-level inventory dataset: {ov['rows']:,} daily
      records spanning {ov['n_stores']} stores, {ov['n_categories']} categories and {ov['n_regions']} regions,
      {ov['date_min']} through {ov['date_max']}.</p>
    <div class="meta-row">
      <span><b>{ov['rows']:,}</b> rows</span>
      <span><b>0</b> missing values</span>
      <span><b>0</b> duplicate records</span>
      <span><b>673</b> rows with invalid forecast values (clipped)</span>
      <span><b>27</b> columns after cleaning (15 source + 12 derived)</span>
    </div>
  </header>

  <section id="summary">
    <div class="section-head">
      <p class="eyebrow">Executive summary</p>
      <h2>What the data actually says</h2>
      <p>The dataset is well-formed but strikingly uniform — most fields a retailer would expect to drive
        demand show almost no effect here. Two findings dominate.</p>
    </div>
    <ul class="findings">
      <li><span><b>Demand forecast tracks actual sales almost exactly</b> (r = 0.997) but is
        systematically <b>{abs(fa['mean_bias']):.1f} units high on average</b> — a consistent over-forecast bias,
        not random noise (MAE {fa['mae']:.1f} units, MAPE {fa['mape']:.1f}%).</span></li>
      <li><span><b>Price and competitor pricing move in lockstep</b> (r = 0.994), with the store priced above
        the competitor on <b>{pc['pct_priced_above_competitor']:.0f}%</b> of records — essentially a coin flip,
        suggesting competitor pricing was generated as a function of the store's own price.</span></li>
      <li><span><b>Region, store, category, season, weekday, weather and discount level each move average
        units sold by well under 2%</b> — none is a meaningful demand driver in this dataset (see "What moves
        the needle" below).</span></li>
      <li><span><b>Stock is rarely a binding constraint:</b> the stockout proxy rate is
        <b>{ov['overall_stockout_rate']*100:.2f}%</b> and average sell-through is only
        <b>{ov['avg_sell_through_rate']*100:.1f}%</b> — stores are holding roughly 2× the inventory they sell
        through day to day.</span></li>
      <li><span><b>Product ID is not a unique product key</b> — the same 20 IDs cycle through all 5 categories
        within a single store, so <code>product_id</code> alone cannot be treated as a SKU (see Data quality notes).</span></li>
    </ul>
  </section>

  <section id="kpis">
    <div class="section-head">
      <p class="eyebrow">Headline metrics</p>
      <h2>Two-year overview</h2>
    </div>
    <div class="kpi-grid">{kpi_html}
    </div>
  </section>

  <section id="trend">
    <div class="section-head">
      <p class="eyebrow">Time series</p>
      <h2>Revenue held flat across the full period</h2>
      <p>Monthly revenue oscillates in a tight band with no visible growth trend or seasonal cycle over 24
        full months (the trailing single day of Jan 2024 is excluded as a partial period).</p>
    </div>
    <div class="panel panel-wide">
      <h3>Monthly revenue, Jan 2022 – Dec 2023</h3>
      <p class="panel-sub">Sum of units_sold × price × (1 − discount), all stores &amp; categories</p>
      <div class="chart-wrap">{C['chart_revenue_trend']}</div>
    </div>
  </section>

  <section id="breakdown">
    <div class="section-head">
      <p class="eyebrow">Where the revenue sits</p>
      <h2>Category and region are nearly interchangeable</h2>
      <p>Revenue splits almost evenly — the gap between the top and bottom category is under 3%, and under
        2% between regions.</p>
    </div>
    <div class="panel-grid">
      <div class="panel">
        <h3>Revenue by category</h3>
        <p class="panel-sub">Two-year total, sorted descending</p>
        <div class="chart-wrap">{C['chart_cat_revenue']}</div>
      </div>
      <div class="panel">
        <h3>Revenue by region</h3>
        <p class="panel-sub">Two-year total, sorted descending</p>
        <div class="chart-wrap">{C['chart_region_revenue']}</div>
      </div>
    </div>
  </section>

  <section id="drivers">
    <div class="section-head">
      <p class="eyebrow">Driver check</p>
      <h2>What moves the needle on units sold — almost nothing</h2>
      <p>Average daily units sold by season, weekday, discount tier and weather condition. Each axis spans a
        narrow 132–139 unit band against an overall mean of {ov['total_units_sold']/ov['rows']:.0f} units/row —
        none of these operational levers show a practically meaningful effect.</p>
    </div>
    <div class="panel-grid quarters">
      <div class="panel">
        <h3>By season</h3>
        <div class="chart-wrap">{C['chart_season']}</div>
      </div>
      <div class="panel">
        <h3>By weekday</h3>
        <div class="chart-wrap">{C['chart_weekday']}</div>
      </div>
      <div class="panel">
        <h3>By discount tier</h3>
        <div class="chart-wrap">{C['chart_discount']}</div>
      </div>
      <div class="panel">
        <h3>By weather</h3>
        <div class="chart-wrap">{C['chart_weather']}</div>
      </div>
    </div>
  </section>

  <section id="forecast">
    <div class="section-head">
      <p class="eyebrow">Forecast accuracy</p>
      <h2>The demand forecast consistently overshoots</h2>
      <p>Every category's forecast sits above actual units sold by roughly the same margin — a structural
        bias worth correcting before the forecast is used for replenishment decisions.</p>
    </div>
    <div class="panel-grid">
      <div class="panel">
        <h3>Actual vs. forecast, by category</h3>
        <p class="panel-sub">Average units per store-day</p>
        <div class="legend">
          <span class="legend-item"><span class="legend-swatch" style="background:var(--series-1)"></span>Actual units sold</span>
          <span class="legend-item"><span class="legend-swatch" style="background:var(--series-4)"></span>Demand forecast</span>
        </div>
        <div class="chart-wrap">{C['chart_forecast']}</div>
      </div>
      <div class="panel">
        <h3>Forecast error summary</h3>
        <p class="panel-sub">units_sold − demand_forecast, full dataset</p>
        <table class="dq">
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Mean bias</td><td class="mono">{fa['mean_bias']:+.2f} units/day</td></tr>
          <tr><td>Mean absolute error (MAE)</td><td class="mono">{fa['mae']:.2f} units</td></tr>
          <tr><td>RMSE</td><td class="mono">{fa['rmse']:.2f} units</td></tr>
          <tr><td>MAPE</td><td class="mono">{fa['mape']:.1f}%</td></tr>
          <tr><td>Rows with negative raw forecast (clipped in cleaning)</td><td class="mono">673 (0.92%)</td></tr>
        </table>
      </div>
    </div>
  </section>

  <section id="correlation">
    <div class="section-head">
      <p class="eyebrow">Relationships between variables</p>
      <h2>Two pairs dominate; everything else is near-independent</h2>
      <p><code>demand_forecast</code> ↔ <code>units_sold</code> (0.997) and <code>price</code> ↔
        <code>competitor_pricing</code> (0.994) are the only strong relationships in the numeric data.
        <code>inventory_level</code> shows a moderate positive link to sales (~0.59) — stock is somewhat
        demand-aware, just not tightly so.</p>
    </div>
    <div class="panel panel-wide">
      <h3>Correlation matrix</h3>
      <p class="panel-sub">Pearson r, cleaned numeric fields</p>
      <div class="chart-wrap">{C['chart_corr']}</div>
    </div>
  </section>

  <section id="methodology">
    <div class="section-head">
      <p class="eyebrow">Methodology</p>
      <h2>Cleaning steps applied</h2>
    </div>
    <div class="steps">
      <div class="step"><span class="tag">Schema</span><span class="body">Column headers normalized to
        <code>snake_case</code>; <code>date</code> parsed to datetime; <code>store_id</code>, <code>product_id</code>,
        <code>category</code>, <code>region</code>, <code>weather_condition</code> and <code>seasonality</code>
        cast to categorical; <code>holiday_promotion</code> cast to boolean.</span></div>
      <div class="step"><span class="tag">Validity</span><span class="body"><b>673 rows (0.92%)</b> had a
        negative <code>demand_forecast</code> (min −9.99) — not possible for a demand quantity. Clipped to 0
        and flagged in <code>demand_forecast_was_negative</code> rather than dropped, so the rows stay in the
        dataset for every other field.</span></div>
      <div class="step"><span class="tag">Duplicates</span><span class="body">Checked for exact duplicate rows
        and duplicate <code>(date, store_id, product_id, category)</code> keys — <b>zero found</b>. The panel
        is a complete, evenly-spaced grid: 731 days × 5 stores × 20 product slots = 73,100 rows exactly.</span></div>
      <div class="step"><span class="tag">Missing data</span><span class="body"><b>Zero missing values</b>
        across all 15 source columns — no imputation was necessary.</span></div>
      <div class="step"><span class="tag">Derived fields</span><span class="body">Added <code>revenue</code>
        (units_sold × price × (1 − discount/100)), <code>forecast_error</code> and <code>abs_forecast_error</code>,
        <code>stockout_flag</code> (units_sold ≥ inventory_level), <code>sell_through_rate</code>,
        <code>price_vs_competitor</code>, plus calendar fields (<code>year</code>, <code>month</code>,
        <code>weekday</code>, <code>is_weekend</code>) for the time-based cuts above.</span></div>
    </div>
  </section>

  <section id="limitations">
    <div class="section-head">
      <p class="eyebrow">Data quality notes &amp; limitations</p>
      <h2>Read these before building on this dataset</h2>
    </div>
    <table class="dq">
      <tr><th>Observation</th><th>Detail</th></tr>
      <tr><td>Product ID is not a stable product key</td><td>Each of the 20 <code>product_id</code> values
        appears under all 5 categories within every store over the two years — it behaves as a recycled slot
        code (1–20), not a persistent SKU. Treat <code>(store_id, product_id, category)</code> as the finest
        reliable grouping, and note even that combination isn't temporally stable.</td></tr>
      <tr><td>Near-perfect synthetic correlations</td><td><code>demand_forecast</code>↔<code>units_sold</code>
        (0.997) and <code>price</code>↔<code>competitor_pricing</code> (0.994) are far tighter than real retail
        telemetry typically shows, consistent with these fields being generated from one another with added
        noise rather than measured independently.</td></tr>
      <tr><td>Operational levers show flat effects</td><td>Holiday/promotion flag, discount tier, weather and
        seasonality each move average units sold by low single-digit percentages — treat this dataset as
        unsuitable for building or validating a promo-uplift or weather-sensitivity model.</td></tr>
      <tr><td>Partial final period</td><td>The series ends 2024-01-01, a single day past 24 full months —
        excluded from the monthly trend chart to avoid an artificial drop.</td></tr>
      <tr><td>Negative demand forecasts</td><td>0.92% of rows had a raw forecast below zero (as low as −9.99);
        clipped to 0 during cleaning and flagged rather than imputed or dropped.</td></tr>
    </table>
  </section>

  <footer class="colophon">
    Source: <code>retail_store_inventory.csv</code> (73,100 rows, 2022-01-01 to 2024-01-01) ·
    Cleaned dataset: <code>data/cleaned/retail_store_inventory_cleaned.csv</code> ·
    Prepared with pandas — see <code>notebooks/01_profile.py</code> through <code>05_assemble_html.py</code>.
  </footer>
</div>
</div>
"""

with open('/tmp/claude-1000/-workspaces-Retail-Store-Inventory-project/6d3a83fb-3bec-4c1b-a1d8-6eedd6d8eb9c/scratchpad/retail_report.html', 'w') as f:
    f.write(html)

print("Wrote report, length:", len(html))
