import base64
import json
import io
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from PIL import Image
    

import rasterio
from rasterio.warp import transform_bounds, transform_geom
from rasterio.mask import mask as rio_mask
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from pyproj import Transformer

# --------------------------------------------------
# TRANSPARENT PLOTLY TEMPLATE
# (Plotly Express draws an opaque white plot/paper
# background by default, even with no plot_bgcolor set
# explicitly — that white rectangle would sit on top of
# the light-purple chart card background (see
# div[class*="st-key-qcd-chart-"] in both dashboards'
# <style> blocks) and hide it. Rather than add
# plot_bgcolor/paper_bgcolor to every individual px.*
# call (38+ call sites across the app), register one
# small template that only sets those two properties and
# make it the session default — every chart, current and
# future, then inherits a transparent background with no
# per-call changes.
#
# Built as a fresh go.layout.Template() rather than by
# reading/mutating pio.templates["plotly"] in place —
# Plotly's docs don't guarantee dict-style template
# assignment deep-copies, so mutating a template fetched
# from the registry risks silently corrupting the
# built-in "plotly" template for any other code that
# still expects its normal (opaque) styling. A from-
# scratch template avoids that question entirely: it
# only ever sets the two properties below, nothing is
# read from or written back into an existing template.
# --------------------------------------------------

_qcd_transparent_template = go.layout.Template()
_qcd_transparent_template.layout.paper_bgcolor = "rgba(0,0,0,0)"
_qcd_transparent_template.layout.plot_bgcolor = "rgba(0,0,0,0)"

pio.templates["qcd_transparent"] = _qcd_transparent_template

# "plotly+qcd_transparent" merges the two: Plotly Express
# keeps its normal default colors, fonts, and gridlines
# from "plotly", and qcd_transparent only overrides the
# two background properties on top.
pio.templates.default = "plotly+qcd_transparent"

# --------------------------------------------------
# DISTRICT NAMING CONSISTENCY
# (single source of truth for district labels,
# ensuring consistent formatting across all pages,
# charts, dropdowns, and maps — always "District 1"
# format, never just "1" in user-facing text)
# --------------------------------------------------

def format_district(district_val):
    """
    Formats a district value (int or str) consistently
    as 'District X' for all user-facing displays.
    Used across all pages to ensure consistency.

    Args:
        district_val: int, str, or pandas Series of district numbers

    Returns:
        Formatted string(s) as "District 1", "District 2", etc.
    """
    if isinstance(district_val, pd.Series):
        return "District " + district_val.astype(str)
    elif isinstance(district_val, (int, float)):
        return f"District {int(district_val)}"
    else:
        return f"District {str(district_val)}"

def extract_district_number(district_label):
    """
    Extracts numeric district from formatted label.
    Inverse of format_district().

    Args:
        district_label: str like "District 1" or just "1"

    Returns:
        int: district number
    """
    if isinstance(district_label, str):
        return int(district_label.replace("District ", "").strip())
    return int(district_label)

DISTRICT_COLORS_MAP = {
    1: "#055B52",   # green gradient — darkest
    2: "#257268",   # green gradient
    3: "#45897E",   # green gradient
    4: "#66A195",   # green gradient
    5: "#86B8AB",   # green gradient
    6: "#A6CFC1"    # green gradient — lightest
}

def format_district_list(districts):
    """
    Formats a list of district numbers for dropdowns/filters.

    Args:
        districts: list or array of district numbers

    Returns:
        list: ["All"] + ["District 1", "District 2", ...]
    """
    sorted_districts = sorted([int(d) for d in districts if pd.notna(d)])
    return ["All"] + [f"District {d}" for d in sorted_districts]

# --------------------------------------------------
# ACCESSIBILITY RATIO INDICATORS
# (facility-per-1,000 ratios from demographics_by_barangay.csv's
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
    },
    "All Care Facilities per 1,000 PWDs": {
        "facility_col": "Total",
        "pop_col": "pwd_registered",
        "ratio_col": "ratio_pwd_all"
    }
}

@st.cache_data
def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# --------------------------------------------------
# CHART PALETTE
# (single source of truth for chart colors, so every
# px.bar/line/pie/scatter call in the dashboard draws
# from the same purple→green family instead of Plotly's
# default rainbow palette. Order matters: series are
# assigned colors in this order, so the first category
# in a chart always gets the same purple, the second the
# same violet, etc., across different pages.
#
#   QCD_CATEGORICAL — for bar/pie/scatter series (3+ steps,
#                     purple through green, alternating
#                     light/dark so adjacent bars stay
#                     distinguishable)
#   QCD_SEQUENTIAL  — single-hue purple ramp, for ordered/
#                     magnitude charts with one series
#                     (e.g. a single bar chart ranked by
#                     value) where a sequential read makes
#                     more sense than categorical colors
#
# Risk/severity choropleth maps (flood exposure, priority
# scores) intentionally keep Plotly's built-in "Reds" /
# "Purples" continuous scales rather than this palette —
# red still means "high risk" on those, which is a more
# useful convention than forcing every chart to one family.
# --------------------------------------------------

