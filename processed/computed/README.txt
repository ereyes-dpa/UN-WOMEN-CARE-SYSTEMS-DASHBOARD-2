COMPUTED/
=========

This folder contains verification snapshots. The application does not
read from this folder; it calls the same compute_*() functions in
functions.py directly, live, on every load, so these figures always
reflect the current state of processed/editable/. This folder exists so
the current figures can be reviewed as a plain CSV without running the
application.

Regenerate after editing a file in processed/editable/:

    python3 regenerate_computed_data.py

See assets/COMPUTED_DATA_FORMULAS.txt for what each column means and
exactly how it is calculated.

FILE                              REPLACES                                          COMPUTED FROM
----                               --------                                          -------------
childcare_summary.csv              processed/editable/childcare_summary.csv         care_supply_facilities.csv

senior_summary.csv                 processed/editable/senior_summary.csv            demographics_by_barangay.csv
                                                                                      (combines OSCA registration and
                                                                                      2020 Census -- see the "source"
                                                                                      column on each row)

demand_district_context.csv        processed/editable/demand_district_context.csv   demographics_by_district.csv's
                                                                                      seniors_registered/pwd_registered
                                                                                      columns

facility_counts_and_ratios.csv     Facility-count and ratio_* columns formerly       care_supply_facilities.csv,
                                    stored directly in                                grouped by barangay, joined
                                    demographics_by_barangay.csv                      against demographics_by_barangay.csv

demographics_by_district.csv       processed/editable/demographics_by_district.csv   demographics_by_barangay.csv
