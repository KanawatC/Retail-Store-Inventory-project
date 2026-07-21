import json
import pandas as pd
import numpy as np

with open('forecasting/comparison_summary_category.json') as f:
    CMP = json.load(f)
gran_df = pd.read_csv('forecasting/granularity_hypothesis_results.csv')
feat_df = pd.read_csv('forecasting/feature_hypothesis_by_category.csv')
diag_df = pd.read_csv('forecasting/diagnostics_by_category.csv')
stock_df = pd.read_csv('forecasting/stock_plan.csv')
with open('forecasting/results_lstm_category.json') as f:
    LSTM = json.load(f)

categories = sorted(CMP['by_category_series'].keys())

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def bar_path(x, y0, y1, w, r=4):
    h = y0 - y1
    if h < r:
        r = max(h, 0)
    return (f"M{x},{y0} L{x},{y1+r} Q{x},{y1} {x+r},{y1} "
            f"L{x+w-r},{y1} Q{x+w},{y1} {x+w},{y1+r} L{x+w},{y0} Z")

CAT_COLORS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)", "var(--series-8)"]

def grouped_vbar_chart(labels, series, width=760, height=260, colors=("var(--series-4)", "var(--series-2)", "var(--series-1)"),
                        value_fmt=None, pad_top=24, pad_bottom=38):
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(labels)
    ns = len(series)
    all_vals = [v for _, vals in series for v in vals]
    max_v = max(all_vals) * 1.08
    plot_h = height - pad_top - pad_bottom
    baseline_y = height - pad_bottom
    group_gap = 30
    bar_w = 16
    inner_gap = 3
    group_w = ns * bar_w + (ns - 1) * inner_gap
    total_w = n * group_w + (n + 1) * group_gap
    svg = [f'<svg viewBox="0 0 {max(width, total_w)} {height}" width="100%" role="img" aria-label="grouped MAE comparison">']
    svg.append(f'<line x1="0" y1="{baseline_y}" x2="{max(width, total_w)}" y2="{baseline_y}" class="axis-line"/>')
    x = group_gap
    for gi, label in enumerate(labels):
        gx = x
        for si, (name, vals) in enumerate(series):
            v = vals[gi]
            bh = (v / max_v) * plot_h if max_v else 0
            bx = gx + si * (bar_w + inner_gap)
            path = bar_path(bx, baseline_y, baseline_y - bh, bar_w, r=3)
            svg.append(f'<path d="{path}" fill="{colors[si % len(colors)]}"><title>{esc(name)} - {esc(label)}: MAE {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{gx + group_w/2}" y="{baseline_y + 20}" text-anchor="middle" class="axis-label">{esc(label)}</text>')
        x += group_w + group_gap
    svg.append('</svg>')
    return ''.join(svg)


def small_multiple_line(dates, series_dict, width=430, height=190, pad_top=14, pad_bottom=24, pad_left=44, pad_right=8):
    n = len(dates)
    all_vals = [v for vals in series_dict.values() for v in vals]
    max_v, min_v = max(all_vals), min(all_vals)
    pad = (max_v - min_v) * 0.1 or 1
    max_v += pad
    min_v -= pad
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    baseline_y = height - pad_bottom

    def xf(i):
        return pad_left + (i / (n - 1)) * plot_w
    def yf(v):
        return pad_top + (1 - (v - min_v) / (max_v - min_v)) * plot_h

    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="category forecast comparison">']
    for t in range(3):
        gv = min_v + (max_v - min_v) * t / 2
        gy = yf(gv)
        svg.append(f'<line x1="{pad_left}" y1="{gy:.1f}" x2="{width-pad_right}" y2="{gy:.1f}" class="grid-line"/>')
        svg.append(f'<text x="0" y="{gy-3:.1f}" class="tick-label">{gv:,.0f}</text>')

    colors = {'Actual': 'var(--text-primary)', 'Mean baseline': 'var(--series-4)',
              'ARIMA': 'var(--series-2)', 'LSTM': 'var(--series-1)'}
    dash = {'Mean baseline': '4,3'}
    for name, vals in series_dict.items():
        c = colors.get(name, 'var(--series-3)')
        d = dash.get(name)
        line = f"M{xf(0):.1f},{yf(vals[0]):.1f} "
        for i in range(1, n):
            line += f"L{xf(i):.1f},{yf(vals[i]):.1f} "
        sw = 2.2 if name == 'Actual' else 1.8
        dash_attr = f' stroke-dasharray="{d}"' if d else ''
        svg.append(f'<path d="{line}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>')
    idxs = [0, n - 1]
    for i in idxs:
        svg.append(f'<text x="{xf(i):.1f}" y="{height-6}" text-anchor="middle" class="axis-label">{esc(dates[i][5:])}</text>')
    svg.append('</svg>')
    return ''.join(svg)


