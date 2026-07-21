import json

with open('forecasting/report_fragments.json') as f:
    F = json.load(f)
with open('forecasting/comparison_summary.json') as f:
    CMP = json.load(f)

best_model = CMP['table'][0]['model']
lstm_row = next(r for r in CMP['table'] if r['model'].startswith('LSTM'))
arima_row = next(r for r in CMP['table'] if r['model'].startswith('ARIMA'))
mean_row = next(r for r in CMP['table'] if r['model'] == 'Historical mean')

html = f"""<!-- Challenge 1: Time Series Demand Forecasting -->
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
    --good: #0ca30c; --warn: #c98500;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:where(:not([data-theme="light"])) .viz-root {{
      color-scheme: dark;
      --page: #0d0d0d; --surface: #17181a; --surface-sunken: #1e1f21;
      --text-primary: #f5f5f3; --text-secondary: #c3c2b7; --text-muted: #8f8d86;
      --grid: #2c2c2a; --axis: #3a3a37; --line: #2a2a28; --accent: #6ba3ea;
      --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500;
      --series-5: #d55181; --series-6: #35b135; --series-7: #9085e9; --series-8: #e66767;
      --div-pos: #3987e5; --div-neg: #e66767; --div-mid: #383835;
      --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
      --good: #0ca30c; --warn: #c98500;
    }}
  }}
  :root[data-theme="dark"] .viz-root {{
    color-scheme: dark;
    --page: #0d0d0d; --surface: #17181a; --surface-sunken: #1e1f21;
    --text-primary: #f5f5f3; --text-secondary: #c3c2b7; --text-muted: #8f8d86;
    --grid: #2c2c2a; --axis: #3a3a37; --line: #2a2a28; --accent: #6ba3ea;
    --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70; --series-4: #c98500;
    --series-5: #d55181; --series-6: #35b135; --series-7: #9085e9; --series-8: #e66767;
    --div-pos: #3987e5; --div-neg: #e66767; --div-mid: #383835;
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
    --good: #0ca30c; --warn: #c98500;
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
  .mono {{ font-family: ui-monospace, "SF Mono", "Cascadia Mono", Consolas, monospace; font-variant-numeric: tabular-nums; }}

  .wrap {{ max-width: 960px; margin: 0 auto; padding: 0 24px 96px; }}

  .masthead {{ border-bottom: 1px solid var(--line); padding: 56px 0 32px; }}
  .eyebrow {{ text-transform: uppercase; letter-spacing: 0.09em; font-size: 12px; font-weight: 600; color: var(--accent); margin: 0 0 14px; }}
  .masthead h1 {{ font-size: clamp(28px, 4.4vw, 42px); line-height: 1.12; margin: 0 0 12px; font-weight: 600; text-wrap: balance; letter-spacing: -0.01em; }}
  .masthead .dek {{ font-size: 17px; color: var(--text-secondary); max-width: 66ch; margin: 0 0 22px; }}
  .meta-row {{ display: flex; flex-wrap: wrap; gap: 20px; font-size: 13px; color: var(--text-muted); border-top: 1px solid var(--line); padding-top: 16px; }}
  .meta-row span b {{ color: var(--text-secondary); font-weight: 600; }}

  section {{ padding: 44px 0; border-bottom: 1px solid var(--line); }}
  section:last-of-type {{ border-bottom: none; }}
  .section-head {{ margin-bottom: 20px; }}
  .section-head .eyebrow {{ margin-bottom: 8px; }}
  .section-head h2 {{ font-size: 23px; font-weight: 600; margin: 0 0 6px; letter-spacing: -0.005em; }}
  .section-head p {{ color: var(--text-secondary); font-size: 15px; max-width: 70ch; margin: 0; }}

  .verdict {{
    display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap;
    background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
    padding: 22px 26px; box-shadow: var(--shadow); margin-bottom: 4px;
  }}
  .verdict .big {{ font-size: 30px; font-weight: 700; font-family: ui-monospace, "SF Mono", Consolas, monospace; }}
  .verdict .big.yes {{ color: var(--good); }}
  .verdict .sub {{ color: var(--text-secondary); font-size: 14.5px; max-width: 56ch; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }}
  .kpi {{ background: var(--surface); padding: 18px 18px 16px; }}
  .kpi-label {{ font-size: 12.5px; color: var(--text-muted); margin-bottom: 8px; }}
  .kpi-value {{ font-family: ui-monospace, "SF Mono", Consolas, monospace; font-size: 22px; font-weight: 600; letter-spacing: -0.01em; margin-bottom: 6px; }}
  .kpi-note {{ font-size: 12px; color: var(--text-muted); }}

  .panel-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media (max-width: 760px) {{ .panel-grid {{ grid-template-columns: 1fr; }} }}
  .panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 18px 20px 16px; box-shadow: var(--shadow); }}
  .panel h3 {{ font-size: 14px; font-weight: 600; margin: 0 0 2px; }}
  .panel .panel-sub {{ font-size: 12.5px; color: var(--text-muted); margin: 0 0 14px; }}
  .panel-wide {{ grid-column: 1 / -1; }}

  .chart-wrap {{ width: 100%; overflow-x: auto; }}
  .axis-label {{ font-size: 11.5px; fill: var(--text-muted); }}
  .value-label {{ font-size: 12px; fill: var(--text-secondary); font-variant-numeric: tabular-nums; }}
  .tick-label {{ font-size: 10.5px; fill: var(--text-muted); text-anchor: start; }}
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

  table.dq {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  table.dq th {{ text-align: left; font-weight: 600; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
  table.dq td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); color: var(--text-secondary); }}
  table.dq td:first-child, table.dq th:first-child {{ color: var(--text-primary); }}
  table.dq tr:last-child td {{ border-bottom: none; }}
  table.dq tr.highlight td {{ background: var(--surface-sunken); color: var(--text-primary); font-weight: 600; }}
  .table-wrap {{ overflow-x: auto; }}

  footer.colophon {{ padding-top: 28px; font-size: 12.5px; color: var(--text-muted); }}
</style>

<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Challenge 1 &middot; Time series demand forecasting</p>
    <h1 class="serif">Does an LSTM beat ARIMA on this dataset? — a hypothesis-driven forecast</h1>
    <p class="dek">Before modeling anything, we let hypothesis tests decide two things a forecaster usually
      guesses at: what granularity to forecast, and which features earn a place in the model. Both questions
      came back with the same answer: <b>almost nothing in this dataset predicts demand except its own
      history</b> — and even that history turns out to carry very little signal.</p>
    <div class="meta-row">
      <span><b>731</b> days modeled</span>
      <span><b>90-day</b> blind holdout</span>
      <span><b>{F['arima_order'][0]},{F['arima_order'][1]},{F['arima_order'][2]}</b> ARIMA order (grid-searched)</span>
      <span><b>14-day</b> LSTM lookback window</span>
    </div>
  </header>

  <section id="verdict">
    <div class="section-head">
      <p class="eyebrow">Direct answer</p>
      <h2>Yes — narrowly. It also barely beats guessing the average.</h2>
    </div>
    <div class="verdict">
      <span class="big yes">LSTM MAE {lstm_row['mae']:,.0f}</span>
      <span class="sub">vs. <b>ARIMA{tuple(F['arima_order'])}</b> at {arima_row['mae']:,.0f} units/day
        ({F['lstm_vs_arima_pct']:+.1f}% MAE) — the LSTM wins on every metric (MAE, RMSE, MAPE). But it's
        statistically indistinguishable from simply forecasting the <b>historical mean</b>
        ({mean_row['mae']:,.0f} units, {F['lstm_vs_mean_pct']:+.1f}% MAE change) — because the series has
        no learnable temporal structure beyond its own average.</span>
    </div>
  </section>

  <section id="hypotheses">
    <div class="section-head">
      <p class="eyebrow">Step 1 &middot; Hypothesis testing for granularity</p>
      <h2>Does demand depend on store or product?</h2>
      <p>One-way ANOVA on <code>units_sold</code>, grouped by each candidate dimension. At n=73,100, even a
        trivial difference can be "statistically significant" — so the decision is made on <b>effect size
        (&eta;&sup2;)</b>, not the p-value alone (Cohen's guideline: &eta;&sup2; &lt; 0.01 is a negligible
        practical effect).</p>
    </div>
    <div class="panel panel-wide">
      <div class="table-wrap">
        <table class="dq">
          <tr><th>Grouping variable</th><th>Groups</th><th>p (ANOVA)</th><th>&eta;&sup2;</th><th>Mean spread</th><th>Verdict</th></tr>
          {F['gran_rows']}
        </table>
      </div>
      <p class="panel-sub" style="margin-top:14px">All four candidate dimensions score &eta;&sup2; &lt; 0.0003
        — two orders of magnitude below the "negligible" threshold. <b>Decision: forecast total daily demand,
        aggregated across all stores and products</b>, rather than fragmenting into 100 near-identical,
        noisier per-store-product series.</p>
    </div>
  </section>

  <section id="features">
    <div class="section-head">
      <p class="eyebrow">Step 2 &middot; Hypothesis testing for features</p>
      <h2>Which exogenous variables earn a place in the model?</h2>
      <p>Candidate features aggregated to daily level and tested against daily total demand (Pearson r&sup2;
        for continuous variables, one-way ANOVA &eta;&sup2; for categorical ones). Selection rule: p &lt; 0.05
        <b>and</b> effect &ge; 0.02.</p>
    </div>
    <div class="panel panel-wide">
      <div class="table-wrap">
        <table class="dq">
          <tr><th>Variable</th><th>Effect metric</th><th>p-value</th><th>Effect size</th><th>Verdict</th></tr>
          {F['feat_rows']}
        </table>
      </div>
      <p class="panel-sub" style="margin-top:14px"><code>avg_inventory_level</code> and
        <code>avg_demand_forecast</code> correlate strongly but were excluded a priori as <b>leakage</b>:
        inventory is drawn down by the same day's sale, and the pre-existing forecast column is a competing
        prediction, not a causal input. Every legitimate candidate — price, discount, promotion, weather,
        season, weekday — failed both the significance and effect-size bar.
        <b>Decision: a purely univariate model</b> (demand's own history only, no exogenous regressors);
        SARIMAX-with-features and a multivariate LSTM were both ruled out by the data itself.</p>
    </div>
  </section>

  <section id="diagnostics">
    <div class="section-head">
      <p class="eyebrow">Step 3 &middot; Series diagnostics</p>
      <h2>The series is already stationary — and close to noise</h2>
      <p>Augmented Dickey-Fuller: stationary (p &lt; 0.001, no differencing required). Linear trend: slope
        not significant (p = 0.55, r&sup2; &asymp; 0). ACF/PACF out to 21 lags: only lag 10 crosses the 95%
        significance band — a single hit among 21 tests, consistent with chance (~1 expected false positive
        at &alpha;=0.05) and not tied to any real cycle (not weekly=7, not biweekly=14).</p>
    </div>
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Daily mean demand</div><div class="kpi-value">13,646</div><div class="kpi-note">units/day, coefficient of variation 7.6%</div></div>
      <div class="kpi"><div class="kpi-label">Trend</div><div class="kpi-value">None</div><div class="kpi-note">slope p = 0.55</div></div>
      <div class="kpi"><div class="kpi-label">Autocorrelation</div><div class="kpi-value">~0</div><div class="kpi-note">no significant lag out to 21 days</div></div>
      <div class="kpi"><div class="kpi-label">Stationarity</div><div class="kpi-value">Confirmed</div><div class="kpi-note">ADF p &lt; 0.001, d=0</div></div>
    </div>
  </section>

  <section id="results">
    <div class="section-head">
      <p class="eyebrow">Step 4 &middot; Model comparison</p>
      <h2>90-day blind forecast: actual vs. mean vs. ARIMA vs. LSTM</h2>
      <p>All three models forecast the same 90-day holdout with no access to test-period truth: ARIMA and
        LSTM both roll forward blindly from the end of the training window (ARIMA's native multi-step
        forecast; the LSTM feeds its own predictions back in as input, matching ARIMA's protocol for a fair
        comparison).</p>
    </div>
    <div class="panel panel-wide">
      <h3>Actual demand vs. each model's 90-day forecast</h3>
      <p class="panel-sub">Daily total units sold, held-out test period</p>
      <div class="legend">
        <span class="legend-item"><span class="legend-swatch" style="background:var(--text-primary)"></span>Actual</span>
        <span class="legend-item"><span class="legend-swatch" style="background:var(--series-1)"></span>LSTM</span>
        <span class="legend-item"><span class="legend-swatch" style="background:var(--series-2)"></span>ARIMA</span>
        <span class="legend-item"><span class="legend-swatch dash" style="color:var(--series-4)"></span>Historical mean</span>
      </div>
      <div class="chart-wrap">{F['chart_compare']}</div>
    </div>
    <div class="panel-grid" style="margin-top:16px">
      <div class="panel">
        <h3>Mean absolute error by model</h3>
        <p class="panel-sub">Lower is better &middot; dashed line marks the historical-mean baseline</p>
        <div class="chart-wrap">{F['chart_mae']}</div>
      </div>
      <div class="panel">
        <h3>Full metrics</h3>
        <p class="panel-sub">90-day held-out test period</p>
        <div class="table-wrap">
          <table class="dq">
            <tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>Bias</th></tr>
            {F['table_rows']}
          </table>
        </div>
      </div>
    </div>
  </section>

  <section id="methodology">
    <div class="section-head">
      <p class="eyebrow">Methodology</p>
      <h2>How each model was built</h2>
    </div>
    <div class="steps">
      <div class="step"><span class="tag">Split</span><span class="body">Time-ordered, no shuffling:
        <b>train</b> = first 581 days, <b>validation</b> = next 60 days, <b>test</b> = final 90 days (held out
        entirely from both training and order/hyperparameter selection).</span></div>
      <div class="step"><span class="tag">Baselines</span><span class="body"><b>Historical mean</b> (train
        average, flat line), <b>naive persistence</b> (last known value), <b>seasonal-naive</b> (value from
        7 days earlier, walk-forward with true values) — establishes the bar any model needs to clear.</span></div>
      <div class="step"><span class="tag">ARIMA</span><span class="body">Grid search over
        p,q &isin; [0,4], d &isin; {{0,1}} on train, ranked by 60-day validation MAE (not AIC alone, since the
        lowest-AIC order didn't validate best). Best order refit on train+validation, then forecast the
        test horizon natively via <code>statsmodels</code>' multi-step forecast.</span></div>
      <div class="step"><span class="tag">LSTM</span><span class="body">Single-layer LSTM (32 units) +
        Dense(16, relu) + Dense(1), 14-day lookback, trained with early stopping on validation loss
        (patience 20). Retrained for the selected number of epochs on train+validation, then forecast the
        test horizon by feeding each prediction back in as the next input — the same blind multi-step
        protocol as ARIMA, so the comparison is fair.</span></div>
    </div>
  </section>

  <section id="conclusion">
    <div class="section-head">
      <p class="eyebrow">Conclusion</p>
      <h2>The honest takeaway</h2>
    </div>
    <ul class="findings">
      <li><span><b>The LSTM does outperform ARIMA</b> on every metric (MAE {F['lstm_vs_arima_pct']:+.1f}%,
        and lower RMSE and MAPE too) — it's more robust to the noisy, structure-free series because it
        doesn't fit spurious AR/MA coefficients the way the grid-searched ARIMA(4,0,4) did.</span></li>
      <li><span><b>Neither model beats simply forecasting the historical average</b> to a meaningful degree.
        The LSTM lands within {abs(F['lstm_vs_mean_pct']):.1f}% of the mean baseline's MAE — a difference with
        no practical significance, mirroring the &eta;&sup2; results from Step 1.</span></li>
      <li><span><b>This is a property of the data, not the modeling.</b> Hypothesis testing in Steps 1-2
        already showed no factor in the dataset — store, product, category, region, price, discount,
        promotion, weather, season — moves demand by a practically meaningful amount. Diagnostics in Step 3
        confirmed the series itself has no trend and no autocorrelation. With no signal to learn, every model
        converges toward predicting the unconditional mean — which is exactly what the results show.</span></li>
      <li><span><b>Recommendation:</b> if this were a real forecasting problem, the finding itself is the
        deliverable — invest in better demand drivers (real promotional calendars, actual competitor
        actions, local events) before investing in model architecture. On this dataset as given, a simple
        moving-average forecast is a defensible production baseline; the LSTM's edge over it is not
        worth the added complexity.</span></li>
    </ul>
  </section>

  <footer class="colophon">
    Target: total daily <code>units_sold</code>, aggregated across 5 stores &times; 20 product slots &middot;
    Source: <code>data/cleaned/retail_store_inventory_cleaned.csv</code> &middot;
    Pipeline: <code>forecasting/01_hypothesis_granularity.py</code> through <code>09_assemble_html.py</code>
  </footer>
</div>
</div>
"""

out_path = '/tmp/claude-1000/-workspaces-Retail-Store-Inventory-project/6d3a83fb-3bec-4c1b-a1d8-6eedd6d8eb9c/scratchpad/forecasting_report.html'
with open(out_path, 'w') as f:
    f.write(html)
print("Wrote report, length:", len(html))
