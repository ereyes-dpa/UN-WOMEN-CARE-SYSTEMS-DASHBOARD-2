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
    "Health Centers per 1,000 People with Disabilities": {
        "facility_col": "Health centers",
        "pop_col": "pwd_registered",
        "ratio_col": "ratio_pwd_health"
    },
    "Long-Term Care & Rehabilitation per 1,000 People with Disabilities": {
        "facility_col": "Long-term care and rehabilitation services",
        "pop_col": "pwd_registered",
        "ratio_col": "ratio_pwd"
    },
    "All Care Facilities per 1,000 People with Disabilities": {
        "facility_col": "Total",
        "pop_col": "pwd_registered",
        "ratio_col": "ratio_pwd_all"
    },
    "Bus Stops per 1,000 People": {
        "facility_col": "Bus stops",
        "pop_col": "pop_census",
        "ratio_col": "ratio_bus_stops"
    },
    "Bus Stops per 1,000 Females": {
        "facility_col": "Bus stops",
        "pop_col": "pop_female",
        "ratio_col": "ratio_bus_stops_f"
    },
    "Bus Stops per 1,000 Males": {
        "facility_col": "Bus stops",
        "pop_col": "pop_male",
        "ratio_col": "ratio_bus_stops_m"
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
# UNMAPPED CATEGORY COLOR
# (Shared fallback for every category_color-style function below
# — childcare_color, school_color, ltc_color, opc_color,
# health_category_mapper. A brand-new raw category value that
# shows up in a source CSV (the client adds a new Category/type
# that didn't exist before) will not match any of the specific
# branches in these functions, and used to silently fall back to
# the same color as an existing, unrelated category — meaning a
# new type of facility looked like it belonged to whichever
# category happened to be the fallback, with no visual sign
# anything was missing. Returning this distinct gray instead means
# an unmapped category is immediately visible as "not yet styled"
# on the map, rather than silently miscounted as something else.
# Sidebar filters/legends still work for it either way, since
# those are derived from the data directly, not from this color
# mapping — only the *color* needs a person to add a real one.)
# --------------------------------------------------

UNMAPPED_CATEGORY_COLOR = "#9CA3AF"

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

    return UNMAPPED_CATEGORY_COLOR


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
    elif "parent" in category and "child" in category:
        return "#7C5ABF"  # lighter purple, distinct from "Private
                           # school" — also not a grade level

    return UNMAPPED_CATEGORY_COLOR


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
# OLDER PERSONS CARE FUNCTIONS
# (categories reassigned from the generic "Nursing care
# center"/"Bahay Aruga for Abandoned Elderly" split to the
# facility-type categories in the eldercare data review —
# see care_supply_facilities.csv. Exact-match dict, since several
# category names now share substrings like "Residential" and
# "Care Facility" that a keyword-contains check (the old opc_color
# logic) would confuse. All shades stay in the same green family
# used for "Older Persons" everywhere else in the app (e.g.
# DISTRICT_COLORS_MAP, the Care Services Explorer legend).
# --------------------------------------------------

OPC_CATEGORY_COLORS_MAP = {
    "Residential Care Facility": "#055B52",
    "Retirement and Assisted Living Facility": "#0B7A6E",
    "Government Residential Care Facility": "#128C7E",
    "Nursing care center": "#189A8C",
    "Home Healthcare Service Provider": "#1FA89A",
    "Residential and Assisted Living Facility": "#2FB8A8",
    "Home Care and Respite Care Provider": "#4AC3B4",
    "Assisted Living and Memory Care Facility": "#66CFC0",
    "Nursing home and Memory Care Facility": "#83DBCC",
    "Retirement and Residential Care Facility": "#9FE3D6",
    "Clergy Retirement Home": "#B8ECE1",
    "Residential Care Facility and Home Healthcare Service Provider": "#3E8914",
    "Community-based and Specialized Residential Care Home": "#A6CFC1",
    "Home care": "#5FCDBE",
}

def opc_color(category):

    category = str(category).strip()

    return OPC_CATEGORY_COLORS_MAP.get(category, UNMAPPED_CATEGORY_COLOR)


# --------------------------------------------------
# HEALTHCARE FUNCTIONS
# (HEALTH_CATEGORY_COLORS is the single source of truth for
# health-facility category colors — category_hex/marker_color/
# category_color all key off it directly by exact mapped-category
# name (see health_category_mapper below), rather than each
# re-implementing its own substring matching. That substring
# matching used to cause two bugs: "Health Centers with Pharmacy"
# would match the "HEALTH CENTER" branch before ever reaching
# "PHARMACY", and unmatched categories fell back to the same hex
# as "Super Health Centers", making them visually indistinguishable
# on the map. Generic, unqualified "Hospital" rows are all Google
# API-sourced (validated by the client against BPLD), with no
# LGU/National owner named — classed as Private Hospitals, kept
# separate from QC LGU-run and National Government Hospitals per
# the client's category spec — no catch-all "Other" bucket.)
# --------------------------------------------------

HEALTH_CATEGORY_COLORS = {
    "QC LGU-run Hospitals": "#4C1D95",
    "National Government Hospitals": "#643BAA",
    "Private Hospitals": "#8B5FBF",
    "Lying-in Clinics": "#B39DDB",
    "Super Health Centers": "#7C5ABF",
    "Health Centers": "#9478D3",
    "Health Centers with Pharmacy": "#AC97E8",
    "Milk Bank": "#C4B5FD",
    # No "Unmapped" entry here on purpose — this dict's keys feed
    # the sidebar filter and legend directly (see app.py), and the
    # client doesn't want a non-category option showing there. An
    # unrecognized raw category (see health_category_mapper below)
    # still gets a distinct, visibly-uncategorized color via the
    # UNMAPPED_CATEGORY_COLOR fallback in category_hex/marker_color
    # just below — it just isn't listed as a selectable category.
}

def category_hex(cat):
    return HEALTH_CATEGORY_COLORS.get(str(cat), UNMAPPED_CATEGORY_COLOR)

def marker_color(category):
    return HEALTH_CATEGORY_COLORS.get(str(category), UNMAPPED_CATEGORY_COLOR)

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

    # Generic therapy/therapeutic clinic or center (Google API-sourced,
    # no more specific therapy type named) — "THERAP" catches both
    # "Therapy center" and "Therapeutic clinic".
    elif "THERAP" in category:
        return "#DDD6FE"   # purple gradient — lightest, distinct from
                            # KABAHAGI's shade

    return UNMAPPED_CATEGORY_COLOR

def ltc_hex(category):
    return ltc_color(category)

# --------------------------------------------------
# BUS STOPS FUNCTIONS (NEW - care_supply_facilities.csv)
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


def category_color(cat):
    return hex_to_rgb(marker_color(cat))


def health_category_mapper(cat):
    """
    Maps a raw care_supply_facilities.csv health-facility `category` string to one
    of the keys in HEALTH_CATEGORY_COLORS. Order matters: "lying"
    is checked first so "LGU-run lying-in clinic" is classified as
    a lying-in clinic rather than an LGU hospital; generic
    "Hospital" (Google API-sourced, validated against BPLD, no
    LGU/National owner named) is classed as a Private Hospital, per
    the client's category spec — kept separate from QC LGU-run and
    National Government Hospitals.

    A raw category that doesn't match any branch below (a brand
    new Category value the client adds to the source data that
    isn't yet one of these known health-facility types) maps to
    "Unmapped" rather than silently being folded into "Health
    Centers" — keeps it out of every real tier's count, and its
    marker still gets a distinct gray via category_hex/
    marker_color's fallback, instead of visually passing as
    whatever tier it happened to land on. "Unmapped" isn't a key
    in HEALTH_CATEGORY_COLORS on purpose, so it never shows up as
    a selectable option in the sidebar filter or legend — this
    return value is only a signal, in code, that this function
    needs a new branch for it.
    """

    cat = str(cat).lower().strip()

    if "lying" in cat:
        return "Lying-in Clinics"

    elif "lgu" in cat and "hospital" in cat:
        return "QC LGU-run Hospitals"

    elif "national" in cat:
        return "National Government Hospitals"

    elif "hospital" in cat:
        return "Private Hospitals"

    elif "pharmacy" in cat:
        return "Health Centers with Pharmacy"

    elif "super" in cat:
        return "Super Health Centers"

    elif "health" in cat and "center" in cat:
        return "Health Centers"

    elif "milk" in cat:
        return "Milk Bank"

    return "Unmapped"


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
    # major_division/sub_division/category on the *full* care_supply_facilities
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

    # No Provider Type (Public/Private) source data exists for
    # administrative-source health centers, so Sector is real NaN
    # there (not the string "nan" or "Not available") so popups can
    # show a "Provider Type: Not available" fallback consistently.
    # Google-sourced rows already have sub_division defaulted to
    # "Private" upstream in load_data() — carried through here
    # rather than overwritten.
    df["Sector"] = df["sub_division"] if "sub_division" in df.columns else pd.NA

    return df

# --------------------------------------------------
# OVERLAPPING MARKER SPREAD
# (a handful of facilities sit close enough together — same
# building, same small complex — that their map markers render
# on top of each other at city-wide zoom, e.g. two eldercare
# facilities ~12m apart looked like one dot and undercounted the
# visible total by one. This nudges each point in a tight cluster
# out into a small circle around the cluster's own center, just
# far enough apart to render as distinct markers, without moving
# any point far enough to affect flood-zone sampling or any other
# distance-based calculation that reads these coordinates.)
# --------------------------------------------------

def spread_overlapping_points(
    df,
    lat_col="latitude",
    lon_col="longitude",
    min_distance_m=15,
    spread_radius_m=12
):
    """
    Returns a copy of df with lat/lon nudged apart for any group
    of rows within min_distance_m of each other (great-circle,
    approximated via a flat-earth degrees-to-meters conversion —
    fine at this scale, city-sized distances). Groups are found
    by a simple union-find over all pairwise distances, so chains
    of 3+ mutually-close points are spread as one cluster rather
    than only fixing the closest pair.

    Points in a cluster are placed evenly around a circle of
    spread_radius_m centered on the cluster's original centroid,
    so each one moves only a few meters — well under the
    resolution of anything downstream (raster sampling, ratio
    calculations) that also reads these columns.
    """

    n = len(df)

    if n < 2:
        return df

    lat = df[lat_col].to_numpy(dtype=float)
    lon = df[lon_col].to_numpy(dtype=float)

    # Degrees-per-meter at this latitude (roughly constant across
    # Quezon City's small extent, so one reference latitude is fine).
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * np.cos(np.radians(np.nanmean(lat)))

    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(n):
        for j in range(i + 1, n):
            dy = (lat[i] - lat[j]) * meters_per_deg_lat
            dx = (lon[i] - lon[j]) * meters_per_deg_lon
            if (dx * dx + dy * dy) ** 0.5 < min_distance_m:
                union(i, j)

    clusters = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)

    new_lat = lat.copy()
    new_lon = lon.copy()

    for members in clusters.values():

        if len(members) < 2:
            continue

        center_lat = np.nanmean(lat[members])
        center_lon = np.nanmean(lon[members])

        for k, idx in enumerate(members):

            angle = 2 * np.pi * k / len(members)

            new_lat[idx] = (
                center_lat
                + (spread_radius_m * np.sin(angle)) / meters_per_deg_lat
            )
            new_lon[idx] = (
                center_lon
                + (spread_radius_m * np.cos(angle)) / meters_per_deg_lon
            )

    result = df.copy()
    result[lat_col] = new_lat
    result[lon_col] = new_lon

    return result

