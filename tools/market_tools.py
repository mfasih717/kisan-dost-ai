from agents import function_tool
from database.db_setup import get_connection
from models.schemas import MandiPriceResponse, MandiPrice


@function_tool
def mandi_price_lookup(
    crop_name: str,
    district: str | None = None
) -> MandiPriceResponse:
    """
    Look up mandi prices for a crop.

    If district is provided, return only that district's price.
    If district is not provided, return prices across all available districts.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # CROP + DISTRICT DONO DIYE GAYE HAIN
    # -----------------------------------------------------

    if district:

        cursor.execute(
            """
            SELECT *
            FROM mandi_prices
            WHERE LOWER(crop_name) = LOWER(?)
              AND LOWER(district) = LOWER(?)
            ORDER BY date_recorded DESC
            """,
            (crop_name.strip(), district.strip())
        )

    # -----------------------------------------------------
    # SIRF CROP DIYA GAYA HAI
    # -----------------------------------------------------

    else:

        cursor.execute(
            """
            SELECT *
            FROM mandi_prices
            WHERE LOWER(crop_name) = LOWER(?)
            ORDER BY date_recorded DESC
            """,
            (crop_name.strip(),)
        )


    rows = cursor.fetchall()

    conn.close()


    # -----------------------------------------------------
    # DATA NA MILE
    # -----------------------------------------------------

    if not rows:

        return MandiPriceResponse(
            prices=[],
            best_district=None
        )


    # -----------------------------------------------------
    # DATABASE ROWS -> RESPONSE MODEL
    # -----------------------------------------------------

    prices = [

        MandiPrice(
            crop_name=row["crop_name"],
            district=row["district"],
            price_per_maund=row["price_per_maund"],
            date_recorded=row["date_recorded"]
        )

        for row in rows
    ]


    # -----------------------------------------------------
    # BEST DISTRICT
    # -----------------------------------------------------

    best = max(
        prices,
        key=lambda p: p.price_per_maund
    )


    return MandiPriceResponse(
        prices=prices,
        best_district=best.district
    )