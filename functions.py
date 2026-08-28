import base64
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.io as pio
import plotly.graph_objects as go

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

    if "GOVERNMENT" in category:
        return "#055B52"   # green gradient — darkest

    elif "RETIREMENT" in category or "ASSISTED LIVING" in category:
        return "#45897E"   # green gradient — mid

    elif "RESIDENTIAL" in category:
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
        return "#582C9F"   # purple gradient

    elif "PRIVATE HOSPITAL" in category:
        return "#643BAA"   # purple gradient

    elif "LYING-IN" in category:
        return "#7C5ABF"   # purple gradient

    elif "SUPER HEALTH" in category:
        return "#9478D3"   # purple gradient

    elif "PHARMACY" in category:
        return "#C4B5FD"   # purple gradient

    elif "HEALTH CENTER" in category:
        return "#AC97E8"   # purple gradient

    elif "MILK BANK" in category:
        return "#DDD0FB"   # purple gradient — lightest (still visible on map)

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
# BUS STOPS FUNCTIONS
# --------------------------------------------------
def bus_stops_color(category=None):
    """
    Color for Bus stops layer in Care Explorer.
    Uses a distinct orange/transit color from the palette
    to differentiate from care facilities.
    """
    return "#F97316"  # bright orange for transit/bus stops


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return [
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    ]

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


def infer_provider_type(category_text):
    """
    Infers Public/Private only where the category text itself makes
    it unambiguous (e.g. "LGU-run hospital", "National government-
    owned hospital", "Private hospital"). Health Centers and Long-
    Term Care facility records don't carry a sub_division (Public/
    Private) value in the source data, so anything without a clear
    ownership word in its category returns "Not available" rather
    than guessing.
    """

    cat = str(category_text).lower()

    if "private" in cat:
        return "Private"

    elif "lgu" in cat or "national" in cat or "government" in cat:
        return "Public"

    return "Not available"


def health_category_mapper(cat):

    cat = str(cat).lower().strip()

    if "lying-in" in cat or "lying in" in cat:
        return "Lying-in Clinics"

    elif "national" in cat:
        return "National Government Hospitals"

    elif "private" in cat and "hospital" in cat:
        return "Private Hospitals"

    elif ("lgu" in cat or "qc" in cat) and "hospital" in cat:
        return "QC LGU-run Hospitals"

    elif "pharmacy" in cat:
        return "Health Centers with Pharmacy"

    elif "super" in cat:
        return "Super Health Centers"

    elif "health" in cat and "center" in cat:
        return "Health Centers"

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
    # major_division/sub_division/category on the *full* care
    # dataframe before it gets split by major_division. A
    # categorical column remembers every level that ever existed
    # in the unfiltered data, even after rows are filtered out,
    # so .value_counts()/px.pie() downstream would otherwise
    # report a 0-count slice for every OTHER division's category
    # (Schools, Childcare, etc.) in what should be a health-only
    # chart. Casting to plain string drops that stale level list.
    df["Category"] = df["Category"].astype(str)

    df["Sector"] = df["category"].apply(infer_provider_type)

    with pd.option_context("future.no_silent_downcasting", True):
        if "address_clean" in df.columns and "address" in df.columns:
            df["Address"] = df["address_clean"].fillna(df["address"]).fillna("Not available")
        elif "address_clean" in df.columns:
            df["Address"] = df["address_clean"].fillna("Not available")
        elif "address" in df.columns:
            df["Address"] = df["address"].fillna("Not available")
        else:
            df["Address"] = "Not available"

    df = df.rename(
        columns={
            "name_original": "Name",
            "district": "District"
        }
    )

    df["District"] = pd.to_numeric(
        df["District"],
        errors="coerce"
    ).astype("Int64")

    df["Name"] = (
        df["Name"]
        .str.title()
        # str.title() lowercases every letter after the first in
        # each word, which turns the "QC" acronym into "Qc" (e.g.
        # "St. Joseph College of QC" -> "...of Qc") — restore it.
        .str.replace(r"\bQc\b", "QC", regex=True)
    )


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
    # `category` dtype on the full care dataframe *before*
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

    df["Name"] = (
        df["Name"]
        .str.title()
        # str.title() lowercases every letter after the first in
        # each word, which turns the "QC" acronym into "Qc" (e.g.
        # "St. Joseph College of QC" -> "...of Qc") — restore it.
        .str.replace(r"\bQc\b", "QC", regex=True)
    )

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

    care = pd.read_csv("processed/care.csv")

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
        care["major_division"] == "Trainings"
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
    long_term_care["Sector"]  = long_term_care["Category"].apply(infer_provider_type)
    action_offices            = clean_dataframe(action_offices)
    action_offices["Name"]    = (
        "District "
        + action_offices["District"].astype(int).astype(str)
        + " Action Office"
    )
    action_offices["Category"] = action_offices["Name"]
    action_offices["open_hours"]  = "8:00 AM"
    action_offices["close_hours"] = "5:00 PM"
    migration_centers          = clean_dataframe(migration_centers)
    migration_centers["open_hours"]  = "8:00 AM"
    migration_centers["close_hours"] = "5:00 PM"
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
