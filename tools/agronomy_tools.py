from agents import function_tool
from database.db_setup import get_connection
from models.schemas import CropAdvisorResponse, CropPlan, FertilizerPlan


@function_tool
def crop_advisor(season: str, soil_type: str, water_availability: str) -> CropAdvisorResponse:
    """Recommend best crops based on season, soil type, and water availability.

    Args:
        season: 'Rabi' or 'Kharif'
        soil_type: 'loamy', 'sandy', or 'clay'
        water_availability: 'low', 'medium', or 'high'
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT crop_name, season, expected_yield_per_acre, expected_profit_per_acre
        FROM crops
        WHERE season = ? AND soil_type = ?
    """, (season, soil_type))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return CropAdvisorResponse(recommendations=[], notes="No matching crops found for these conditions.")

    plans = [
        CropPlan(
            crop_name=row["crop_name"],
            season=row["season"],
            expected_yield_per_acre=row["expected_yield_per_acre"],
            expected_profit_per_acre=row["expected_profit_per_acre"],
            reason=f"Suits {soil_type} soil with {water_availability} water availability in {season} season."
        )
        for row in rows
    ]
    return CropAdvisorResponse(recommendations=plans, notes=f"Based on {soil_type} soil and {water_availability} water.")


@function_tool
def fertilizer_calculator(crop_name: str, acres: float) -> FertilizerPlan:
    """Calculate Urea/DAP bags needed and total cost for a given crop and land size.

    Args:
        crop_name: Name of the crop (e.g. 'Wheat', 'Cotton')
        acres: Land size in acres
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT urea_bags_per_acre, dap_bags_per_acre, urea_price_per_bag, dap_price_per_bag
        FROM fertilizer_rates WHERE crop_name = ?
    """, (crop_name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return FertilizerPlan(crop_name=crop_name, acres=acres, urea_bags=0, dap_bags=0, total_cost_pkr=0)

    urea_bags = round(row["urea_bags_per_acre"] * acres, 1)
    dap_bags = round(row["dap_bags_per_acre"] * acres, 1)
    total_cost = round((urea_bags * row["urea_price_per_bag"]) + (dap_bags * row["dap_price_per_bag"]), 2)

    return FertilizerPlan(crop_name=crop_name, acres=acres, urea_bags=urea_bags, dap_bags=dap_bags, total_cost_pkr=total_cost)