import json
import pandas as pd

with open('forecasting/results_old_forecast_category.json') as f:
    OLD = json.load(f)
with open('forecasting/comparison_summary_category.json') as f:
    CMP = json.load(f)

categories = sorted(OLD['by_category'].keys())

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def bar_path(x, y0, y1, w, r=4):
    h = y0 - y1
    if h < r:
        r = max(h, 0)
    return (f"M{x},{y0} L{x},{y1+r} Q{x},{y1} {x+r},{y1} "
            f"L{x+w-r},{y1} Q{x+w},{y1} {x+w},{y1+r} L{x+w},{y0} Z")

def hbar_chart(items, width=640, bar_h=24, gap=16, value_fmt=None, left_pad=200, right_pad=80, colors=None):
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(items)
    row_h = bar_h + gap
    height = n * row_h + gap
    max_v = max(v for _, v in items) * 1.08
    plot_w = width - left_pad - right_pad
    default_colors = ["var(--series-3)", "var(--series-1)", "var(--series-4)", "var(--series-2)", "var(--series-8)"]
    colors = colors or default_colors
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="MAE comparison including existing forecast column">']
    for i, (label, v) in enumerate(items):
        y0 = gap + i * row_h
        bw = max((v / max_v) * plot_w, 2)
        c = colors[i % len(colors)]
        x0 = left_pad
        svg.append(f'<text x="{x0-10}" y="{y0+bar_h*0.65}" text-anchor="end" class="axis-label">{esc(label)}</text>')
        path = bar_path(x0, y0+bar_h, y0, bw, r=4)
        svg.append(f'<path d="{path}" fill="{c}"><title>{esc(label)}: MAE {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{x0+bw+8}" y="{y0+bar_h*0.65}" class="value-label">{value_fmt(v)}</text>')
    svg.append('</svg>')
    return ''.join(svg)

chart_old_vs_new = hbar_chart(
    [
        ("Existing forecast column (bias-corrected)", OLD['avg_mae_corrected']),
        ("Existing forecast column (raw)", OLD['avg_mae']),
        ("LSTM (new, category-level)", CMP['avg_mae']['lstm_mae']),
        ("Mean baseline (new, category-level)", CMP['avg_mae']['mean_mae']),
        ("ARIMA (new, category-level)", CMP['avg_mae']['arima_mae']),
    ],
    value_fmt=lambda v: f"{v:,.0f} units",
    colors=["var(--series-3)", "var(--series-3)", "var(--series-1)", "var(--series-4)", "var(--series-2)"],
)

def per_cat_rows():
    rows = []
    for cat in categories:
        r = OLD['by_category'][cat]
        c = next(x for x in CMP['table'] if x['category'] == cat)
        rows.append(
            f"<tr><td>{esc(cat)}</td>"
            f"<td class='mono'>{r['metrics']['mae']:,.0f}</td>"
            f"<td class='mono'>{r['metrics_corrected']['mae']:,.0f}</td>"
            f"<td class='mono'>{c['mean_mae']:,.0f}</td>"
            f"<td class='mono'>{c['arima_mae']:,.0f}</td>"
            f"<td class='mono'>{c['lstm_mae']:,.0f}</td></tr>"
        )
    return '\n'.join(rows)

with open('forecasting/report_fragments_oldforecast.json', 'w') as f:
    json.dump({
        'chart_old_vs_new': chart_old_vs_new,
        'per_cat_rows': per_cat_rows(),
        'avg_mae_raw': OLD['avg_mae'],
        'avg_mae_corrected': OLD['avg_mae_corrected'],
        'avg_mape_raw': OLD['avg_mape'],
        'avg_mape_corrected': OLD['avg_mape_corrected'],
        'avg_bias_raw': OLD['avg_bias'],
        'avg_bias_corrected': OLD['avg_bias_corrected'],
    }, f)
print("Built old-forecast comparison fragments OK")
