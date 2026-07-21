import json
import pandas as pd
import numpy as np

with open('outputs/eda_summary.json') as f:
    D = json.load(f)

df = pd.read_csv('data/cleaned/retail_store_inventory_cleaned.csv', parse_dates=['date'])
fc_by_cat = df.groupby('category', observed=True).agg(
    avg_units_sold=('units_sold', 'mean'),
    avg_demand_forecast=('demand_forecast', 'mean'),
).reset_index().sort_values('avg_units_sold', ascending=False)

# ---------- helpers ----------

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

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# rounded-top bar path: x is left edge, y0 baseline, y1 top, w width, r radius
def bar_path(x, y0, y1, w, r=4):
    h = y0 - y1
    if h < r:
        r = max(h, 0)
    return (f"M{x},{y0} L{x},{y1+r} Q{x},{y1} {x+r},{y1} "
            f"L{x+w-r},{y1} Q{x+w},{y1} {x+w},{y1+r} L{x+w},{y0} Z")

CAT_COLORS = ["var(--series-1)", "var(--series-2)", "var(--series-3)",
              "var(--series-4)", "var(--series-5)", "var(--series-6)",
              "var(--series-7)", "var(--series-8)"]

def hbar_chart(items, width=560, bar_h=22, gap=14, value_fmt=None, color="var(--series-1)",
               left_pad=118, right_pad=64, multi_color=False, unit=""):
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(items)
    row_h = bar_h + gap
    height = n * row_h + gap
    max_v = max(v for _, v in items) or 1
    plot_w = width - left_pad - right_pad
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="bar chart">']
    for i, (label, v) in enumerate(items):
        y0 = gap + i * row_h
        bw = max((v / max_v) * plot_w, 2)
        c = CAT_COLORS[i % len(CAT_COLORS)] if multi_color else color
        x0 = left_pad
        svg.append(f'<text x="{x0-10}" y="{y0+bar_h*0.68}" text-anchor="end" class="axis-label">{esc(label)}</text>')
        path = bar_path(x0, y0+bar_h, y0, bw, r=4)
        # bar_path expects y0(baseline,bottom) then y1(top); recompute correctly
        path = bar_path(x0, y0+bar_h, y0, bw, r=4)
        svg.append(f'<path d="{path}" fill="{c}"><title>{esc(label)}: {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{x0+bw+8}" y="{y0+bar_h*0.68}" class="value-label">{value_fmt(v)}{unit}</text>')
    svg.append('</svg>')
    return ''.join(svg)


def vbar_chart(items, width=560, height=220, bar_w=34, value_fmt=None, color="var(--series-1)",
               multi_color=False, unit="", pad_top=22, pad_bottom=34):
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(items)
    max_v = max(v for _, v in items) or 1
    min_v = min(0, min(v for _, v in items))
    plot_h = height - pad_top - pad_bottom
    baseline_y = height - pad_bottom
    gap = 18
    total_gap = gap * (n + 1)
    bw = min(bar_w, (width - total_gap) / n)
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="bar chart">']
    svg.append(f'<line x1="0" y1="{baseline_y}" x2="{width}" y2="{baseline_y}" class="axis-line"/>')
    x = gap
    for i, (label, v) in enumerate(items):
        bh = (v / max_v) * plot_h if max_v else 0
        c = CAT_COLORS[i % len(CAT_COLORS)] if multi_color else color
        path = bar_path(x, baseline_y, baseline_y - bh, bw, r=4)
        svg.append(f'<path d="{path}" fill="{c}"><title>{esc(label)}: {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{x+bw/2}" y="{baseline_y - bh - 8}" text-anchor="middle" class="value-label">{value_fmt(v)}{unit}</text>')
        svg.append(f'<text x="{x+bw/2}" y="{baseline_y + 20}" text-anchor="middle" class="axis-label">{esc(label)}</text>')
        x += bw + gap
    svg.append('</svg>')
    return ''.join(svg)