QCD_CATEGORICAL = [
    "#4C1D95",  # deep purple
    "#80AA31",  # green
    "#7F47ED",  # core purple (brand)
    "#1A9E5C",  # mid green
    "#9478D3",  # light purple
    "#A6CFC1",  # light green
    "#C4B5FD",  # lightest purple
    "#055B52",  # deep green
]

QCD_SEQUENTIAL = [
    "#EEEDFE",
    "#C4B5FD",
    "#9478D3",
    "#7F47ED",
    "#643BAA",
    "#4C1D95",
]


# --------------------------------------------------
# KPI CARD
# (boxed replacement for st.metric — white surface,
# soft shadow, no border, purple label/value type to
# match the dashboard's existing #7F47ED system. The
# optional `polarity` arg draws a small static arrow
# next to the value to signal whether a high or low
# number is the "good" outcome for that metric, since
# the underlying data has no real prior-period value
# to diff against. This is a fixed visual cue, not a
# computed delta — it never changes value-to-value.
#
#   polarity="up_good"   -> green up arrow   (more is better)
#   polarity="down_good" -> green down arrow (less is better)
#   polarity=None         -> no arrow (text values, raw
#                             demographic counts, or metrics
#                             with no clear "better" direction)
#
# `caption`, if given, renders a small line below the value
# — used for the handful of KPIs that used to pass a third
# positional arg to st.metric() as a delta/sub-label (e.g.
# "1,234 est. residents") rather than an actual delta.
#
# `target` is whatever Streamlit column/container object
# .metric() used to be called on (e.g. k1, col2, st itself)
# — call as kpi_card(k1, "Facilities", f"{n:,}", "up_good")
# in place of k1.metric("Facilities", f"{n:,}").
# --------------------------------------------------

_KPI_ARROW = {
    "up_good": ("&#9650;", "#7ED957"),    # ▲ bright green, visible on purple card bg
    "down_good": ("&#9660;", "#7ED957"),  # ▼ bright green, visible on purple card bg
}

def kpi_card(target, label, value, polarity=None, caption=None):

    arrow_html = ""

    if polarity in _KPI_ARROW:

        glyph, color = _KPI_ARROW[polarity]

        arrow_html = (
            f'<span class="qcd-kpi-arrow" style="color:{color};">'
            f'{glyph}'
            f'</span>'
        )

    caption_html = ""

    if caption:

        caption_html = (
            f'<div class="qcd-kpi-caption">{caption}</div>'
        )

    # NOTE: this HTML is built as one unbroken string with no
    # leading whitespace on any line. Streamlit's st.markdown
    # runs unsafe_allow_html content through a Markdown parser
    # first — and Markdown treats 4+ spaces of leading indent
    # as a fenced code block, which prints the HTML as literal
    # text (e.g. a visible "</div>") instead of rendering it.
    # A previous version used an indented triple-quoted f-string
    # and hit exactly that bug. Do not reintroduce indentation
    # here, even for readability.
    html = (
        '<div class="qcd-kpi-card">'
        f'<div class="qcd-kpi-label">{label}</div>'
        '<div class="qcd-kpi-value-row">'
        f'<span class="qcd-kpi-value">{value}</span>'
        f'{arrow_html}'
        '</div>'
        f'{caption_html}'
        '</div>'
    )

    target.markdown(html, unsafe_allow_html=True)



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
        return "#C4B5FD"   # purple gradient — light

    elif "SUPERVISED NEIGHBORHOOD PLAY" in category:
        return "#E0D4FD"   # purple gradient — lightest (still visible on map)

    return "#C4B5FD"


# --------------------------------------------------
# SCHOOLS FUNCTIONS
# --------------------------------------------------
def school_color(category):
    """
    Returns color for a school based on its category (school type).
    Uses UN WOMEN Blue gradient from darkest (Preschool) to lightest (High school).
    """
    category = str(category).strip().lower()

    if "preschool" in category:
        return "#2E5090"  # darkest UN WOMEN blue
    elif "elementary" in category:
        return "#4472C4"  # UN WOMEN Blue (primary)
    elif "junior high" in category or "junior high school" in category:
        return "#6B8FD4"  # medium UN WOMEN blue
    elif "senior high" in category or "senior high school" in category:
        return "#8FA8E0"  # light UN WOMEN blue
    elif "high school" in category:
        return "#B5CBEE"  # lighter UN WOMEN blue
    elif "special education" in category:
        return "#D9E6F7"  # lightest UN WOMEN blue
    elif "private school" in category:
        return "#4C1D95"  # UN WOMEN purple, outside the grade-tier
                           # blue gradient since "Private school" isn't
                           # a grade level like the others — same
                           # purple used for "private/generic" facility
                           # markers elsewhere (e.g. Childcare Centers,
                           # Health Centers on Care Services Explorer)

    return "#4472C4"  # default to UN WOMEN Blue


