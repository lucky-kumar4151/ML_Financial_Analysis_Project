import os
import re
from django.utils import timezone

API_KEY = os.getenv("API_KEY")

# Extract float from strings like "3 Years: 47%" → 47.0
def extract_float(text):
    if text is None:
        return None
    try:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(numbers[-1]) if numbers else None
    except:
        return None


def generate_pros_cons(api_json: dict, max_items=3):
    pros, cons = [], []

    # -----------------------------
    # 1. BASIC EXTRACTS
    # -----------------------------
    company_info = api_json.get("company", {})
    data = api_json.get("data", {})

    bs = data.get("balancesheet", [])
    pl = data.get("profitandloss", [])
    analysis = data.get("analysis", [])

    # safeguard
    if not bs or not pl:
        return {"pros": [], "cons": [], "metrics": {}, "analysis_generated_at": str(timezone.now())}

    latest_pl = pl[-1]
    prev_pl = pl[-2] if len(pl) >= 2 else None
    latest_bs = bs[-1]
    prev_bs = bs[-2] if len(bs) >= 2 else None

    # -----------------------------
    # 2. HELPER to extract floats
    # -----------------------------
    def extract_float(x):
        import re
        if x is None:
            return None
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(x))
        return float(nums[-1]) if nums else None

    # -----------------------------
    # 3. Extract core metrics
    # -----------------------------
    roe = extract_float(company_info.get("roe_percentage"))
    dividend = extract_float(latest_pl.get("dividend_payout"))
    sales_now = extract_float(latest_pl.get("sales"))

    borrow_now = extract_float(latest_bs.get("borrowings"))
    borrow_prev = extract_float(prev_bs.get("borrowings")) if prev_bs else None

    # Sales growth (fallback)
    sales_prev = extract_float(prev_pl.get("sales")) if prev_pl else None
    sales_growth = None
    if sales_now and sales_prev and sales_prev != 0:
        sales_growth = ((sales_now - sales_prev) / sales_prev) * 100

    # Profit growth (fallback)
    profit_now = extract_float(latest_pl.get("net_profit"))
    profit_prev = extract_float(prev_pl.get("net_profit")) if prev_pl else None
    profit_growth = None
    if profit_now and profit_prev and profit_prev != 0:
        profit_growth = ((profit_now - profit_prev) / profit_prev) * 100

    # -----------------------------
    # 4. If ANALYSIS block exists → use it
    # -----------------------------
    sales_5y = None
    roe_3y = None
    profit_5y = None

    if analysis:
        for block in analysis:
            cs = block.get("compounded_sales_growth")
            cp = block.get("compounded_profit_growth")
            roe_b = block.get("roe")

            if "5 Years" in str(cs):
                sales_5y = extract_float(cs)

            if "3 Years" in str(roe_b):
                roe_3y = extract_float(roe_b)

            if "5 Years" in str(cp):
                profit_5y = extract_float(cp)

    # -----------------------------
    # 5. ML CLASSIFICATION (UNIVERSAL)
    # -----------------------------

    # ---- DEBT ----
    if borrow_now is not None and borrow_now < 200:
        pros.append("Company is almost debt-free.")
    if borrow_prev and borrow_now and borrow_now < borrow_prev:
        pros.append("Company has reduced debt over the years.")
    else:
        cons.append("Company has not reduced debt in recent years.")

    # ---- ROE ----
    final_roe = roe_3y or roe
    if final_roe:
        if final_roe > 10:
            pros.append(f"Company has strong ROE of {final_roe}%.")
        else:
            cons.append(f"Company has weak ROE of {final_roe}%.")

    # ---- DIVIDEND ----
    if dividend and dividend >= 30:
        pros.append(f"Company maintains a healthy dividend payout of {dividend}%.")
    else:
        cons.append("Company has low dividend payout.")

    # ---- SALES GROWTH ----
    final_sales_growth = sales_5y or sales_growth
    if final_sales_growth:
        if final_sales_growth > 10:
            pros.append(f"Company has healthy sales growth of {round(final_sales_growth,2)}%.")
        else:
            cons.append(f"Company has poor sales growth of {round(final_sales_growth,2)}%.")

    # ---- PROFIT GROWTH ----
    final_profit_growth = profit_5y or profit_growth
    if final_profit_growth:
        if final_profit_growth > 10:
            pros.append(f"Company has strong profit growth of {round(final_profit_growth,2)}%.")
        else:
            cons.append(f"Company has weak profit growth of {round(final_profit_growth,2)}%.")

    # -----------------------------
    # 6. LIMIT TO MAX & CLEAN
    # -----------------------------
    def unique_limit(lst):
        final = []
        for x in lst:
            if x not in final:
                final.append(x)
            if len(final) == max_items:
                break
        return final

    pros = unique_limit(pros)
    cons = unique_limit(cons)

    # -----------------------------
    # 7. Output
    # -----------------------------
    metrics = {
        "roe": final_roe,
        "dividend": dividend,
        "sales_growth": final_sales_growth,
        "profit_growth": final_profit_growth,
        "borrowings_now": borrow_now,
    }

    return {
        "pros": pros,
        "cons": cons,
        "metrics": metrics,
        "analysis_generated_at": str(timezone.now()),
    }