def grouped_vbar_chart(labels, series, width=620, height=240, colors=("var(--series-1)", "var(--series-2)"),
                        value_fmt=None, pad_top=24, pad_bottom=34):
    """series: list of (name, [values...]) same length as labels"""
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(labels)
    ns = len(series)
    all_vals = [v for _, vals in series for v in vals]
    max_v = max(all_vals) or 1
    plot_h = height - pad_top - pad_bottom
    baseline_y = height - pad_bottom
    group_gap = 26
    bar_w = 20
    inner_gap = 4
    group_w = ns * bar_w + (ns - 1) * inner_gap
    total_w = n * group_w + (n + 1) * group_gap
    scale = width / total_w if total_w > width else 1
    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="grouped bar chart">']
    svg.append(f'<line x1="0" y1="{baseline_y}" x2="{width}" y2="{baseline_y}" class="axis-line"/>')
    x = group_gap
    for gi, label in enumerate(labels):
        gx = x
        for si, (name, vals) in enumerate(series):
            v = vals[gi]
            bh = (v / max_v) * plot_h if max_v else 0
            bx = gx + si * (bar_w + inner_gap)
            path = bar_path(bx, baseline_y, baseline_y - bh, bar_w, r=3)
            svg.append(f'<path d="{path}" fill="{colors[si % len(colors)]}"><title>{esc(name)} — {esc(label)}: {value_fmt(v)}</title></path>')
        svg.append(f'<text x="{gx + group_w/2}" y="{baseline_y + 20}" text-anchor="middle" class="axis-label">{esc(label)}</text>')
        x += group_w + group_gap
    svg.append('</svg>')
    return ''.join(svg)


