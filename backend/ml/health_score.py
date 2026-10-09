from typing import Dict, Any

def compute_health_score(fundamentals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transparent Fundamental Health Evaluation.
    Breaks down 10 analytical pillars with clear objective thresholds.
    Never gives personalized investment advice.
    """
    components = {}
    total_score = 0.0
    max_score = 100.0

    # 1. Revenue Growth
    rev_growth = float(fundamentals.get("revenue_growth", 0.0))
    if rev_growth >= 15.0:
        components["Revenue Growth"] = {"status": "Strong", "score": 10, "detail": f"+{rev_growth}% YoY"}
        total_score += 10
    elif rev_growth >= 8.0:
        components["Revenue Growth"] = {"status": "Moderate", "score": 7, "detail": f"+{rev_growth}% YoY"}
        total_score += 7
    elif rev_growth >= 0.0:
        components["Revenue Growth"] = {"status": "Neutral", "score": 4, "detail": f"+{rev_growth}% YoY"}
        total_score += 4
    else:
        components["Revenue Growth"] = {"status": "Weak", "score": 1, "detail": f"{rev_growth}% YoY"}
        total_score += 1

    # 2. Profit Growth
    prof_growth = float(fundamentals.get("profit_growth", 0.0))
    if prof_growth >= 20.0:
        components["Profit Growth"] = {"status": "Strong", "score": 10, "detail": f"+{prof_growth}% YoY"}
        total_score += 10
    elif prof_growth >= 10.0:
        components["Profit Growth"] = {"status": "Moderate", "score": 7, "detail": f"+{prof_growth}% YoY"}
        total_score += 7
    elif prof_growth >= 0.0:
        components["Profit Growth"] = {"status": "Neutral", "score": 4, "detail": f"+{prof_growth}% YoY"}
        total_score += 4
    else:
        components["Profit Growth"] = {"status": "Weak", "score": 1, "detail": f"{prof_growth}% YoY"}
        total_score += 1

    # 3. ROE
    roe = float(fundamentals.get("roe", 0.0))
    if roe >= 20.0:
        components["ROE"] = {"status": "Strong", "score": 10, "detail": f"{roe}%"}
        total_score += 10
    elif roe >= 14.0:
        components["ROE"] = {"status": "Moderate", "score": 7, "detail": f"{roe}%"}
        total_score += 7
    elif roe >= 8.0:
        components["ROE"] = {"status": "Neutral", "score": 4, "detail": f"{roe}%"}
        total_score += 4
    else:
        components["ROE"] = {"status": "Weak", "score": 1, "detail": f"{roe}%"}
        total_score += 1

    # 4. ROCE
    roce = float(fundamentals.get("roce", 0.0))
    if roce >= 20.0:
        components["ROCE"] = {"status": "Strong", "score": 10, "detail": f"{roce}%"}
        total_score += 10
    elif roce >= 14.0:
        components["ROCE"] = {"status": "Moderate", "score": 7, "detail": f"{roce}%"}
        total_score += 7
    elif roce >= 8.0:
        components["ROCE"] = {"status": "Neutral", "score": 4, "detail": f"{roce}%"}
        total_score += 4
    else:
        components["ROCE"] = {"status": "Weak", "score": 1, "detail": f"{roce}%"}
        total_score += 1

    # 5. Debt to Equity
    de = float(fundamentals.get("debt_to_equity", 0.0))
    if de <= 0.2:
        components["Debt"] = {"status": "Negligible / Low", "score": 10, "detail": f"D/E {de}x"}
        total_score += 10
    elif de <= 0.8:
        components["Debt"] = {"status": "Manageable", "score": 8, "detail": f"D/E {de}x"}
        total_score += 8
    elif de <= 1.5:
        components["Debt"] = {"status": "Moderate", "score": 5, "detail": f"D/E {de}x"}
        total_score += 5
    else:
        components["Debt"] = {"status": "High", "score": 2, "detail": f"D/E {de}x"}
        total_score += 2

    # 6. Operating Margin / EBITDA Margin
    ebitda_margin = float(fundamentals.get("ebitda_margin", 0.0))
    if ebitda_margin >= 25.0:
        components["EBITDA Margin"] = {"status": "Strong", "score": 10, "detail": f"{ebitda_margin}%"}
        total_score += 10
    elif ebitda_margin >= 15.0:
        components["EBITDA Margin"] = {"status": "Moderate", "score": 7, "detail": f"{ebitda_margin}%"}
        total_score += 7
    else:
        components["EBITDA Margin"] = {"status": "Neutral", "score": 4, "detail": f"{ebitda_margin}%"}
        total_score += 4

    # 7. Cash Flow
    fcf = float(fundamentals.get("free_cash_flow", 0.0))
    if fcf > 1000.0:
        components["Cash Flow"] = {"status": "Strong Positive", "score": 10, "detail": f"₹{fcf} Cr FCF"}
        total_score += 10
    elif fcf > 0.0:
        components["Cash Flow"] = {"status": "Positive", "score": 7, "detail": f"₹{fcf} Cr FCF"}
        total_score += 7
    else:
        components["Cash Flow"] = {"status": "Negative / Constrained", "score": 3, "detail": f"₹{fcf} Cr FCF"}
        total_score += 3

    # 8. Valuation (P/E relative)
    pe = float(fundamentals.get("pe", 0.0))
    if 0 < pe <= 20.0:
        components["Valuation"] = {"status": "Attractive", "score": 10, "detail": f"P/E {pe}x"}
        total_score += 10
    elif pe <= 35.0:
        components["Valuation"] = {"status": "Fair / Neutral", "score": 7, "detail": f"P/E {pe}x"}
        total_score += 7
    elif pe <= 60.0:
        components["Valuation"] = {"status": "Elevated", "score": 4, "detail": f"P/E {pe}x"}
        total_score += 4
    else:
        components["Valuation"] = {"status": "High Premium", "score": 2, "detail": f"P/E {pe}x"}
        total_score += 2

    # 9. Liquidity (Current Ratio)
    cr = float(fundamentals.get("current_ratio", 1.0))
    if cr >= 1.5:
        components["Liquidity"] = {"status": "Strong", "score": 10, "detail": f"Ratio {cr}"}
        total_score += 10
    elif cr >= 1.0:
        components["Liquidity"] = {"status": "Adequate", "score": 7, "detail": f"Ratio {cr}"}
        total_score += 7
    else:
        components["Liquidity"] = {"status": "Tight", "score": 3, "detail": f"Ratio {cr}"}
        total_score += 3

    # 10. Promoter Holding
    promoter = float(fundamentals.get("promoter_holding", 50.0))
    if promoter >= 50.0:
        components["Promoter Holding"] = {"status": "Majority (>50%)", "score": 10, "detail": f"{promoter}%"}
        total_score += 10
    elif promoter >= 25.0:
        components["Promoter Holding"] = {"status": "Substantial", "score": 7, "detail": f"{promoter}%"}
        total_score += 7
    elif promoter == 0.0:
        components["Promoter Holding"] = {"status": "Institutional / Widely Held", "score": 8, "detail": "Professional Board"}
        total_score += 8
    else:
        components["Promoter Holding"] = {"status": "Low (<25%)", "score": 4, "detail": f"{promoter}%"}
        total_score += 4

    overall_label = "Strong" if total_score >= 75 else ("Moderate" if total_score >= 55 else ("Watchlist" if total_score >= 40 else "Weak"))

    return {
        "overall_health": overall_label,
        "score_out_of_100": round(total_score, 1),
        "components": components,
        "disclaimer": "This analytical score is purely mathematical based on public filings and does not constitute financial advice."
    }
