import base64
import json
import io
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import numpy as np
from PIL import Image

# --------------------------------------------------
# ACCESSIBILITY RATIO INDICATORS
# (facility-per-1,000 ratios from demographics.csv's
# pre-computed ratio_* columns — facility count for the
# relevant type, divided by the population it serves, per
# 1,000. See indicators_codebook.csv, "Accesibility"
# category. Shared between the Accessibility Map page and
# the Accessibility Analysis page so both stay in sync —
# update this dict once, not in two places.)
# --------------------------------------------------

ACCESSIBILITY_RATIO_INDICATORS = {
    "Childcare per 1,000 Children (0-5)": {
        "facility_col": "Childcare",
        "pop_col": "age_0_5",
        "ratio_col": "ratio_childcare"
    },
    "Childcare per 1,000 Female Children (0-5)": {
        "facility_col": "Childcare",
        "pop_col": "age_0_5_f",
        "ratio_col": "ratio_childcare_f"
    },
    "Childcare per 1,000 Male Children (0-5)": {
        "facility_col": "Childcare",
        "pop_col": "age_0_5_m",
        "ratio_col": "ratio_childcare_m"
    },
    "School Facilities per 1,000 Children (3-5)": {
        "facility_col": "Schools",
        "pop_col": "age_3_5",
        "ratio_col": "ratio_school_3_5"
    },
    "School Facilities per 1,000 Female Children (3-5)": {
        "facility_col": "Schools",
        "pop_col": "age_3_5_f",
        "ratio_col": "ratio_school_3_5_f"
    },
    "School Facilities per 1,000 Male Children (3-5)": {
        "facility_col": "Schools",
        "pop_col": "age_3_5_m",
        "ratio_col": "ratio_school_3_5_m"
    },
    "School Facilities per 1,000 Children (6-17)": {
        "facility_col": "Schools",
        "pop_col": "age_6_17",
        "ratio_col": "ratio_school_6_17"
    },
    "School Facilities per 1,000 Female Children (6-17)": {
        "facility_col": "Schools",
        "pop_col": "age_6_17_f",
        "ratio_col": "ratio_school_6_17_f"
    },
    "School Facilities per 1,000 Male Children (6-17)": {
        "facility_col": "Schools",
        "pop_col": "age_6_17_m",
        "ratio_col": "ratio_school_6_17_m"
    },
    "Eldercare Facilities per 1,000 Older Persons (60+)": {
        "facility_col": "Older persons care",
        "pop_col": "age_60plus",
        "ratio_col": "ratio_old_60"
    },
    "Eldercare Facilities per 1,000 Female Older Persons (60+)": {
        "facility_col": "Older persons care",
        "pop_col": "age_60plus_f",
        "ratio_col": "ratio_old_60_f"
    },
    "Eldercare Facilities per 1,000 Male Older Persons (60+)": {
        "facility_col": "Older persons care",
        "pop_col": "age_60plus_m",
        "ratio_col": "ratio_old_60_m"
    },
    "Eldercare Facilities per 1,000 Older Persons (80+)": {
        "facility_col": "Older persons care",
        "pop_col": "age_80plus",
        "ratio_col": "ratio_old_80"
    },
    "Eldercare Facilities per 1,000 Female Older Persons (80+)": {
        "facility_col": "Older persons care",
        "pop_col": "age_80plus_f",
        "ratio_col": "ratio_old_80_f"
    },
    "Eldercare Facilities per 1,000 Male Older Persons (80+)": {
        "facility_col": "Older persons care",
        "pop_col": "age_80plus_m",
        "ratio_col": "ratio_old_80_m"
    },
    "Health Centers per 1,000 People": {
        "facility_col": "Health centers",
        "pop_col": "pop_census",
        "ratio_col": "ratio_pop_health"
    },
    "Health Centers per 1,000 Females": {
        "facility_col": "Health centers",
        "pop_col": "pop_female",
        "ratio_col": "ratio_pop_health_f"
    },
    "Health Centers per 1,000 Males": {
        "facility_col": "Health centers",
        "pop_col": "pop_male",
        "ratio_col": "ratio_pop_health_m"
    },
    "Health Centers per 1,000 Children (0-5)": {
        "facility_col": "Health centers",
        "pop_col": "age_0_5",
        "ratio_col": "ratio_child_health"
    },
    "Health Centers per 1,000 Female Children (0-5)": {
        "facility_col": "Health centers",
        "pop_col": "age_0_5_f",
        "ratio_col": "ratio_child_health_f"
    },
    "Health Centers per 1,000 Male Children (0-5)": {
        "facility_col": "Health centers",
        "pop_col": "age_0_5_m",
        "ratio_col": "ratio_child_health_m"
    },
    "Health Centers per 1,000 Older Persons (60+)": {
        "facility_col": "Health centers",
        "pop_col": "age_60plus",
        "ratio_col": "ratio_old_health"
    },
    "Health Centers per 1,000 Female Older Persons (60+)": {
        "facility_col": "Health centers",
        "pop_col": "age_60plus_f",
        "ratio_col": "ratio_old_health_f"
    },
    "Health Centers per 1,000 Male Older Persons (60+)": {
        "facility_col": "Health centers",
        "pop_col": "age_60plus_m",
        "ratio_col": "ratio_old_health_m"
    },
    "Health Centers per 1,000 PWDs": {
        "facility_col": "Health centers",
        "pop_col": "pwd_registered",
        "ratio_col": "ratio_pwd_health"
    },
    "Long-Term Care & Rehabilitation per 1,000 PWDs": {
        "facility_col": "Long-term care and rehabilitation services",
        "pop_col": "pwd_registered",
        "ratio_col": "ratio_pwd"
    }
}