def line_chart(points, width=760, height=240, color="var(--series-1)", value_fmt=None,
               pad_top=24, pad_bottom=30, pad_left=8, pad_right=8, n_yticks=4):
    """points: list of (label, value)"""
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(points)
    vals = [v for _, v in points]
    max_v = max(vals)
    min_v = min(0, min(vals))
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    baseline_y = height - pad_bottom

    def xf(i):
        return pad_left + (i / (n - 1)) * plot_w if n > 1 else pad_left
    def yf(v):
        if max_v == min_v:
            return baseline_y
        return pad_top + (1 - (v - min_v) / (max_v - min_v)) * plot_h

    svg = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="line chart">']
    # gridlines
    for t in range(n_yticks + 1):
        gv = min_v + (max_v - min_v) * t / n_yticks
        gy = yf(gv)
        svg.append(f'<line x1="{pad_left}" y1="{gy:.1f}" x2="{width-pad_right}" y2="{gy:.1f}" class="grid-line"/>')
        svg.append(f'<text x="0" y="{gy-4:.1f}" class="tick-label">{value_fmt(gv)}</text>')

    # area fill
    area = f"M{xf(0):.1f},{baseline_y} "
    for i, (_, v) in enumerate(points):
        area += f"L{xf(i):.1f},{yf(v):.1f} "
    area += f"L{xf(n-1):.1f},{baseline_y} Z"
    svg.append(f'<path d="{area}" fill="{color}" opacity="0.10"/>')

    # line
    line = f"M{xf(0):.1f},{yf(points[0][1]):.1f} "
    for i, (_, v) in enumerate(points[1:], start=1):
        line += f"L{xf(i):.1f},{yf(v):.1f} "
    svg.append(f'<path d="{line}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')

    # end marker
    ex, ey = xf(n-1), yf(points[-1][1])
    svg.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="{color}" stroke="var(--surface)" stroke-width="2"/>')
    svg.append(f'<text x="{ex-6:.1f}" y="{ey-12:.1f}" text-anchor="end" class="value-label">{value_fmt(points[-1][1])}</text>')

    # x labels: first, mid, last
    idxs = sorted(set([0, n // 2, n - 1]))
    for i in idxs:
        svg.append(f'<text x="{xf(i):.1f}" y="{height-6}" text-anchor="middle" class="axis-label">{esc(points[i][0])}</text>')
    # invisible hover dots with tooltip
    for i, (lab, v) in enumerate(points):
        svg.append(f'<circle cx="{xf(i):.1f}" cy="{yf(v):.1f}" r="7" fill="transparent"><title>{esc(lab)}: {value_fmt(v)}</title></circle>')
    svg.append('</svg>')
    return ''.join(svg)


def heatmap(cols, matrix, width=640, cell=68):
    n = len(cols)
    pad_left = 130
    pad_top = 100
    height = pad_top + n * cell + 10
    svg_w = pad_left + n * cell + 10
    svg = [f'<svg viewBox="0 0 {svg_w} {height}" width="100%" role="img" aria-label="correlation heatmap">']
    # column labels (rotated)
    for j, c in enumerate(cols):
        cx = pad_left + j * cell + cell/2
        svg.append(f'<text x="{cx}" y="{pad_top-10}" text-anchor="start" class="axis-label" transform="rotate(-40 {cx} {pad_top-10})">{esc(c)}</text>')
    for i, r in enumerate(cols):
        cy = pad_top + i * cell + cell/2
        svg.append(f'<text x="{pad_left-10}" y="{cy+4}" text-anchor="end" class="axis-label">{esc(r)}</text>')
        for j, c in enumerate(cols):
            v = matrix[i][j]
            x = pad_left + j * cell
            y = pad_top + i * cell
            if v >= 0:
                t = v
                color = f'color-mix(in oklab, var(--div-pos) {t*100:.0f}%, var(--div-mid))'
            else:
                t = -v
                color = f'color-mix(in oklab, var(--div-neg) {t*100:.0f}%, var(--div-mid))'
            txt_color = 'var(--text-primary)' if abs(v) < 0.6 else '#ffffff'
            svg.append(f'<rect x="{x+1}" y="{y+1}" width="{cell-2}" height="{cell-2}" rx="3" fill="{color}"><title>{esc(r)} vs {esc(c)}: {v:.2f}</title></rect>')
            svg.append(f'<text x="{x+cell/2}" y="{y+cell/2+4}" text-anchor="middle" style="fill:{txt_color};font-size:12px;font-variant-numeric:tabular-nums">{v:.2f}</text>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- build chart data ----------

monthly = [m for m in D['monthly_trend'] if m['date'] != '2024-01']  # drop partial single-day month
rev_points = [(m['date'][2:], m['revenue']) for m in monthly]
chart_revenue_trend = line_chart(rev_points, value_fmt=lambda v: fmt_money(v, 1))

cat_rev_items = [(c['category'], c['revenue']) for c in D['by_category']]
chart_cat_revenue = hbar_chart(cat_rev_items, value_fmt=lambda v: fmt_money(v, 1), multi_color=True)

reg_rev_items = [(r['region'], r['revenue']) for r in D['by_region']]
chart_region_revenue = hbar_chart(reg_rev_items, value_fmt=lambda v: fmt_money(v, 1), multi_color=True, width=480)

season_items = [(s['seasonality'], s['avg_units_sold']) for s in D['by_season']]
chart_season = vbar_chart(season_items, value_fmt=lambda v: f"{v:.0f}", multi_color=True, width=280, height=200)

weekday_items = [(w['weekday'][:3], w['units_sold']) for w in D['by_weekday']]
chart_weekday = vbar_chart(weekday_items, value_fmt=lambda v: f"{v:.0f}", color="var(--series-1)", width=340, height=200, bar_w=28)

discount_items = [(f"{d['discount']}%", d['avg_units_sold']) for d in D['by_discount']]
chart_discount = vbar_chart(discount_items, value_fmt=lambda v: f"{v:.0f}", color="var(--series-1)", width=280, height=200)

weather_items = [(w['weather_condition'], w['avg_units_sold']) for w in D['by_weather']]
chart_weather = vbar_chart(weather_items, value_fmt=lambda v: f"{v:.0f}", multi_color=True, width=340, height=200, bar_w=28)

fc_labels = fc_by_cat['category'].tolist()
fc_actual = fc_by_cat['avg_units_sold'].round(1).tolist()
fc_forecast = fc_by_cat['avg_demand_forecast'].round(1).tolist()
chart_forecast = grouped_vbar_chart(
    fc_labels,
    [('Actual units sold', fc_actual), ('Demand forecast', fc_forecast)],
    value_fmt=lambda v: f"{v:.0f}",
    colors=("var(--series-1)", "var(--series-4)"),
)

chart_corr = heatmap(D['correlation']['columns'], D['correlation']['matrix'])

with open('outputs/charts_cache.json', 'w') as f:
    json.dump({
        'chart_revenue_trend': chart_revenue_trend,
        'chart_cat_revenue': chart_cat_revenue,
        'chart_region_revenue': chart_region_revenue,
        'chart_season': chart_season,
        'chart_weekday': chart_weekday,
        'chart_discount': chart_discount,
        'chart_weather': chart_weather,
        'chart_forecast': chart_forecast,
        'chart_corr': chart_corr,
    }, f)

print("Charts built OK")
