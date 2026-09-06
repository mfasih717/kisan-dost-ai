from agents import function_tool
from database.db_setup import get_connection
from models.schemas import ProfitEstimate


@function_tool
def profit_estimator(crop_name: str, acres: float) -> ProfitEstimate:
    """Estimate full season profit: input costs vs expected revenue.

    Args:
        crop_name: Name of the crop
        acres: Land size in acres
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT expected_yield_per_acre, expected_profit_per_acre FROM crops WHERE crop_name = ?", (crop_name,))
    crop_row = cursor.fetchone()

    cursor.execute("""
        SELECT urea_bags_per_acre, dap_bags_per_acre, urea_price_per_bag, dap_price_per_bag
        FROM fertilizer_rates WHERE crop_name = ?
    """, (crop_name,))
    fert_row = cursor.fetchone()
    conn.close()

    if not crop_row or not fert_row:
        return ProfitEstimate(crop_name=crop_name, acres=acres, total_input_cost_pkr=0,
                               expected_revenue_pkr=0, net_margin_pkr=0, break_even_yield_per_acre=0)

    fert_cost = ((fert_row["urea_bags_per_acre"] * fert_row["urea_price_per_bag"]) +
                 (fert_row["dap_bags_per_acre"] * fert_row["dap_price_per_bag"])) * acres
    revenue = crop_row["expected_profit_per_acre"] * acres + fert_cost  # profit table already net, add back cost for gross
    net_margin = (crop_row["expected_profit_per_acre"] * acres)
    break_even = fert_cost / (revenue / (crop_row["expected_yield_per_acre"] * acres)) if revenue else 0

    return ProfitEstimate(
        crop_name=crop_name, acres=acres,
        total_input_cost_pkr=round(fert_cost, 2),
        expected_revenue_pkr=round(revenue, 2),
        net_margin_pkr=round(net_margin, 2),
        break_even_yield_per_acre=round(break_even, 2)
    )