def clean_dataframe(df, require_coordinates=True):
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
    # `category` dtype on the full care_supply_facilities dataframe *before*
    # splitting it by major_division (see load_data() in this
    # file). A categorical column keeps every level that existed
    # in the unfiltered data even after rows are dropped, so any
    # .value_counts() / px.pie() built on this subset's Category
    # or Sector would silently include a 0-count slice for every
    # OTHER division's categories too (e.g. a Schools chart
    # listing Childcare/Health Center/District labels at 0%).
    # Casting to plain string drops that stale level list so each
    # facility type only ever reports the categories it actually
    # has rows for. Done via .where() rather than a plain
    # .astype(str) so genuinely-missing values stay real NaN
    # instead of becoming the literal string "nan" — a previous
    # version used astype(str) directly, which made pd.notna()
    # checks downstream (e.g. the Sector/Provider Type line in
    # facility popups) always true and printed "Sector: nan" for
    # every facility with no Sector value (Bus Stops, Action
    # Offices, Migration Resource Centers, and any Schools/LTC/OPC
    # row missing one).
    for col in ("Category", "Sector"):
        if col in df.columns:
            df[col] = df[col].astype(str).where(df[col].notna())

    # Skippable for callers that need every record regardless of
    # whether it can be plotted (e.g. KPI/count tables), since
    # barangay/district assignment doesn't depend on having
    # coordinates — only map rendering does.
    if require_coordinates:
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
        "processed/reference/qc_barangays.geojson",
        engine="pyogrio"
    )

    bounds = gdf.total_bounds

    return gdf.__geo_interface__, bounds

