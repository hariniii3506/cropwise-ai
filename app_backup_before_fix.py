import os
from functools import wraps
from flask import Flask, request, session, render_template, redirect, url_for, flash, jsonify

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "cropwise_ai_secret_key_2026"
)
def check_eligibility(
    scheme,
    country,
    state,
    district,
    recommended_crop,
    land_area,
    farmer_category
):
    """Return scheme eligibility status and explanation."""

    # ---------------------------------------------------------
    # COUNTRY CHECK
    # ---------------------------------------------------------
    allowed_countries = scheme.get("countries") or scheme.get("country")

    if allowed_countries:
        if isinstance(allowed_countries, str):
            allowed_countries = [allowed_countries]

        allowed_country_names = {
            str(value).strip().lower()
            for value in allowed_countries
            if value
        }

        if country and country.strip().lower() not in allowed_country_names:
            return (
                "ineligible",
                "This scheme is not available in your country."
            )

    # ---------------------------------------------------------
    # STATE CHECK
    # ---------------------------------------------------------
    allowed_states = scheme.get("states") or scheme.get("state")

    if allowed_states:
        if isinstance(allowed_states, str):
            allowed_states = [allowed_states]

        allowed_state_names = {
            str(value).strip().lower()
            for value in allowed_states
            if value
        }

        if state and state.strip().lower() not in allowed_state_names:
            return (
                "ineligible",
                "This scheme is not available in your state."
            )

    # ---------------------------------------------------------
    # FARMER CATEGORY CHECK
    # ---------------------------------------------------------
    required_category = (
        scheme.get("farmer_category")
        or scheme.get("category_eligibility")
    )

    if required_category:
        if isinstance(required_category, str):
            required_category = [required_category]

        allowed_categories = {
            str(value).strip().lower()
            for value in required_category
            if value
        }

        current_category = str(farmer_category or "").strip().lower()

        if current_category and current_category not in allowed_categories:
            return (
                "ineligible",
                "Your farmer category does not match this scheme."
            )

    # ---------------------------------------------------------
    # CROP CHECK
    # ---------------------------------------------------------
    required_crop = scheme.get("crop") or scheme.get("crops")

    if required_crop and recommended_crop:
        if isinstance(required_crop, str):
            required_crop = [required_crop]

        allowed_crops = {
            str(value).strip().lower()
            for value in required_crop
            if value
        }

        current_crop = str(recommended_crop).strip().lower()

        if current_crop not in allowed_crops:
            return (
                "ineligible",
                "This scheme does not support the recommended crop."
            )

    # ---------------------------------------------------------
    # LAND AREA
    # ---------------------------------------------------------
    # Land area is kept available for future scheme-specific
    # eligibility rules. Do not reject the farmer here unless
    # the scheme actually contains a land-area requirement.
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # DISTRICT
    # ---------------------------------------------------------
    # District is also retained for future district-specific
    # scheme rules.
    # ---------------------------------------------------------

    return (
        "eligible",
        "You meet the available eligibility criteria."
    )


