"""
Regenerates the verification snapshots in processed/computed/.

The app itself never reads from processed/computed/ — it calls the same
compute_*() functions in functions.py directly, live, on every load (so it
can never go stale). This script exists only so a human can open a plain CSV
and check the numbers currently backing the dashboard, without running
Streamlit. Run it any time after editing a file in processed/editable/:

    python3 regenerate_computed_data.py

See assets/COMPUTED_DATA_FORMULAS.txt for what each column means and how it's
calculated.
"""

import functions as f

OUT_DIR = "processed/computed"


def main():
    childcare_centers, schools, health_centers, older_person_care, \
        long_term_care, action_offices, migration_centers, bus_stops = \
        f.load_data()

    demographics = f.load_demographics()

    childcare_summary = f.compute_childcare_summary(childcare_centers)
    childcare_summary.to_csv(f"{OUT_DIR}/childcare_summary.csv", index=False)
    print(f"wrote {OUT_DIR}/childcare_summary.csv ({len(childcare_summary)} rows)")

    senior_summary = f.compute_senior_summary(demographics)
    senior_summary.to_csv(f"{OUT_DIR}/senior_summary.csv", index=False)
    print(f"wrote {OUT_DIR}/senior_summary.csv ({len(senior_summary)} rows)")

    _, district_context = f.load_demand_context()
    district_context.to_csv(f"{OUT_DIR}/demand_district_context.csv", index=False)
    print(f"wrote {OUT_DIR}/demand_district_context.csv ({len(district_context)} rows)")

    facility_cols = f.FACILITY_COUNT_DIVISIONS + ["Trainings", "Total", "Bus stops"]
    ratio_cols = [
        spec["ratio_col"] for spec in f.ACCESSIBILITY_RATIO_INDICATORS.values()
    ]
    facility_ratios = demographics[["barangay"] + facility_cols + ratio_cols]
    facility_ratios.to_csv(f"{OUT_DIR}/facility_counts_and_ratios.csv", index=False)
    print(f"wrote {OUT_DIR}/facility_counts_and_ratios.csv ({len(facility_ratios)} rows)")

    demographics_by_district = f.load_demographics_by_district()
    demographics_by_district.to_csv(f"{OUT_DIR}/demographics_by_district.csv", index=False)
    print(f"wrote {OUT_DIR}/demographics_by_district.csv ({len(demographics_by_district)} rows)")


if __name__ == "__main__":
    main()