def school_provider_type_color(provider_type):
    """
    Returns color for a school based on its provider type (Public/Private).
    Used for alternative color mapping when needed.
    """
    provider_type = str(provider_type).strip().upper()

    if "PUBLIC" in provider_type:
        return "#2E5090"   # dark UN WOMEN blue for public
    elif "PRIVATE" in provider_type:
        return "#B5CBEE"   # light UN WOMEN blue for private

    return "#4472C4"  # default UN WOMEN blue

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
# BUS STOPS FUNCTIONS (NEW - care_v6.csv)
# --------------------------------------------------
def bus_stops_color(category=None):
    """
    Color for Bus stops layer in Care Explorer.
    Uses a distinct orange/transit color from the palette
    to differentiate from care facilities.
    """
    return "#F97316"  # bright orange for transit/bus stops


# --------------------------------------------------
# ACTION OFFICES FUNCTIONS
# --------------------------------------------------

def district_color(district):
    """
    Returns the color for a given district.
    Uses the centralized DISTRICT_COLORS_MAP defined above.
    """
    try:
        district = int(district)
        return DISTRICT_COLORS_MAP.get(
            district,
            "#DDD6FE"
        )

    except:
        return "#DDD6FE"

# --------------------------------------------------
# SCHOOL TYPE COLOR MAPPING
# (New classification system for schools by type:
# Preschool, Elementary, Junior High, Senior High,
# High School, Special Education Program.
# Uses distinct blue gradient to avoid confusion
# with district colors.)
# --------------------------------------------------

SCHOOL_TYPE_COLORS_MAP = {
    "Preschool": "#2E5090",                          # darkest UN WOMEN blue
    "Elementary school": "#4472C4",                  # UN WOMEN Blue (primary)
    "Junior high school": "#6B8FD4",                 # medium UN WOMEN blue
    "Senior high school": "#8FA8E0",                 # light UN WOMEN blue
    "High school": "#B5CBEE",                        # lighter UN WOMEN blue
    "Special Education Program": "#D9E6F7",          # lightest UN WOMEN blue
    "Private school": "#4C1D95"                      # UN WOMEN purple, outside the grade-tier gradient
}