@app.route("/schemes", methods=["GET", "POST"])
@login_required
def schemes():

    user_id = session["user_id"]

    # ---------------------------------------------------------
    # GET USER
    # ---------------------------------------------------------
    user = get_user_by_id(user_id)

    if not user:
        flash("User information not found.", "danger")
        return redirect(url_for("dashboard"))

    # ---------------------------------------------------------
    # GET LATEST RECOMMENDATION
    # ---------------------------------------------------------
    history = get_recommendation_history(user_id, limit=1)

    recommended_crop = None

    if history:
        recommended_crop = history[0].get("recommended_crop")

    # ---------------------------------------------------------
    # DEFAULT USER DETAILS
    # ---------------------------------------------------------
    country = "India"
    state = "Tamil Nadu"
    district = ""

    land_area = str(user.get("land_area") or "1.0")
    farmer_category = "General"

    # ---------------------------------------------------------
    # GET LOCATION FROM PROFILE
    # ---------------------------------------------------------
    location = str(user.get("farm_location") or "").strip()

    if location:

        parts = [
            part.strip()
            for part in location.split(",")
            if part.strip()
        ]

        # First part is treated as district/location
        if parts:
            district = parts[0]

        # Detect Tamil Nadu
        location_lower = location.lower()

        if "tamil" in location_lower or "nadu" in location_lower:
            state = "Tamil Nadu"

    # ---------------------------------------------------------
    # POST - UPDATE CHECKING DETAILS
    # ---------------------------------------------------------
    if request.method == "POST":

        country = request.form.get("country", "").strip()
        state = request.form.get("state", "").strip()
        district = request.form.get("district", "").strip()

        land_area = request.form.get(
            "land_area",
            land_area
        ).strip()

        farmer_category = request.form.get(
            "farmer_category",
            "General"
        ).strip()

        # Prevent empty values
        if not country:
            country = "India"

        if not state:
            state = "Tamil Nadu"

        if not farmer_category:
            farmer_category = "General"

    # ---------------------------------------------------------
    # SEARCH / FILTER
    # ---------------------------------------------------------
    search_q = request.args.get(
        "search",
        ""
    ).strip().lower()

    filter_category = request.args.get(
        "category",
        ""
    ).strip()

    filter_eligibility = request.args.get(
        "eligibility",
        ""
    ).strip().lower()

    # ---------------------------------------------------------
    # CATEGORY ORDER
    # ---------------------------------------------------------
    CATEGORIES_ORDER = [
        "Crop-specific schemes/support",
        "General farmer assistance schemes",
        "Irrigation schemes",
        "Crop insurance",
        "Seeds/input assistance",
        "Farm equipment subsidies",
        "Soil/land improvement",
        "Organic/natural farming",
        "Other agriculture subsidies"
    ]

    # ---------------------------------------------------------
    # CREATE GROUPS
    # ---------------------------------------------------------
    grouped_schemes = {
        category: []
        for category in CATEGORIES_ORDER
    }

    # ---------------------------------------------------------
    # PROCESS GOVERNMENT SCHEMES
    # ---------------------------------------------------------
    for scheme in GOVT_SCHEMES:

        status, reason = check_eligibility(
            scheme,
            country,
            state,
            district,
            recommended_crop,
            land_area,
            farmer_category
        )

        # Make a copy so original GOVT_SCHEMES
        # is not modified
        scheme_copy = scheme.copy()

        scheme_copy["status"] = status
        scheme_copy["eligibility_reason"] = reason

        # -----------------------------------------------------
        # SEARCH FILTER
        # -----------------------------------------------------
        if search_q:

            scheme_name = str(
                scheme.get("name") or ""
            ).lower()

            scheme_purpose = str(
                scheme.get("purpose") or ""
            ).lower()

            scheme_department = str(
                scheme.get("department") or ""
            ).lower()

            scheme_category = str(
                scheme.get("category") or ""
            ).lower()

            searchable_text = " ".join([
                scheme_name,
                scheme_purpose,
                scheme_department,
                scheme_category
            ])

            if search_q not in searchable_text:
                continue

        # -----------------------------------------------------
        # CATEGORY FILTER
        # -----------------------------------------------------
        scheme_category = str(
            scheme.get("category") or ""
        ).strip()

        if filter_category:
            if scheme_category != filter_category:
                continue

        # -----------------------------------------------------
        # ELIGIBILITY FILTER
        # -----------------------------------------------------
        if filter_eligibility:

            if (
                filter_eligibility == "eligible"
                and status != "eligible"
            ):
                continue

            if (
                filter_eligibility == "ineligible"
                and status != "ineligible"
            ):
                continue

            if (
                filter_eligibility == "unconfirmed"
                and status != "unconfirmed"
            ):
                continue

        # -----------------------------------------------------
        # ADD TO CATEGORY
        # -----------------------------------------------------
        if scheme_category in grouped_schemes:
            grouped_schemes[scheme_category].append(
                scheme_copy
            )

    # ---------------------------------------------------------
    # RENDER SCHEMES PAGE
    # ---------------------------------------------------------
    return render_template(
        "schemes.html",
        grouped_schemes=grouped_schemes,
        categories=CATEGORIES_ORDER,
        selected_category=filter_category,
        selected_eligibility=filter_eligibility,
        search_q=search_q,
        country=country,
        state=state,
        district=district,
        recommended_crop=recommended_crop,
        land_area=land_area,
        farmer_category=farmer_category
    )


@app.route("/scheme-apply")
@login_required
def scheme_apply():

    scheme_id = request.args.get(
        "scheme",
        ""
    ).strip()

    # Find requested scheme
    scheme = next(
        (
            item
            for item in GOVT_SCHEMES
            if str(item.get("id", "")) == scheme_id
        ),
        None
    )

    # Scheme not found
    if not scheme:
        flash(
            "Government scheme not found.",
            "danger"
        )
        return redirect(url_for("schemes"))

    # Official URL not available
    if not scheme.get("url"):
        flash(
            "Official scheme portal not found.",
            "danger"
        )
        return redirect(url_for("schemes"))

    return render_template(
        "scheme_apply.html",
        scheme=scheme
    )


# -------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------

@app.route("/api/crop_info/<crop_name>")
def api_crop_info(crop_name):

    crop_name = str(crop_name).strip()

    if crop_name in crop_database:
        return jsonify(
            crop_database[crop_name]
        )

    return jsonify({
        "error": "Crop not found"
    }), 404


# -------------------------------------------------------------
# APPLICATION START
# -------------------------------------------------------------

if __name__ == "__main__":

    # Optional SMTP connection test
    if "--check-smtp" in os.sys.argv:
        raise SystemExit(
            0 if check_smtp_connection() else 1
        )

    host = os.environ.get(
        "FLASK_RUN_HOST",
        "0.0.0.0"
    )

    port = int(
        os.environ.get(
            "FLASK_RUN_PORT",
            5000
        )
    )

    app.run(
        debug=True,
        host=host,
        port=port
    )