@st.cache_data
def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    

# --------------------------------------------------
# CHILDCARE FUNCTIONS
# --------------------------------------------------
def childcare_color(category):

    category = str(category).upper()

    if "CHILD DEVELOPMENT" in category:
        return "#4C1D95"   # purple gradient — darkest

    elif "CHILD LEARNING" in category:
        return "#8869C9"   # purple gradient — mid

    elif "DAY CARE" in category:
        return "#C4B5FD"   # purple gradient — lightest (still visible on map)

    return "#C4B5FD"


# --------------------------------------------------
# SCHOOLS FUNCTIONS
# --------------------------------------------------
def school_color(category):

    category = str(category).upper()

    if "PUBLIC SCHOOL" in category:
        return "#055B52"   # green gradient — darkest

    elif "PRIVATE SCHOOL" in category:
        return "#A6CFC1"   # green gradient — lightest (still visible on map)

    return "#A6CFC1"

# --------------------------------------------------
# OLDERS CARE FUCNTIONS
# --------------------------------------------------
def opc_color(category):

    category = str(category).upper()

    if "NURSING" in category:
        return "#055B52"   # green gradient — darkest

    elif "BAHAY ARUGA" in category:
        return "#A6CFC1"   # green gradient — lightest (still visible on map)

    return "#A6CFC1"


# --------------------------------------------------
# HEALTHCARE FUNCTIONS
# --------------------------------------------------
def category_hex(cat):

    rgb = category_color(cat)

    return "#{:02X}{:02X}{:02X}".format(
        rgb[0],
        rgb[1],
        rgb[2]
    )

def marker_color(category):

    category = str(category).upper()

    if "QC LGU" in category:
        return "#4C1D95"   # purple gradient — darkest

    elif "NATIONAL" in category:
        return "#643BAA"   # purple gradient

    elif "SUPER HEALTH" in category:
        return "#7C5ABF"   # purple gradient

    elif "HEALTH CENTER" in category:
        return "#9478D3"   # purple gradient

    elif "PHARMACY" in category:
        return "#AC97E8"   # purple gradient

    elif "MILK BANK" in category:
        return "#C4B5FD"   # purple gradient — lightest (still visible on map)

    return "#7C5ABF"

# --------------------------------------------------
# LONGTERM CARE FUNCTIONS
# --------------------------------------------------
def ltc_color(category):

    category = str(category).upper()

    # Rehabilitation-focused
    if "REHABILITATION" in category:
        return "#4C1D95"   # purple gradient — darkest

    # Physical therapy
    elif "PHYSICAL THERAPY" in category:
        return "#643BAA"   # purple gradient

    # Occupational therapy / schools
    elif "OCCUPATIONAL" in category:
        return "#7C5ABF"   # purple gradient

    # Psychological services
    elif "PSYCHOLOGICAL" in category:
        return "#9478D3"   # purple gradient

    # Psychiatric rehabilitation
    elif "PSYCHIATRIC" in category:
        return "#AC97E8"   # purple gradient

    # Disability support center
    elif "KABAHAGI" in category:
        return "#C4B5FD"   # purple gradient — lightest (still visible on map)

    return "#C4B5FD"

def ltc_hex(category):
    return ltc_color(category)

# --------------------------------------------------
# SATELLITE OFFICES FUNCTIONS
# --------------------------------------------------
DISTRICT_COLORS = {
    1: "#055B52",   # green gradient — darkest
    2: "#257268",   # green gradient
    3: "#45897E",   # green gradient
    4: "#66A195",   # green gradient
    5: "#86B8AB",   # green gradient
    6: "#A6CFC1"    # green gradient — lightest (still visible on map)
}

def district_color(district):

    try:
        district = int(district)
        return DISTRICT_COLORS.get(
            district,
            "#DDD6FE"
        )

    except:
        return "#DDD6FE"
    
def category_color(cat):

    cat = str(cat).upper()

    if "QC LGU" in cat:
        return [76, 29, 149]     # #4C1D95 purple gradient — darkest

    elif "NATIONAL" in cat:
        return [100, 59, 170]    # #643BAA purple gradient

    elif "SUPER HEALTH" in cat:
        return [124, 90, 191]    # #7C5ABF purple gradient

    elif "HEALTH CENTER" in cat:
        return [148, 120, 211]   # #9478D3 purple gradient

    elif "PHARMACY" in cat:
        return [172, 151, 232]   # #AC97E8 purple gradient

    elif "MILK BANK" in cat:
        return [196, 181, 253]   # #C4B5FD purple gradient — lightest

    return [124, 90, 191]


def health_category_mapper(cat):

    cat = str(cat)

    if "National government-owned hospitals" in cat:
        return "National"

    elif "LGU-run hospitals" in cat:
        return "QC LGU"

    elif "LGU-run lying-in clinics" in cat:
        return "QC LGU"

    elif "Health center pharmacy" in cat:
        return "Pharmacy"

    elif "Super health care centers" in cat:
        return "Super Health"

    elif "Health centers" in cat:
        return "Health Center"

    elif "Human milk bank" in cat:
        return "Milk Bank"

    return "Other"