def hbar_chart(items, width=560, bar_h=22, gap=14, value_fmt=None, left_pad=170, right_pad=70):
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(items)
    row_h = bar_h + gap
    height = n * row_h + gap
    max_v = max(v for _, v in items) * 1.08
    plot_w = width - left_pad - right_pad
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="stock allocation per store">']
    for i, (label, v) in enumerate(items):
        y0 = gap + i * row_h
        bw = max((v / max_v) * plot_w, 2)
        c = CAT_COLORS[i % len(CAT_COLORS)]
        x0 = left_pad
        svg.append(f'<text x="{x0-10}" y="{y0+bar_h*0.65}" text-anchor="end" class="axis-label">{esc(label)}</text>')
        path = bar_path(x0, y0+bar_h, y0, bw, r=4)
        svg.append(f'<path d="{path}" fill="{c}"><title>{esc(label)}: {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{x0+bw+8}" y="{y0+bar_h*0.65}" class="value-label">{value_fmt(v)}</text>')
    svg.append('</svg>')
    return ''.join(svg)


# ---------- build charts ----------
chart_mae_grouped = grouped_vbar_chart(
    categories,
    [('Mean baseline', [CMP['table'][i]['mean_mae'] for i in range(len(categories))]),
     ('ARIMA', [CMP['table'][i]['arima_mae'] for i in range(len(categories))]),
     ('LSTM', [CMP['table'][i]['lstm_mae'] for i in range(len(categories))])],
)

small_multiples = {}
for cat in categories:
    s = CMP['by_category_series'][cat]
    small_multiples[cat] = small_multiple_line(
        s['test_dates'],
        {'Actual': s['y_test'], 'Mean baseline': s['mean_baseline'], 'ARIMA': s['arima'], 'LSTM': s['lstm']},
    )

chart_stock = hbar_chart(
    [(r['category'], r['per_store_daily_stock']) for r in stock_df.to_dict(orient='records')],
    value_fmt=lambda v: f"{v:.0f} units/store/day",
)

def diag_rows():
    rows = []
    for _, r in diag_df.iterrows():
        lags = eval(r['sig_acf_lags']) if isinstance(r['sig_acf_lags'], str) else r['sig_acf_lags']
        lag_str = ', '.join(str(x) for x in lags) if lags else 'none'
        rows.append(f"<tr><td>{esc(r['category'])}</td><td class='mono'>{r['mean']:,.0f}</td>"
                     f"<td class='mono'>{r['cv']*100:.1f}%</td><td class='mono'>{r['adf_p']:.4f}</td>"
                     f"<td class='mono'>{r['trend_slope']:+.3f}</td><td class='mono'>{r['trend_p']:.3f}</td>"
                     f"<td>{lag_str}</td></tr>")
    return '\n'.join(rows)

def cmp_table_rows():
    rows = []
    for r in CMP['table']:
        best = r['best_model']
        rows.append(
            f"<tr><td>{esc(r['category'])}</td>"
            f"<td class='mono'>{r['mean_mae']:,.0f}</td>"
            f"<td class='mono'>ARIMA{tuple(r['arima_order'])}: {r['arima_mae']:,.0f}</td>"
            f"<td class='mono'>{r['lstm_mae']:,.0f}</td>"
            f"<td>{esc(best)}</td></tr>"
        )
    return '\n'.join(rows)

def stock_rows():
    rows = []
    for r in stock_df.to_dict(orient='records'):
        rows.append(f"<tr><td>{esc(r['category'])}</td><td class='mono'>{r['chain_daily_demand_forecast']:,.0f}</td>"
                     f"<td class='mono'>{r['per_store_daily_stock']:,.0f}</td></tr>")
    return '\n'.join(rows)

n_feat_kept = int(feat_df['p_value'].lt(0.05).astype(int).sum())  # just for reference, real gate uses effect too

with open('forecasting/report_fragments_category.json', 'w') as f:
    json.dump({
        'chart_mae_grouped': chart_mae_grouped,
        'small_multiples': small_multiples,
        'chart_stock': chart_stock,
        'diag_rows': diag_rows(),
        'cmp_table_rows': cmp_table_rows(),
        'stock_rows': stock_rows(),
        'avg_mae': CMP['avg_mae'],
        'lstm_vs_arima_pct': CMP['lstm_vs_arima_mae_pct'] if 'lstm_vs_arima_mae_pct' in CMP else CMP['lstm_vs_arima_pct'],
        'lstm_vs_mean_pct': CMP['lstm_vs_mean_pct'],
    }, f)
print("Built category report fragments OK")
