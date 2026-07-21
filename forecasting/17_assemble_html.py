import json

with open('forecasting/report_fragments_category.json') as f:
    F = json.load(f)
with open('forecasting/comparison_summary_category.json') as f:
    CMP = json.load(f)
with open('forecasting/report_fragments_oldforecast.json') as f:
    OLDF = json.load(f)

categories = sorted(F['small_multiples'].keys())
small_mult_panels = '\n'.join(f"""
      <div class="panel">
        <h3>{cat}</h3>
        <p class="panel-sub">MAE — mean {r['mean_mae']:,.0f} · ARIMA{tuple(r['arima_order'])} {r['arima_mae']:,.0f} · LSTM {r['lstm_mae']:,.0f}</p>
        <div class="chart-wrap">{F['small_multiples'][cat]}</div>
      </div>""" for cat, r in zip(categories, CMP['table']))

html = f"""<!-- Challenge 1 (redo): per-category demand forecasting -->
<div class="viz-root">
<style>
  .viz-root {{
    color-scheme: light;
    --page: #f9f9f7; --surface: #fffffe; --surface-sunken: #f3f2ee;
    --text-primary: #14171c; --text-secondary: #52514e; --text-muted: #898781;
    --grid: #e6e5df; --axis: #c3c2b7; --line: #e2e1da; --accent: #2a5fa5;
    --series-1: #2a78d6; --series-2: #eb6834; --series-3: #1baf7a; --series-4: #eda100;
    --series-5: #e87ba4; --series-6: #008300; --series-7: #4a3aa7; --series-8: #e34948;
    --shadow: 0 1px 2px rgba(20,23,28,0.04), 0 8px 24px -12px rgba(20,23,28,0.10);
    --good: #0ca30c;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:where(:not([data-theme="light"])) .viz-root {{
      color-scheme: dark;
      --page: #0d0d0d; --surface: #17181a; --surface-sunken: #1e1f21;
      --text-primary: #f5f5f3; --text-secondary: #c3c2b7; --text-muted: #8f8d86;
      --grid: #2c2c2a; --axis: #3a3a37; --line: #2a2a28; --accent: #6ba3ea;
      --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500;
      --series-5: #d55181; --series-6: #35b135; --series-7: #9085e9; --series-8: #e66767;
      --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
      --good: #0ca30c;
    }}
  }}
  :root[data-theme="dark"] .viz-root {{
    color-scheme: dark;
    --page: #0d0d0d; --surface: #17181a; --surface-sunken: #1e1f21;
    --text-primary: #f5f5f3; --text-secondary: #c3c2b7; --text-muted: #8f8d86;
    --grid: #2c2c2a; --axis: #3a3a37; --line: #2a2a28; --accent: #6ba3ea;
    --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500;
    --series-5: #d55181; --series-6: #35b135; --series-7: #9085e9; --series-8: #e66767;
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
    --good: #0ca30c;
  }}
  :root[data-theme="light"] .viz-root {{
    color-scheme: light;
    --page: #f9f9f7; --surface: #fffffe; --surface-sunken: #f3f2ee;
    --text-primary: #14171c; --text-secondary: #52514e; --text-muted: #898781;
    --grid: #e6e5df; --axis: #c3c2b7; --line: #e2e1da; --accent: #2a5fa5;
  }}

  .viz-root {{ background: var(--page); color: var(--text-primary);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; line-height: 1.5; -webkit-font-smoothing: antialiased; }}
  .viz-root * {{ box-sizing: border-box; }}
  .serif {{ font-family: Georgia, "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif; }}
  .mono {{ font-family: ui-monospace, "SF Mono", Consolas, monospace; font-variant-numeric: tabular-nums; }}

  .wrap {{ max-width: 980px; margin: 0 auto; padding: 0 24px 96px; }}

  .masthead {{ border-bottom: 1px solid var(--line); padding: 56px 0 32px; }}
  .eyebrow {{ text-transform: uppercase; letter-spacing: 0.09em; font-size: 12px; font-weight: 600; color: var(--accent); margin: 0 0 14px; }}
  .masthead h1 {{ font-size: clamp(28px, 4.2vw, 40px); line-height: 1.14; margin: 0 0 12px; font-weight: 600; text-wrap: balance; letter-spacing: -0.01em; }}
  .masthead .dek {{ font-size: 17px; color: var(--text-secondary); max-width: 68ch; margin: 0 0 22px; }}
  .meta-row {{ display: flex; flex-wrap: wrap; gap: 20px; font-size: 13px; color: var(--text-muted); border-top: 1px solid var(--line); padding-top: 16px; }}
  .meta-row span b {{ color: var(--text-secondary); font-weight: 600; }}

  section {{ padding: 44px 0; border-bottom: 1px solid var(--line); }}
  section:last-of-type {{ border-bottom: none; }}
  .section-head {{ margin-bottom: 20px; }}
  .section-head .eyebrow {{ margin-bottom: 8px; }}
  .section-head h2 {{ font-size: 22px; font-weight: 600; margin: 0 0 6px; letter-spacing: -0.005em; }}
  .section-head p {{ color: var(--text-secondary); font-size: 15px; max-width: 72ch; margin: 0; }}

  .callout {{
    background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
    padding: 20px 24px; box-shadow: var(--shadow); font-size: 14.5px; color: var(--text-secondary);
  }}
  .callout b {{ color: var(--text-primary); }}

  .panel-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .panel-grid.thirds {{ grid-template-columns: repeat(3, 1fr); }}
  @media (max-width: 760px) {{ .panel-grid, .panel-grid.thirds {{ grid-template-columns: 1fr; }} }}
  .panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 18px 20px 16px; box-shadow: var(--shadow); }}
  .panel h3 {{ font-size: 14px; font-weight: 600; margin: 0 0 2px; }}
  .panel .panel-sub {{ font-size: 12px; color: var(--text-muted); margin: 0 0 12px; }}
  .panel-wide {{ grid-column: 1 / -1; }}

  .chart-wrap {{ width: 100%; overflow-x: auto; }}
  .axis-label {{ font-size: 11px; fill: var(--text-muted); }}
  .value-label {{ font-size: 12px; fill: var(--text-secondary); font-variant-numeric: tabular-nums; }}
  .tick-label {{ font-size: 10px; fill: var(--text-muted); text-anchor: start; }}
  .grid-line {{ stroke: var(--grid); stroke-width: 1; }}
  .axis-line {{ stroke: var(--axis); stroke-width: 1; }}

  .legend {{ display: flex; gap: 16px; margin-bottom: 12px; font-size: 12.5px; color: var(--text-secondary); flex-wrap: wrap; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-swatch {{ width: 16px; height: 2px; display: inline-block; border-radius: 1px; }}
  .legend-swatch.dash {{ background-image: linear-gradient(90deg, currentColor 50%, transparent 50%); background-size: 6px 2px; background-color: transparent !important; }}

  .findings {{ display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }}
  .findings li {{ display: grid; grid-template-columns: 22px 1fr; gap: 10px; font-size: 14.5px; color: var(--text-secondary); line-height: 1.55; }}
  .findings li::before {{ content: "\\2014"; color: var(--accent); font-weight: 600; }}
  .findings b {{ color: var(--text-primary); font-weight: 600; }}

  .steps {{ display: grid; gap: 14px; }}
  .step {{ display: grid; grid-template-columns: 110px 1fr; gap: 16px; font-size: 14px; }}
  .step .tag {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); padding-top: 2px; }}
  .step .body {{ color: var(--text-secondary); }}
  .step .body b {{ color: var(--text-primary); }}
  code {{ font-family: ui-monospace, "SF Mono", Consolas, monospace; background: var(--surface-sunken); padding: 1px 5px; border-radius: 4px; font-size: 0.92em; color: var(--text-primary); }}

  table.dq {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  table.dq th {{ text-align: left; font-weight: 600; color: var(--text-muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.04em; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
  table.dq td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); color: var(--text-secondary); }}
  table.dq td:first-child, table.dq th:first-child {{ color: var(--text-primary); }}
  table.dq tr:last-child td {{ border-bottom: none; }}
  .table-wrap {{ overflow-x: auto; }}

  footer.colophon {{ padding-top: 28px; font-size: 12.5px; color: var(--text-muted); }}
</style>

<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Challenge 1 &middot; redo &middot; per-category demand forecasting</p>
    <h1 class="serif">Forecast each product type, then split evenly across stores</h1>
    <p class="dek">The first pass collapsed everything into one flat "total demand" number — not actionable
      for stocking, since a warehouse needs to know how much <em>Furniture</em> vs. <em>Groceries</em> to
      hold, not a single company-wide figure. This redo forecasts demand <b>per product category</b>
      (the stable "type" grouping — <code>product_id</code> was already flagged as an unstable, recycled
      slot code, not a real SKU), summed across all 5 stores. Store identity is then dropped from the
      forecast entirely and reintroduced only as an even split, because both the original and a
      within-category re-test confirm store has no meaningful effect on demand.</p>
    <div class="meta-row">
      <span><b>5</b> category series (731 days each)</span>
      <span><b>90-day</b> blind holdout, per category</span>
      <span><b>5</b> independent ARIMA fits</span>
      <span><b>1</b> global LSTM across all 5 categories</span>
    </div>
  </header>

  <section id="verdict">
    <div class="section-head">
      <p class="eyebrow">Direct answer</p>
      <h2>LSTM beats ARIMA — but the CSV's own forecast beats both by ~18&times;</h2>
    </div>
    <div class="callout">
      Two separate questions, two separate answers. <b>Among the models built in this challenge</b>: LSTM MAE
      {F['avg_mae']['lstm_mae']:,.0f} vs. ARIMA MAE {F['avg_mae']['arima_mae']:,.0f}
      ({F['lstm_vs_arima_pct']:+.1f}%) — the global LSTM wins, more clearly than in the single-series version,
      because a per-category ARIMA is more exposed to fitting a spurious trend on a single, shorter, noisier
      series (see Groceries below). But <b>neither comes close to the dataset's own pre-existing
      <code>Demand Forecast</code> column</b>, aggregated to the same grain: {OLDF['avg_mae_raw']:,.0f} MAE raw,
      {OLDF['avg_mae_corrected']:,.0f} once its known bias is corrected — roughly 18&times; better than the
      best new model. See "Reality check" below. What the category split does fix is actionability: the
      output is now a genuine <b>per-category, per-store stock plan</b>, not one number for the whole chain.
    </div>
  </section>

  <section id="granularity">
    <div class="section-head">
      <p class="eyebrow">Step 1 &middot; granularity, corrected</p>
      <h2>Product type is the forecast unit; store is an even split</h2>
      <p>The original hypothesis test (kept from the first pass) showed store, product, category and region
        all move demand by a practically negligible amount at the row level — but that test answers "does the
        <em>average level</em> differ," not "do I need separate numbers to run a warehouse." A retailer still
        stocks Furniture and Groceries as physically different goods, regardless of whether their average
        daily volumes are statistically close. So category — not the full aggregate — is the right forecasting
        unit. Store, on the other hand, really can be dropped: re-testing store's effect
        <em>within each category separately</em> confirms it stays negligible everywhere.</p>
    </div>
    <div class="panel panel-wide">
      <div class="table-wrap">
        <table class="dq">
          <tr><th>Category</th><th>Within-category store &eta;&sup2;</th><th>Interpretation</th></tr>
          <tr><td>Clothing</td><td class="mono">0.00038</td><td>negligible</td></tr>
          <tr><td>Electronics</td><td class="mono">0.00025</td><td>negligible</td></tr>
          <tr><td>Furniture</td><td class="mono">0.00035</td><td>negligible</td></tr>
          <tr><td>Groceries</td><td class="mono">0.00000</td><td>negligible</td></tr>
          <tr><td>Toys</td><td class="mono">0.00070</td><td>negligible</td></tr>
        </table>
      </div>
      <p class="panel-sub" style="margin-top:14px">All five re-tests land far below the 0.01 "negligible"
        threshold — an even 1/5 split across stores is a statistically defensible stocking rule for every
        category, not just on average.</p>
    </div>
  </section>

  <section id="features-diag">
    <div class="section-head">
      <p class="eyebrow">Step 2 &middot; features and diagnostics, re-run per category</p>
      <h2>Still nothing to add — and one category has a real trend</h2>
      <p>Price, discount, promotion, weather, season and weekday were re-tested against each category's own
        daily demand (5 categories &times; 8 variables = 40 tests). <b>Zero survived</b> the same p&lt;0.05 and
        effect&ge;0.02 bar — the univariate decision from the first pass holds per category too. Diagnostics
        turned up one exception worth flagging: Groceries has a small but statistically real downward trend.</p>
    </div>
    <div class="panel panel-wide">
      <div class="table-wrap">
        <table class="dq">
          <tr><th>Category</th><th>Mean</th><th>CV</th><th>ADF p</th><th>Trend slope</th><th>Trend p</th><th>Significant ACF lags</th></tr>
          {F['diag_rows']}
        </table>
      </div>
      <p class="panel-sub" style="margin-top:14px">All five series are already stationary. Groceries is the
        only one with a significant trend (p=0.009, about &minus;0.33 units/day) — small, but enough that
        ARIMA's order search picked a differenced random-walk model for it (see below), which turned out to
        be a costly choice once the trend didn't continue into the test window.</p>
    </div>
  </section>

  <section id="results">
    <div class="section-head">
      <p class="eyebrow">Step 3 &middot; model comparison, per category</p>
      <h2>Five categories, three models, one 90-day blind test each</h2>
      <p>Same protocol as before: both ARIMA and the LSTM forecast the full 90-day holdout with zero access
        to test-period truth. The LSTM is a single <b>global</b> model trained jointly across all 5 category
        series (with category as an input), rather than 5 separate networks — the practical advantage of
        deep learning over classical methods at this scale: one training run instead of five independent
        fits.</p>
    </div>
    <div class="panel panel-wide">
      <h3>Mean absolute error by category and model</h3>
      <p class="panel-sub">Lower is better</p>
      <div class="legend">
        <span class="legend-item"><span class="legend-swatch" style="background:var(--series-4)"></span>Mean baseline</span>
        <span class="legend-item"><span class="legend-swatch" style="background:var(--series-2)"></span>ARIMA</span>
        <span class="legend-item"><span class="legend-swatch" style="background:var(--series-1)"></span>LSTM</span>
      </div>
      <div class="chart-wrap">{F['chart_mae_grouped']}</div>
    </div>
    <div class="panel panel-wide" style="margin-top:16px">
      <div class="table-wrap">
        <table class="dq">
          <tr><th>Category</th><th>Mean baseline MAE</th><th>ARIMA MAE</th><th>LSTM MAE</th><th>Best on test</th></tr>
          {F['cmp_table_rows']}
        </table>
      </div>
    </div>

    <div class="section-head" style="margin-top:32px">
      <h2 style="font-size:18px">Actual vs. forecast, per category</h2>
    </div>
    <div class="legend">
      <span class="legend-item"><span class="legend-swatch" style="background:var(--text-primary)"></span>Actual</span>
      <span class="legend-item"><span class="legend-swatch" style="background:var(--series-1)"></span>LSTM</span>
      <span class="legend-item"><span class="legend-swatch" style="background:var(--series-2)"></span>ARIMA</span>
      <span class="legend-item"><span class="legend-swatch dash" style="color:var(--series-4)"></span>Mean baseline</span>
    </div>
    <div class="panel-grid">{small_mult_panels}
    </div>
  </section>

  <section id="old-vs-new">
    <div class="section-head">
      <p class="eyebrow">Reality check</p>
      <h2>Does any new model actually beat the CSV's own forecast column?</h2>
      <p>Everything above compares the new models to each other. The dataset also ships a pre-existing
        <code>Demand Forecast</code> column, generated per store-product-day. Summed to the same category-daily
        grain as everything else here, how does it stack up?</p>
    </div>
    <div class="callout" style="margin-bottom:16px">
      <b>It wins by a wide margin — not a close call.</b> Raw, the existing column's category-daily MAE is
      {OLDF['avg_mae_raw']:,.0f} units, already 6&times; better than any new model. Correct its one flaw — a
      consistent over-forecast, estimated from the training period only and applied forward — and its MAE
      drops to {OLDF['avg_mae_corrected']:,.0f} units ({OLDF['avg_mape_corrected']:.2f}% MAPE, essentially zero
      residual bias). None of the models built in this challenge come close.
    </div>
    <div class="panel panel-wide">
      <h3>Average MAE across all 5 categories</h3>
      <p class="panel-sub">Lower is better &middot; existing-forecast bars in green, new models in blue/amber/orange</p>
      <div class="chart-wrap">{OLDF['chart_old_vs_new']}</div>
    </div>
    <div class="panel panel-wide" style="margin-top:16px">
      <div class="table-wrap">
        <table class="dq">
          <tr><th>Category</th><th>Old forecast (raw)</th><th>Old forecast (corrected)</th><th>Mean baseline</th><th>ARIMA</th><th>LSTM</th></tr>
          {OLDF['per_cat_rows']}
        </table>
      </div>
    </div>
    <p class="panel-sub" style="margin-top:16px; max-width:72ch">
      <b>Why the gap is this large:</b> the existing column forecasts at store-product-day granularity —
      about 20 individual forecasts feed each category-day total. Each of those row-level forecasts already
      tracks its own actual sale closely (r=0.997, from the original data-quality audit), so their sum tracks
      the category total closely too. The new models in this challenge never see that row-level detail — they
      only see the daily category total itself, a series with no autocorrelation and no useful external
      predictor (Steps 1-2), so they have nothing to work with beyond the historical average. A forecast built
      from finer-grained, genuinely predictive inputs beats a time-series model applied to a coarser series
      with no signal in it, regardless of whether that model is ARIMA or an LSTM.
    </p>
  </section>

  <section id="stock-plan">
    <div class="section-head">
      <p class="eyebrow">The practical output</p>
      <h2>Recommended daily stock, per store, per category</h2>
      <p>Chain-wide daily demand forecast per category (historical mean — the most robust estimator across
        all 5 categories in the comparison above), split evenly across the 5 stores per the store-independence
        finding.</p>
    </div>
    <div class="panel-grid">
      <div class="panel">
        <h3>Per-store daily stock target</h3>
        <p class="panel-sub">Chain-wide forecast &divide; 5 stores</p>
        <div class="chart-wrap">{F['chart_stock']}</div>
      </div>
      <div class="panel">
        <h3>Full numbers</h3>
        <div class="table-wrap">
          <table class="dq">
            <tr><th>Category</th><th>Chain daily demand</th><th>Per store, per day</th></tr>
            {F['stock_rows']}
          </table>
        </div>
      </div>
    </div>
  </section>

  <section id="methodology">
    <div class="section-head">
      <p class="eyebrow">Methodology</p>
      <h2>What changed from the first pass</h2>
    </div>
    <div class="steps">
      <div class="step"><span class="tag">Target</span><span class="body">5 series (one per
        <code>category</code>), each the sum of <code>units_sold</code> across all 5 stores and every
        <code>product_id</code> in that category, per day — instead of 1 series summed across everything.</span></div>
      <div class="step"><span class="tag">Store</span><span class="body">Not modeled — aggregated into the
        category total, then reintroduced only as an even 1/5 split at the end, justified by a fresh
        within-category hypothesis test rather than assumed.</span></div>
      <div class="step"><span class="tag">ARIMA</span><span class="body">5 independent grid searches
        (p,q&isin;[0,3], d&isin;{{0,1}}), each ranked by 60-day validation MAE on that category's own train
        split, refit on train+validation, then a native multi-step forecast of that category's 90-day
        holdout.</span></div>
      <div class="step"><span class="tag">LSTM</span><span class="body">One global model — LSTM(32) over a
        14-day lookback, concatenated with a 5-dim category one-hot, Dense(16) &rarr; Dense(1) — trained
        jointly on sequences from all 5 categories at once, then a blind multi-step rollout for each
        category's own 90-day holdout using that category's own scaler and one-hot flag.</span></div>
    </div>
  </section>

  <section id="conclusion">
    <div class="section-head">
      <p class="eyebrow">Conclusion</p>
      <h2>What this redo actually fixes</h2>
    </div>
    <ul class="findings">
      <li><span><b>The output is now usable.</b> The first pass produced one number for the whole company;
        this version produces a stock target per product type per store — the thing a warehouse manager can
        actually act on.</span></li>
      <li><span><b>LSTM's advantage over ARIMA is now clearer</b> ({F['lstm_vs_arima_pct']:+.1f}% average MAE,
        up from the single-series version's +3.6%), and the reason is visible in the data: ARIMA fits each
        category in isolation and is more exposed to noise — its differenced random-walk pick for Groceries
        (chasing a small real trend that didn't continue) was its single worst result. The global LSTM,
        trained across all 5 categories at once, doesn't have that failure mode.</span></li>
      <li><span><b>Neither model beats the historical mean by much</b> — confirming, at finer grain, what
        Steps 1-2 already showed: none of the dataset's other variables (price, discount, promotion, weather,
        season, weekday) carry usable signal, so a category's own recent average remains the strongest
        available predictor.</span></li>
      <li><span><b>None of that matters next to the reality check:</b> the CSV's own
        <code>Demand Forecast</code> column, simply summed to the same grain, beats every model built here —
        raw ({OLDF['avg_mae_raw']:,.0f} MAE) and especially once its bias is corrected
        ({OLDF['avg_mae_corrected']:,.0f} MAE, {OLDF['avg_mape_corrected']:.2f}% MAPE). It wins because it's
        built from ~20 row-level forecasts per category-day that each individually track their own actual
        sale (r=0.997) — information the daily-aggregate models never see.</span></li>
      <li><span><b>Recommendation, revised:</b> don't replace the existing forecast column with a new
        time-series model — <b>correct its bias and ship it.</b> The bias is a fixed, learnable offset
        (estimate it on a training window, as done here), not something that needs a new model to fix. The
        mean/ARIMA/LSTM work above is still useful as a fallback for a product or store with no row-level
        forecast available, and the global LSTM remains the more robust of the two learned methods in that
        scenario — but it is not the recommended primary forecast when the existing column is available.</span></li>
    </ul>
  </section>

  <footer class="colophon">
    Target: daily <code>units_sold</code> per <code>category</code>, summed across 5 stores &middot;
    Source: <code>data/cleaned/retail_store_inventory_cleaned.csv</code> &middot;
    Pipeline: <code>forecasting/10_category_series.py</code> through <code>17_assemble_html.py</code>
  </footer>
</div>
</div>
"""

out_path = '/tmp/claude-1000/-workspaces-Retail-Store-Inventory-project/6d3a83fb-3bec-4c1b-a1d8-6eedd6d8eb9c/scratchpad/forecasting_report_category.html'
with open(out_path, 'w') as f:
    f.write(html)
print("Wrote report, length:", len(html))
