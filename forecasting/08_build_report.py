import json
import pandas as pd
import numpy as np

with open('forecasting/comparison_summary.json') as f:
    CMP = json.load(f)
with open('forecasting/granularity_hypothesis_results.csv'.replace('.csv', '.csv')) as f:
    pass
gran_df = pd.read_csv('forecasting/granularity_hypothesis_results.csv')
feat_df = pd.read_csv('forecasting/feature_hypothesis_results.csv')
with open('forecasting/results_arima.json') as f:
    ARIMA = json.load(f)
with open('forecasting/results_lstm.json') as f:
    LSTM = json.load(f)

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def bar_path(x, y0, y1, w, r=4):
    h = y0 - y1
    if h < r:
        r = max(h, 0)
    return (f"M{x},{y0} L{x},{y1+r} Q{x},{y1} {x+r},{y1} "
            f"L{x+w-r},{y1} Q{x+w},{y1} {x+w},{y1+r} L{x+w},{y0} Z")

CAT_COLORS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)", "var(--series-8)"]

def hbar_chart(items, width=620, bar_h=24, gap=16, value_fmt=None, left_pad=190, right_pad=70, ref_line=None):
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(items)
    row_h = bar_h + gap
    height = n * row_h + gap
    max_v = max(v for _, v in items) * 1.05
    plot_w = width - left_pad - right_pad
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="MAE comparison bar chart">']
    if ref_line is not None:
        rx = left_pad + (ref_line / max_v) * plot_w
        svg.append(f'<line x1="{rx:.1f}" y1="{gap*0.3}" x2="{rx:.1f}" y2="{height-gap*0.3}" stroke="var(--text-muted)" stroke-width="1" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{rx:.1f}" y="{gap*0.3-4}" text-anchor="middle" class="tick-label">mean baseline</text>')
    for i, (label, v) in enumerate(items):
        y0 = gap + i * row_h
        bw = max((v / max_v) * plot_w, 2)
        c = CAT_COLORS[i % len(CAT_COLORS)]
        x0 = left_pad
        svg.append(f'<text x="{x0-10}" y="{y0+bar_h*0.65}" text-anchor="end" class="axis-label">{esc(label)}</text>')
        path = bar_path(x0, y0+bar_h, y0, bw, r=4)
        svg.append(f'<path d="{path}" fill="{c}"><title>{esc(label)}: MAE {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{x0+bw+8}" y="{y0+bar_h*0.65}" class="value-label">{value_fmt(v)}</text>')
    svg.append('</svg>')
    return ''.join(svg)


def multi_line_chart(dates, series_dict, width=920, height=320, pad_top=24, pad_bottom=34, pad_left=54, pad_right=16):
    n = len(dates)
    all_vals = [v for vals in series_dict.values() for v in vals]
    max_v, min_v = max(all_vals), min(all_vals)
    pad = (max_v - min_v) * 0.08
    max_v += pad
    min_v -= pad
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    baseline_y = height - pad_bottom

    def xf(i):
        return pad_left + (i / (n - 1)) * plot_w
    def yf(v):
        return pad_top + (1 - (v - min_v) / (max_v - min_v)) * plot_h

    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="forecast comparison line chart">']
    for t in range(5):
        gv = min_v + (max_v - min_v) * t / 4
        gy = yf(gv)
        svg.append(f'<line x1="{pad_left}" y1="{gy:.1f}" x2="{width-pad_right}" y2="{gy:.1f}" class="grid-line"/>')
        svg.append(f'<text x="0" y="{gy-4:.1f}" class="tick-label">{gv:,.0f}</text>')

    colors = {'Actual': 'var(--text-primary)', 'Historical mean': 'var(--series-4)',
              'ARIMA': 'var(--series-2)', 'LSTM': 'var(--series-1)'}
    dash = {'Historical mean': '4,3'}
    for name, vals in series_dict.items():
        c = colors.get(name, 'var(--series-3)')
        d = dash.get(name)
        line = f"M{xf(0):.1f},{yf(vals[0]):.1f} "
        for i in range(1, n):
            line += f"L{xf(i):.1f},{yf(vals[i]):.1f} "
        sw = 2.4 if name == 'Actual' else 2
        dash_attr = f' stroke-dasharray="{d}"' if d else ''
        svg.append(f'<path d="{line}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>')

    idxs = sorted(set([0, n // 3, 2 * n // 3, n - 1]))
    for i in idxs:
        svg.append(f'<text x="{xf(i):.1f}" y="{height-8}" text-anchor="middle" class="axis-label">{esc(dates[i][5:])}</text>')
    svg.append('</svg>')
    return ''.join(svg)


chart_mae = hbar_chart(
    [(r['model'], r['mae']) for r in CMP['table']],
    value_fmt=lambda v: f"{v:,.0f} units",
    ref_line=next(r['mae'] for r in CMP['table'] if r['model'] == 'Historical mean'),
)

chart_compare = multi_line_chart(
    CMP['test_dates'],
    {
        'Actual': CMP['y_test'],
        'Historical mean': CMP['series']['Historical mean'],
        'ARIMA': CMP['series']['ARIMA'],
        'LSTM': CMP['series']['LSTM'],
    },
)

def gran_rows():
    rows = []
    for _, r in gran_df.iterrows():
        rows.append(f"<tr><td>{esc(r['variable'])}</td><td>{int(r['n_groups'])}</td>"
                     f"<td class='mono'>{r['p_anova']:.3f}</td><td class='mono'>{r['eta_squared']:.5f}</td>"
                     f"<td class='mono'>{r['group_mean_spread_pct']:.2f}%</td><td>negligible</td></tr>")
    return '\n'.join(rows)

def feat_rows():
    rows = []
    for _, r in feat_df.iterrows():
        name = r['variable']
        excluded = 'EXCLUDED' in name
        eff = r['effect']
        verdict = 'excluded (leakage)' if excluded else ('negligible' if eff < 0.02 else 'kept')
        rows.append(f"<tr><td>{esc(name)}</td><td>{esc(r['effect_name'])}</td>"
                     f"<td class='mono'>{r['p_value']:.3f}</td><td class='mono'>{eff:.4f}</td><td>{verdict}</td></tr>")
    return '\n'.join(rows)

table_rows = '\n'.join(
    f"<tr><td>{esc(r['model'])}</td><td class='mono'>{r['mae']:,.1f}</td><td class='mono'>{r['rmse']:,.1f}</td>"
    f"<td class='mono'>{r['mape']:.2f}%</td><td class='mono'>{r['bias']:+,.1f}</td></tr>"
    for r in CMP['table']
)

with open('forecasting/report_fragments.json', 'w') as f:
    json.dump({
        'chart_mae': chart_mae,
        'chart_compare': chart_compare,
        'gran_rows': gran_rows(),
        'feat_rows': feat_rows(),
        'table_rows': table_rows,
        'arima_order': ARIMA['order'],
        'lstm_vs_arima_pct': CMP['lstm_vs_arima_mae_pct'],
        'lstm_vs_mean_pct': CMP['lstm_vs_mean_mae_pct'],
    }, f)
print("Built chart fragments OK")