# --------------------------------------------------
# CLEANNING
# --------------------------------------------------
def clean_health_centers(df) :
    df["Category"] = (
        df["category"]
        .apply(health_category_mapper)
    )

    df = df.rename(
        columns={
            "name_original": "Name",
            "address_clean": "Address",
            "district": "District"
        }
    )

    df["District"] = pd.to_numeric(
        df["District"],
        errors="coerce"
    ).astype("Int64")

    df["Name"] = df["Name"].str.title()


    return df

def clean_dataframe(df) :
    df = df.rename(
    columns={
            "name_original": "Name",
            "district": "District",
            "address_clean": "Address",
            "sub_division": "Sector",
            "category": "Category"
        }
    )

    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    df["Name"] = df["Name"].str.title()

    df["District"] = (
        pd.to_numeric(df["District"], errors="coerce")
        .astype("Int64")
    )
        
    return df

@st.cache_data
def load_geo():
    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    bounds = gdf.total_bounds

    return gdf.__geo_interface__, bounds

@st.cache_data
def load_geo_explorer():

    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    gdf["geometry"] = (
        gdf.geometry
        .simplify(
            tolerance=0.0001,
            preserve_topology=True
        )
    )

    bounds = gdf.total_bounds

    return gdf.__geo_interface__, bounds


@st.cache_resource
def load_qc_boundary():
    """
    Reads the barangay-level boundaries and dissolves them into
    a single Quezon City outline (shapely geometry, EPSG:4326).
    Used to crop climate rasters to the city limits instead of
    showing their full rectangular extent.
    """

    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    # union_all() replaced the unary_union property in
    # geopandas 1.0 — fall back for older installs.
    if hasattr(gdf, "union_all"):
        dissolved = gdf.union_all()
    else:
        dissolved = gdf.unary_union

    return dissolved


@st.cache_resource
def get_boundary_geojson(geo_json):
    return folium.GeoJson(
        geo_json,
        style_function=lambda x: {
            "fillColor": "#A6CFC1",   # secondary light green
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.15,
        }
    )

@st.cache_data
def load_data():

    care = pd.read_csv("processed/care_v3.csv")

    category_cols = [
        "major_division",
        "sub_division",
        "category"
    ]

    for col in category_cols:
        if col in care.columns:
            care[col] = care[col].astype("category")

    care["open_hours"] = (
        care["open_hours"]
        .fillna("Not available")
    )

    care["close_hours"] = (
        care["close_hours"]
        .fillna("Not available")
    )        

    # Clean coordinates
    care["latitude"] = pd.to_numeric(
        care["latitude"],
        errors="coerce"
    )

    care["longitude"] = pd.to_numeric(
        care["longitude"],
        errors="coerce"
    )

    care = care.dropna(
        subset=["latitude", "longitude"]
    )

    childcare_centers = care[
        care["major_division"] == "Childcare"
    ].copy()

    schools = care[
        care["major_division"] == "Schools"
    ].copy()

    health_centers = care[
        care["major_division"] == "Health centers"
    ].copy()

    older_person_care = care[
        care["major_division"] == "Older persons care"
    ].copy()

    long_term_care = care[
        care["major_division"]
        == "Long-term care and rehabilitation services"
    ].copy()

    satellite_offices = care[
        care["major_division"]
        == "Quezon City satellite offices for services"
    ].copy()

    migration_centers = care[
        care["major_division"] == "Trainings"
    ].copy()

    # --------------------------------------------------
    # CLEANING
    # --------------------------------------------------

    health_centers            = clean_health_centers(health_centers)
    childcare_centers         = clean_dataframe(childcare_centers)
    schools                   = clean_dataframe(schools)
    older_person_care         = clean_dataframe(older_person_care)
    long_term_care            = clean_dataframe(long_term_care)
    satellite_offices         = clean_dataframe(satellite_offices)
    satellite_offices["Name"] = "District " + satellite_offices["District"].astype(int).astype(str)
    migration_centers         = clean_dataframe(migration_centers)

    return (
        childcare_centers,
        schools,
        health_centers,
        older_person_care,
        long_term_care,
        satellite_offices,
        migration_centers
    )

@st.cache_data
def load_data_for_kpis():
    """
    Loads the consolidated barangay-level demographics table
    (processed/indicators/demographics.csv) and reshapes it into
    the same three dataframes this function has always returned
    — population_summary, population_sex, population_age — so
    every downstream page (Population Overview, Schools, Health
    Centers, Older Persons, Long-Term Care, Accessibility
    Analysis, Care Planning & Investment Priorities, Barangay
    Clusters) keeps working unchanged.

    demographics.csv replaces the four legacy files this used to
    read (population_summary.csv, population_2024_by_sex.csv,
    population_2024_by_age_group.csv,
    barangay_district_mapping.csv) with a single, richer,
    barangay-level source that also carries the new accessibility,
    disability, and CBMS socio-economic indicators (consumed by
    other parts of the dashboard via load_demographics() below).

    Unlike the legacy pipeline, demographics.csv already carries
    a clean integer "district" per barangay, so no separate
    barangay-to-district mapping/merge step is needed here.
    """

    import pandas as pd

    # ==================================================
    # LOAD FILE
    # ==================================================

    demographics = pd.read_csv(
        "processed/indicators/demographics.csv"
    )

    # ==================================================
    # POPULATION SUMMARY (city-wide total — kept for
    # backward compatibility; not consumed elsewhere in
    # the dashboard today, but other code may still
    # unpack it from this function's return value)
    # ==================================================

    population_summary = pd.DataFrame({
        "Total": [demographics["pop_census"].sum()],
        "Male": [demographics["pop_male"].sum()],
        "Female": [demographics["pop_female"].sum()]
    })

    # ==================================================
    # POPULATION BY SEX (one row per barangay)
    # ==================================================

    population_sex = demographics[
        [
            "barangay",
            "district",
            "pop_male",
            "pop_female",
            "pop_census"
        ]
    ].rename(
        columns={
            "barangay": "Barangay",
            "district": "District",
            "pop_male": "Male",
            "pop_female": "Female",
            "pop_census": "Total"
        }
    )

    # ==================================================
    # POPULATION BY AGE GROUP (one row per barangay)
    # Column names match the four bands the rest of the
    # dashboard already expects.
    # ==================================================

    population_age = demographics[
        [
            "barangay",
            "district",
            "age_0_5",
            "age_6_17",
            "age_18_59",
            "age_60plus",
            "pop_census"
        ]
    ].rename(
        columns={
            "barangay": "Barangay",
            "district": "District",
            "age_0_5": "0-5 (Early Childhood)",
            "age_6_17": "6-17 (School Age Children)",
            "age_18_59": "18-59 (Working Age Adult)",
            "age_60plus": "60+ (Elderly)",
            "pop_census": "Total"
        }
    )

    # ==================================================
    # RETURN
    # ==================================================

    return (
        population_summary,
        population_sex,
        population_age
    )