def school_type_color(school_type):
    """
    Returns the color for a given school type.
    Uses the centralized SCHOOL_TYPE_COLORS_MAP defined above.

    Args:
        school_type: str, the school type category

    Returns:
        str: hex color code
    """
    try:
        school_type = str(school_type).strip()
        return SCHOOL_TYPE_COLORS_MAP.get(school_type, "#E5E7EB")
    except:
        return "#E5E7EB"


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

    cat = str(cat).lower().strip()

    # Handle already-mapped values (if raw CSV is already in mapped form)
    if cat in ["national", "qc lgu", "pharmacy", "super health", "health center", "milk bank"]:
        return cat.title() if " " not in cat else ("QC LGU" if "qc" in cat else cat.title())

    # Handle raw unmapped values
    if "national" in cat:
        return "National"

    elif "lgu" in cat or "qc" in cat:
        return "QC LGU"

    elif "pharmacy" in cat:
        return "Pharmacy"

    elif "super" in cat:
        return "Super Health"

    elif "health" in cat and "center" in cat:
        return "Health Center"

    elif "milk" in cat:
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

    # df["category"] (and therefore the Category column derived
    # from it) is still a pandas `category` dtype at this point
    # — see load_data()'s category_cols loop, which casts
    # major_division/sub_division/category on the *full* care_v3
    # dataframe before it gets split by major_division. A
    # categorical column remembers every level that ever existed
    # in the unfiltered data, even after rows are filtered out,
    # so .value_counts()/px.pie() downstream would otherwise
    # report a 0-count slice for every OTHER division's category
    # (Schools, Childcare, etc.) in what should be a health-only
    # chart. Casting to plain string drops that stale level list.
    df["Category"] = df["Category"].astype(str)

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
    # Phase 1 Optimization: Address fallback logic
    # Use address_clean if available, fall back to address, then "Not available"
    # (future.no_silent_downcasting keeps fillna from attempting the
    # deprecated object-dtype downcast, which otherwise raises a
    # FutureWarning on every load; the column stays object dtype
    # either way.)
    with pd.option_context("future.no_silent_downcasting", True):
        if "address_clean" in df.columns and "address" in df.columns:
            df["Address"] = df["address_clean"].fillna(df["address"]).fillna("Not available")
        elif "address_clean" in df.columns:
            df["Address"] = df["address_clean"].fillna("Not available")
        elif "address" in df.columns:
            df["Address"] = df["address"].fillna("Not available")
        else:
            df["Address"] = "Not available"

    # Rename other columns
    rename_dict = {
        "name_original": "Name",
        "district": "District",
        "sub_division": "Sector",
        "category": "Category"
    }

    # Only rename columns that exist
    rename_dict = {k: v for k, v in rename_dict.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    # Category and Sector are still pandas `category` dtype here
    # — load_data() casts major_division/sub_division/category to
    # `category` dtype on the full care_v6 dataframe *before*
    # splitting it by major_division (see load_data() in this
    # file). A categorical column keeps every level that existed
    # in the unfiltered data even after rows are dropped, so any
    # .value_counts() / px.pie() built on this subset's Category
    # or Sector would silently include a 0-count slice for every
    # OTHER division's categories too (e.g. a Schools chart
    # listing Childcare/Health Center/District labels at 0%).
    # Casting to plain string drops that stale level list so each
    # facility type only ever reports the categories it actually
    # has rows for.
    for col in ("Category", "Sector"):
        if col in df.columns:
            df[col] = df[col].astype(str)

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

@st.cache_data(show_spinner=False)
def load_geo():
    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    bounds = gdf.total_bounds

    return gdf.__geo_interface__, bounds

@st.cache_data(show_spinner=False)
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

@st.cache_data(show_spinner=False)
def load_data():

    # Updated to load care_v6.csv with latest facility data
    care = pd.read_csv("processed/care_v6.csv")

    # Remove API facilities
    care = care[~care["data_source"].str.contains("Google API", na=False)]

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

    action_offices = care[
        care["major_division"]
        == "Quezon City satellite offices for services"
    ].copy()

    migration_centers = care[
        care["major_division"] == "Migration Resource Centers"
    ].copy()

    # Phase 1 Optimization: New Bus stops category for Care Explorer
    bus_stops = care[
        care["major_division"] == "Bus stops"
    ].copy()

    # --------------------------------------------------
    # CLEANING
    # --------------------------------------------------

    health_centers            = clean_health_centers(health_centers)
    childcare_centers         = clean_dataframe(childcare_centers)
    schools                   = clean_dataframe(schools)
    older_person_care         = clean_dataframe(older_person_care)
    long_term_care            = clean_dataframe(long_term_care)
    action_offices            = clean_dataframe(action_offices)
    action_offices["Name"]    = "District " + action_offices["District"].astype(int).astype(str)
    migration_centers         = clean_dataframe(migration_centers)
    bus_stops                 = clean_dataframe(bus_stops)

    return (
        childcare_centers,
        schools,
        health_centers,
        older_person_care,
        long_term_care,
        action_offices,
        migration_centers,
        bus_stops
    )

@st.cache_data(show_spinner=False)
def load_data_for_kpis():
    """
    Loads the consolidated barangay-level demographics table
    (processed/indicators/demographics_by_barangay.csv) and reshapes it into
    the same three dataframes this function has always returned
    — population_summary, population_sex, population_age — so
    every downstream page (Population Overview, Schools, Health
    Centers, Older Persons, Long-Term Care, Accessibility
    Analysis, Care Planning & Investment Priorities, Barangay
    Clusters) keeps working unchanged.

    demographics_by_barangay.csv replaces the four legacy files this used to
    read (population_summary.csv, population_2024_by_sex.csv,
    population_2024_by_age_group.csv,
    barangay_district_mapping.csv) with a single, richer,
    barangay-level source that also carries the new accessibility,
    disability, and CBMS socio-economic indicators (consumed by
    other parts of the dashboard via load_demographics() below).

    Unlike the legacy pipeline, demographics_by_barangay.csv already carries
    a clean integer "district" per barangay, so no separate
    barangay-to-district mapping/merge step is needed here.
    """
    # ==================================================
    # LOAD FILE
    # ==================================================

    demographics = pd.read_csv(
        "processed/indicators/demographics_by_barangay.csv"
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
            "age_60plus": "60+ (Older Persons)",
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


@st.cache_data(show_spinner=False)
def load_demographics():
    """
    Loads the full consolidated barangay-level indicators table
    (processed/indicators/demographics_by_barangay.csv) with all 87 columns
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

    demographics = pd.read_csv(
        "processed/indicators/demographics_by_barangay.csv"
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


@st.cache_data(show_spinner=False)
def load_demographics_by_district():
    """
    Loads district-level consolidated demographics table
    (processed/indicators/demographics_by_district.csv).

    Returns a DataFrame with one row per district (1-6) containing:
    - Area and population totals
    - Age/sex breakdowns (matches barangay columns for consistency)
    - Socioeconomic indicators (disability, food insecurity, housing)
    - Migrant worker counts
    - Pre-computed density and ratio metrics

    Use this alongside load_demographics() to provide district context
    when displaying barangay-level data, creating district comparisons,
    or prioritizing resources by district need.
    """

    demographics_district = pd.read_csv(
        "processed/indicators/demographics_by_district.csv"
    )

    # Normalize district to int (1-6) for consistency with barangay data
    demographics_district["district"] = (
        pd.to_numeric(demographics_district["district"], errors="coerce")
        .astype("Int64")
    )

    return demographics_district


@st.cache_data(show_spinner=False)
def load_climate_context():
    """
    Loads the city-wide (non-barangay) flood risk indicators
    from processed/indicators/climate.csv. These figures are
    WorldPop-based and only available at the Quezon City total
    level — there is no per-barangay breakdown — so they're
    meant for KPI cards/context on the Climate & Hazard Exposure
    page, not for a choropleth map.
    """

    climate = pd.read_csv(
        "processed/indicators/climate.csv"
    )

    return climate


@st.cache_data(show_spinner=False)
def load_demand_context():
    """
    Loads the two city/district-level administrative context
    tables that sit alongside demographics_by_barangay.csv:

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


@st.cache_data(show_spinner=False)
def load_domestic_workers():
    """
    Loads registered domestic worker counts (female/male/total)
    from processed/indicators/domestic_workers.csv — a separate
    source from demographics_by_barangay.csv, at barangay level with each
    row already tagged with its district.

    Returns (barangay_df, district_df):

    - barangay_df: one row per barangay, columns
      ["barangay", "barangay_key", "district", "domestic_workers_female",
      "domestic_workers_male", "domestic_workers_total"]. "barangay"
      is rewritten to match demographics_by_barangay.csv's spelling wherever a
      verified match exists (see RENAME MAP below), so this frame
      can be merged against demographics_by_barangay.csv or qc_barangays.geojson
      using the same barangay_key convention used everywhere else
      in this dashboard. barangay_key is the .strip().upper() form.
    - district_df: the same three count columns, summed up to
      one row per district (district as int 1-6, matching
      demographics_by_barangay.csv's "district" column).

    The source file has more rows (147) than demographics_by_barangay.csv has
    barangays (142) for two different reasons, both resolved here
    rather than left for every caller to rediscover:

    1. GENUINE DUPLICATE ROWS (same barangay, listed twice under
       different spellings) — both kept counts summed into one
       row, written under demographics_by_barangay.csv's spelling:
         - "N.S. AMORANTO" + "NS AMORANTO" (1 female + 1 male
           between them) -> "N. S. Amoranto (Gintong Silahis)"
       And two more pairs where one of the two rows is all-zero,
       so summing vs. simply dropping the zero row gives the same
       result either way — the all-zero row is dropped:
         - "AURORA" (0/0/0, District 4) is a duplicate of
           "DOÑA AURORA" (0/0/0) -> kept as "Doña Aurora"
         - "SANTO NIÑO" (0/0/0, District 4) is a duplicate of
           "STO. NIÑO" (24/0/24) -> kept as "Sto. Niño"
         - "KAUNLARAN" appears under both District 1 (0/0/0) and
           District 4 (0/0/0) — Quezon City has only one real
           Kaunlaran, in District 4 (confirmed against
           qc_barangays.geojson, demographics_by_barangay.csv, and the QC
           government's barangay directory) — the District 1 row
           is dropped.

    2. SPELLING/FORMAT VARIANTS of the same real barangay —
       rewritten to demographics_by_barangay.csv's spelling so the join
       works (see RENAME_MAP):
       roman-numeral vs. digit Escopa suffixes, "UP" vs. "U. P.",
       a missing parenthetical on Claro and Sto. Domingo, and a
       hyphen/casing difference on Balong-bato.

    Two source rows are NOT touched by either fix above, since
    they are not duplicates or misspellings but appear to be
    genuinely distinct from anything in demographics_by_barangay.csv:
    "SAN ISIDRO LABRADOR" (District 1) and "SAN ISIDRO GALAS"
    (District 4) are both real Quezon City barangays per public
    barangay directories, but demographics_by_barangay.csv has only a plain
    "San Isidro" (District 4) — which doesn't district-match
    "San Isidro Labrador" and isn't confirmed to be the same
    barangay as "San Isidro Galas" either. Both source rows are
    all-zero, so this has no effect on any total, but they are
    kept as their own (unmatched) rows rather than force-mapped
    to "San Isidro" — a barangay-geometry join will show them as
    unmatched/excluded rather than silently misattributing their
    (zero) count to the wrong polygon. "DILIMAN VILLAGE" (also
    all-zero) has no counterpart under any spelling and isn't a
    barangay on Quezon City's official District IV list either;
    it's dropped rather than guessed at.
    """

    dw = pd.read_csv(
        "processed/domestic_workers.csv"
    )

    dw = dw.rename(
        columns={
            "BARANGAY": "barangay",
            "DISTRICT": "district",
            "FEMALE": "domestic_workers_female",
            "MALE": "domestic_workers_male",
            "TOTAL": "domestic_workers_total"
        }
    )

    dw["barangay"] = dw["barangay"].astype(str).str.strip()
    dw["district"] = dw["district"].astype(str).str.strip()

    # --------------------------------------------------
    # DROP confirmed all-zero duplicate rows (see docstring
    # case 1 above — only the spurious half of each pair)
    # --------------------------------------------------

    drop_mask = (
        (
            (dw["barangay"].str.upper() == "AURORA")
            & (dw["district"] == "DISTRICT 4")
        )
        | (
            (dw["barangay"].str.upper() == "SANTO NIÑO")
            & (dw["district"] == "DISTRICT 4")
        )
        | (
            (dw["barangay"].str.upper() == "KAUNLARAN")
            & (dw["district"] != "DISTRICT 4")
        )
        | (dw["barangay"].str.upper() == "DILIMAN VILLAGE")
    )

    dw = dw.loc[~drop_mask]

    # --------------------------------------------------
    # MERGE the N.S./NS Amoranto split into one row
    # (the one genuine duplicate that isn't all-zero on
    # one side, so it's summed rather than dropped)
    # --------------------------------------------------

    amoranto_mask = dw["barangay"].isin(
        ["N.S. AMORANTO", "NS AMORANTO"]
    )

    if amoranto_mask.sum() > 1:

        merged_row = {
            "barangay": "N. S. Amoranto (Gintong Silahis)",
            "district": dw.loc[amoranto_mask, "district"].iloc[0],
            "domestic_workers_female":
                dw.loc[amoranto_mask, "domestic_workers_female"].sum(),
            "domestic_workers_male":
                dw.loc[amoranto_mask, "domestic_workers_male"].sum(),
            "domestic_workers_total":
                dw.loc[amoranto_mask, "domestic_workers_total"].sum()
        }

        dw = dw.loc[~amoranto_mask]
        dw = pd.concat(
            [dw, pd.DataFrame([merged_row])],
            ignore_index=True
        )

    # --------------------------------------------------
    # RENAME remaining spelling/format variants to match
    # demographics_by_barangay.csv exactly (see docstring case 2 above)
    # --------------------------------------------------

    RENAME_MAP = {
        "AURORA": "Doña Aurora",
        "SANTO NIÑO": "Sto. Niño",
        "ESCOPA I": "Escopa 1",
        "ESCOPA II": "Escopa 2",
        "ESCOPA III": "Escopa 3",
        "ESCOPA IV": "Escopa 4",
        "UP CAMPUS": "U. P. Campus",
        "UP VILLAGE": "U. P. Village",
        "CLARO": "Claro (Quirino 3-B)",
        "STO. DOMINGO": "Sto. Domingo (Matalahib)",
        "BALONG BATO": "Balong-bato"
    }

    dw["barangay"] = (
        dw["barangay"]
        .str.upper()
        .map(RENAME_MAP)
        .fillna(dw["barangay"])
    )

    # --------------------------------------------------
    # NORMALIZE DISTRICT TO INT (matches demographics_by_barangay.csv)
    # --------------------------------------------------

    dw["district"] = (
        dw["district"]
        .str.replace("DISTRICT ", "", regex=False)
        .astype(int)
    )

    dw["barangay_key"] = (
        dw["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    barangay_df = dw[
        [
            "barangay",
            "barangay_key",
            "district",
            "domestic_workers_female",
            "domestic_workers_male",
            "domestic_workers_total"
        ]
    ].reset_index(drop=True)

    district_df = (
        barangay_df
        .groupby("district", as_index=False)[
            [
                "domestic_workers_female",
                "domestic_workers_male",
                "domestic_workers_total"
            ]
        ]
        .sum()
    )

    return barangay_df, district_df


@st.cache_data(show_spinner=False)
def sample_raster_at_points(path, lats, lons):
    """
    Samples a single-band GeoTIFF (any CRS) at a list of point
    coordinates given in EPSG:4326 (lat/lon — the CRS every
    facility dataframe in this dashboard already uses).

    Returns a numpy array of raw raster values, one per point,
    in the same order as lats/lons. Points outside the raster's
    extent, or that land on a nodata pixel, come back as np.nan.

    This is built for exposure-flagging a few hundred facility
    points against a hazard layer (e.g. "is this health center
    in the flood zone?") — NOT for sampling a population raster
    pixel-by-pixel across millions of points, which would need a
    different (zonal-stats style) approach.

    Implementation notes:
    - All points are reprojected to the raster's native CRS in
      one batched pyproj transform, then read via rasterio's
      src.sample(), which streams values without loading the
      full raster into memory. This is the "supply-side"
      counterpart to raster_to_bitmap_layer/raster_to_image_overlay
      (which render the raster), and to the city-wide WorldPop
      population-in-flood-zone figures in climate.csv (which are
      the "demand-side" / population equivalent at a coarser,
      pre-aggregated level) — this function is what's new:
      per-facility point exposure.
    - lats/lons are accepted as tuples (not raw lists/Series) by
      the caller so this stays hashable for @st.cache_data; see
      flag_facilities_at_risk below, which handles that
      conversion.
    """

    with rasterio.open(path) as src:

        src_crs = src.crs
        nodata = src.nodata

        if src_crs.to_epsg() != 4326:

            transformer = Transformer.from_crs(
                "EPSG:4326",
                src_crs,
                always_xy=True
            )

            xs, ys = transformer.transform(
                np.array(lons),
                np.array(lats)
            )

        else:
            xs, ys = np.array(lons), np.array(lats)

        sampled = np.array(
            [
                val[0]
                for val in src.sample(zip(xs, ys))
            ],
            dtype="float64"
        )

        if nodata is not None and not np.isnan(nodata):
            sampled = np.where(sampled == nodata, np.nan, sampled)

        # Points that fall outside the raster's own bounding box
        # come back from rasterio as the band's fill value rather
        # than raising, so they're already covered by the nodata
        # check above in the normal case. Belt-and-suspenders
        # bounds check in case nodata is undefined on the source:
        left, bottom, right, top = src.bounds

        out_of_bounds = (
            (xs < left) | (xs > right) |
            (ys < bottom) | (ys > top)
        )

        sampled = np.where(out_of_bounds, np.nan, sampled)

    return sampled


@st.cache_data(show_spinner=False)
def flag_facilities_at_risk(
    df,
    raster_path="processed/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
    lat_col="latitude",
    lon_col="longitude",
    out_col="flood_risk"
):
    """
    Supply-side climate exposure flag: adds a boolean column to
    a facility dataframe marking which rows sit inside the given
    hazard raster's "at risk" footprint.

    Built around the flood layer (binary: 1 = 50cm inundation
    in a 100-yr event, see climate_layers config on the Climate
    & Hazard Exposure page) since that's the only *binary*
    raster — a clean yes/no per facility. The continuous layers
    (LST, NDVI) don't have a single natural risk threshold, so
    they're intentionally left out of this flag; if a heat
    threshold is wanted later, sample_raster_at_points already
    returns raw values, so a cutoff (e.g. "top decile LST") could
    be added as a second flag column without changing this
    function's signature.

    Rows with missing/invalid coordinates, or that fall outside
    the raster extent, get False rather than NaN — "not known to
    be at risk" — so the column stays a clean boolean usable
    directly for filtering/counting (df[out_col].sum()).

    Returns a copy of df with out_col added; does not mutate the
    input.
    """

    df = df.copy()

    valid = (
        df[lat_col].notna()
        & df[lon_col].notna()
    )

    df[out_col] = False

    if valid.any():

        sampled = sample_raster_at_points(
            raster_path,
            tuple(df.loc[valid, lat_col]),
            tuple(df.loc[valid, lon_col])
        )

        df.loc[valid, out_col] = (sampled == 1)

    return df


@st.cache_data(show_spinner=False)
def compute_barangay_flood_exposure(
    raster_path="processed/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
    barangay_path="processed/qc_barangays.geojson",
    name_col="barangay_name"
):
    """
    Demand-side, *land-area* counterpart to flag_facilities_at_risk
    above: for every barangay polygon, computes what share of its
    land area falls inside the binary flood-inundation mask
    (>50cm depth, 100-yr event).

    Returns a DataFrame with one row per barangay:
        [name_col, "flood_area_pct", "barangay_area_km2",
         "flood_area_km2"]

    IMPORTANT — this is an AREA metric, not a population metric.
    "60% flood_area_pct" means 60% of that barangay's land area
    is in the flood footprint; it says nothing on its own about
    how many people live on that land vs. the dry 40%. Where this
    is combined with pop_census to estimate an exposed headcount
    (see the Climate & Hazard Exposure page), that calculation
    assumes population is spread evenly across the barangay —
    a simplification made explicit wherever it's displayed, since
    real settlement patterns are essentially never uniform
    (e.g. dense housing on high ground, open low-lying fields).
    A true population-weighted figure would need a population
    raster (e.g. WorldPop) sampled the same way; none was
    available at the time this was written, so this area-based
    proxy is what's wired into the dashboard for now.

    Implementation: for each barangay geometry, rasterio.mask
    clips the flood raster to that polygon (same masking
    mechanism as raster_to_bitmap_layer/raster_to_image_overlay
    use for the whole-city boundary), then flood_area_pct is the
    clipped pixel count where the mask == 1, divided by total
    valid pixel count in that clip. Barangays are looped one at a
    time — a few hundred small clips against an already-binary
    raster — rather than vectorized, since rasterio.mask works
    geometry-by-geometry and this only runs once per app session
    thanks to @st.cache_data.
    """

    barangay_gdf = gpd.read_file(
        barangay_path,
        engine="pyogrio"
    )

    # Land area in km^2 from the polygon geometry itself (not
    # demographics_by_barangay.csv's area_km2) so this stays self-contained
    # and usable even if that column's CRS/precision differs —
    # reproject to a metric CRS (EPSG:3123, the same Philippine
    # projected CRS the climate rasters already use) purely for
    # an accurate area calculation, not for the raster clipping
    # below (which reprojects the geometry per-row instead).
    barangay_area_km2 = (
        barangay_gdf.geometry
        .to_crs("EPSG:3123")
        .area
        / 1_000_000
    )

    results = []

    with rasterio.open(raster_path) as src:

        src_crs = src.crs
        nodata = src.nodata

        for idx, row in barangay_gdf.iterrows():

            geom_native = transform_geom(
                "EPSG:4326",
                src_crs,
                row.geometry.__geo_interface__
            )

            try:

                clipped, _ = rio_mask(
                    src,
                    [geom_native],
                    crop=True,
                    nodata=(
                        nodata if nodata is not None else -9999
                    ),
                    filled=True
                )

                arr = clipped[0].astype("float64")

                fill_value = (
                    nodata if nodata is not None else -9999
                )

                valid = arr != fill_value

                total_valid = valid.sum()

                if total_valid > 0:
                    flood_pct = (
                        100
                        * (arr[valid] == 1).sum()
                        / total_valid
                    )
                else:
                    flood_pct = np.nan

            except ValueError:
                # rio_mask raises ValueError when the geometry
                # doesn't overlap the raster extent at all
                # (e.g. a barangay fully outside the flood
                # layer's coverage) — treat as 0% rather than
                # letting the whole computation fail.
                flood_pct = 0.0

            results.append({
                name_col: row[name_col],
                "flood_area_pct": flood_pct,
                "barangay_area_km2": barangay_area_km2.loc[idx]
            })

    result_df = pd.DataFrame(results)

    result_df["flood_area_km2"] = (
        result_df["barangay_area_km2"]
        * result_df["flood_area_pct"]
        / 100
    )

    return result_df


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
@st.cache_data(show_spinner=False)
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
        "Barangay", "0-5 (Early Childhood)", "60+ (Older Persons)"

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
        .reset_index(name="Older Persons-Serving Facilities")
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

    out["Older Persons-Serving Facilities"] = (
        out["Older Persons-Serving Facilities"].fillna(0)
    )

    # children per facility — np.nan when there are no
    # facilities, rather than infinity, so it reads cleanly
    # in tables/charts (mirrors the notebooks' np.where guard)
    out["Children per Facility"] = np.where(
        out["Child-Serving Facilities"] != 0,
        out["0-5 (Early Childhood)"] / out["Child-Serving Facilities"],
        np.nan
    )

    out["Older Persons per Facility"] = np.where(
        out["Older Persons-Serving Facilities"] != 0,
        out["60+ (Older Persons)"] / out["Older Persons-Serving Facilities"],
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
@st.cache_data(show_spinner=False)
def build_cluster_features(
    _barangay_df,
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
      to carry real signal; Older persons care, Action
      Offices, and Trainings are each present in well under
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
    load_demographics() (processed/indicators/demographics_by_barangay.csv).
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

    out = _barangay_df.copy()

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

def get_district_comparison(barangay_df, district_df, metric_col):
    """
    Compare a barangay's metric against its district average.

    Args:
        barangay_df: one row from demographics (barangay level)
        district_df: one row from demographics_district
        metric_col: column name to compare (e.g., "disability_prevalence_rate_pct")

    Returns:
        dict with keys: barangay_value, district_avg, difference, pct_difference
    """

    barangay_val = barangay_df[metric_col]
    district_val = district_df[metric_col]

    return {
        "barangay_value": barangay_val,
        "district_avg": district_val,
        "difference": barangay_val - district_val,
        "pct_difference": (
            ((barangay_val - district_val) / district_val * 100)
            if district_val != 0 else np.nan
        )
    }


@st.cache_data(show_spinner=False)
def run_barangay_clustering(
    _df,
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

    OPTIMIZATION: Cached to avoid recalculating clustering
    when page reruns. Reduced n_init from 10 to 3 for 3-5x
    faster convergence (diminishing returns after n_init=3).
    """

    work = _df.copy()

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
        n_init=3
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
    ],
    # Oranges — mirrors the Climate Layers page's population
    # choropleth (POP_COLOR_STOPS in app.py), so its legend can
    # use the same gradient-bar rendering as the other raster
    # legends on that page instead of discrete swatches. A warm
    # ramp is deliberate: that choropleth sits directly under
    # the flood layer's semi-transparent blue, and blue reads
    # far more clearly against an orange base (its complement)
    # than it did against the green tried first.
    "Oranges": [
        (0.00, (254, 237, 222)),
        (0.25, (253, 190, 133)),
        (0.50, (253, 141, 60)),
        (0.75, (230, 85, 13)),
        (1.00, (166, 54, 3))
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
        f'margin-bottom:4px;color:#1a1a1a;">{label}</div>'
        if label else ""
    )

    vmin_display = 0.0 if round(vmin, 1) == 0 else vmin
    vmax_display = 0.0 if round(vmax, 1) == 0 else vmax

    return f"""
    <div style="
        margin-top:8px;
        margin-bottom:8px;
        background:#ffffff;
        padding:8px 10px;
        border-radius:6px;
    ">
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
            color:#1a1a1a;
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
