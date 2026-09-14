#!/usr/bin/env python3
"""
Narmada Basin — Utilizable Flow: analysis & baseline forecast.

Reads  narmada/data/utilizable_flow_statement.csv  (units: MCM),
validates it, recomputes the total columns, and produces:

  * narmada/data/derived_summary.json  — clean series for the web page
  * a baseline forecast for the next water year (linear trend)

Pure standard library — no numpy/pandas needed. Run:

    python3 narmada/analysis/model.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "utilizable_flow_statement.csv")
OUT = os.path.join(HERE, "..", "data", "derived_summary.json")

NUM_COLS = [
    "util_major_MCM", "util_medium_MCM", "util_minor_MCM", "util_total_MCM",
    "ssp_rbph_outflow_MCM", "ssp_spillage_MCM", "ssp_canal_head_MCM",
    "ssp_outflow_total_MCM", "live_storage_1nov_MCM", "utilizable_flow_total_MCM",
]


def parse_num(v):
    """Return float for a filled cell, else None."""
    if v is None:
        return None
    v = v.strip().replace(",", "")
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def load_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for raw in f:
            if raw.lstrip().startswith("#"):   # skip comment lines
                continue
            rows.append(raw)
    reader = csv.DictReader(rows)
    out = []
    for r in reader:
        rec = {"water_year": (r.get("water_year") or "").strip(),
               "assessment_date": (r.get("assessment_date") or "").strip(),
               "remarks": (r.get("remarks") or "").strip()}
        for c in NUM_COLS:
            rec[c] = parse_num(r.get(c))
        out.append(rec)
    return out


def recompute_totals(rec):
    """Fill util_total / ssp_outflow_total from components when missing;
    flag mismatches when both a stated total and its components exist."""
    warnings = []
    comps = [rec["util_major_MCM"], rec["util_medium_MCM"], rec["util_minor_MCM"]]
    if all(c is not None for c in comps):
        s = round(sum(comps), 3)
        if rec["util_total_MCM"] is None:
            rec["util_total_MCM"] = s
        elif abs(rec["util_total_MCM"] - s) > 0.5:
            warnings.append(f"{rec['water_year']}: util_total {rec['util_total_MCM']} != major+medium+minor {s}")

    outs = [rec["ssp_rbph_outflow_MCM"], rec["ssp_spillage_MCM"], rec["ssp_canal_head_MCM"]]
    present = [o for o in outs if o is not None]
    if present:
        s = round(sum(present), 3)
        if rec["ssp_outflow_total_MCM"] is None:
            rec["ssp_outflow_total_MCM"] = s
        elif abs(rec["ssp_outflow_total_MCM"] - s) > 0.5:
            warnings.append(f"{rec['water_year']}: ssp_outflow_total {rec['ssp_outflow_total_MCM']} != sum of parts {s}")
    return warnings


def linear_trend_forecast(xs, ys):
    """Ordinary least squares y = a + b*x; return (a, b, next_prediction)."""
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    a = my - b * mx
    nxt = xs[-1] + 1
    return {"intercept": round(a, 2), "slope_per_year": round(b, 2),
            "next_x": nxt, "prediction_MCM": round(a + b * nxt, 2)}


def main():
    if not os.path.exists(DATA):
        print(f"ERROR: data file not found: {DATA}", file=sys.stderr)
        sys.exit(1)

    rows = load_rows(DATA)
    all_warnings = []
    for rec in rows:
        all_warnings += recompute_totals(rec)

    # Rows that actually carry a utilizable-flow figure.
    filled = [r for r in rows if r["utilizable_flow_total_MCM"] is not None]

    summary = {
        "unit": "MCM",
        "n_years_defined": len(rows),
        "n_years_with_utilizable_flow": len(filled),
        "rows": rows,
        "warnings": all_warnings,
        "forecast": None,
    }

    print("=" * 60)
    print("Narmada Utilizable Flow — analysis")
    print("=" * 60)
    print(f"Water years listed        : {len(rows)}")
    print(f"Years with a flow figure  : {len(filled)}")
    for w in all_warnings:
        print("  ! consistency warning:", w)

    if len(filled) >= 3:
        # Use an ordinal index for the year to keep the trend simple.
        xs = list(range(len(filled)))
        ys = [r["utilizable_flow_total_MCM"] for r in filled]
        fc = linear_trend_forecast(xs, ys)
        if fc:
            fc["basis_years"] = [r["water_year"] for r in filled]
            summary["forecast"] = fc
            print(f"\nBaseline linear-trend forecast for next year: "
                  f"{fc['prediction_MCM']} MCM "
                  f"(slope {fc['slope_per_year']} MCM/yr)")
            print("NOTE: baseline only — refine once the full series is loaded.")
    else:
        print("\nNot enough data yet for a forecast (need >= 3 years with figures).")
        print("Add rows to utilizable_flow_statement.csv and re-run.")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWrote {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