@st.cache_data
def load_demographics():
    """
    Loads the full consolidated barangay-level indicators table
    (processed/indicators/demographics.csv) with all 87 columns
    intact — facility counts, age/sex breakdowns, registered
    seniors/PWDs, CBMS socio-economic indicators, migrant worker
    counts, and the pre-computed demand/accessibility ratio
    columns (ratio_*).

    Use this (rather than re-deriving figures from population_age
    /population_sex) wherever a page needs the newer indicators
    that aren't part of the legacy population_summary/sex/age
    shape — e.g. registered PWDs, CBMS food insecurity, or the
    facilities-per-1,000 ratio columns.
    """

    import pandas as pd

    demographics = pd.read_csv(
        "processed/indicators/demographics.csv"
    )

    demographics["barangay"] = (
        demographics["barangay"]
        .astype(str)
        .str.strip()
    )

    demographics["district"] = (
        pd.to_numeric(demographics["district"], errors="coerce")
        .astype("Int64")
    )

    return demographics


@st.cache_data
def load_climate_context():
    """
    Loads the city-wide (non-barangay) flood risk indicators
    from processed/indicators/climate.csv. These figures are
    WorldPop-based and only available at the Quezon City total
    level — there is no per-barangay breakdown — so they're
    meant for KPI cards/context on the Climate & Hazard Exposure
    page, not for a choropleth map.
    """

    import pandas as pd

    climate = pd.read_csv(
        "processed/indicators/climate.csv"
    )

    return climate


@st.cache_data
def load_demand_context():
    """
    Loads the two city/district-level administrative context
    tables that sit alongside demographics.csv:

    - processed/indicators/demand_city_context.csv — city-wide
      breakdowns (seniors by sex/age, seniors also registered
      as PWD, PWDs by disability type with male/female splits).
      No barangay or district breakdown; OSCA and PDAO figures
      for "seniors with disability" are kept as two separate
      rows since they use different registration bases and
      disagree (4,677 vs 6,429) — this is documented in the
      "note" column rather than reconciled.
    - processed/indicators/demand_district_context.csv —
      registered seniors and PWDs per district (roman numeral
      districts I-VI, converted here to integers 1-6 to match
      the "district" column used elsewhere in the dashboard).

    Returns (city_context, district_context).
    """

    import pandas as pd

    city_context = pd.read_csv(
        "processed/indicators/demand_city_context.csv"
    )

    district_context = pd.read_csv(
        "processed/indicators/demand_district_context.csv"
    )

    roman_to_int = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6
    }

    district_context["district"] = (
        district_context["district"]
        .map(roman_to_int)
    )

    return city_context, district_context


def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return [
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    ]