@st.cache_data(show_spinner=False)
def load_geo_explorer():

    gdf = gpd.read_file(
        "processed/reference/qc_barangays.geojson",
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
        "processed/reference/qc_barangays.geojson",
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
def compute_bus_stop_counts_by_barangay(bus_stops):
    """
    Bus stop counts per barangay. As of care_supply_facilities.csv's original
    version, bus stops carried no barangay or district at all —
    every column was blank except name, coordinates,
    frequency/route info, and source — so barangay was assigned
    via a point-in-polygon spatial join against
    qc_barangays.geojson, the same boundary file every other
    barangay-level figure in this dashboard uses.

    Prefers a real "barangay" value where care_supply_facilities.csv has one
    (rows a human has actually assigned), and only spatially joins
    the rest — so once care_supply_facilities.csv is updated with real barangay
    assignments for bus stops, this automatically stops guessing
    from coordinates for whichever rows now have a real answer.

    Takes any dataframe with "longitude"/"latitude" columns (and
    optionally "barangay") — the raw care_supply_facilities.csv rows filtered to
    major_division == "Bus stops" work directly, no cleaning
    /renaming required.

    Returns one row per barangay with a "Bus stops" count column,
    ready to left-merge into a demographics_by_barangay.csv-shaped
    dataframe — see ACCESSIBILITY_RATIO_INDICATORS's "Bus Stops
    per 1,000..." entries, which read the resulting column through
    the same facility_col/pop_col ratio logic every other
    indicator already uses, rather than needing their own special
    -cased formula.

    Bus stops with no real barangay AND no coordinate match to any
    barangay polygon are dropped rather than guessed at, so this
    can slightly undercount relative to the true total — acceptable
    for a per-1,000-population ratio at barangay scale.
    """

    has_barangay = (
        "barangay" in bus_stops.columns
        and bus_stops["barangay"].notna()
    )

    assigned = bus_stops[has_barangay].copy() if "barangay" in bus_stops.columns else bus_stops.iloc[0:0]
    unassigned = bus_stops[~has_barangay] if "barangay" in bus_stops.columns else bus_stops

    if len(assigned):
        assigned["barangay"] = normalize_barangay_names(assigned["barangay"])

    if len(unassigned):

        barangay_gdf = gpd.read_file(
            "processed/reference/qc_barangays.geojson",
            engine="pyogrio"
        )[["barangay_name", "geometry"]]

        points = gpd.GeoDataFrame(
            {"_id": range(len(unassigned))},
            geometry=gpd.points_from_xy(
                unassigned["longitude"],
                unassigned["latitude"]
            ),
            crs="EPSG:4326"
        )

        joined = gpd.sjoin(
            points,
            barangay_gdf,
            how="left",
            predicate="within"
        )

        spatially_assigned = (
            joined
            .dropna(subset=["barangay_name"])
            ["barangay_name"]
            .rename("barangay")
        )

    else:
        spatially_assigned = pd.Series([], name="barangay", dtype=object)

    all_barangays = pd.concat(
        [assigned["barangay"], spatially_assigned],
        ignore_index=True
    )

    return (
        all_barangays
        .value_counts()
        .rename_axis("barangay")
        .reset_index(name="Bus stops")
    )


@st.cache_data(show_spinner=False)
def load_all_schools():
    """
    Every school in care_supply_facilities.csv, regardless of whether
    it has mappable coordinates — unlike load_data()'s `schools`
    dataframe, which drops any row missing latitude/longitude
    before it's ever split out by division (needed for map
    rendering, but not for barangay/district-level counting, since
    a school's barangay assignment doesn't depend on having
    coordinates).

    Use this for KPI cards, counts, and tables on the Schools page
    that should reflect every school on file, not just the subset
    with plottable coordinates. Still one row per grade level a
    school offers — deduplicate by (barangay, "Name") for counts of
    physical schools, same as compute_facility_counts_by_barangay().
    """

    care = pd.read_csv("processed/editable/care_supply_facilities.csv")

    schools = care[
        care["major_division"] == "Schools"
    ].copy()

    return clean_dataframe(schools, require_coordinates=False)


@st.cache_data(show_spinner=False)
def load_data():

    # Updated to load care_supply_facilities.csv with latest facility data
    care = pd.read_csv("processed/editable/care_supply_facilities.csv")

    # The source file now records the QC Migrants Resource Center row
    # as major_division "Trainings" / category "QC Migrants Resource
    # Center" instead of its own "Migration Resource Centers"
    # division. Normalized back to the original division here, right
    # after reading, so every downstream filter in this file and in
    # app.py that looks for "Migration Resource Centers" keeps working
    # unchanged.
    is_migration_center = (
        (care["major_division"] == "Trainings")
        & (care["category"] == "QC Migrants Resource Center")
    )
    care.loc[is_migration_center, "major_division"] = "Migration Resource Centers"

    # data_source only distinguishes "Administrative data" from
    # "Google API" in the raw file — whether a Google-sourced row has
    # actually been field-validated lives instead in source_reference.
    # Two formats seen so far: the original file spelled this out as
    # the substring "Google API - Validated"; a later file shortened
    # it to source_reference being exactly "Google API" (as opposed
    # to "For Validation") — same 58-row set both times, just a
    # shorter label. Checking both keeps this working regardless of
    # which spelling shows up in a given data drop, so the rest of
    # the app can filter and label by validation status directly
    # from data_source.
    is_google = care["data_source"] == "Google API"
    _source_ref = care["source_reference"].astype(str).str.strip()
    is_validated = (
        _source_ref.str.contains("Google API - Validated", na=False)
        | (_source_ref == "Google API")
    )
    care.loc[is_google & is_validated, "data_source"] = "Google API - Validated"
    care.loc[is_google & ~is_validated, "data_source"] = "Google API - For Validation"

    # district is Roman numerals ("I".."VI") for a large share of
    # rows now, mixed with plain integers for the rest.
    # pd.to_numeric() can't parse a Roman numeral, so it silently
    # became NaN downstream — as of the file that surfaced this,
    # 166 of 182 Long-Term Care rows and roughly a third of
    # Childcare/Schools rows lost their district entirely, which
    # crashes any .astype(int) on the column and breaks every
    # district-based filter/color for those rows. Converted to
    # plain integers here before that numeric parsing ever runs.
    ROMAN_TO_DISTRICT = {
        "I": "1", "II": "2", "III": "3",
        "IV": "4", "V": "5", "VI": "6",
    }
    care["district"] = (
        care["district"].astype(str).str.strip().str.upper()
        .replace(ROMAN_TO_DISTRICT)
    )

    # Google-sourced facilities essentially never carry a Public/Private
    # sub_division (they're discovered independently of the official
    # public/private registries that tag the administrative rows) —
    # default them to "Private", since a facility findable only via
    # Google Maps and not an official public-sector roster is, in
    # practice, privately run. Applies across all facility types.
    is_google_sourced = (
        care["sub_division"].isna()
        & (care["data_source"].isin(
            ["Google API - Validated", "Google API - For Validation"]
        ))
    )
    care.loc[is_google_sourced, "sub_division"] = "Private"

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
    action_offices             = clean_dataframe(action_offices)
    action_offices["Name"]     = (
        "District "
        + action_offices["District"].astype(int).astype(str)
        + " Action Office"
    )
    action_offices["Category"] = action_offices["Name"]
    # All District Action Offices keep the same posted hours
    # regardless of what care_supply_facilities.csv has on file for this row.
    action_offices["open_hours"]  = "8:00 AM"
    action_offices["close_hours"] = "5:00 PM"

    migration_centers              = clean_dataframe(migration_centers)
    migration_centers["Name"]      = "QC Migrants Resource Center"
    # Category was already correctly-cased in the raw data (Name
    # wasn't — clean_dataframe()'s str.title() turns "QC" into
    # "Qc"), so it's left alone rather than reset from Name here.
    migration_centers["Sector"]    = "Public"
    migration_centers["open_hours"]  = "8:00 AM"
    migration_centers["close_hours"] = "5:00 PM"

    bus_stops                 = clean_dataframe(bus_stops)

    # Spread markers that sit close enough together (same building/
    # complex) to render as one dot on the map — see
    # spread_overlapping_points's docstring. Skipped for
    # action_offices (one per district, positions are already
    # representative) and bus_stops (many genuinely sit within a
    # few meters of each other at the same intersection/stop).
    childcare_centers  = spread_overlapping_points(childcare_centers)
    schools            = spread_overlapping_points(schools)
    health_centers     = spread_overlapping_points(health_centers)
    older_person_care  = spread_overlapping_points(older_person_care)
    long_term_care     = spread_overlapping_points(long_term_care)
    migration_centers  = spread_overlapping_points(migration_centers)

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
    (processed/editable/demographics_by_barangay.csv) and reshapes it into
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
        "processed/editable/demographics_by_barangay.csv"
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


# Major_division values that count as a "care facility" for
# demand/accessibility purposes, and the demographics column name
# each rolls up into. Bus stops is deliberately excluded here — it
# has no barangay in care_supply_facilities.csv at all and is handled separately
# by compute_bus_stop_counts_by_barangay's spatial join — and
# Migration Resource Centers is excluded because it's a single
# citywide facility, not something meaningfully rated per-barangay.
FACILITY_COUNT_DIVISIONS = [
    "Childcare",
    "Health centers",
    "Long-term care and rehabilitation services",
    "Older persons care",
    "Quezon City satellite offices for services",
    "Schools",
]


# Bridges barangay-name spellings in care_supply_facilities.csv that
# don't match qc_barangays.geojson's canonical spelling even after
# case-insensitive comparison — abbreviations/missing punctuation,
# not just casing. Keys are UPPERCASE for lookup convenience.
BARANGAY_NAME_ALIASES = {
    "STO. DOMINGO": "Sto. Domingo (Matalahib)",
    "STO DOMINGO": "Sto. Domingo (Matalahib)",
    "UP CAMPUS": "U. P. Campus",
    "UP VILLAGE": "U. P. Village",
    "SIENA": "Sienna",
    "QUIRINO 2A": "Quirino 2-A",
    "QUIRINO 2B": "Quirino 2-B",
    "QUIRINO 2C": "Quirino 2-C",
    "QUIRINO 3A": "Quirino 3-A",
}


@st.cache_data(show_spinner=False)
def normalize_barangay_names(barangay_series):
    """
    Maps a Series of raw barangay strings to qc_barangays.geojson's
    canonical spelling wherever possible, so a groupby/merge on
    "barangay" doesn't silently drop rows whose casing or minor
    spelling differs from the canonical form (e.g. "SACRED HEART" /
    "STO. DOMINGO" from care_supply_facilities.csv's administrative
    -data rows vs. "Sacred Heart" / "Sto. Domingo (Matalahib)" in
    demographics_by_barangay.csv and the boundary file). Verified
    necessary: as of the file that surfaced this, 302 of 2292
    facility rows matched their canonical barangay only after
    uppercasing both sides, and a further ~18 needed the alias map
    above (abbreviations, not just casing) — without this, those
    rows' facility counts silently zero out in every ratio and KPI
    that depends on them.

    Values with no match at all (including genuinely blank barangay)
    are left as-is; a normal groupby/merge on "barangay" will then
    correctly exclude them rather than mis-assign them.
    """

    barangay_gdf = gpd.read_file(
        "processed/reference/qc_barangays.geojson",
        engine="pyogrio"
    )[["barangay_name"]]

    canonical_by_upper = {
        name.strip().upper(): name.strip()
        for name in barangay_gdf["barangay_name"]
    }

    def _normalize(raw):
        if pd.isna(raw):
            return raw
        cleaned = str(raw).strip()
        upper = cleaned.upper()
        if upper in canonical_by_upper:
            return canonical_by_upper[upper]
        if upper in BARANGAY_NAME_ALIASES:
            return BARANGAY_NAME_ALIASES[upper]
        return cleaned

    return barangay_series.map(_normalize)


@st.cache_data(show_spinner=False)
def compute_facility_counts_by_barangay(care):
    """
    Facility counts per barangay, live from care_supply_facilities.csv, replacing
    the Childcare/Health centers/etc. columns that used to be
    baked into demographics_by_barangay.csv by hand.

    Grouped from care_supply_facilities.csv's own "barangay" column
    (normalized via normalize_barangay_names() first — see that
    function's docstring) directly — NOT from the map's
    lat/lon-filtered dataframes (see functions.py's
    clean_dataframe/spread_overlapping_points) — since a facility's
    barangay assignment doesn't depend on whether it has mappable
    coordinates: e.g. 75/514 Childcare rows lack lat/lon but still
    have a real barangay value, and would be undercounted here if
    coordinate-filtered rows were used instead.

    "Trainings" has no corresponding major_division in care_supply_facilities.csv
    at all (nothing has ever mapped to it) and is kept at a fixed
    0 for schema stability with any code still expecting the
    column. "PWD care" — a facility-count column that existed in a
    previous version of demographics_by_barangay.csv — has been
    dropped entirely: it doesn't correspond to any
    ACCESSIBILITY_RATIO_INDICATORS entry and neither its source
    nor its definition could be identified, so rather than compute
    a misleading zero it's simply not reproduced here.

    "Total" is the row-sum of the other facility columns (verified
    against the old baked-in values to match exactly) — it does
    NOT include Bus Stops, consistent with that historical
    behavior.

    Schools rows are deduplicated by (barangay, name_original)
    before counting — one physical school is listed as a separate
    row per grade level it offers (e.g. a school with a Preschool,
    Elementary, and Junior High program appears as 3 rows, all
    sharing the same name and location), so counting rows directly
    would count that one school 3 times. Verified this key is safe
    for schools specifically: only 1 of 683 deduplicated school
    groups has an inconsistent address across its rows. Other
    facility types are not deduplicated — none show this
    one-row-per-category pattern (their row counts already match
    their number of distinct name+barangay combinations almost
    exactly).
    """

    care_for_counts = care.copy()
    care_for_counts["barangay"] = normalize_barangay_names(
        care_for_counts["barangay"]
    )

    is_school = care_for_counts["major_division"] == "Schools"
    schools_deduped = care_for_counts[is_school].drop_duplicates(
        subset=["barangay", "name_original"]
    )
    care_for_counts = pd.concat(
        [care_for_counts[~is_school], schools_deduped]
    )

    counts = (
        care_for_counts[care_for_counts["major_division"].isin(FACILITY_COUNT_DIVISIONS)]
        .groupby(["barangay", "major_division"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=FACILITY_COUNT_DIVISIONS, fill_value=0)
    )

    counts["Trainings"] = 0
    counts["Total"] = counts.sum(axis=1)

    counts = counts.reset_index()

    bus_stop_rows = care[care["major_division"] == "Bus stops"]
    bus_counts = compute_bus_stop_counts_by_barangay(bus_stop_rows)

    counts = counts.merge(bus_counts, on="barangay", how="left")
    counts["Bus stops"] = counts["Bus stops"].fillna(0)

    return counts


@st.cache_data(show_spinner=False)
def compute_pwd_facility_counts_by_barangay(care):
    """
    Facilities considered PWD-relevant care, per barangay. Two rules:

    1. Long-term care and rehabilitation services categories whose
       name contains "center" but not "clinic" — the client's own
       definition, on the reasoning that a "clinic" reads as
       health-related rather than disability-support-specific,
       while a named "center" reads as the latter. Verified against
       the current category list: this matches "Psychiatric
       rehabilitation center", "Therapy center", and "Quezon City
       Kabahagi Center For Children With Disabilitites" — and
       excludes every "* clinic" and "* school" category.

    2. Schools rows categorized "Special Education Program" —
       included explicitly since it's a different major_division
       and wouldn't be caught by rule 1.

    Used to populate "PWD Facilities" in load_demographics() (and,
    from there, the Disability Priority Score on the Care Planning
    page, which previously had no disability-facility count at all
    and treated every barangay as equally 0).
    """

    care = care.copy()
    care["barangay"] = normalize_barangay_names(care["barangay"])

    category_lower = care["category"].astype(str).str.lower()

    is_ltc_center = (
        (care["major_division"] == "Long-term care and rehabilitation services")
        & category_lower.str.contains("center", na=False)
        & ~category_lower.str.contains("clinic", na=False)
    )
    is_sped = (
        (care["major_division"] == "Schools")
        & (care["category"] == "Special Education Program")
    )

    pwd_rows = care[is_ltc_center | is_sped]

    return (
        pwd_rows
        .groupby("barangay")
        .size()
        .reset_index(name="PWD Facilities")
    )


@st.cache_data(show_spinner=False)
def compute_childcare_facility_counts_by_barangay(care):
    """
    Facilities considered childcare-relevant, per barangay -- i.e.
    facilities that actually serve the 0-5 population the Childcare
    Priority Score's demand side (age_0_5) is measuring against. Two
    rules, the same shape as compute_pwd_facility_counts_by_barangay
    above:

    1. Every row in the "Childcare" major_division (Child Development
       Centers/Supervised Play, Child Learning Centers, Day Care
       Centers) -- all of it is 0-5-relevant by definition.

    2. Schools rows categorized "Preschool" specifically -- the
       school-based equivalent serving the same age range.

    This replaces the old childcare_facility_cols = ["Childcare",
    "Schools"] in app.py's Care Planning page, which summed the
    ENTIRE Schools major_division -- Elementary, Junior High, Senior
    High, Special Education Program included -- into a count meant to
    represent capacity for 0-5-year-olds. A barangay with several
    large high schools but no preschools looked well-supplied for
    childcare under that count even though none of those schools
    enroll a single child in the actual demand bracket.

    No dedup-by-name needed here the way compute_facility_counts_by_
    barangay dedups Schools rows before counting them as "Total"
    facilities: that dedup exists because one physical school can
    have a Preschool row, an Elementary row, a Junior High row, etc.,
    and counting all of a school's rows would count that one school
    several times. Filtering to category == "Preschool" already keeps
    at most one row per school per address, so no further dedup is
    needed.
    """

    care = care.copy()
    care["barangay"] = normalize_barangay_names(care["barangay"])

    is_childcare_division = care["major_division"] == "Childcare"
    is_preschool = (
        (care["major_division"] == "Schools")
        & (care["category"] == "Preschool")
    )

    childcare_rows = care[is_childcare_division | is_preschool]

    return (
        childcare_rows
        .groupby("barangay")
        .size()
        .reset_index(name="Childcare-Relevant Facilities")
    )


@st.cache_data(show_spinner=False)
def compute_facility_ratios(demographics, facility_counts):
    """
    Merges live facility counts into a demographics_by_barangay
    -shaped dataframe and computes every ratio_* column defined by
    ACCESSIBILITY_RATIO_INDICATORS — the same facility_col/pop_col
    pairs already used to build the accessibility-ratio dropdown,
    reused here as the single source of truth for the formula
    rather than duplicating "facility / population * 1000" by
    hand. Verified against the old baked-in ratio_* columns before
    this replaced them: exact match (max diff 0.0) on every
    formula, across every barangay except one with a known,
    already-flagged source-data issue (Veterans Village).
    """

    merged = demographics.merge(facility_counts, on="barangay", how="left")

    for col in facility_counts.columns:
        if col != "barangay":
            merged[col] = merged[col].fillna(0)

    for spec in ACCESSIBILITY_RATIO_INDICATORS.values():

        facility_col = spec["facility_col"]
        pop_col = spec["pop_col"]
        ratio_col = spec["ratio_col"]

        if facility_col in merged.columns and pop_col in merged.columns:

            merged[ratio_col] = (
                merged[facility_col] / merged[pop_col] * 1000
            ).replace([np.inf, -np.inf], np.nan)

    return merged


@st.cache_data(show_spinner=False)
def load_demographics():
    """
    Loads the barangay-level population/CBMS/administrative
    indicators table (processed/editable/demographics_by_barangay.csv),
    then merges in live-computed facility counts and ratio_*
    accessibility ratios — see compute_facility_counts_by_barangay
    and compute_facility_ratios. Those two used to be static
    columns hand-maintained inside demographics_by_barangay.csv
    itself; they're computed here instead so they can never go
    stale relative to care_supply_facilities.csv.

    Use this (rather than re-deriving figures from population_age
    /population_sex) wherever a page needs the newer indicators
    that aren't part of the legacy population_summary/sex/age
    shape — e.g. registered PWDs, CBMS food insecurity, or the
    facilities-per-1,000 ratio columns.
    """

    demographics = pd.read_csv(
        "processed/editable/demographics_by_barangay.csv"
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

    care = pd.read_csv("processed/editable/care_supply_facilities.csv")
    facility_counts = compute_facility_counts_by_barangay(care)
    demographics = compute_facility_ratios(demographics, facility_counts)

    pwd_facility_counts = compute_pwd_facility_counts_by_barangay(care)
    demographics = demographics.merge(pwd_facility_counts, on="barangay", how="left")
    demographics["PWD Facilities"] = demographics["PWD Facilities"].fillna(0)

    childcare_facility_counts = compute_childcare_facility_counts_by_barangay(care)
    demographics = demographics.merge(childcare_facility_counts, on="barangay", how="left")
    demographics["Childcare-Relevant Facilities"] = (
        demographics["Childcare-Relevant Facilities"].fillna(0)
    )

    return demographics


# --------------------------------------------------
# AUTO-COMPUTED SUMMARY STATS
# (replaces the old manually-maintained processed/editable/
# childcare_summary.csv and senior_summary.csv — every value here
# is derived live from care_supply_facilities.csv / demographics_by_barangay.csv
# so it can never go stale. regenerate_computed_data.py calls
# these same functions to write a verifiable snapshot to
# processed/computed/, so the on-disk snapshot and what the app
# displays can never drift apart from each other.)
# --------------------------------------------------

def compute_childcare_summary(childcare_centers):
    """
    One row: count of Child Development Centers among mapped
    childcare facilities. Uses the same "Child Development" match
    as childcare_color() above, so this always agrees with what's
    colored/labeled as a CDC on the map.

    Note: this will generally NOT match any previously-published
    DSWD registry figure — it counts facilities present in
    care_supply_facilities.csv with valid coordinates, not DSWD's full licensing
    roster (some licensed CDCs may not be mapped yet, or vice
    versa).
    """
    child_development_centers = int(
        childcare_centers["Category"]
        .str.contains("Child Development", case=False, na=False)
        .sum()
    )

    return pd.DataFrame([
        {
            "metric": "child_development_centers",
            "value": child_development_centers,
            "source": "care_supply_facilities.csv (live count)"
        }
    ])


def compute_senior_summary(demographics):
    """
    Mixes two different sources, tagged per row in the "source"
    column:
      - registered_seniors: OSCA administrative registration total
        (demographics_by_barangay.csv's seniors_registered column).
      - female / male / age_60_79 / age_80_plus: 2020 Census
        (age_60plus_f / age_60plus_m / age_80plus).

    These do not sum to the same total on purpose — OSCA's registry
    is cumulative (seniors who have since died or moved away stay
    on the count) and was last refreshed in a different year than
    the 2020 Census, so the two are expected to diverge rather than
    reconcile. See the "Why don't these figures add up?" note on
    the Older Persons & Senior Citizens page.
    """
    age_80_plus = int(demographics["age_80plus"].sum())
    age_60_79 = int(demographics["age_60plus"].sum()) - age_80_plus

    return pd.DataFrame([
        {
            "metric": "registered_seniors",
            "value": int(demographics["seniors_registered"].sum()),
            "source": "OSCA registration (demographics_by_barangay.csv)"
        },
        {
            "metric": "female",
            "value": int(demographics["age_60plus_f"].sum()),
            "source": "2020 Census"
        },
        {
            "metric": "male",
            "value": int(demographics["age_60plus_m"].sum()),
            "source": "2020 Census"
        },
        {
            "metric": "age_60_79",
            "value": age_60_79,
            "source": "2020 Census"
        },
        {
            "metric": "age_80_plus",
            "value": age_80_plus,
            "source": "2020 Census"
        },
    ])


DISTRICT_SUM_COLS = [
    "area_km2", "pop_census", "pop_male", "pop_female",
    "age_0_2", "age_0_2_m", "age_0_2_f",
    "age_3_5", "age_3_5_m", "age_3_5_f",
    "age_0_5", "age_0_5_m", "age_0_5_f",
    "age_6_17", "age_6_17_m", "age_6_17_f",
    "age_18_59", "age_18_59_m", "age_18_59_f",
    "age_60plus", "age_60plus_m", "age_60plus_f",
    "age_80plus", "age_80plus_m", "age_80plus_f",
    "age_0_4", "women_15_49",
    "children_0_5_childcare", "children_0_17_total",
    "seniors_registered", "pwd_registered",
    "migrant_workers_total", "migrant_workers_male", "migrant_workers_female",
    "pop_cbms_secondary", "cbms_responding_hh",
]

DISTRICT_CBMS_DUAL_WEIGHTED_COLS = [
    "cbms_food_insecurity_prevalence_pct",
    "cbms_food_severe_wholeday_pct",
    "cbms_food_intensity_score",
    "cbms_housing_inadequacy_index_pct",
    "cbms_housing_makeshift_severe_pct",
    "cbms_avg_household_size",
    "cbms_avg_nuclear_families_per_hh",
]


@st.cache_data(show_spinner=False)
def compute_demographics_by_district(demographics):
    """
    Aggregates demographics_by_barangay.csv to district level. Two
    kinds of columns, aggregated differently:

    1. Summable columns (DISTRICT_SUM_COLS) — population, age bands,
       seniors/PWD registrations, migrant workers, CBMS coverage —
       simple sum across each district's barangays.
    2. Derived columns (density, ratios, rates, shares, CBMS
       percentages) — recomputed from the district-level sums, never
       averaged from barangay-level values directly (a per-1,000 rate
       or a percentage doesn't average correctly across barangays of
       different sizes).

    CBMS indicators are computed under two weighting schemes per
    barangay: _hhw (weighted by cbms_responding_hh — each barangay
    counts by how much CBMS data it contributed) and _popw (weighted
    by pop_census — each resident counts once, consistent with every
    other derived variable here).
    """

    work = demographics.copy()

    for col in DISTRICT_SUM_COLS:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    rows = []

    for district, group in work.groupby("district"):

        row = {"district": district}

        for col in DISTRICT_SUM_COLS:
            row[col] = (
                round(group[col].sum(), 4)
                if col == "area_km2"
                else group[col].sum()
            )

        pop = row["pop_census"]
        area = row["area_km2"]

        row["pop_density_km2"] = round(pop / area, 1) if area else None
        row["sex_ratio_m_per_100f"] = (
            round(row["pop_male"] / row["pop_female"] * 100, 1)
            if row["pop_female"] else None
        )
        row["share_women_18_59_pct"] = (
            round(row["age_18_59_f"] / pop * 100, 2) if pop else None
        )
        row["child_woman_ratio"] = (
            round(row["age_0_4"] / row["women_15_49"] * 1000, 1)
            if row["women_15_49"] else None
        )
        row["seniors_density_km2"] = (
            round(row["seniors_registered"] / area, 1) if area else None
        )
        row["seniors_per_1000_census"] = (
            round(row["seniors_registered"] / pop * 1000, 1) if pop else None
        )
        row["pwd_density_km2"] = (
            round(row["pwd_registered"] / area, 1) if area else None
        )
        row["pwd_per_1000_census"] = (
            round(row["pwd_registered"] / pop * 1000, 1) if pop else None
        )
        row["disability_prevalence_rate_pct"] = (
            round(row["pwd_registered"] / pop * 100, 2) if pop else None
        )

        for col in DISTRICT_CBMS_DUAL_WEIGHTED_COLS:

            vals = pd.to_numeric(group[col], errors="coerce")
            w_hh = pd.to_numeric(group["cbms_responding_hh"], errors="coerce")
            w_pop = pd.to_numeric(group["pop_census"], errors="coerce")

            mask_hh = vals.notna() & w_hh.notna()
            mask_pop = vals.notna() & w_pop.notna()

            row[f"{col}_hhw"] = (
                round((vals[mask_hh] * w_hh[mask_hh]).sum() / w_hh[mask_hh].sum(), 2)
                if w_hh[mask_hh].sum() else None
            )
            row[f"{col}_popw"] = (
                round((vals[mask_pop] * w_pop[mask_pop]).sum() / w_pop[mask_pop].sum(), 2)
                if w_pop[mask_pop].sum() else None
            )

        rows.append(row)

    result = pd.DataFrame(rows)
    result["district"] = result["district"].astype("Int64")

    return result


@st.cache_data(show_spinner=False)
def load_demographics_by_district():
    """
    District-level demographics, computed live from
    demographics_by_barangay.csv — see compute_demographics_by_district.

    Returns a DataFrame with one row per district (1-6) containing:
    - Area and population totals
    - Age/sex breakdowns (matches barangay columns for consistency)
    - Socioeconomic indicators (disability, food insecurity, housing)
    - Migrant worker counts
    - Density and ratio metrics

    Use this alongside load_demographics() to provide district context
    when displaying barangay-level data, creating district comparisons,
    or prioritizing resources by district need.
    """

    demographics = load_demographics()

    return compute_demographics_by_district(demographics)


@st.cache_data(show_spinner=False)
def load_climate_context():
    """
    Loads the city-wide (non-barangay) flood risk indicators
    from processed/reference/climate/climate.csv. These figures are
    WorldPop-based and only available at the Quezon City total
    level — there is no per-barangay breakdown — so they're
    meant for KPI cards/context on the Climate & Hazard Exposure
    page, not for a choropleth map.
    """

    climate = pd.read_csv(
        "processed/reference/climate/climate.csv"
    )

    return climate


@st.cache_data(show_spinner=False)
def load_demand_context():
    """
    Loads city_context and computes district_context, the two
    district/city-level companions to demographics_by_barangay.csv:

    - processed/editable/demand_city_context.csv — city-wide
      breakdowns (seniors by sex/age, seniors also registered
      as PWD, PWDs by disability type with male/female splits).
      No barangay or district breakdown; OSCA and PDAO figures
      for "seniors with disability" are kept as two separate
      rows since they use different registration bases and
      disagree (4,677 vs 6,429) — this is documented in the
      "note" column rather than reconciled. Left as its own
      manually-maintained file — it isn't derivable from anything
      else (city-level only, no barangay/district breakdown to
      derive it from).
    - district_context — registered seniors and PWDs per district.
      Used to be its own manually-maintained file
      (demand_district_context.csv), but that file's numbers were
      just a slightly-stale duplicate of
      demographics_by_district.csv's own seniors_registered/
      pwd_registered columns (same OSCA/PDAO source, off by a
      handful per district from a different pull date) — so this
      is now read from there instead, live, rather than kept in
      sync by hand in two places.

    Returns (city_context, district_context).
    """

    city_context = pd.read_csv(
        "processed/editable/demand_city_context.csv"
    )

    demographics_district = load_demographics_by_district()

    district_context = demographics_district[
        ["district", "seniors_registered", "pwd_registered"]
    ].copy()

    district_context["source"] = "demographics_by_district.csv"

    return city_context, district_context


@st.cache_data(show_spinner=False)
def load_domestic_workers():
    """
    Returns registered domestic worker counts (female/male/total)
    as (barangay_df, district_df).

    The counts now live directly in demographics_by_barangay.csv
    (domestic_workers_female/male/total columns) — they used to
    come from a separate processed/domestic_workers.csv, which
    needed a fair amount of barangay-name reconciliation to line
    up with demographics_by_barangay.csv's spelling (147 source
    rows for 142 barangays: a few genuine duplicates to sum, a
    few spelling variants to rewrite, two barangays — "Doña
    Aurora"/"Aurora" and "San Isidro"/"San Isidro Galas" — left
    unmatched as genuinely ambiguous). That reconciliation was
    run once and the resulting columns were merged into
    demographics_by_barangay.csv directly, so this function no
    longer needs to redo it on every load — it just slices those
    columns out. Kept as its own function (rather than inlining
    at each call site) so every caller keeps using the same
    (barangay_df, district_df) shape as before.

    - barangay_df: one row per barangay, columns
      ["barangay", "barangay_key", "district", "domestic_workers_female",
      "domestic_workers_male", "domestic_workers_total"].
    - district_df: the same three count columns, summed to one
      row per district (district as int 1-6).
    """

    demo = pd.read_csv(
        "processed/editable/demographics_by_barangay.csv"
    )

    demo["barangay_key"] = (
        demo["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    barangay_df = demo[
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
    raster_path="processed/reference/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
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
    raster_path="processed/reference/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
    barangay_path="processed/reference/qc_barangays.geojson",
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


_MISSING_TOOLTIP_VALUES = {"", "not available", "nan", "none", "<na>"}


def build_tooltip_html(df, name_col, fields):
    """
    Builds a per-row map tooltip HTML string with only the fields
    that have a real value for that row — a field that's missing,
    blank, or "Not available" is left out of the tooltip entirely
    rather than shown with an empty-looking line, since pydeck has
    no per-row conditional logic of its own: the same static HTML
    template is substituted for every point, so hiding one point's
    "Open:" line without hiding every point's requires building the
    whole HTML string here in Python first, then pointing the
    pydeck tooltip at this single precomputed column.

    df: the facility dataframe (used only to read values from —
        returns a new Series, doesn't mutate df).
    name_col: column holding the bold header line (always shown).
    fields: list of (label, column) pairs, rendered in order as
        "<br/>Label: value" — skipped whenever that row's value in
        `column` is null or one of the recognized missing-value
        placeholders ("Not available", "", "nan", etc.).

    Returns a pandas Series of HTML strings, aligned to df's index
    — assign it as a column and reference {that_column} as the
    entire tooltip "html" template.
    """

    def _row_html(row):

        html = f"<b>{row[name_col]}</b>"

        for label, col in fields:

            if col not in row:
                continue

            val = row[col]

            if pd.isna(val):
                continue

            if str(val).strip().lower() in _MISSING_TOOLTIP_VALUES:
                continue

            html += f"<br/>{label}: {val}"

        return html

    return df.apply(_row_html, axis=1)


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
    care_supply_facilities.csv major_division values.
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
    load_demographics() (processed/editable/demographics_by_barangay.csv).
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


# --------------------------------------------------
# DISCRETE CHOROPLETH BINS
# (matches the client's reference GIS maps — discrete legend
# swatches with labeled ranges, e.g. "0-1", "1-2", "2-4" — rather
# than a continuous gradient. Bin edges are computed from
# quantiles of the data itself rather than hand-picked per
# indicator, since this dashboard drives the same choropleth off
# ~20 different accessibility ratios with very different scales
# (ACCESSIBILITY_RATIO_INDICATORS in this file); a fixed bin set
# tuned for one indicator would be meaningless for another.
# --------------------------------------------------

def compute_quantile_bins(values, n_bins=6):
    """
    Computes up to n_bins discrete bin edges from the strictly
    positive values in `values` (a pandas Series). Zero and NaN
    are excluded here, the caller treats zero as its own "No
    facility" bin rather than the bottom of this range, matching
    the reference maps' explicit no-facility styling.

    Returns a sorted list of unique edges (may be shorter than
    n_bins+1 if the data has few distinct positive values, e.g.
    a sparse indicator with mostly 0s and a handful of 1s).
    """

    positive = values[(values > 0) & values.notna()]

    if positive.empty:
        return []

    quantile_points = np.linspace(0, 1, n_bins + 1)
    edges = sorted(positive.quantile(quantile_points).unique())

    return edges


def _round_bin_edge(value):
    """
    Rounds a bin edge to a readable precision that scales with
    its magnitude, matching how the reference maps show whole
    numbers for high-magnitude indicators (e.g. "16+") and
    decimals for low-magnitude ones (e.g. "0.25").
    """

    if value < 1:
        return round(value, 2)
    elif value < 10:
        return round(value, 1)
    else:
        return round(value)


def format_bin_label(lo, hi, is_last):
    """
    Formats one bin's range as a legend label, e.g. "2 - 4" or,
    for the open-ended top bin, "16+". Shared by
    discrete_bin_color_and_label (per-value lookup) and the
    legend-building code (per-bin, independent of any single
    value) so both describe the same bin the same way.
    """

    lo_r, hi_r = _round_bin_edge(lo), _round_bin_edge(hi)

    if is_last and hi_r == lo_r:
        return f"{lo_r}+"

    return f"{lo_r} - {hi_r}"


def bin_edges_to_labels(edges):
    """
    Turns a full list of bin edges (from compute_quantile_bins)
    into one range label per bin, in the same low-to-high order
    as the `colors` list passed to discrete_bin_color_and_label —
    for building a legend without needing a real data value per
    bin.
    """

    return [
        format_bin_label(edges[i], edges[i + 1], i == len(edges) - 2)
        for i in range(len(edges) - 1)
    ]


def discrete_bin_color_and_label(value, edges, colors, zero_color):
    """
    Assigns a fill color and a legend-style range label to a
    single ratio value, given the bin edges from
    compute_quantile_bins() and a light-to-dark `colors` list
    (one per bin, low value = light, high value = dark — higher
    ratio means more facilities per capita, so darker reads as
    "better served", the same convention as the reference maps).

    zero_color is used for exactly 0 (no facility of this type at
    all) — kept visually distinct from the lightest positive bin
    rather than folded into it, so "none" and "very few" don't
    look the same on the map. NaN (unmatched/no-data barangay)
    reuses zero_color since the map has no way to tell "zero"
    apart from "missing" without a separate data-quality layer.
    """

    if pd.isna(value) or value == 0 or not edges:
        return zero_color, "No facility"

    for i in range(len(edges) - 1):

        lo, hi = edges[i], edges[i + 1]
        is_last = i == len(edges) - 2

        if (lo <= value <= hi) if is_last else (lo <= value < hi):

            color = colors[min(i, len(colors) - 1)]
            label = format_bin_label(lo, hi, is_last)

            return color, label

    # Falls outside every bin (shouldn't happen given edges span
    # the data's own min/max, but guards against float edge cases)
    return colors[-1], format_bin_label(edges[-1], edges[-1], True)


def render_discrete_legend_html(bin_labels_colors, zero_label, zero_color, label=None):
    """
    Builds a discrete swatch legend (colored square + range label
    per row) matching the reference GIS maps' legend style, as an
    alternative to render_colormap_legend_html's continuous
    gradient bar.

    bin_labels_colors: list of (label, [r,g,b] or [r,g,b,a]) pairs,
    already ordered light-to-dark / low-to-high.
    zero_label/zero_color: the "No facility" row, shown first.

    Returns a raw HTML string; pass to st.markdown(...,
    unsafe_allow_html=True).
    """

    def _swatch_item(swatch_label, rgb):

        r, g, b = rgb[0], rgb[1], rgb[2]

        return (
            '<span style="display:inline-flex;align-items:center;'
            'margin-right:20px;margin-top:4px;white-space:nowrap;">'
            f'<span style="display:inline-block;width:16px;height:16px;'
            f'background:rgb({r},{g},{b});border:1px solid #999;'
            'margin-right:6px;flex-shrink:0;"></span>'
            f'<span style="font-size:12px;color:#1a1a1a;">{swatch_label}</span>'
            '</span>'
        )

    label_html = (
        f'<div style="font-size:13px;font-weight:600;'
        f'margin-bottom:4px;color:#1a1a1a;">{label}</div>'
        if label else ""
    )

    items_html = _swatch_item(zero_label, zero_color)

    for swatch_label, rgb in bin_labels_colors:
        items_html += _swatch_item(swatch_label, rgb)

    return f"""
    <div style="
        margin-top:8px;
        margin-bottom:8px;
        background:#ffffff;
        padding:10px 12px;
        border-radius:6px;
    ">
        {label_html}
        <div style="display:flex;flex-wrap:wrap;align-items:center;">
            {items_html}
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