# --------------------------------------------------
# DEMAND-PER-FACILITY INDICATORS
# (methodology adapted from the supply/cluster
# indicator notebooks: population in a target age
# group divided by the number of facilities serving
# that age group — computed per group, not combined)
# --------------------------------------------------
def compute_population_per_facility(
    barangay_pop,
    care_clean,
    children_divisions=None,
    elderly_divisions=None
):
    """
    Computes children-per-facility and elderly-per-facility
    at the barangay level.

    barangay_pop must contain:
        "Barangay", "0-5 (Early Childhood)", "60+ (Elderly)"

    care_clean must contain:
        "barangay", "major_division"

    children_divisions / elderly_divisions let the caller
    decide which major_division values count as serving
    children vs. older persons. Defaults match the QC
    care_v3.csv major_division values.
    """

    if children_divisions is None:
        children_divisions = [
            "Childcare",
            "Schools"
        ]

    if elderly_divisions is None:
        elderly_divisions = [
            "Older persons care",
            "Long-term care and rehabilitation services"
        ]

    care_clean = care_clean.copy()

    care_clean["barangay"] = (
        care_clean["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    child_facilities = (
        care_clean[
            care_clean["major_division"].isin(children_divisions)
        ]
        .groupby("barangay")
        .size()
        .reset_index(name="Child-Serving Facilities")
    )

    elderly_facilities = (
        care_clean[
            care_clean["major_division"].isin(elderly_divisions)
        ]
        .groupby("barangay")
        .size()
        .reset_index(name="Elderly-Serving Facilities")
    )

    out = barangay_pop.copy()

    out["Barangay"] = (
        out["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    out = out.merge(
        child_facilities,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    ).drop(columns=["barangay"], errors="ignore")

    out = out.merge(
        elderly_facilities,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    ).drop(columns=["barangay"], errors="ignore")

    out["Child-Serving Facilities"] = (
        out["Child-Serving Facilities"].fillna(0)
    )

    out["Elderly-Serving Facilities"] = (
        out["Elderly-Serving Facilities"].fillna(0)
    )

    # children per facility — np.nan when there are no
    # facilities, rather than infinity, so it reads cleanly
    # in tables/charts (mirrors the notebooks' np.where guard)
    out["Children per Facility"] = np.where(
        out["Child-Serving Facilities"] != 0,
        out["0-5 (Early Childhood)"] / out["Child-Serving Facilities"],
        np.nan
    )

    out["Elderly per Facility"] = np.where(
        out["Elderly-Serving Facilities"] != 0,
        out["60+ (Elderly)"] / out["Elderly-Serving Facilities"],
        np.nan
    )

    return out


# --------------------------------------------------
# BARANGAY CLUSTERING
# (methodology adapted from Clustering Exploration &
# Cluster Indicators notebooks: standardize a feature
# set describing demographics + service mix, then
# K-means to group barangays into comparable zones)
# --------------------------------------------------
def build_cluster_features(
    barangay_df,
    demographics,
    feature_cols=None
):
    """
    Builds the standardized feature matrix used for
    barangay clustering, spanning three dimensions:

    - Demographic: population_density, children_pct,
      elderly_pct (passed in via barangay_df, computed on
      the Population Overview page), plus sex_ratio_m_per_100f
      from demographics.
    - Accessibility: facilities_per_10k (facilities of any
      kind per 10,000 residents) plus a facility-type mix
      (share of local facilities that are Childcare, Health
      centers, Long-term care and rehabilitation services, or
      Schools — the four facility types with enough barangays
      to carry real signal; Older persons care, satellite
      offices, and Trainings are each present in well under
      5% of barangays and were dropped as near-constant/
      zero-inflated, which would otherwise dominate distance
      calculations with noise rather than signal).
    - Socio-economic: disability_prevalence_rate_pct,
      cbms_food_insecurity_prevalence_pct,
      cbms_housing_inadequacy_index_pct, and migrant workers
      per 1,000 population (registered OFWs, normalized by
      population since raw counts aren't comparable across
      barangays of different sizes).

    barangay_df is expected to already carry, per barangay:
    Total, population_density, children_pct, elderly_pct (as
    produced on the Population Overview page).

    demographics must be the full indicators table loaded by
    load_demographics() (processed/indicators/demographics.csv).
    """

    facility_type_cols = [
        "Childcare",
        "Health centers",
        "Long-term care and rehabilitation services",
        "Schools"
    ]

    demo = demographics.copy()

    demo["barangay"] = (
        demo["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ----------------------------------------------------
    # ACCESSIBILITY: overall facilities per 10k population
    # ----------------------------------------------------

    demo["facilities_per_10k"] = (
        demo["Total"]
        /
        demo["pop_census"]
        * 10000
    )

    # ----------------------------------------------------
    # ACCESSIBILITY: facility-type mix shares (the four
    # types with enough barangays present to carry signal)
    # ----------------------------------------------------

    facility_totals = demo[facility_type_cols].sum(axis=1)

    share_cols = []

    for col in facility_type_cols:

        share_col = f"share_{col.lower().replace(' ', '_')}"
        share_cols.append(share_col)

        demo[share_col] = np.where(
            facility_totals > 0,
            demo[col] / facility_totals,
            0
        )

    # ----------------------------------------------------
    # SOCIO-ECONOMIC: migrant workers per 1,000 population
    # (registry has a handful of barangays with no entry;
    # treated as 0 registered migrant workers, not missing)
    # ----------------------------------------------------

    demo["migrant_per_1000"] = (
        demo["migrant_workers_total"].fillna(0)
        /
        demo["pop_census"]
        * 1000
    )

    socioeconomic_cols = [
        "sex_ratio_m_per_100f",
        "disability_prevalence_rate_pct",
        "cbms_food_insecurity_prevalence_pct",
        "cbms_housing_inadequacy_index_pct",
        "migrant_per_1000"
    ]

    demo_features = demo[
        [
            "barangay",
            "facilities_per_10k"
        ]
        + share_cols
        + socioeconomic_cols
    ]

    out = barangay_df.copy()

    out["Barangay"] = (
        out["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    out = out.merge(
        demo_features,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    ).drop(columns=["barangay"], errors="ignore")

    new_numeric_cols = (
        ["facilities_per_10k"]
        + share_cols
        + socioeconomic_cols
    )

    out[new_numeric_cols] = out[new_numeric_cols].fillna(0)

    if feature_cols is None:
        feature_cols = [
            "population_density",
            "children_pct",
            "elderly_pct",
            "facilities_per_10k"
        ] + share_cols + socioeconomic_cols

    feature_cols = [
        c for c in feature_cols if c in out.columns
    ]

    return out, feature_cols



def run_barangay_clustering(
    df,
    feature_cols,
    n_clusters=4,
    random_state=0
):
    """
    Standardizes features and runs K-means, mirroring
    Section 1 of the Clustering Exploration notebook
    (sklearn StandardScaler + KMeans). Returns the
    dataframe with a "Cluster" column added (1-indexed,
    to match the original notebooks' cluster numbering)
    plus the scaled feature matrix, for profiling.
    """

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    work = df.copy()

    feat = (
        work[feature_cols]
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    scaler = StandardScaler()
    scaled = scaler.fit_transform(feat)

    km = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10
    ).fit(scaled)

    work["Cluster"] = km.labels_ + 1

    scaled_df = pd.DataFrame(
        scaled,
        columns=feature_cols,
        index=work.index
    )

    return work, scaled_df


CLUSTER_PALETTE = [
    "#7F47ED",   # primary purple
    "#055B52",   # secondary dark green
    "#682680",   # accent purple
    "#80AA31",   # secondary green
    "#A78BFA",   # light purple
    "#A6CFC1"    # secondary light green
]


def cluster_color(cluster_id):

    try:
        cluster_id = int(cluster_id)
        return CLUSTER_PALETTE[
            (cluster_id - 1) % len(CLUSTER_PALETTE)
        ]

    except (TypeError, ValueError):
        return "#DDD6FE"


# --------------------------------------------------
# CLIMATE RASTER RENDERING
# (converts a GeoTIFF in any CRS into an RGBA PNG +
# lat/lon bounding box, suitable for pydeck's
# BitmapLayer. Color ramps are applied client-side
# here rather than relying on the raster's own
# values, since pydeck has no native raster-colormap
# support — it only draws pre-rendered images.)
# --------------------------------------------------
import base64
import io


def _lerp_color(stops, t):
    """Linearly interpolate an RGB color from a list of
    (t, (r,g,b)) stops, for t in [0, 1]."""

    t = min(max(t, 0.0), 1.0)

    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]

        if t0 <= t <= t1:
            local_t = (t - t0) / (t1 - t0) if t1 > t0 else 0
            r = c0[0] + (c1[0] - c0[0]) * local_t
            g = c0[1] + (c1[1] - c0[1]) * local_t
            b = c0[2] + (c1[2] - c0[2]) * local_t
            return int(r), int(g), int(b)

    return stops[-1][1]


# Approximations of common matplotlib colormaps, as
# (t, (r,g,b)) stops, t in [0, 1]
COLORMAPS = {
    # YlOrRd — used for Land-Surface Temperature
    "YlOrRd": [
        (0.00, (255, 255, 178)),
        (0.25, (254, 204, 92)),
        (0.50, (253, 141, 60)),
        (0.75, (227, 26, 28)),
        (1.00, (128, 0, 38))
    ],
    # Greens — used for NDVI (vegetation)
    "Greens": [
        (0.00, (247, 252, 245)),
        (0.25, (199, 233, 192)),
        (0.50, (116, 196, 118)),
        (0.75, (35, 139, 69)),
        (1.00, (0, 68, 27))
    ],
    # Blues — used for flood inundation
    "Blues": [
        (0.00, (247, 251, 255)),
        (0.50, (107, 174, 214)),
        (1.00, (8, 48, 107))
    ],
    # Purples — used for barangay/district choropleths
    # on the Population Overview and District pages
    "Purples": [
        (0.00, (252, 251, 253)),
        (0.25, (218, 218, 235)),
        (0.50, (158, 154, 200)),
        (0.75, (106, 81, 163)),
        (1.00, (63, 0, 125))
    ]
}


def value_to_rgba(
    value,
    vmin,
    vmax,
    colormap="Purples",
    alpha=190
):
    """
    Maps a single numeric value to an [r, g, b, a] list using
    one of the COLORMAPS ramps, given a (vmin, vmax) range.

    Used for pydeck GeoJsonLayer choropleths (e.g. the
    Population Overview barangay map and District map), as a
    polygon-fill equivalent of Plotly's color_continuous_scale
    + cmin/cmax — vmin/vmax are expected to already be clipped
    (e.g. to the 5th-95th percentile) by the caller, the same
    way the Plotly version clips via update_coloraxes.
    """

    if vmax <= vmin or pd.isna(value):
        t = 0.0
    else:
        t = (value - vmin) / (vmax - vmin)

    r, g, b = _lerp_color(COLORMAPS[colormap], t)

    return [r, g, b, alpha]


def render_colormap_legend_html(
    colormap,
    vmin,
    vmax,
    unit="",
    label=None,
    n_stops=20
):
    """
    Builds a small HTML/CSS horizontal gradient bar for one of
    the COLORMAPS ramps, with vmin/vmax labels at each end —
    the same kind of color-scale legend shown on the static
    reference PNGs (Heatwaves.png, Flood_QC.png), recreated here
    as inline HTML so it can sit directly under a raster layer
    in the Streamlit UI (folium's rendered HTML and pydeck's
    BitmapLayer don't carry their own legend, so this fills that
    gap for continuous layers like Land-Surface Temperature and
    NDVI).

    n_stops controls how many color samples make up the CSS
    gradient — 20 is enough to look smooth without generating an
    excessively long style string.

    Returns a raw HTML string; pass it to st.markdown(...,
    unsafe_allow_html=True).
    """

    stops = COLORMAPS[colormap]

    gradient_stops = []

    for i in range(n_stops + 1):

        t = i / n_stops
        r, g, b = _lerp_color(stops, t)
        pct = t * 100

        gradient_stops.append(
            f"rgb({r},{g},{b}) {pct:.1f}%"
        )

    gradient_css = ", ".join(gradient_stops)

    label_html = (
        f'<div style="font-size:13px;font-weight:600;'
        f'margin-bottom:4px;">{label}</div>'
        if label else ""
    )

    vmin_display = 0.0 if round(vmin, 1) == 0 else vmin
    vmax_display = 0.0 if round(vmax, 1) == 0 else vmax

    return f"""
    <div style="margin-top:8px;margin-bottom:8px;">
        {label_html}
        <div style="
            width:100%;
            height:16px;
            border-radius:3px;
            background:linear-gradient(to right, {gradient_css});
            border:1px solid #999;
        "></div>
        <div style="
            display:flex;
            justify-content:space-between;
            font-size:12px;
            color:#444;
            margin-top:2px;
        ">
            <span>{vmin_display:.1f} {unit}</span>
            <span>{vmax_display:.1f} {unit}</span>
        </div>
    </div>
    """


def _render_raster_rgba(
    path,
    colormap="YlOrRd",
    clip_percentiles=(2, 98),
    opacity=180,
    binary=False,
    mask_geometry=None
):
    """
    Shared core for rendering a GeoTIFF (any CRS) into a colored
    RGBA array. Returns (rgba, bounds_latlon, vmin, vmax) where
    bounds_latlon is the flat (west, south, east, north) tuple in
    EPSG:4326. Used by both raster_to_bitmap_layer (pydeck) and
    raster_to_image_overlay (folium), which each reformat
    bounds_latlon differently for their respective map libraries.

    See raster_to_bitmap_layer's docstring for the meaning of
    binary and mask_geometry.
    """

    import rasterio
    from rasterio.warp import transform_bounds, transform_geom
    from rasterio.mask import mask as rio_mask

    with rasterio.open(path) as src:

        src_crs = src.crs
        nodata = src.nodata

        if mask_geometry is not None:

            # Reproject the mask boundary (EPSG:4326) into the
            # raster's native CRS before clipping, then read only
            # the masked window. rasterio.mask.mask sets pixels
            # outside the geometry to `nodata` (or NaN if no
            # nodata value is defined on the source).
            geom_native = transform_geom(
                "EPSG:4326",
                src_crs,
                mask_geometry.__geo_interface__
            )

            fill_value = (
                nodata
                if nodata is not None
                else np.nan
            )

            clipped, clipped_transform = rio_mask(
                src,
                [geom_native],
                crop=True,
                nodata=fill_value,
                filled=True
            )

            arr = clipped[0].astype("float64")

            if nodata is not None and not np.isnan(nodata):
                arr = np.where(arr == nodata, np.nan, arr)

            height, width = arr.shape

            bounds_native = rasterio.transform.array_bounds(
                height,
                width,
                clipped_transform
            )

            left, bottom, right, top = bounds_native

        else:

            arr = src.read(1).astype("float64")

            if nodata is not None and not np.isnan(nodata):
                arr = np.where(arr == nodata, np.nan, arr)

            bounds_native = src.bounds
            left, bottom, right, top = (
                bounds_native.left,
                bounds_native.bottom,
                bounds_native.right,
                bounds_native.top
            )

        bounds_latlon = transform_bounds(
            src_crs,
            "EPSG:4326",
            left,
            bottom,
            right,
            top
        )

    stops = COLORMAPS.get(colormap, COLORMAPS["YlOrRd"])

    if binary:

        vmin, vmax = 0, 1
        top_color = stops[-1][1]

        rgba = np.zeros(
            (arr.shape[0], arr.shape[1], 4),
            dtype="uint8"
        )

        mask = arr == 1

        rgba[..., 0] = np.where(mask, top_color[0], 0)
        rgba[..., 1] = np.where(mask, top_color[1], 0)
        rgba[..., 2] = np.where(mask, top_color[2], 0)
        rgba[..., 3] = np.where(mask, opacity, 0)

    else:

        finite = arr[np.isfinite(arr)]

        vmin, vmax = np.percentile(
            finite,
            clip_percentiles
        )

        if vmax <= vmin:
            vmax = vmin + 1e-6

        t = (arr - vmin) / (vmax - vmin)
        valid = np.isfinite(arr)

        # NaN positions get masked out via `valid` below anyway,
        # but np.nan_to_num avoids an "invalid cast" warning when
        # converting NaN to the int32 LUT index.
        t = np.nan_to_num(t, nan=0.0)
        t = np.clip(t, 0, 1)

        rgba = np.zeros(
            (arr.shape[0], arr.shape[1], 4),
            dtype="uint8"
        )

        # Vectorized colormap lookup via a fine-grained LUT,
        # rather than per-pixel Python interpolation (which
        # would be far too slow for million-pixel rasters)
        lut_size = 256

        lut = np.array(
            [_lerp_color(stops, i / (lut_size - 1)) for i in range(lut_size)],
            dtype="uint8"
        )

        idx = np.clip(
            (t * (lut_size - 1)).astype("int32"),
            0,
            lut_size - 1
        )

        rgba[..., 0] = np.where(valid, lut[idx, 0], 0)
        rgba[..., 1] = np.where(valid, lut[idx, 1], 0)
        rgba[..., 2] = np.where(valid, lut[idx, 2], 0)
        rgba[..., 3] = np.where(valid, opacity, 0)

    return rgba, bounds_latlon, vmin, vmax


@st.cache_data(show_spinner=False)
def raster_to_bitmap_layer(
    path,
    colormap="YlOrRd",
    clip_percentiles=(2, 98),
    opacity=180,
    binary=False,
    _mask_geometry=None
):
    """
    Reads a GeoTIFF (any CRS) and returns:
      (png_data_uri, bounds_corners, vmin, vmax)

    For use with pydeck's BitmapLayer:
        pdk.Layer("BitmapLayer", image=png_data_uri, bounds=bounds_corners, ...)

    png_data_uri   — a string already wrapped in literal quote
                      characters (e.g. '"data:image/png;base64,..."')
                      so pydeck's JSON layer renders it as a string
                      constant rather than trying to evaluate it as
                      a JS expression. Pass directly as the `image`
                      argument — do NOT wrap it in another layer of
                      quotes.
    bounds_corners — [[west, south], [west, north], [east, north],
                      [east, south]] in EPSG:4326 — the 4-corner
                      quadrilateral format pydeck's BitmapLayer
                      `bounds` expects (NOT a flat
                      [west, south, east, north] tuple).
    vmin, vmax     — the data range actually used for the color
                      scale (after percentile clipping), so a
                      legend can be drawn to match

    binary=True treats the raster as a 0/1 mask (e.g. flood
    extent) instead of a continuous color ramp: 0 is fully
    transparent, 1 is drawn as a flat color from the colormap's
    top stop.

    _mask_geometry — optional shapely geometry (e.g. the dissolved
    Quezon City boundary) in EPSG:4326. When provided, pixels
    outside this geometry are set to transparent/nodata before
    rendering, so the bitmap is cropped to the boundary rather
    than showing the raster's full rectangular extent. The
    raster's own bounds/resolution are unchanged — only pixel
    values outside the boundary are masked.

    The leading underscore on _mask_geometry tells Streamlit's
    @st.cache_data to skip hashing it (shapely geometries aren't
    hashable). This is safe as long as callers always pass the
    same boundary object for the same city/dataset — e.g. the
    cached return value of load_qc_boundary() — rather than a
    geometry that legitimately changes between calls with
    otherwise-identical arguments, which would silently return a
    stale cached bitmap.

    This function is itself cached: rendering a multi-million-
    pixel raster (reading, masking, building the colormap LUT,
    PNG-encoding, base64-encoding) is expensive enough that
    re-running it on every Streamlit widget interaction makes the
    page noticeably slow. Caching keys on (path, colormap,
    clip_percentiles, opacity, binary) — change any of those and
    the cache misses correctly.

    Requires rasterio + pyproj (both already dependencies of
    geopandas, used elsewhere in this app).
    """

    rgba, bounds_latlon, vmin, vmax = _render_raster_rgba(
        path,
        colormap=colormap,
        clip_percentiles=clip_percentiles,
        opacity=opacity,
        binary=binary,
        mask_geometry=_mask_geometry
    )

    img = Image.fromarray(rgba, mode="RGBA")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    png_b64 = base64.b64encode(png_bytes).decode()

    # pydeck serializes Layer properties through deck.gl's JSON
    # converter, which treats plain strings as JS expressions to
    # evaluate (this is how accessor strings like
    # "properties.fill_color" work). A literal string value must
    # itself be wrapped in quote characters, or the parser tries
    # to evaluate "data:image/png;base64,..." as an expression and
    # fails on the colon. See visgl/deck.gl issues #4977 and #5151.
    png_data_uri = (
        '"data:image/png;base64,' + png_b64 + '"'
    )

    west, south, east, north = bounds_latlon

    # pydeck's BitmapLayer expects `bounds` as a quadrilateral of
    # 4 [lng, lat] corners, not a flat [west, south, east, north]
    # tuple. Order matches the official pydeck BitmapLayer example.
    bounds_corners = [
        [west, south],
        [west, north],
        [east, north],
        [east, south]
    ]

    return png_data_uri, bounds_corners, vmin, vmax


@st.cache_data(show_spinner=False)
def raster_to_image_overlay(
    path,
    colormap="YlOrRd",
    clip_percentiles=(2, 98),
    opacity=180,
    binary=False,
    _mask_geometry=None
):
    """
    Reads a GeoTIFF (any CRS) and returns:
      (rgba_array, folium_bounds, vmin, vmax)

    For use with folium's ImageOverlay:
        folium.raster_layers.ImageOverlay(
            image=rgba_array, bounds=folium_bounds, origin="upper"
        ).add_to(m)

    rgba_array    — numpy uint8 array of shape (height, width, 4).
                     folium converts this to PNG internally — no
                     base64/quoting handling needed (unlike the
                     pydeck path in raster_to_bitmap_layer).
    folium_bounds — [[lat_min, lon_min], [lat_max, lon_max]] in
                     EPSG:4326 — folium's own bounds convention,
                     which is [lat, lon] order, NOT [lon, lat]
                     like pydeck uses. Don't mix the two up.
    vmin, vmax    — the data range actually used for the color
                     scale, for drawing a matching legend.

    See raster_to_bitmap_layer's docstring for the meaning of
    binary and _mask_geometry (including the caching/hashing
    note) — both behave identically here. This function is
    cached for the same reason: re-rendering a multi-million-
    pixel raster on every widget interaction is slow.
    """

    rgba, bounds_latlon, vmin, vmax = _render_raster_rgba(
        path,
        colormap=colormap,
        clip_percentiles=clip_percentiles,
        opacity=opacity,
        binary=binary,
        mask_geometry=_mask_geometry
    )

    west, south, east, north = bounds_latlon

    folium_bounds = [
        [south, west],
        [north, east]
    ]

    return rgba, folium_bounds, vmin, vmax
