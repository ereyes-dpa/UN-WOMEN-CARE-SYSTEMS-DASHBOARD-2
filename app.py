import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import numpy as np
import math
import json
from functions import *
import pydeck as pdk
from pydeck.types import String
import plotly.express as _px4

# PRIVATE VERSION

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Quezon Caring City Dashboard",
    layout="wide"
)

# --------------------------------------------------
# RESERVOIR LANDMARK LAYER
# (La Mesa Reservoir isn't one of the 142 barangays and carries no
# demographic/facility data — shown on every barangay-boundary map
# purely as a geographic landmark, name-only on hover, never part
# of any barangay count or list. Kept non-pickable by default since
# most pages build their own custom tooltip template keyed to their
# own data columns, which the reservoir feature doesn't have.)
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def load_reservoir_layer(pickable=False):
    reservoir_gdf = gpd.read_file(
        "processed/reference/qc_reservoir.geojson",
        engine="pyogrio"
    )
    return pdk.Layer(
        "GeoJsonLayer",
        data=json.loads(reservoir_gdf.to_json()),
        stroked=True,
        filled=False,
        get_line_color=[80, 80, 80, 200],
        line_width_min_pixels=1.2,
        pickable=pickable,
    )

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Roboto:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
}

h1, h2, h3, h4 {
    font-family: 'Montserrat', sans-serif !important;
    color: #7F47ED !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Montserrat', sans-serif;
}

[data-testid="stMetricValue"] {
    color: #7F47ED;
}

/* --------------------------------------------------
   HOMEPAGE COMPONENTS
   (extends the existing purple/Montserrat system rather
   than introducing a second palette, soft purple-tinted
   neutrals for card surfaces, the same #7F47ED/#4C1D95
   used everywhere else for accents and headings.)
   -------------------------------------------------- */

.qcd-hero {
    background: linear-gradient(135deg, #4C1D95 0%, #7F47ED 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
}

.qcd-hero h2 {
    color: #FFFFFF !important;
    margin: 0 0 8px 0;
    font-size: 1.7rem;
}

.qcd-hero p {
    color: #E4DEF7;
    margin: 0;
    max-width: 640px;
    font-size: 0.95rem;
    line-height: 1.5;
}

.qcd-hero-badge {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 10px;
    padding: 12px 22px;
    text-align: center;
    flex-shrink: 0;
}

.qcd-hero-badge .qcd-badge-value {
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 1.9rem;
    line-height: 1.1;
}

.qcd-hero-badge .qcd-badge-label {
    color: #E4DEF7;
    font-size: 0.78rem;
    line-height: 1.3;
}

.qcd-card {
    background: #EEEDFE;
    border: 1px solid #E4DEF7;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
}

.qcd-card-accent {
    border-left: 4px solid #7F47ED;
    background: #EEEDFE;
    border-top: 1px solid #E4DEF7;
    border-right: 1px solid #E4DEF7;
    border-bottom: 1px solid #E4DEF7;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

.qcd-eyebrow {
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #7F47ED;
    margin-bottom: 4px;
}

.qcd-card-title {
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 0.98rem;
    color: #1a1a1a;
    margin-bottom: 2px;
}

.qcd-card-body {
    font-size: 0.86rem;
    color: #1a1a1a;
    line-height: 1.45;
    margin: 0;
}

.qcd-section-label {
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #7F47ED;
    border-bottom: 2px solid #E4DEF7;
    padding-bottom: 6px;
    margin-bottom: 14px;
}

/* Reusable "takeaway" box for under a chart, states the
   one-sentence insight in plain language, the way the PBIX
   reference dashboard does. Not yet applied to any page;
   ready to drop under a chart with:
   st.markdown('<div class="qcd-insight"><div class="qcd-insight-label">Insight</div>...</div>', unsafe_allow_html=True) */

.qcd-insight {
    background: #EEEDFE;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 8px;
    margin-bottom: 10px;
}

.qcd-insight-label {
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #4C1D95;
    margin-bottom: 3px;
}

.qcd-insight-body {
    font-size: 0.88rem;
    color: #1a1a1a;
    line-height: 1.45;
    margin: 0;
}

/* --------------------------------------------------
   KPI CARDS
   (replaces bare st.metric with a boxed, elevated card,    purple gradient surface, white text, matching the
   dashboard's hero banner treatment. Used via the
   kpi_card() helper in functions.py rather than
   st.metric directly, so the optional polarity arrow can
   be drawn next to the value.)
   -------------------------------------------------- */

.qcd-kpi-card {
    background: linear-gradient(135deg, #4C1D95 0%, #7F47ED 100%);
    border-radius: 12px;
    padding: 16px 18px 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(76, 29, 149, 0.18);
    min-height: 88px;
}

.qcd-kpi-label {
    font-family: 'Roboto', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    color: #E4DEF7;
    margin-bottom: 6px;
    line-height: 1.3;
}

.qcd-kpi-value-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
}

.qcd-kpi-value {
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 1.6rem;
    color: #FFFFFF;
    line-height: 1.1;
}

.qcd-kpi-arrow {
    font-size: 0.85rem;
    line-height: 1;
}

.qcd-kpi-caption {
    font-family: 'Roboto', sans-serif;
    font-size: 0.74rem;
    color: #E4DEF7;
    margin-top: 4px;
    line-height: 1.3;
}

/* --------------------------------------------------
   CHART / TABLE CARDS
   (every chart/table container is created with
   st.container(border=True, key="qcd-chart-..."), the
   key prefix lets this single selector catch all of them
   via Streamlit's auto-generated .st-key-<key> class,
   without also restyling tabs, expanders, or other
   containers Streamlit generates internally that also
   use stVerticalBlockBorderWrapper under the hood.

   Light purple tint (not the solid KPI gradient) so chart
   text/axis labels and table contents stay legible without
   needing to flip every label to white. Note: st.dataframe
   renders its grid in its own internal component with a
   transparent cell background by design (a Streamlit
   limitation, not a CSS bug here), this tint colors the
   panel and padding around a table, but individual table
   cells may still show through as white/default underneath.
   Plotly charts render as inline SVG, so they pick up this
   background cleanly.)
   -------------------------------------------------- */

div[class*="st-key-qcd-chart-"] {
    background: #EEEDFE;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(76, 29, 149, 0.08);
    border-color: transparent !important;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOGOS ROW
# --------------------------------------------------

fcdo_logo = get_base64("assets/fcdo_logo.png")
un_logo   = get_base64("assets/unwomen_logo.png")
qc_logo   = get_base64("assets/qc_logo.png")
gad_logo  = get_base64("assets/qc.png")

# Heights are chosen for consistent *visual weight*, not
# identical pixel height: QC is a dense, near-square seal,
# while FCDO and UN Women are wide wordmark+icon banners
# with a lot of thin strokes, whitespace, and small caption
# text. At equal pixel height the seal reads as too small
# and the wordmark captions become illegible, so QC is sized
# up relative to the banners until the three read as
# comparably "heavy" on the page. All three sit in one
# shared flex row so they share a single vertical-center
# alignment, no per-logo nudging needed.
LOGO_ROW_HEIGHT = 100

FCDO_HEIGHT = 56
UN_HEIGHT   = 56
QC_HEIGHT   = 85
GAD_HEIGHT  = 60

left_col, spacer_col, right_col = st.columns([1, 3, 3])

# QC Logo (left)
with left_col:

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:20px;
            height:{LOGO_ROW_HEIGHT}px;
        ">
            <a href="https://quezoncity.gov.ph/" target="_blank">
                <img src="data:image/png;base64,{qc_logo}"
                     style="height:{QC_HEIGHT}px; width:auto;">
            </a>
            <img src="data:image/png;base64,{gad_logo}"
                 style="height:{GAD_HEIGHT}px; width:auto;">
        </div>
        """,
        unsafe_allow_html=True
    )

# FCDO + UN Women (right)
with right_col:

    st.markdown(
        f"""
        <div style="
            display:flex;
            justify-content:flex-end;
            align-items:center;
            gap:20px;
            height:{LOGO_ROW_HEIGHT}px;
        ">
            <a href="https://www.gov.uk/government/organisations/foreign-commonwealth-development-office"
               target="_blank">
                <img src="data:image/webp;base64,{fcdo_logo}"
                     style="height:{FCDO_HEIGHT}px; width:auto;">
            </a>
            <a href="https://www.unwomen.org/en"
               target="_blank">
                <img src="data:image/png;base64,{un_logo}"
                     style="height:{UN_HEIGHT}px; width:auto;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown(
    """
    <h1 style="
        text-align:center;
        color:#7F47ED;
        font-size:2.6rem;
        margin-top:5px;
        margin-bottom:0px;
        line-height:1.1;
    ">
        Quezon Caring City Dashboard
    <
    """,
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

(
    childcare_centers,
    schools,
    health_centers,
    older_person_care,
    long_term_care,
    action_offices,
    migration_centers,
    bus_stops
) = load_data()  # Updated to load bus_stops from care_v4.csv

geo, bounds = load_geo()

# --------------------------------------------------
# POPULATION DATA
# --------------------------------------------------

population_summary, population_sex, population_age = (
    load_data_for_kpis()
)

# --------------------------------------------------
# FULL INDICATORS TABLE (new accessibility, disability,
# and CBMS socio-economic columns beyond the legacy
# population_summary/sex/age shape above) + city-wide
# climate context figures.
# --------------------------------------------------

demographics = load_demographics()
demographics_district = load_demographics_by_district()  # NEW: District-level demographics
climate_context = load_climate_context()
demand_city_context, demand_district_context = load_demand_context()
domestic_workers_barangay, domestic_workers_district = (
    load_domestic_workers()
)

# --------------------------------------------------
# BARANGAY AND DISTRICT DATAFRAMES (for KPIs and charts)
# --------------------------------------------------

barangay_map = gpd.read_file(
        "processed/reference/qc_barangays.geojson"
    )

district_map = gpd.read_file(
        "processed/reference/qc_districts.geojson"
    )
# Normalize join keys
barangay_map["barangay_name"] = (
    barangay_map["barangay_name"]
    .astype(str)
    .str.strip()
    .str.upper()
)

population_age["Barangay"] = (
    population_age["Barangay"]
    .astype(str)
    .str.strip()
    .str.upper()
)

population_sex["Barangay"] = (
    population_sex["Barangay"]
    .astype(str)
    .str.strip()
    .str.upper()
)

barangay_df = barangay_map.merge(
    population_age,
    left_on="barangay_name",
    right_on="Barangay",
    how="left"
)

barangay_df = barangay_df.merge(
    population_sex[
        [
            "Barangay",
            "Male",
            "Female"
        ]
    ],
    on="Barangay",
    how="left"
)

age_group_definition = {
    "children_0_17": [
        "0-5 (Early Childhood)",
        "6-17 (School Age Children)"
    ],
    "working_age_18_59": [
        "18-59 (Working Age Adult)"
    ],
    "elderly_60_plus": [
        "60+ (Older Persons)"
    ]
}

barangay_df["children_0_17"] = barangay_df[
    age_group_definition["children_0_17"]
].sum(axis=1)

barangay_df["working_age"] = barangay_df[
    age_group_definition["working_age_18_59"]
].sum(axis=1)

barangay_df["elderly"] = barangay_df[
    age_group_definition["elderly_60_plus"]
].sum(axis=1)

# District population
district_pop = (
    population_age[
        [
            "District",
            "0-5 (Early Childhood)",
            "6-17 (School Age Children)",
            "18-59 (Working Age Adult)",
            "60+ (Older Persons)",
            "Total"
        ]
    ]
    .groupby("District")
    .sum()
    .reset_index()
    .rename(
        columns={
            "0-5 (Early Childhood)":
                "Early Childhood (0-5)",
            "6-17 (School Age Children)":
                "School Age (6-17)",
            "18-59 (Working Age Adult)":
                "Working Age (18-59)",
            "60+ (Older Persons)":
                "Older Persons (60+)"
        }
    )
)

district_pop = district_pop.merge(
    population_sex[
        [
            "District",
            "Male",
            "Female"
        ]
    ]
    .groupby("District")
    .sum()
    .reset_index(),
    on="District",
    how="left"
)

# --------------------------------------------------
# SUPPLY-SIDE CLIMATE EXPOSURE
# (flags each facility as inside/outside the 100-yr flood
# inundation footprint, see flag_facilities_at_risk in
# functions.py. Computed once here, for every service type,
# so both the Care Services Explorer page and any future
# page can reuse the same flood_risk column without
# resampling the raster repeatedly.)
# --------------------------------------------------

childcare_centers   = flag_facilities_at_risk(childcare_centers)
schools             = flag_facilities_at_risk(schools)
health_centers      = flag_facilities_at_risk(health_centers)
older_person_care   = flag_facilities_at_risk(older_person_care)
long_term_care      = flag_facilities_at_risk(long_term_care)
action_offices   = flag_facilities_at_risk(action_offices)
migration_centers   = flag_facilities_at_risk(migration_centers)


# --------------------------------------------------
# QC CENTER
# --------------------------------------------------
minx, miny, maxx, maxy = bounds

center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2

southwest = [miny, minx]
northeast = [maxy, maxx]

st.markdown("""
<style>
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color:#7F47ED !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR STYLE
# --------------------------------------------------

st.markdown("""
<style>

/* Sidebar titles */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #7F47ED !important;
}

/* Reduce top padding */
[data-testid="stSidebarContent"] {
    padding-top: -15rem;
}

/* Compact buttons */
[data-testid="stSidebar"] .stButton > button {
    min-height: 0px;
    padding: 0rem 0rem;
    font-size: 0.85rem;
    border-radius: 5px;
}

/* Reduce spacing between widgets */
[data-testid="stSidebar"] .element-container {
    margin-bottom: 0.0001rem;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PAGE STATE
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"


@st.cache_data(show_spinner="Building map...")
def build_explorer_map(
    selected_layers,
    selected_district,
    selected_climate_layers=None,
    flood_risk_only=False,
    show_risk_rings=True,
    demand_pop_col=None,
    demand_pop_label=None,
    demand_pop_source="demographics",
    demand_metric="density",
    selected_source="All"
):
    """
    Builds the full Care Services Explorer map and returns
    (deck, climate_legend_info, demand_legend_info).

    Built on pydeck rather than folium — folium's rendered HTML
    pulls in Leaflet.js, jQuery, Bootstrap, and Leaflet.awesome-markers
    from 4 separate external CDNs (folium's default boilerplate;
    this map never actually used the jQuery/Bootstrap/awesome-marker
    pieces). If any one of those is blocked by the viewer's network
    or an ad-blocker, the whole map renders blank with no error —
    every other map in this app is pydeck-based (bundled with
    Streamlit, no external JS CDN dependency beyond the tile
    images themselves) and none of those are reported blank.

    Cached on (selected_layers, selected_district,
    selected_climate_layers, flood_risk_only, show_risk_rings, ...)
    so a rerun that doesn't change any of these arguments returns
    the previously-built Deck immediately instead of re-encoding
    every raster overlay and rebuilding every marker from scratch.

    flood_risk_only, when True, only facilities flagged by
    flag_facilities_at_risk (i.e. df["flood_risk"] == True) are
    drawn as markers. This is the supply-side exposure filter:
    "which facilities sit inside the 100-yr flood footprint?",
    computed once for every facility type up top (see
    flag_facilities_at_risk calls near DATA LOADING), not
    recomputed here. Only offered as a UI control on the Care
    Services Explorer tab inside Climate, Hazard and Population
    Analysis; the main Care Services Explorer page always passes
    False, since that page is meant to stay a plain facility map
    with no flood-risk framing.

    show_risk_rings, when True, gives flood-exposed facilities a
    thicker red outline so they stand out even with
    flood_risk_only off and the climate overlay off. When False
    (used by the main Care Services Explorer page), markers render
    with their normal outline only.

    climate_legend_info is a dict of {layer_name: (vmin, vmax)}
    for every selected *non-binary* climate layer (Land-Surface
    Temperature, NDVI), used by the caller to render a color-scale
    legend outside this function. Binary layers (Flood Inundation)
    are intentionally excluded since they're a flooded/not-flooded
    mask, not a continuous scale.

    demand_pop_col/demand_pop_label pick which demographic column
    drives the population-density choropleth (e.g. "age_0_5" /
    "Child population (ages 0-5)") — None (the default) skips the
    layer entirely. demand_pop_source picks which table
    demand_pop_col is looked up on: "demographics" (default) for
    the shared `demographics` table, or "domestic_workers" for the
    separate domestic_workers_barangay table (see
    load_domestic_workers() in functions.py) — needed because
    registered domestic worker counts aren't part of `demographics`.
    demand_legend_info is either None or (vmin, vmax, label,
    colormap), same rationale as climate_legend_info.

    demand_metric switches the population layer between
    "density" (default — people per km², "Greens" ramp) and
    "count" (raw population for the selected group, "Oranges" ramp
    so it reads as visually distinct from density and doesn't
    compete with the Blues flood layer or green boundary fill it
    sits under).

    selected_source filters every service layer's facilities to
    just one data_source value (from care_supply_facilities.csv —
    "Administrative data", "Google API - Validated", or
    "Google API - For Validation") when not "All".
    """

    # Each service type is drawn as one color-coded dot (no
    # per-type symbol shapes in pydeck's ScatterplotLayer, unlike
    # folium's DivIcon markers) — colors picked to all be clearly
    # distinct from each other at a glance, since color is now the
    # only way to tell types apart on the map itself (the legend
    # above the map and each point's tooltip still name the type).
    service_layers = {

        "Childcare Centers": {
            "df": childcare_centers,
            "color": "#4C1D95",
            "symbol": "◆",
            "source": "Childcare Center",
        },

        "Schools": {
            "df": schools,
            "color": "#4472C4",
            "symbol": "▲",
            "source": "School",
        },

        "Health Centers": {
            "df": health_centers,
            "color": "#4C1D95",
            "symbol": "✚",
            "source": "Health Facility",
        },

        "Older Persons Facilities": {
            "df": older_person_care,
            "color": "#055B52",
            "symbol": "●",
            "source": "Older Persons Facility",
        },

        "Long-Term Care & Rehabilitation": {
            "df": long_term_care,
            "color": "#4C1D95",
            "symbol": "✦",
            "source": "Rehabilitation Facility",
        },

        "Action Offices": {
            "df": action_offices,
            "color": "#055B52",
            "symbol": "■",
            "source": "Action Office",
        },

        "Migration Resource Centers": {
            "df": migration_centers,
            "color": "#C4B5FD",
            "symbol": "✈",
            "source": "Migration Resource Center",
        },

        "Bus Stops": {
            "df": bus_stops,
            "color": "#F97316",
            "symbol": "⊙",
            "source": "Bus Stop",
        },
    }

    climate_overlay_layers = {
        "Land-Surface Temperature": {
            "path": "processed/reference/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
            "colormap": "YlOrRd",
            "binary": False
        },
        "Vegetation (NDVI)": {
            "path": "processed/reference/climate/ndvi_mean_2025_EPSG3123.tif",
            "colormap": "Greens",
            "binary": False
        },
        "Flood Inundation (100-yr)": {
            "path": "processed/reference/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
            "colormap": "Blues",
            "binary": True
        }
    }

    layers = []

    # ------------------------------------------
    # BARANGAY BOUNDARIES (context only, not interactive — see
    # the note on the facility ScatterplotLayer below for why
    # only one layer per deck carries the tooltip)
    # ------------------------------------------

    layers.append(
        pdk.Layer(
            "GeoJsonLayer",
            data=geo,
            stroked=True,
            filled=True,
            get_fill_color=[127, 191, 127, 38],
            get_line_color=[102, 102, 102],
            line_width_min_pixels=1,
            pickable=False
        )
    )

    # ------------------------------------------
    # POPULATION DENSITY / COUNT CHOROPLETH (Demand Layer)
    # ------------------------------------------

    demand_legend_info = None

    if demand_pop_col is not None:

        barangay_map_gdf = gpd.read_file("processed/reference/qc_barangays.geojson")
        barangay_map_gdf["barangay_name"] = (
            barangay_map_gdf["barangay_name"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        _demand_source_df = (
            demographics if demand_pop_source == "demographics"
            else domestic_workers_barangay
        )

        barangay_pop = _demand_source_df[
            ["barangay", demand_pop_col]
        ].drop_duplicates().copy()

        barangay_pop["barangay"] = (
            barangay_pop["barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        barangay_map_gdf = barangay_map_gdf.merge(
            barangay_pop,
            left_on="barangay_name",
            right_on="barangay",
            how="left"
        )

        if demand_metric == "count":

            barangay_map_gdf["demand_value"] = (
                barangay_map_gdf[demand_pop_col].fillna(0)
            )

            _demand_colormap = "Oranges"
            _demand_unit = ""
            _demand_legend_suffix = ""

        else:

            barangay_map_gdf_proj = barangay_map_gdf.to_crs("EPSG:3123")

            barangay_map_gdf["area_km2"] = (
                barangay_map_gdf_proj.geometry.area / 1_000_000
            )

            barangay_map_gdf["demand_value"] = (
                barangay_map_gdf[demand_pop_col] /
                barangay_map_gdf["area_km2"]
            ).fillna(0)

            _demand_colormap = "Greens"
            _demand_unit = "/km²"
            _demand_legend_suffix = " Density (per km²)"

        _density_vmin, _density_vmax = (
            barangay_map_gdf["demand_value"]
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .quantile([0.02, 0.98])
        )

        barangay_map_gdf["demand_display"] = (
            barangay_map_gdf["demand_value"]
            .map(lambda v: f"{v:,.1f}{_demand_unit}")
        )

        barangay_map_gdf["fill_color"] = barangay_map_gdf["demand_value"].apply(
            lambda v: value_to_rgba(v, _density_vmin, _density_vmax, colormap=_demand_colormap)
        )

        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                data=json.loads(barangay_map_gdf.to_json()),
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color=[153, 153, 153, 150],
                line_width_min_pixels=0.5,
                pickable=False
            )
        )

        demand_legend_info = (
            _density_vmin,
            _density_vmax,
            f"{demand_pop_label}{_demand_legend_suffix}",
            _demand_colormap
        )

    # ------------------------------------------
    # CLIMATE OVERLAYS
    # ------------------------------------------

    climate_legend_info = {}

    if selected_climate_layers:

        qc_boundary_explorer = load_qc_boundary()

        for climate_layer_name in selected_climate_layers:

            climate_layer = climate_overlay_layers[climate_layer_name]

            try:

                png_data_uri, bounds_corners, layer_vmin, layer_vmax = (
                    raster_to_bitmap_layer(
                        climate_layer["path"],
                        colormap=climate_layer["colormap"],
                        binary=climate_layer["binary"],
                        _mask_geometry=qc_boundary_explorer
                    )
                )

                if not climate_layer["binary"]:
                    climate_legend_info[climate_layer_name] = (
                        layer_vmin,
                        layer_vmax
                    )

                layers.append(
                    pdk.Layer(
                        "BitmapLayer",
                        image=png_data_uri,
                        bounds=bounds_corners,
                        opacity=0.7
                    )
                )

            except Exception:
                # Surfaced to the user outside this cached function
                # (see the explorer page body), since st commands
                # inside cached functions only show on the first,
                # uncached run.
                pass

    # ------------------------------------------
    # RESERVOIR LANDMARK
    # ------------------------------------------

    layers.append(load_reservoir_layer())

    # ------------------------------------------
    # FACILITY MARKERS
    # (one combined ScatterplotLayer across every selected service
    # type, each row carrying its own precomputed tooltip_html —
    # pydeck has one shared tooltip template per deck, not
    # per-layer, so every row needs the same field name regardless
    # of which service type it came from. All 8 service dataframes
    # share the same column schema after load_data()/
    # clean_dataframe(), so one field list covers all of them.)
    # ------------------------------------------

    all_points = []
    at_risk_points = []

    # Per-category marker color, restoring the original per-row
    # shading (a childcare marker's exact shade of purple depends on
    # whether it's a Child Development Center, Learning Center, or
    # Day Care Center, etc.) rather than one flat color per service
    # type — the same color functions used on each type's own
    # dedicated map page.
    ROW_COLOR_FN = {
        "Childcare Centers": lambda row: childcare_color(row["Category"]),
        "Schools": lambda row: school_color(row["Category"]),
        "Health Centers": lambda row: marker_color(row["Category"]),
        "Older Persons Facilities": lambda row: opc_color(row["Category"]),
        "Long-Term Care & Rehabilitation": lambda row: ltc_color(row["Category"]),
        "Action Offices": lambda row: district_color(row["District"]),
    }

    for layer_name in selected_layers:

        layer = service_layers[layer_name]

        df = layer["df"].copy()

        if selected_district != "All":

            df = df[
                df["District"].astype(int) == selected_district
            ]

        if flood_risk_only:

            df = df[
                df.get("flood_risk", pd.Series(False, index=df.index))
            ]

        if selected_source != "All" and "data_source" in df.columns:

            df = df[df["data_source"] == selected_source]

        df = df.dropna(subset=["latitude", "longitude"])

        if df.empty:
            continue

        df["Type"] = layer_name

        df["tooltip_html"] = build_tooltip_html(
            df, "Name",
            [
                ("Type", "Type"),
                ("Category", "Category"),
                ("Provider Type", "Sector"),
                ("District", "District"),
                ("Barangay", "barangay"),
                ("Address", "Address"),
                ("Open", "open_hours"),
                ("Close", "close_hours"),
                ("Source", "data_source"),
            ]
        )

        color_fn = ROW_COLOR_FN.get(layer_name)
        row_hex = df.apply(color_fn, axis=1) if color_fn else layer["color"]
        colors = row_hex.apply(hex_to_rgb) if color_fn else [hex_to_rgb(layer["color"])] * len(df)

        df["r"] = [c[0] for c in colors]
        df["g"] = [c[1] for c in colors]
        df["b"] = [c[2] for c in colors]
        df["symbol"] = layer["symbol"]

        all_points.append(
            df[["latitude", "longitude", "r", "g", "b", "symbol", "tooltip_html"]]
        )

        if show_risk_rings:
            at_risk_points.append(
                df[df.get("flood_risk", pd.Series(False, index=df.index))]
                [["latitude", "longitude"]]
            )

    if at_risk_points:

        at_risk_combined = pd.concat(at_risk_points, ignore_index=True)

        if not at_risk_combined.empty:
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=at_risk_combined,
                    get_position="[longitude, latitude]",
                    get_fill_color=[0, 0, 0, 0],
                    get_line_color=[185, 28, 28, 220],
                    stroked=True,
                    filled=True,
                    line_width_min_pixels=2.5,
                    get_radius=60,
                    radius_min_pixels=10,
                    radius_max_pixels=10,
                    pickable=False
                )
            )

    if all_points:

        combined = pd.concat(all_points, ignore_index=True)

        # deck.gl's TextLayer only pre-renders its default character
        # set — printable ASCII — into the font atlas it builds; any
        # character outside that range (every symbol here) rendered
        # as nothing, with no error, regardless of whether the
        # viewer's font actually has a glyph for it. character_set
        # explicitly tells it to also render these 8 symbols into
        # the atlas, restoring the original icons instead of falling
        # back to plain letters.
        _explorer_symbols = "".join(
            layer["symbol"] for layer in service_layers.values()
        )

        layers.append(
            pdk.Layer(
                "TextLayer",
                data=combined,
                get_position="[longitude, latitude]",
                get_text="symbol",
                get_color="[r, g, b]",
                get_size=18,
                size_min_pixels=14,
                size_max_pixels=22,
                get_angle=0,
                get_text_anchor='"middle"',
                get_alignment_baseline='"center"',
                character_set='"' + _explorer_symbols + '"',
                font_weight=700,
                pickable=True
            )
        )

    # ------------------------------------------
    # VIEW STATE + DECK
    # ------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=12,
        pitch=0,
        min_zoom=11,
        max_zoom=18,
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={
            "html": "{tooltip_html}",
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "12px"
            }
        },
        map_style="light"
    )

    return deck, climate_legend_info, demand_legend_info

# Default values so variables always exist
selected_category = "All"
selected_health_source = "All"

selected_childcare_category = "All"
selected_childcare_source = "All"

selected_school_sector = "All"
selected_school_category = "All"
selected_school_source = "All"

selected_opc_category = "All"
selected_opc_sector = "All"
selected_opc_source = "All"

selected_ltc_category = "All"
selected_ltc_source = "All"

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

if st.sidebar.button(
    "Home",
    width="stretch"
):
    st.session_state.page = "Home"
    st.rerun()

if st.sidebar.button(
    "Population Overview",
    width="stretch"
):
    st.session_state.page = "Population Overview"
    st.rerun()

st.sidebar.subheader("Care Maps")


# --------------------------------------------------
# CHILDCARE
# --------------------------------------------------

if st.sidebar.button(
    "Childcare Facilities",
    width='stretch'
):
    st.session_state.page = "Childcare Centers"
    st.rerun()

if st.session_state.page == "Childcare Centers":

    st.sidebar.markdown("##### Filters")

    # Derived from the data rather than hardcoded — a new Category
    # value added to care_supply_facilities.csv shows up here
    # automatically next time the data is refreshed, no code
    # change needed. (The source data only ever records the
    # combined "Child development center and supervised
    # neighborhood play" as one category — there is no row where
    # either half stands alone — so that's the only childcare-
    # center-type option, not a bug.)
    selected_childcare_category = st.sidebar.radio(
        "Facility Category",
        ["All"] + sorted(childcare_centers["Category"].dropna().unique()),
        key="childcare_category"
    )

    # Derived from the data rather than hardcoded — data_source now
    # splits "Google API" into "Google API - Validated" and
    # "Google API - For Validation" (see load_data() in functions.py),
    # and a hardcoded list here would silently exclude both.
    selected_childcare_source = st.sidebar.radio(
        "Data Source",
        ["All"] + sorted(childcare_centers["data_source"].dropna().unique()),
        key="childcare_source"
    )

# --------------------------------------------------
# SCHOOLS
# --------------------------------------------------

if st.sidebar.button(
    "Schools",
    width='stretch'
):
    st.session_state.page = "Schools"
    st.rerun()

if st.session_state.page == "Schools":

    st.sidebar.markdown("##### Filters")

    selected_school_sector = st.sidebar.radio(
        "Provider Type",
        [
            "All",
            "Public",
            "Private"
        ],
        key="school_sector"
    )

    # Derived from the data rather than hardcoded — was previously
    # a fixed list that silently went stale whenever a new school
    # Category value appeared in the source data (e.g. it once
    # missed "Junior high school", "Private school", and "Special
    # Education Program" for months). A new category now shows up
    # here automatically next time the data is refreshed.
    selected_school_category = st.sidebar.radio(
        "School Category",
        ["All"] + sorted(schools["Category"].dropna().unique()),
        key="school_category"
    )

    selected_school_source = st.sidebar.radio(
        "Data Source",
        ["All"] + sorted(schools["data_source"].dropna().unique()),
        key="school_source"
    )

# --------------------------------------------------
# HEALTH CENTERS
# --------------------------------------------------

if st.sidebar.button(
    "Health Centers",
    width='stretch'
):
    st.session_state.page = "Health Centers Map"
    st.rerun()

if st.session_state.page == "Health Centers Map":

    st.sidebar.markdown("##### Filters")

    selected_category = st.sidebar.radio(
        "Facility Type",
        ["All"] + list(HEALTH_CATEGORY_COLORS.keys()),
        key="health_category"
    )

    selected_health_source = st.sidebar.radio(
        "Data Source",
        ["All"] + sorted(health_centers["data_source"].dropna().unique()),
        key="health_source"
    )

# --------------------------------------------------
# OLDER PERSONS
# --------------------------------------------------

if st.sidebar.button(
    "Older Persons Care Facilities",
    width='stretch'
):
    st.session_state.page = "Older Persons Center Map"
    st.rerun()

if st.session_state.page == "Older Persons Center Map":

    st.sidebar.markdown("##### Filters")

    # Derived from the data (like Long-Term Care's category
    # filter below) rather than hardcoded, since the eldercare
    # dataset review reassigned every facility from the old
    # generic "Nursing Care Center"/"Bahay Aruga" split to a
    # dozen more specific facility-type categories — hardcoding
    # them here would silently go stale the next time the
    # underlying data changes.
    opc_categories = sorted(
        older_person_care["Category"]
        .dropna()
        .unique()
    )

    selected_opc_category = st.sidebar.radio(
        "Facility Type",
        ["All"] + list(opc_categories),
        key="opc_category"
    )

    selected_opc_sector = st.sidebar.radio(
        "Provider Type",
        [
            "All",
            "Public",
            "Private"
        ],
        key="opc_sector"
    )

    selected_opc_source = st.sidebar.radio(
        "Data Source",
        ["All"] + sorted(older_person_care["data_source"].dropna().unique()),
        key="opc_source"
    )

# --------------------------------------------------
# LONG TERM CARE
# --------------------------------------------------

if st.sidebar.button(
    "Long-Term Care & Rehabilitation",
    width='stretch'
):
    st.session_state.page = "Long-Term Care & Rehabilitation"
    st.rerun()

if st.session_state.page == "Long-Term Care & Rehabilitation":

    st.sidebar.markdown("##### Filters")

    ltc_categories = sorted(
        long_term_care["Category"]
        .dropna()
        .unique()
    )

    selected_ltc_category = st.sidebar.radio(
        "Facility Category",
        ["All"] + list(ltc_categories),
        key="ltc_category"
    )

    selected_ltc_source = st.sidebar.radio(
        "Data Source",
        ["All"] + sorted(long_term_care["data_source"].dropna().unique()),
        key="ltc_source"
    )

# --------------------------------------------------
# ACTION OFFICES
# --------------------------------------------------

if st.sidebar.button(
    "Action Offices",
    width='stretch'
):
    st.session_state.page = "Action Offices"
    st.rerun()

# --------------------------------------------------
# MIGRATION
# --------------------------------------------------

if st.sidebar.button(
    "Migration Resource Center",
    width='stretch'
):
    st.session_state.page = "Migration Resource Center"
    st.rerun()

# --------------------------------------------------
# TOOLS
# --------------------------------------------------

st.sidebar.subheader("Analysis Tools")

if st.sidebar.button(
    "Care Services Explorer",
    width='stretch'
):
    st.session_state.page = "Care Services Explorer"
    st.rerun()

if st.sidebar.button(
    "Accessibility Analysis",
    width='stretch'
):
    st.session_state.page = "Accessibility Analysis"
    st.rerun()

if st.sidebar.button(
    "Climate Layers",
    width='stretch'
):
    st.session_state.page = "Climate Layers"
    st.rerun()

if st.sidebar.button(
    "Care Planning & Investment Priorities",
    width='stretch'
):
    st.session_state.page = "Care Planning & Investment Priorities"
    st.rerun()

if st.sidebar.button(
    "Barangay Clusters",
    width='stretch'
):
    st.session_state.page = "Barangay Clusters"
    st.rerun()

if st.sidebar.button(
    "Zoning Map",
    width='stretch'
):
    st.session_state.page = "Zoning Map"
    st.rerun()

# --------------------------------------------------
# ACTIVE PAGE
# --------------------------------------------------

page = st.session_state.page

if page == "Care Services Explorer":

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Child Care")

    # Derived from the data (like Health Services below) rather
    # than hardcoded — the raw data only ever has one combined
    # "Child Development Center And Supervised Neighborhood Play"
    # category, never either half alone, so a fixed 4-option list
    # here would show two categories that don't exist.
    for cat in sorted(childcare_centers["Category"].dropna().unique()):

        st.sidebar.markdown(
            f"""
            <span style="color:{childcare_color(cat)};font-size:22px;">◆</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Schools")

    for cat in sorted(schools["Category"].dropna().unique()):

        st.sidebar.markdown(
            f"""
            <span style="color:{school_color(cat)};font-size:22px;">▲</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Health Services")

    ordered_categories = list(HEALTH_CATEGORY_COLORS.keys())

    for cat in ordered_categories:

        st.sidebar.markdown(
            f"""
            <span style="
                color:{category_hex(cat)};
                font-size:22px;
            ">✚</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Older Persons")

    for cat in sorted(older_person_care["Category"].dropna().unique()):

        st.sidebar.markdown(
            f"""
            <span style="
                color:{opc_color(cat)};
                font-size:22px;
            ">●</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Long-Term Care")

    for cat in sorted(long_term_care["Category"].dropna().unique()):

        st.sidebar.markdown(
            f"""
            <span style="
                color:{ltc_color(cat)};
                font-size:22px;
            ">✦</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )


    st.sidebar.markdown("---")
    st.sidebar.markdown("## Action Offices")

    st.sidebar.markdown(
        """
        <span style="color:#055B52;font-size:22px;">■</span>
        <b>District Offices</b>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Migration Services")

    st.sidebar.markdown(
        """
        <span style="color:#C4B5FD;font-size:22px;">✈</span>
        <b>Migration Resource Center</b>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# PAGES
# --------------------------------------------------
if page == "Home":

    # =====================================================
    # HERO
    # =====================================================

    citywide_population = population_summary["Total"].iloc[0]

    st.markdown(
        f"""
        <div class="qcd-hero">
            <div>
                <h2>Quezon Caring City Dashboard</h2>
                <p>
                    Strategic reference for care-service planning,
                    resource allocation, and climate-resilient
                    policymaking across Quezon City's 142 barangays.
                </p>
            </div>
            <div class="qcd-hero-badge">
                <div class="qcd-badge-value">
                    {citywide_population:,.0f}
                </div>
                <div class="qcd-badge-label">
                    residents citywide
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # STRATEGIC KPIs WITH CONTEXT
    # =====================================================

    st.markdown(
        '<div class="qcd-section-label">Citywide Care Landscape</div>',
        unsafe_allow_html=True
    )

    # Calculate key metrics
    elderly_pop = population_age[
        age_group_definition["elderly_60_plus"]
    ].sum().sum()

    children_pop = (
        population_age[age_group_definition["children_0_17"][0]].sum() +
        population_age[age_group_definition["children_0_17"][1]].sum()
    )

    elderly_pct = (elderly_pop / citywide_population) * 100
    children_pct = (children_pop / citywide_population) * 100

    # Total facilities across all types
    total_facilities = (
        len(childcare_centers) +
        len(schools) +
        len(health_centers) +
        len(older_person_care) +
        len(long_term_care) +
        len(action_offices) +
        len(migration_centers)
    )

    k1, k2, k3, k4 = st.columns(4)


    k1.metric(
        "Older Persons (60+)",
        f"{elderly_pct:.1f}%",
        f"~{int(elderly_pop):,} residents"
    )

    k2.metric(
        "Children (0-17)",
        f"{children_pct:.1f}%",
        f"~{int(children_pop):,} residents"
    )

    k3.metric(
        "Care Facilities",
        f"{total_facilities:,}",
        "across all service types"
    )

    # Total barangays and districts
    total_barangays = len(barangay_df)
    total_districts = len(district_pop)

    k4.metric(
        "Coverage",
        f"{total_barangays} barangays",
        f"in {total_districts} districts"
    )


    st.divider()

    # =====================================================
    # EXECUTIVE SUMMARY (TOP INSIGHTS)
    # =====================================================

    st.markdown(
        '<div class="qcd-section-label">Executive Briefing</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **Current Status & Critical Gaps:**
    Quezon City serves 2.95M residents with uneven care-service distribution.
    Barangays in northern and southern districts face the dual challenge of
    high population density and low facility access. Climate hazards (flood,
    heat) compound vulnerability for older persons, children, and persons with disabilities.
    """)

    with st.expander("Key Decision Points", expanded=False):
        st.info(
            """
            1. **Accessibility Gaps** → Which districts lack childcare, health, and older persons care?
            2. **Climate Vulnerability Hotspots** → Which barangays have high-risk populations + flood exposure?
            3. **Resource Efficiency** → Where can facility expansion or relocation have the highest impact?

            Use the pages below to answer each question. Start with **Accessibility Analysis** to map
            current gaps, then **Climate Layers** for risk overlay, and **Care Planning**
            for investment scenarios.
            """
        )

    # =====================================================
    # RECOMMENDED POLICY ACTIONS
    # =====================================================

    with st.expander("Recommended Policy Actions for This Briefing", expanded=False):

        st.markdown("""
        **Immediate Actions (Next 30 Days):**
        1. **Review Accessibility Analysis page** → Identify the 3–5 barangays with the lowest facility ratios
           (particularly health and childcare). These are your highest-impact intervention sites.

        2. **Cross-check Climate Vulnerability** → Use the Climate Layers page to flag
           barangays with both low facility access AND high flood/climate risk. These require
           climate-resilient infrastructure (e.g., mobile clinics, flood-resistant facilities).

        3. **Scenario-test in Care Planning** → Use the Care Planning & Investment Priorities page to
           model 2–3 allocation scenarios (e.g., "Add 10 childcare centers in District 4" or
           "Prioritize older persons care in southern barangays"). Check the impact on accessibility metrics.

        **Medium-term (Next 90 Days):**
        - Export the **Barangay Clusters** analysis to identify peer barangays for shared
          service models (e.g., shared health clinics across a cluster of 3–4 similar barangays).
        - Commission a detailed **Site Selection Study** for the top 5 priority barangays, informed by
          this dashboard's accessibility and climate data.

        **Long-term (Next 12 Months):**
        - Integrate this dashboard into quarterly policy reviews; track progress on facility ratios and
          climate resilience metrics.
        """)

    st.divider()

    # =====================================================
    # TOOL CATALOG (NAVIGATION)
    # =====================================================

    st.markdown(
            '<div class="qcd-section-label">Navigate by Use Case</div>',
            unsafe_allow_html=True
        )

    nav_col, contents_col = st.columns([1, 1.3])

    with nav_col:

            st.markdown(
                '<div style="font-family: Montserrat, sans-serif; font-size: 0.95rem; font-weight: 600; color: #7F47ED; margin-bottom: 12px;">How to Navigate</div>',
                unsafe_allow_html=True
            )

            nav_steps = [
                (
                    "1. Diagnose",
                    "Use <b>Population Overview</b> and <b>Accessibility Analysis</b> "
                    "to identify demographic profiles and current care-service gaps."
                ),
                (
                    "2. Risk-Map",
                    "Use <b>Climate Layers</b> to overlay climate hazards "
                    "on vulnerable populations and facility locations."
                ),
                (
                    "3. Plan & Decide",
                    "Use <b>Care Planning & Investment Priorities</b> to model interventions "
                    "and <b>Barangay Clusters</b> to identify peer groups for shared solutions."
                )
            ]

            for idx, (step_title, step_body) in enumerate(nav_steps):

                min_height = "auto"

                st.markdown(
                    f"""
                    <div class="qcd-card" style="border: 1px solid #e0e0e0; border-radius: 8px; min-height: {min_height}; padding: 16px; margin-bottom: 12px;">
                        <div class="qcd-card-title">{step_title}</div>
                        <p class="qcd-card-body">{step_body}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with contents_col:

            st.markdown(
                '<div style="font-family: Montserrat, sans-serif; font-size: 0.95rem; font-weight: 600; color: #7F47ED; margin-bottom: 12px;">What\'s Available</div>',
                unsafe_allow_html=True
            )

            content_groups = [
                (
                    "#055B52",
                    "Care Services Maps",
                    "Interactive maps for childcare, schools, health centers, "
                    "older persons care, long-term rehabilitation, action offices, and migration centers. "
                    "Filter by district and identify gaps."
                ),
                (
                    "#7F47ED",
                    "Analysis & Planning Tools",
                    "Population Overview, Accessibility Analysis, Care Planning & Investment Priorities, "
                    "and Barangay Clusters. Drill down into demographics, facility ratios, climate risk, "
                    "and resource allocation."
                ),
                (
                    "#B91C1C",
                    "Climate & Hazard Risk",
                    "Flood, heat, and vegetation layers with facility locations and population "
                    "shading. Supports climate-resilient facility placement."
                )
            ]

            for idx, (accent_color, group_title, group_body) in enumerate(content_groups):

                min_height = "auto"

                st.markdown(
                    f"""
                    <div class="qcd-card-accent" style="border: 1px solid #e0e0e0; border-left: 4px solid {accent_color}; border-radius: 8px; min-height: {min_height}; padding: 16px; margin-bottom: 12px;">
                        <div class="qcd-card-title">{group_title}</div>
                        <p class="qcd-card-body">{group_body}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

elif page == "Population Overview":


    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Population Overview
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Demographic profile of Quezon City to support planning,
    resource allocation, and care service delivery decisions.
    """)

    # =====================================================
    # AGE GROUP DEFINITION,  PENDING CONFIRMATION WITH MARIAN
    # (same definition documented in Notebook 2, Section 2.1.0)
    # Source data arrives pre-aggregated into these four bands,
    # so a different elderly/children cutoff (e.g. 65+ instead
    # of 60+) cannot be derived from what we have, it would
    # require re-tabulating from a more granular source.
    # =====================================================

    age_group_definition = {
        "children_0_17": [
            "0-5 (Early Childhood)",
            "6-17 (School Age Children)"
        ],
        "working_age_18_59": [
            "18-59 (Working Age Adult)"
        ],
        "elderly_60_plus": [
            "60+ (Older Persons)"
        ]
    }

    # =====================================================
    # LOAD MAPS
    # =====================================================

    barangay_map = gpd.read_file(
        "processed/reference/qc_barangays.geojson"
    )

    district_map = gpd.read_file(
        "processed/reference/qc_districts.geojson"
    )

    # =====================================================
    # CLEAN DATA
    # =====================================================

    for col in ["Male", "Female", "Total"]:

        if col in population_sex.columns:

            population_sex[col] = (
                population_sex[col]
                .astype(str)
                .str.replace(",", "")
                .astype(float)
            )

    age_cols = [
        "0-5 (Early Childhood)",
        "6-17 (School Age Children)",
        "18-59 (Working Age Adult)",
        "60+ (Older Persons)"
    ]

    for col in age_cols + ["Total"]:

        population_age[col] = (
            population_age[col]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
        )

    # =====================================================
    # KPIs (TOP)
    # =====================================================

    total_population = population_sex["Total"].sum()
    total_male = population_sex["Male"].sum()
    total_female = int(math.ceil(population_sex["Female"].sum()))

    early_childhood = population_age[
        age_group_definition["children_0_17"][0]
    ].sum()

    school_age = population_age[
        age_group_definition["children_0_17"][1]
    ].sum()

    working_age = population_age[
        age_group_definition["working_age_18_59"]
    ].sum().sum()

    elderly = population_age[
        age_group_definition["elderly_60_plus"]
    ].sum().sum()

    sex_ratio_overall = (
        total_male
        / total_female
        * 100
    )

    early_childhood_pct = (
        early_childhood
        / total_population
        * 100
    )

    school_age_pct = (
        school_age
        / total_population
        * 100
    )

    working_age_pct = (
        working_age
        / total_population
        * 100
    )

    elderly_pct = (
        elderly
        / total_population
        * 100
    )

    # Total Population - Primary Metric
    top1, top2 = st.columns([1, 1])
    kpi_card(
        top1,
        "Total Population",
        f"{total_population:,.0f}",
        caption="residents citywide"
    )

    total_domestic_workers = (
        domestic_workers_barangay["domestic_workers_total"].sum()
    )

    kpi_card(
        top2,
        "Registered Domestic Workers",
        f"{total_domestic_workers:,.0f}",
        caption="citywide, across barangays"
    )

    st.divider()

    # Sex Ratio and Age Ranges - Secondary Metrics
    st.markdown(
        '<div class="qcd-section-label">Demographic Breakdown</div>',
        unsafe_allow_html=True
    )

    sec1, sec2_col = st.columns([1, 1.8])

    with sec1:
        st.markdown(
            f"""
            <div style="background: #EEEDFE; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
                <div style="font-family: 'Montserrat', sans-serif; font-size: 0.85rem; font-weight: 600; color: #7F47ED; margin-bottom: 8px;">Sex Ratio (M/F)</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #7F47ED;">{sex_ratio_overall:.1f}</div>
                <div style="font-size: 0.78rem; color: #888; margin-top: 4px;">males per 100 females</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with sec2_col:
        st.markdown(
            '<div class="qcd-section-label" style="margin-bottom: 12px;">Age Ranges, % of Total Population</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)

        kpi_card(
            c1,
            "0-5",
            f"{early_childhood_pct:.1f}%"
        )

        kpi_card(
            c2,
            "6-17",
            f"{school_age_pct:.1f}%"
        )

        kpi_card(
            c3,
            "18-59",
            f"{working_age_pct:.1f}%"
        )

        kpi_card(
            c4,
            "60+",
            f"{elderly_pct:.1f}%"
        )

    st.divider()

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2 = st.tabs(
        [
            "Barangay Analysis",
            "District Analysis"
        ]
    )

    # =====================================================
    # BARANGAY TAB
    # =====================================================
    with tab1:

        # Normalize join keys defensively before merging.
        # population_age["Barangay"] / population_sex["Barangay"]
        # come from apply_barangay_mapping() in functions.py,
        # which can return title-case names (e.g. "Greater
        # Lagro") rather than the geojson's raw casing. The two
        # currently happen to agree by coincidence, but relying
        # on that isn't safe, explicitly uppercase both sides,
        # same convention used on the other pages.
        barangay_map["barangay_name"] = (
            barangay_map["barangay_name"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        population_age["Barangay"] = (
            population_age["Barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        population_sex["Barangay"] = (
            population_sex["Barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        barangay_df = barangay_map.merge(
            population_age,
            left_on="barangay_name",
            right_on="Barangay",
            how="left"
        )

        barangay_df = barangay_df.merge(
            population_sex[
                [
                    "Barangay",
                    "Male",
                    "Female"
                ]
            ],
            on="Barangay",
            how="left"
        )

        # ---------------------------------------------------
        # DERIVED INDICATORS
        # (children/working-age/elderly grouping driven by
        # age_group_definition above, update there, not here,
        # once confirmed with Marian)
        # ---------------------------------------------------

        barangay_df["children_0_17"] = barangay_df[
            age_group_definition["children_0_17"]
        ].sum(axis=1)

        # Split out of children_0_17 rather than merged into it —
        # both bands already exist as separate columns on
        # population_age (see age_group_definition["children_0_17"]
        # above), so this is just naming them for the indicator
        # dropdown below, no new data.
        barangay_df["children_0_5"] = (
            barangay_df[age_group_definition["children_0_17"][0]]
        )

        barangay_df["children_6_17"] = (
            barangay_df[age_group_definition["children_0_17"][1]]
        )

        barangay_df["working_age"] = barangay_df[
            age_group_definition["working_age_18_59"]
        ].sum(axis=1)

        barangay_df["elderly"] = barangay_df[
            age_group_definition["elderly_60_plus"]
        ].sum(axis=1)

        barangay_df["children_pct"] = (
            barangay_df["children_0_17"]
            /
            barangay_df["Total"]
            * 100
        )

        barangay_df["elderly_pct"] = (
            barangay_df["elderly"]
            /
            barangay_df["Total"]
            * 100
        )

        barangay_df["sex_ratio"] = (
            barangay_df["Male"]
            /
            barangay_df["Female"]
            * 100
        )

        barangay_metric = (
            barangay_df
            .to_crs("EPSG:32651")
        )

        barangay_df["area_km2"] = (
            barangay_metric.geometry.area
            / 1_000_000
        )

        barangay_df["population_density"] = (
            barangay_df["Total"]
            /
            barangay_df["area_km2"]
        )

        # ---------------------------------------------------
        # DOMESTIC WORKERS (separate source, same convention
        # as the Care Planning page: merged in once here so
        # the indicator dropdown below can treat it like every
        # other population column. barangay_df["Barangay"] was
        # already normalized to the uppercase barangay_key
        # form above, so it lines up directly with
        # domestic_workers_barangay's own barangay_key.
        # ---------------------------------------------------

        barangay_df = barangay_df.merge(
            domestic_workers_barangay[
                [
                    "barangay_key",
                    "domestic_workers_total"
                ]
            ],
            left_on="Barangay",
            right_on="barangay_key",
            how="left"
        )

        # ---------------------------------------------------
        # DOMESTIC WORKER SUPPLY RATIOS, how many registered
        # domestic workers exist relative to the two dependent
        # groups care planning cares most about (children and
        # older persons), not just the raw domestic worker count
        # above. Per-1,000 rather than per-100 to match the
        # "per 1,000 residents" convention already used for
        # domestic workers on the Care Planning page. Barangays
        # with zero children/elderly (division by zero, -> inf)
        # are treated the same as a genuine data gap (NaN), same
        # as any other unmatched barangay on this map.
        # ---------------------------------------------------

        # Per 1,000 children aged 0-5 specifically (not the
        # combined 0-17 band), since domestic worker demand tracks
        # early-childhood care needs far more closely than
        # school-age children.
        barangay_df["domestic_workers_per_1000_children"] = (
            barangay_df["domestic_workers_total"]
            / barangay_df["children_0_5"]
            * 1000
        ).replace([np.inf, -np.inf], np.nan).round(1)

        barangay_df["domestic_workers_per_1000_elderly"] = (
            barangay_df["domestic_workers_total"]
            / barangay_df["elderly"]
            * 1000
        ).replace([np.inf, -np.inf], np.nan).round(1)

        # ---------------------------------------------------
        # MAP, only the indicators that are genuinely useful
        # to visualize spatially (dropped care_demand_index
        # and sex_ratio from the MAP since they read better
        # as ranked bar charts below)
        # ---------------------------------------------------

        indicator = st.selectbox(
            "Select Population Indicator",
            [
                "Total Population",
                "Female Population",
                "Male Population",
                "Children Population (0-17)",
                "Children Population (0-5)",
                "Children Population (6-17)",
                "Working Age Population",
                "Older Persons Population",
                "Children Share (%)",
                "Older Persons Share (%)",
                "Population Density",
                "Domestic Workers Population",
                "Domestic Workers per 1,000 Children (0-5)",
                "Domestic Workers per 1,000 Older Persons (60+)"
            ]
        )

        indicator_map = {
            "Total Population": "Total",
            "Male Population": "Male",
            "Female Population": "Female",
            "Children Population (0-17)":
                "children_0_17",
            "Children Population (0-5)":
                "children_0_5",
            "Children Population (6-17)":
                "children_6_17",
            "Working Age Population":
                "working_age",
            "Older Persons Population":
                "elderly",
            "Children Share (%)":
                "children_pct",
            "Older Persons Share (%)":
                "elderly_pct",
            "Population Density":
                "population_density",
            "Domestic Workers Population":
                "domestic_workers_total",
            "Domestic Workers per 1,000 Children (0-5)":
                "domestic_workers_per_1000_children",
            "Domestic Workers per 1,000 Older Persons (60+)":
                "domestic_workers_per_1000_elderly"
        }

        selected_col = indicator_map[indicator]

        indicator_descriptions = {
            "Total Population":
                "Total number of residents recorded in each barangay.",
            "Male Population":
                "Number of male residents recorded in each barangay.",
            "Female Population":
                "Number of female residents recorded in each barangay.",
            "Children Population (0-17)":
                "Combined count of residents aged 0–5 and 6–17, "
                "the population segment most dependent on schools, "
                "childcare, and pediatric health services.",
            "Children Population (0-5)":
                "Residents aged 0–5 (early childhood), the segment "
                "most dependent on childcare and ECCD services.",
            "Children Population (6-17)":
                "Residents aged 6–17 (school age), the segment "
                "most dependent on schools and pediatric health "
                "services.",
            "Working Age Population":
                "Residents aged 18–59, the segment that typically "
                "supports the local economy and tax base.",
            "Older Persons Population":
                "Residents aged 60 and above, a key group for "
                "senior care planning and health services.",
            "Children Share (%)":
                "Percentage of the barangay's population aged 0–17. "
                "Higher values signal greater demand for schools "
                "and child-focused services.",
            "Older Persons Share (%)":
                "Percentage of the barangay's population aged 60+. "
                "Higher values signal greater demand for older persons "
                "care and health services.",
            "Population Density":
                "Residents per square kilometer. Higher density "
                "areas typically need more concentrated infrastructure "
                "and service delivery points.",
            "Domestic Workers Population":
                "Registered domestic workers, by barangay (raw count). "
                "Source: processed/editable/demographics_by_barangay.csv.",
            "Domestic Workers per 1,000 Children (0-5)":
                "Registered domestic workers per 1,000 children (aged "
                "0-5) in the barangay, a rough proxy for how much "
                "paid care support exists relative to the number of "
                "young children who may need it.",
            "Domestic Workers per 1,000 Older Persons (60+)":
                "Registered domestic workers per 1,000 older persons "
                "(60+) in the barangay, a rough proxy for how much "
                "paid care support exists relative to the number of "
                "older persons who may need it."
        }

        st.caption(indicator_descriptions[indicator])

        # ---------------------------------------------------
        # CHOROPLETH FILL COLORS (continuous, Purples ramp,
        # clipped to 5th-95th percentile, same clipping the
        # Plotly version used via update_coloraxes)
        # ---------------------------------------------------

        vmin = barangay_df[selected_col].quantile(0.05)
        vmax = barangay_df[selected_col].quantile(0.95)

        barangay_df["fill_color"] = barangay_df[selected_col].apply(
            lambda v: value_to_rgba(v, vmin, vmax)
        )

        barangay_geojson = json.loads(
            barangay_df.to_json()
        )

        # ---------------------------------------------------
        # VIEW STATE, locked to the same zoom range as the
        # other maps in this dashboard, so users can't zoom
        # out past the city boundary
        # ---------------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            min_zoom=11,
            max_zoom=17,
        )

        choropleth_layer = pdk.Layer(
            "GeoJsonLayer",
            data=barangay_geojson,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[102, 102, 102],
            line_width_min_pixels=0.5,
            pickable=True,
            auto_highlight=True
        )

        tooltip = {
            "html": f"""
            <b>{{Barangay}}</b><br/>
            District: {{District}}<br/>
            {indicator}: {{{selected_col}}}
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "12px"
            }
        }

        deck = pdk.Deck(
            layers=[
                choropleth_layer,
                load_reservoir_layer()
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-1"):
            # pydeck has no built-in colorbar (unlike Plotly's
            # automatic color_continuous_scale legend), so the
            # fill color here would otherwise be unexplained.
            # render_colormap_legend_html builds the same kind of
            # gradient-bar legend already used for the climate
            # raster layers elsewhere in this app, reusing the
            # same vmin/vmax (5th-95th percentile clip) that was
            # used to compute fill_color above, so the legend
            # matches what's actually drawn on the map.
            indicator_units = {
                "Children Share (%)": "%",
                "Older Persons Share (%)": "%",
                "Population Density": "people/km²",
                "Domestic Workers per 1,000 Children (0-5)": "/1,000 children",
                "Domestic Workers per 1,000 Older Persons (60+)": "/1,000 older persons"
            }

            st.markdown(
                render_colormap_legend_html(
                    "Purples",
                    vmin,
                    vmax,
                    unit=indicator_units.get(indicator, ""),
                    label=f"{indicator} (darker = higher)"
                ),
                unsafe_allow_html=True
            )

            st.pydeck_chart(
                deck,
                height=650
            )

        st.divider()

        # ---------------------------------------------------
        # TOP / BOTTOM BARANGAYS, POPULATION DENSITY
        # ---------------------------------------------------

        st.subheader("Population Density by Barangay")

        st.caption(
            "Population density (people per square kilometer) varies dramatically across barangays. "
            "The highest-density areas (urban cores) may have 20,000+ people/km², while "
            "lowest-density areas (peripheral) may have under 1,000 people/km². "
            "Note: X-axis scales differ to show meaningful variation in each range."
        )

        col_den1, col_den2 = st.columns(2)

        top_den = (
            barangay_df[["Barangay", "District", "population_density"]]
            .dropna()
            .sort_values("population_density", ascending=False)
            .head(10)
        )

        bottom_den = (
            barangay_df[["Barangay", "District", "population_density"]]
            .dropna()
            .sort_values("population_density", ascending=True)
            .head(10)
        )

        with col_den1:
            fig_top_den = px.bar(
                top_den.sort_values("population_density"),
                x="population_density",
                y="Barangay",
                orientation="h",
                title="Highest-Density Barangays: Urban Core Infrastructure Pressure Points",
                color_discrete_sequence=["#7F47ED"]
            )
            fig_top_den.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Population Density"
            )
            with st.container(border=True, key="qcd-chart-2"):
                st.plotly_chart(fig_top_den, use_container_width=True)

        with col_den2:
            fig_bottom_den = px.bar(
                bottom_den.sort_values("population_density", ascending=False),
                x="population_density",
                y="Barangay",
                orientation="h",
                title="Lowest-Density Barangays: Hard-to-Reach Service Gaps",
                color_discrete_sequence=["#80AA31"]
            )
            fig_bottom_den.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Population Density"
            )
            with st.container(border=True, key="qcd-chart-3"):
                st.plotly_chart(fig_bottom_den, use_container_width=True)

        st.divider()

        st.subheader(
            f"Top 15 Barangays by {indicator}"
        )

        with st.container(border=True, key="qcd-chart-4"):
            st.dataframe(
                barangay_df[
                    [
                        "Barangay",
                        "District",
                        selected_col
                    ]
                ]
                .sort_values(
                    selected_col,
                    ascending=False
                )
                .head(15),
                width="stretch"
            )

    # =====================================================
    # DISTRICT TAB
    # =====================================================
    with tab2:

        # ---------------------------------------------------
        # DISTRICT AGGREGATION
        # ---------------------------------------------------

        district_pop = (
            population_age
            .groupby("District")
            .sum(numeric_only=True)
            .reset_index()
        )

        district_sex = (
            population_sex
            .groupby("District")
            .agg(
                Male=("Male", "sum"),
                Female=("Female", "sum")
            )
            .reset_index()
        )

        district_pop = district_pop.merge(
            district_sex,
            on="District",
            how="left"
        )

        district_pop["Sex Ratio"] = (
            district_pop["Male"]
            /
            district_pop["Female"]
            * 100
        )

        # ---------------------------------------------------
        # STANDARDIZE DISTRICT IDS
        # ---------------------------------------------------

        district_pop["District"] = (
            district_pop["District"]
            .astype(str)
            .str.extract(r"(\d+)")[0]
        )

        district_map["district"] = (
            district_map["district"]
            .astype(str)
            .str.extract(r"(\d+)")[0]
        )

        district_geo = district_map.merge(
            district_pop,
            left_on="district",
            right_on="District",
            how="left"
        )

        # ---------------------------------------------------
        # DISTRICT MAP, kept to the indicators that matter
        # most for resource planning (dropped raw M/F split
        # from the map; that's better shown as the pyramid
        # and ratio chart below)
        # ---------------------------------------------------

        district_indicator = st.selectbox(
            "District Indicator",
            [
                "Total Population",
                "Early Childhood (0-5)",
                "School Age (6-17)",
                "Working Age (18-59)",
                "Older Persons (60+)"
            ],
            key="district_indicator"
        )

        district_col_map = {
            "Total Population": "Total",
            "Early Childhood (0-5)":
                "0-5 (Early Childhood)",
            "School Age (6-17)":
                "6-17 (School Age Children)",
            "Working Age (18-59)":
                "18-59 (Working Age Adult)",
            "Older Persons (60+)":
                "60+ (Older Persons)"
        }

        district_col = district_col_map[
            district_indicator
        ]

        district_indicator_descriptions = {
            "Total Population":
                "Total number of residents recorded in each district.",
            "Early Childhood (0-5)":
                "Residents aged 0–5, the segment most dependent on "
                "daycare and early childhood health services.",
            "School Age (6-17)":
                "Residents aged 6–17, the segment that drives demand "
                "for schools and youth programs.",
            "Working Age (18-59)":
                "Residents aged 18–59, the segment that typically "
                "supports the local economy and tax base.",
            "Older Persons (60+)":
                "Residents aged 60 and above, a key group for "
                "senior care planning and health services."
        }

        st.caption(
            district_indicator_descriptions[district_indicator]
        )

        # ---------------------------------------------------
        # CHOROPLETH FILL COLORS (continuous, Purples ramp,
        # full min/max range, this map had no percentile
        # clipping in the Plotly version, so none is added
        # here either)
        # ---------------------------------------------------

        district_vmin = district_geo[district_col].min()
        district_vmax = district_geo[district_col].max()

        district_geo["fill_color"] = district_geo[district_col].apply(
            lambda v: value_to_rgba(v, district_vmin, district_vmax)
        )

        district_geojson = json.loads(
            district_geo.to_json()
        )

        # ---------------------------------------------------
        # VIEW STATE, locked to the same zoom range as the
        # other maps in this dashboard, so users can't zoom
        # out past the city boundary
        # ---------------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            min_zoom=11,
            max_zoom=17,
        )

        district_choropleth_layer = pdk.Layer(
            "GeoJsonLayer",
            data=district_geojson,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[102, 102, 102],
            line_width_min_pixels=0.5,
            pickable=True,
            auto_highlight=True
        )

        tooltip = {
            "html": f"""
            <b>District {{District}}</b><br/>
            {district_indicator}: {{{district_col}}}
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "12px"
            }
        }

        deck = pdk.Deck(
            layers=[
                district_choropleth_layer,
                load_reservoir_layer()
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-5"):
            st.markdown(
                render_colormap_legend_html(
                    colormap="Purples",
                    vmin=district_vmin,
                    vmax=district_vmax,
                    unit="residents",
                    label=f"{district_indicator} by District (darker = higher)"
                ),
                unsafe_allow_html=True
            )
            st.pydeck_chart(
                deck,
                height=650
            )

        st.divider()

        # ---------------------------------------------------
        # DISTRICT AGE STRUCTURE (stacked bars)
        # ---------------------------------------------------

        district_age_long = district_pop.melt(
            id_vars="District",
            value_vars=age_cols,
            var_name="Age Group",
            value_name="Population"
        )

        # Format district names for consistency across all pages
        district_age_long["District"] = format_district(
            district_age_long["District"]
        )

        fig_age = px.bar(
            district_age_long,
            x="District",
            y="Population",
            color="Age Group",
            title="Age Structure Imbalances by District: Resource Demand Implications",
            barmode="stack",
            color_discrete_sequence=QCD_CATEGORICAL
        )

        fig_age.update_layout(height=450)

        with st.container(border=True, key="qcd-chart-6"):
            st.plotly_chart(
                fig_age,
                use_container_width=True
            )

        st.divider()

        # ---------------------------------------------------
        # POPULATION PYRAMID (City-wide, Male vs Female)
        # ---------------------------------------------------

        st.subheader("Population Pyramid, Male vs Female")

        fig_pyramid = go.Figure()

        fig_pyramid.add_trace(
            go.Bar(
                y=["Male"],
                x=[-total_male],
                name="Male",
                orientation="h",
                marker_color="#7F47ED"
            )
        )

        fig_pyramid.add_trace(
            go.Bar(
                y=["Female"],
                x=[total_female],
                name="Female",
                orientation="h",
                marker_color="#80AA31"
            )
        )

        fig_pyramid.update_layout(
            barmode="overlay",
            title="Gender Ratio Stability (Opportunity for Mixed-Gender Service Design)",
            xaxis=dict(
                tickvals=[-total_male, 0, total_female],
                ticktext=[
                    f"{total_male:,.0f}",
                    "0",
                    f"{total_female:,.0f}"
                ],
                title="Population"
            ),
            height=250,
            margin=dict(l=0, r=0, t=40, b=0)
        )

        col_pyr1, col_pyr2 = st.columns([2, 1])

        with col_pyr1:
            with st.container(border=True, key="qcd-chart-7"):
                st.plotly_chart(fig_pyramid, use_container_width=True)

        with col_pyr2:
            # Format district names for consistency
            ratio_data = district_pop.sort_values(
                "Sex Ratio",
                ascending=False
            ).copy()
            ratio_data["District"] = format_district(
                ratio_data["District"]
            )

            fig_ratio = px.bar(
                ratio_data,
                x="District",
                y="Sex Ratio",
                title="Sex Ratio Outliers by District: Migration or Demographic Anomalies",
                color_discrete_sequence=["#7F47ED"]
            )
            fig_ratio.add_hline(
                y=100,
                line_dash="dash",
                line_color="gray",
                annotation_text="Parity (100)"
            )
            fig_ratio.update_layout(
                height=250,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            with st.container(border=True, key="qcd-chart-8"):
                st.plotly_chart(fig_ratio, use_container_width=True)

        st.divider()

        # ---------------------------------------------------
        # DISTRICT SUMMARY TABLE
        # ---------------------------------------------------

        district_summary = (
            population_sex
            .groupby("District")
            .agg(
                Population=("Total", "sum"),
                Male=("Male", "sum"),
                Female=("Female", "sum"),
                Barangays=("Barangay", "nunique")
            )
            .reset_index()
            .sort_values(
                "Population",
                ascending=False
            )
        )

        district_summary["Male %"] = (
            district_summary["Male"]
            /
            district_summary["Population"]
            * 100
        ).round(1)

        district_summary["Female %"] = (
            district_summary["Female"]
            /
            district_summary["Population"]
            * 100
        ).round(1)

        st.subheader(
            "District Demographic Summary"
        )

        with st.container(border=True, key="qcd-chart-9"):
            st.dataframe(
                district_summary,
                width="stretch"
            )

        # ---------------------------------------------------
        # NEW: DISTRICT DEMOGRAPHICS PROFILE
        # (Enhanced with district-level indicators)
        # ---------------------------------------------------

        st.divider()
        st.markdown("### District Demographic Profiles")

        selected_district = st.selectbox(
            "View detailed profile for:",
            options=sorted(demographics_district["district"].unique()),
            format_func=lambda x: f"District {int(x)}",
            key="district_profile_selector"
        )

        district_profile = demographics_district[
            demographics_district["district"] == selected_district
        ].iloc[0]

        # Three-column KPI layout
        p_col1, p_col2, p_col3 = st.columns(3)

        kpi_card(
            p_col1,
            "Total Population",
            f"{district_profile['pop_census']:,.0f}",
            polarity="down_good"
        )

        kpi_card(
            p_col2,
            "Population Density",
            f"{district_profile['pop_density_km2']:,.0f}",
            caption="per km²"
        )

        kpi_card(
            p_col3,
            "Disability Prevalence",
            f"{district_profile['disability_prevalence_rate_pct']:.2f}%",
            caption="of population"
        )

        # Socioeconomic indicators
        se_col1, se_col2, se_col3 = st.columns(3)

        kpi_card(
            se_col1,
            "Food Insecurity",
            f"{district_profile['cbms_food_insecurity_prevalence_pct_hhw']:.1f}%",
            caption="households"
        )

        kpi_card(
            se_col2,
            "Housing Inadequacy",
            f"{district_profile['cbms_housing_inadequacy_index_pct_hhw']:.1f}%",
            caption="households"
        )

        kpi_card(
            se_col3,
            "Avg Household Size",
            f"{district_profile['cbms_avg_household_size_hhw']:.2f}",
            caption="people per HH"
        )

        # Age distribution
        age_dist = pd.DataFrame({
            "Age Group": ["0-5", "6-17", "18-59", "60+"],
            "Male": [
                district_profile["age_0_5_m"],
                district_profile["age_6_17_m"],
                district_profile["age_18_59_m"],
                district_profile["age_60plus_m"]
            ],
            "Female": [
                district_profile["age_0_5_f"],
                district_profile["age_6_17_f"],
                district_profile["age_18_59_f"],
                district_profile["age_60plus_f"]
            ]
        })

        fig_dist_age = px.bar(
            age_dist,
            x="Age Group",
            y=["Male", "Female"],
            barmode="group",
            title=f"District {int(selected_district)} Population by Age & Gender",
            color_discrete_map={"Male": "#4472C4", "Female": "#ED7D31"},
            labels={"value": "Population"}
        )
        fig_dist_age.update_layout(height=350, hovermode="x unified")

        with st.container(border=True, key="qcd-chart-district-age"):
            st.plotly_chart(fig_dist_age, use_container_width=True)

        # Vulnerable populations in this district
        vuln_col1, vuln_col2, vuln_col3, vuln_col4 = st.columns(4)

        kpi_card(
            vuln_col1,
            "Registered Seniors (60+)",
            f"{int(district_profile['seniors_registered']):,.0f}",
            caption=f"{district_profile['seniors_per_1000_census']:.1f} per 1k"
        )

        kpi_card(
            vuln_col2,
            "Registered Persons with Disabilities",
            f"{int(district_profile['pwd_registered']):,.0f}",
            caption=f"{district_profile['pwd_per_1000_census']:.1f} per 1k"
        )

        kpi_card(
            vuln_col3,
            "Migrant Workers (Total)",
            f"{int(district_profile['migrant_workers_total']):,.0f}",
            caption=f"{district_profile['migrant_workers_male']:.0f}M, {district_profile['migrant_workers_female']:.0f}F"
        )

        # Domestic workers live in a separate source
        # (domestic_workers_district, from load_domestic_workers()
        # in functions.py) rather than demographics_district, so
        # it's looked up by district here rather than pulled
        # straight off district_profile like the KPIs above.
        dw_district_row = domestic_workers_district[
            domestic_workers_district["district"] == int(selected_district)
        ]

        dw_district_total = (
            dw_district_row["domestic_workers_total"].iloc[0]
            if not dw_district_row.empty else 0
        )

        dw_district_male = (
            dw_district_row["domestic_workers_male"].iloc[0]
            if not dw_district_row.empty else 0
        )

        dw_district_female = (
            dw_district_row["domestic_workers_female"].iloc[0]
            if not dw_district_row.empty else 0
        )

        kpi_card(
            vuln_col4,
            "Registered Domestic Workers",
            f"{int(dw_district_total):,.0f}",
            caption=f"{dw_district_male:.0f}M, {dw_district_female:.0f}F"
        )

        # Vulnerability comparison across all districts
        st.markdown("### Socioeconomic Vulnerability Across All Districts")

        vuln_comparison = demographics_district[[
            "district",
            "disability_prevalence_rate_pct",
            "cbms_food_insecurity_prevalence_pct_hhw",
            "cbms_housing_inadequacy_index_pct_hhw"
        ]].copy()

        vuln_comparison.columns = [
            "District",
            "Disability (%)",
            "Food Insecurity (%)",
            "Housing Inadequacy (%)"
        ]

        fig_vuln = px.bar(
            vuln_comparison,
            x="District",
            y=["Disability (%)", "Food Insecurity (%)", "Housing Inadequacy (%)"],
            title="Vulnerability Indicators by District",
            barmode="group",
            color_discrete_map={
                "Disability (%)": "#7F47ED",
                "Food Insecurity (%)": "#FF6B6B",
                "Housing Inadequacy (%)": "#FFA500"
            }
        )
        fig_vuln.update_xaxes(tickformat="d")
        fig_vuln.update_layout(height=400, hovermode="x unified")

        with st.container(border=True, key="qcd-chart-district-vuln"):
            st.plotly_chart(fig_vuln, use_container_width=True)

    # =====================================================
    # SOCIO-ECONOMIC TAB
    # =====================================================

if page == "Childcare Centers":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Childcare Facilities
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Explore the spatial distribution of childcare facilities in Quezon City,
    including Child Development Centers, Child Learning Centers, Day Care
    Centers, and Supervised Neighborhood Play facilities. Each facility's
    public or private classification is noted in its individual details.
    """)

    st.markdown("""
    **ECCD (Early Childhood Care and Development)** refers to comprehensive support for children aged 0–5,
    including nutrition, health, learning, and psychosocial development. **ECCD Coverage** is the percentage of
    barangays with at least one registered childcare facility (CDC, child learning center, or day care center).
    """)

    # --------------------------------------------------
    # CHILDCARE KPIs
    # --------------------------------------------------

    childcare_summary = compute_childcare_summary(childcare_centers)

    total_centers = int(
        childcare_summary.loc[
            childcare_summary["metric"]
            == "child_development_centers",
            "value"
        ].iloc[0]
    )

    total_facilities = len(childcare_centers)

    day_care_centers = (
        childcare_centers["Category"]
        .str.contains(
            "Day Care",
            case=False,
            na=False
        )
        .sum()
    )

    supervised_play_centers = (
        childcare_centers["Category"]
        .str.contains(
            "Supervised Neighborhood Play",
            case=False,
            na=False
        )
        .sum()
    )

    # normalize_barangay_names() first — raw ALL-CAPS/abbreviated
    # spellings (e.g. "MARIANA" vs "Mariana") otherwise double-count
    # the same barangay, which can push this past the real 142-
    # barangay ceiling.
    covered_barangays = (
        normalize_barangay_names(childcare_centers["barangay"])
        .nunique()
    )

    covered_districts = (
        childcare_centers["District"]
        .nunique()
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    kpi_card(
        k1,
        "Facilities",
        f"{total_facilities:,}",
        "up_good"
    )

    kpi_card(
        k2,
        "Barangays Served",
        f"{covered_barangays:,}",
        "up_good"
    )

    kpi_card(
        k3,
        "CDCs",
        f"{total_centers:,}",
        "up_good"
    )

    kpi_card(
        k4,
        "Day Care Centers",
        f"{day_care_centers:,}"
    )

    kpi_card(
        k5,
        "Supervised Neighborhood Play",
        f"{supervised_play_centers:,}"
    )

    st.divider()

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        childcare_centers["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in districts]
    )

    st.info("Hover over a facility to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    cc = childcare_centers.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        cc = cc[
            cc["District"] == district_number
        ]

    if selected_childcare_category != "All":

        cc = cc[
            cc["Category"]
            .str.contains(
                selected_childcare_category,
                case=False,
                na=False
            )
        ]

    if selected_childcare_source != "All":

        cc = cc[
            cc["data_source"] == selected_childcare_source
        ]

    # --------------------------------------------------
    # COLOR CONVERSION
    # --------------------------------------------------

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")

        return [
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        ]

    colors = [
        hex_to_rgb(
            childcare_color(cat)
        )
        for cat in cc["Category"].astype(str)
    ]

    cc["r"] = [c[0] for c in colors]
    cc["g"] = [c[1] for c in colors]
    cc["b"] = [c[2] for c in colors]

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # BARANGAY BOUNDARIES
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False
    )

    # --------------------------------------------------
    # CHILDCARE POINTS
    # --------------------------------------------------

    childcare_layer = pdk.Layer(
        "ScatterplotLayer",
        data=cc,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    tooltip = {
        "html": """
        <b>{Name}</b><br/>
        Category: {Category}<br/>
        Provider Type: {Sector}<br/>
        District: {District}<br/>
        Address: {Address}<br/>
        Open: {open_hours}<br/>
        Close: {close_hours}<br/>
        Source: {data_source}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            childcare_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"

    )

    with st.container(border=True, key="qcd-chart-12"):
        st.pydeck_chart(
            deck,
            height=700
        )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------


    st.subheader("Facilities")

    _cc_disp = cc[["Name","Category","Sector","District","barangay","Address"]].copy()
    with st.container(border=True, key="qcd-chart-13"):
        st.dataframe(
            _cc_disp[["Name","Category","Sector","District","Address"]].rename(
                columns={"Sector": "Provider Type"}
            ),
            width='stretch'
        )
    # --------------------------------------------------
    # CHILDCARE ANALYTICS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        category_counts = (
            childcare_centers["Category"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Facilities"
        ]

        fig = px.bar(
            category_counts,
            x="Category",
            y="Facilities",
            title="Childcare Facilities Across Service Types",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-14"):
            st.plotly_chart(
                fig
            )

    with col2:

        district_counts = (
            childcare_centers
            .groupby("District")
            .size()
            .reset_index(name="Facilities")
            .sort_values(
                "Facilities",
                ascending=False
            )
        )

        # Format district names for consistency
        district_counts["District"] = format_district(
            district_counts["District"]
        )

        fig = px.bar(
            district_counts,
            x="District",
            y="Facilities",
            title="Childcare Infrastructure Gaps by District",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-15"):
            st.plotly_chart(
                fig
            )

    early_childhood_population = (
        population_age[
            "0-5 (Early Childhood)"
        ]
        .sum()
    )

    children_per_center = (
        early_childhood_population
        / total_centers
    )

    # % of barangays with at least one childcare facility (CDC,
    # child learning center, or day care center) — matches the
    # "ECCD Coverage" definition given in this page's intro text
    # above. total_barangays is read from population_age rather
    # than hardcoded, so this stays correct at exactly 142.
    total_barangays = population_age["Barangay"].nunique()

    eccd_coverage_pct = (
        covered_barangays
        / total_barangays
        * 100
    )

    c1, c2, c3 = st.columns(3)

    kpi_card(
        c1,
        "Children (0-5)",
        f"{early_childhood_population:,.0f}"
    )

    kpi_card(
        c2,
        "Children per CDC",
        f"{children_per_center:.0f}",
        "down_good"
    )

    kpi_card(
        c3,
        "ECCD Coverage",
        f"{eccd_coverage_pct:.1f}%",
        "up_good"
    )

elif page == "Schools":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Schools
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Explore the spatial distribution of schools across Quezon City,
    including both public and private educational institutions.
    """)

    # KPIS
    # care_supply_facilities.csv lists one row per grade level a
    # school offers (a school running Preschool through Junior
    # High appears as up to 4 rows sharing the same name and
    # location) — deduplicated here the same way as
    # compute_facility_counts_by_barangay(), so these KPIs count
    # physical schools rather than grade-level program rows.
    #
    # Sourced from load_all_schools() rather than the page's own
    # `schools` variable: `schools` (from load_data()) only
    # includes rows with mappable coordinates, since that's what
    # the map on this page needs — but barangay/district
    # assignment doesn't depend on having coordinates, so these
    # KPIs would undercount otherwise. load_all_schools() includes
    # every school on file.
    schools_deduped = (
        load_all_schools()
        .drop_duplicates(subset=["barangay", "Name"])
    )

    total_schools = len(schools_deduped)

    public_schools = (
        schools_deduped["Sector"]
        .str.contains(
            "Public",
            case=False,
            na=False
        )
        .sum()
    )

    private_schools = (
        schools_deduped["Sector"]
        .str.contains(
            "Private",
            case=False,
            na=False
        )
        .sum()
    )

    # normalize_barangay_names() first — see the same fix on the
    # Childcare page for why raw casing double-counts barangays.
    covered_barangays = (
        normalize_barangay_names(schools["barangay"])
        .nunique()
    )

    covered_districts = (
        schools["District"]
        .nunique()
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    kpi_card(
        k1,
        "Total Schools",
        f"{total_schools:,}",
        "up_good"
    )

    kpi_card(
        k2,
        "Barangays Served",
        f"{covered_barangays:,}",
        "up_good"
    )

    kpi_card(
        k3,
        "Districts Served",
        f"{covered_districts:,}",
        "up_good"
    )

    kpi_card(
        k4,
        "Public",
        f"{public_schools:,}"
    )

    kpi_card(
        k5,
        "Private",
        f"{private_schools:,}"
    )

    st.divider()

    # Preschool-relevant population is ages 3-5, not the full 0-5
    # early-childhood band (ages 0-2 aren't school-age) — same
    # age_3_5 column already used by the Schools accessibility
    # ratio ("School Facilities per 1,000 Children (3-5)" in
    # ACCESSIBILITY_RATIO_INDICATORS), pulled from `demographics`
    # since population_age only carries the wider 0-5 band.
    preschool_age_population = (
        demographics["age_3_5"]
        .sum()
    )

    school_age_6_17_population = (
        population_age[
            "6-17 (School Age Children)"
        ]
        .sum()
    )

    # Schools cover the full 3-17 range (Preschool through Senior
    # High), not just the 6-17 band, so the KPI's primary value is
    # the combined total with the two bands broken out in the
    # caption rather than only showing 6-17.
    school_age_population = (
        preschool_age_population
        + school_age_6_17_population
    )

    children_per_school = (
        school_age_population
        / total_schools
    )

    c1, c2 = st.columns(2)

    kpi_card(
        c1,
        "School-Age Population (3-17)",
        f"{school_age_population:,.0f}",
        caption=(
            f"{preschool_age_population:,.0f} (3-5) · "
            f"{school_age_6_17_population:,.0f} (6-17)"
        )
    )

    kpi_card(
        c2,
        "Children per School",
        f"{children_per_school:,.0f}",
        "down_good"
    )

    st.divider()



    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        schools["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in districts]
    )

    st.info("Hover over a school to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    sch = schools.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        sch = sch[
            sch["District"].astype(int)
            == district_number
        ]

    if selected_school_sector != "All":

        sch = sch[
            sch["Sector"]
            .str.contains(
                selected_school_sector,
                case=False,
                na=False
            )
        ]

    if selected_school_category != "All":

        # Exact match, not .str.contains(): "High school" is a
        # substring of "Junior high school" and "Senior high
        # school", so a contains-based filter here pulls in both
        # of those whenever "High school" is selected.
        sch = sch[
            sch["Category"] == selected_school_category
        ]

    if selected_school_source != "All":

        sch = sch[
            sch["data_source"] == selected_school_source
        ]

    # --------------------------------------------------
    # MISSING COORDINATES
    # --------------------------------------------------

    missing_locations = (
        sch["latitude"].isna() |
        sch["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} schools do not have coordinates and are not shown on the map."
        )

    sch = sch.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLOR CONVERSION
    # --------------------------------------------------

    def hex_to_rgb(hex_color):

        hex_color = hex_color.lstrip("#")

        return [
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        ]

    colors = [
        hex_to_rgb(
            school_color(cat)
        )
        for cat in sch["Category"].astype(str)
    ]

    sch["r"] = [c[0] for c in colors]
    sch["g"] = [c[1] for c in colors]
    sch["b"] = [c[2] for c in colors]

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # BARANGAY POLYGONS
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False

    )

    # --------------------------------------------------
    # SCHOOL POINTS
    # --------------------------------------------------

    sch["tooltip_html"] = build_tooltip_html(
        sch, "Name",
        [
            ("Provider Type", "Sector"),
            ("Category", "Category"),
            ("District", "District"),
            ("Address", "Address"),
            ("Open", "open_hours"),
            ("Close", "close_hours"),
            ("Source", "data_source"),
        ]
    )

    # get_line_color used to match get_fill_color exactly (no
    # border contrast at all). That's invisible in practice for
    # "Special Education Program", whose color (#D9E6F7) is a
    # very pale near-white — with no outline it disappears into
    # the light basemap entirely, which is why those dots showed
    # up in the table but not on the map. A fixed dark outline
    # gives every category a visible edge regardless of how pale
    # its fill color is.
    school_layer = pdk.Layer(
        "ScatterplotLayer",
        data=sch,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True,
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    

    tooltip = {
        "html": "{tooltip_html}",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            school_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"

    )

    with st.container(border=True, key="qcd-chart-16"):
        st.pydeck_chart(
            deck,
            height=700
        )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.subheader("Schools")

    _sch_disp = sch[["Name","Sector","Category","District","barangay","Address"]].copy()
    with st.container(border=True, key="qcd-chart-17"):
        st.dataframe(
            _sch_disp[["Name","Sector","Category","District","Address"]],
            width='stretch'
        )
    # --------------------------------------------------
    # SCHOOL KPIs
    # --------------------------------------------------

    # Row 1: Provider Type (Public/Private) and District Distribution
    col1, col2 = st.columns(2)

    with col1:

        # Provider Type Distribution (using Sector column) —
        # deduplicated: Sector is a school-level attribute (a
        # school doesn't change Public/Private status by grade
        # level), so this should reflect physical schools, not
        # one row per grade-level program.
        provider_counts = (
            schools_deduped["Sector"]
            .value_counts()
            .reset_index()
        )

        provider_counts.columns = [
            "Provider",
            "Schools"
        ]

        # Color map for provider types
        provider_colors = [
            "#2E5090" if "Public" in prov else "#B5CBEE"
            for prov in provider_counts["Provider"]
        ]

        fig = px.pie(
            provider_counts,
            names="Provider",
            values="Schools",
            title="School Distribution by Provider Type",
            color_discrete_sequence=provider_colors
        )

        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            texttemplate="%{label}: %{percent:.0%}"
        )

        fig.update_layout(
            showlegend=True,
            uniformtext_minsize=12,
            uniformtext_mode="hide"
        )

        with st.container(border=True, key="qcd-chart-18"):
            st.plotly_chart(
                fig
            )

    with col2:

        # District Distribution
        district_counts = (
            schools_deduped
            .groupby("District")
            .size()
            .reset_index(name="Schools")
            .sort_values(
                "Schools",
                ascending=False
            )
        )

        # Format district names for consistency
        district_counts["District"] = format_district(
            district_counts["District"]
        )

        fig = px.bar(
            district_counts,
            x="District",
            y="Schools",
            text_auto=True,
            title="School Distribution by District",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-19"):
            st.plotly_chart(
                fig
            )

    # Row 2: School Categories and Barangay Distribution
    col3, col4 = st.columns(2)

    with col3:

        # School Categories Distribution (Preschool, Elementary, etc.)
        category_counts = (
            schools["Category"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Schools"
        ]

        school_colors = [
            school_color(cat)
            for cat in category_counts["Category"]
        ]

        fig = px.pie(
            category_counts,
            names="Category",
            values="Schools",
            title="School Distribution by Type",
            color_discrete_sequence=school_colors
        )

        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            texttemplate="%{label}: %{percent:.0%}"
        )

        fig.update_layout(
            showlegend=True,
            uniformtext_minsize=12,
            uniformtext_mode="hide"
        )

        with st.container(border=True, key="qcd-school-categories-chart"):
            st.plotly_chart(
                fig
            )

    with col4:

        # Barangay Distribution (top 15 by count)
        barangay_counts = (
            schools
            .groupby("barangay")
            .size()
            .reset_index(name="Schools")
            .sort_values(
                "Schools",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            barangay_counts,
            x="barangay",
            y="Schools",
            text_auto=True,
            title="Top 15 Barangays by School Count",
            color_discrete_sequence=["#4472C4"]
        )

        fig.update_xaxes(tickangle=-45)

        with st.container(border=True, key="qcd-school-barangay-chart"):
            st.plotly_chart(
                fig
            )
 

    district_schools = (
        schools_deduped
        .groupby("District")
        .size()
        .reset_index(name="Schools")
    )

    district_population = (
        population_age
        .groupby("District")
        [
            "6-17 (School Age Children)"
        ]
        .sum()
        .reset_index()
    )

    district_population = district_population.rename(
        columns={
            "6-17 (School Age Children)":
            "School_Age_Population"
        }
    )

    coverage = district_population.merge(
        district_schools,
        on="District",
        how="left"
    )

    coverage["Schools"] = (
        coverage["Schools"]
        .fillna(0)
    )

    coverage[
        "Children per School"
    ] = (
        coverage["School_Age_Population"]
        / coverage["Schools"]
    ).round(0)

    st.subheader(
        "School Coverage by District"
    )

    with st.container(border=True, key="qcd-chart-20"):
        st.dataframe(
            coverage.sort_values(
                "Children per School",
                ascending=False
            ),
            width="stretch"
        )

    barangay_counts = (
        schools_deduped
        .groupby("barangay")
        .size()
        .reset_index(name="Schools")
        .sort_values(
            "Schools",
            ascending=False
        )
        .head(10)
    )

    st.subheader(
        "Top Barangays by Number of Schools"
    )

    with st.container(border=True, key="qcd-chart-21"):
        st.dataframe(
            barangay_counts,
            width='stretch'
        )

elif page == "Health Centers Map":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:0px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Health Centers & Hospitals
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Explore the spatial distribution of healthcare facilities in Quezon City.
    The map supports the assessment of access to primary healthcare services,
    facility coverage, and the availability of pharmacies across districts.
    """)

    # --------------------------------------------------
    # HEALTH KPIs
    # --------------------------------------------------

    health_capacity = pd.read_csv(
        "processed/editable/health_centers_and_doctors_per_district.csv"
    )

    # The district column in this CSV has inconsistent spacing
    # between "District" and the number (e.g. "District  2" with
    # two spaces vs. "District 1" with one), collapse it once
    # here, right after loading, so every chart/table built from
    # health_capacity downstream (Health Centers by District,
    # Doctors vs Health Centers, Health Coverage by District)
    # sees clean, consistent labels and merges correctly against
    # the "District N" strings built elsewhere in this page.
    health_capacity["district"] = (
        health_capacity["district"]
        .astype(str)
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
        .str.strip()
    )

    total_facilities = len(health_centers)

    total_doctors = (
        health_capacity["doctors"]
        .fillna(0)
        .sum()
    )

    # All four KPIs below compare against the mapped tier names from
    # HEALTH_CATEGORY_COLORS ("Health Centers", "Super Health
    # Centers", etc.), not the raw Category values ("Health center",
    # "Super health care center", etc.) — comparing the raw column
    # directly against these tier names always returned 0 for every
    # one of them. Mapped through health_category_mapper() first,
    # the same function the sidebar filter and marker colors use, so
    # all three stay in agreement about what belongs in each tier.
    _health_tiers = health_centers["Category"].apply(health_category_mapper)

    health_centers_count = (_health_tiers == "Health Centers").sum()

    super_health_centers = (_health_tiers == "Super Health Centers").sum()

    pharmacies = (_health_tiers == "Health Centers with Pharmacy").sum()

    # All three hospital tiers combined — previously this only
    # counted "National"/"QC LGU", which silently included
    # LGU-run lying-in clinics (not hospitals) while excluding the
    # generic, unqualified "Private Hospitals" rows entirely.
    hospitals = _health_tiers.isin([
        "QC LGU-run Hospitals",
        "National Government Hospitals",
        "Private Hospitals",
    ]).sum()

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    kpi_card(
        k1,
        "Facilities",
        f"{total_facilities:,}",
        "up_good"
    )

    kpi_card(
        k2,
        "Doctors",
        f"{int(total_doctors):,}",
        "up_good"
    )

    kpi_card(
        k3,
        "Health Centers",
        f"{health_centers_count:,}",
        "up_good"
    )

    kpi_card(
        k4,
        "Super Health",
        f"{super_health_centers:,}",
        "up_good"
    )

    kpi_card(
        k5,
        "Hospitals",
        f"{hospitals:,}",
        "up_good"
    )

    kpi_card(
        k6,
        "Pharmacies",
        f"{pharmacies:,}",
        "up_good"
    )

    st.divider()
    
    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        health_centers["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in districts]
    )

    st.info("Hover over a facility to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    hc = health_centers.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        hc = hc[
            hc["District"].astype(int)
            == district_number
        ]

    if selected_category != "All":

        # Filter options are the mapped tier names from
        # HEALTH_CATEGORY_COLORS ("QC LGU-run Hospitals", etc.), not
        # the raw Category values ("LGU-run hospital", "Super health
        # care center", etc.) — comparing directly against the raw
        # column always returned zero rows for every option except
        # "All". Map each row's Category through
        # health_category_mapper() first, the same function that
        # already assigns marker colors, so this filter and the map
        # legend agree on what belongs in each tier.
        hc = hc[
            hc["Category"].apply(health_category_mapper) == selected_category
        ]

    if selected_health_source != "All":

        hc = hc[
            hc["data_source"] == selected_health_source
        ]

    # --------------------------------------------------
    # REMOVE MISSING COORDINATES
    # --------------------------------------------------

    hc = hc.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLOR CONVERSION
    # --------------------------------------------------

    def hex_to_rgb(hex_color):

        hex_color = hex_color.lstrip("#")

        return [
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        ]

    colors = [
        hex_to_rgb(
            marker_color(cat)
        )
        for cat in hc["Category"].astype(str)
    ]

    hc["r"] = [c[0] for c in colors]
    hc["g"] = [c[1] for c in colors]
    hc["b"] = [c[2] for c in colors]

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # BARANGAY POLYGONS
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False
    )

    # --------------------------------------------------
    # HEALTH FACILITIES
    # --------------------------------------------------

    hc["tooltip_html"] = build_tooltip_html(
        hc, "Name",
        [
            ("Category", "Category"),
            ("Provider Type", "Sector"),
            ("District", "District"),
            ("Barangay", "barangay"),
            ("Address", "Address"),
            ("Open", "open_hours"),
            ("Close", "close_hours"),
            ("Source", "data_source"),
        ]
    )

    health_layer = pdk.Layer(
        "ScatterplotLayer",
        data=hc,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    tooltip = {
        "html": "{tooltip_html}",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            health_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-22"):
        st.pydeck_chart(
            deck,
            height=700
        )

    # --------------------------------------------------
    # HEALTH KPIs
    # --------------------------------------------------
    population_sex["Total"] = (
        population_sex["Total"]
        .astype(str)
        .str.replace(",", "")
        .astype(float)
    )

    total_population = (
        population_sex["Total"]
        .sum()
    )

    population_per_doctor = (
        total_population
        / total_doctors
    )

    population_per_health_center = (
        total_population
        / health_centers_count
    )

    c1, c2, c3 = st.columns(3)

    kpi_card(
        c1,
        "Population",
        f"{total_population:,.0f}"
    )

    kpi_card(
        c2,
        "Population / Doctor",
        f"{population_per_doctor:,.0f}",
        "down_good"
    )

    kpi_card(
        c3,
        "Population / Health Center",
        f"{population_per_health_center:,.0f}",
        "down_good"
    )

    st.divider()

    st.subheader(
        "Health Capacity by District"
    )

    district_capacity = (
        health_capacity.copy()
    )

    district_capacity = district_capacity[
        district_capacity["district"]
        .str.upper()
        != "TOTAL"
    ]

    # Format district names for consistency
    # Extract numeric part and reformat
    district_capacity_chart = district_capacity.copy()
    district_capacity_chart["district"] = district_capacity_chart[
        "district"
    ].apply(
        lambda x: format_district(
            extract_district_number(x)
        ) if "District" not in str(x) else x
    )

    fig = px.bar(
        district_capacity_chart,
        x="district",
        y="health_centers",
        title="Health Centers by District",
        text_auto=True,
        color_discrete_sequence=["#7F47ED"]
    )

    with st.container(border=True, key="qcd-chart-23"):
        st.plotly_chart(
            fig
        )

    fig = px.scatter(
        district_capacity,
        x="health_centers",
        y="doctors",
        text="district",
        size="doctors",
        title="Doctors vs Health Centers",
        color_discrete_sequence=["#7F47ED"]
    )

    fig.update_traces(
        textposition="top center"
    )

    with st.container(border=True, key="qcd-chart-24"):
        st.plotly_chart(
            fig
        )

    district_population = (
        population_sex
        .groupby("District")["Total"]
        .sum()
        .reset_index()
    )

    district_population["District"] = (
        "District "
        + district_population["District"]
        .astype(str)
    )

    coverage = district_population.merge(
        health_capacity,
        left_on="District",
        right_on="district",
        how="left"
    )

    # health_capacity["health_centers"] only counts facilities
    # tagged specifically as a "Health Center" in that lookup
    # CSV, it doesn't reflect the full range of health-related
    # facility types (Super Health Centers, pharmacies, national/
    # LGU hospitals, milk banks, etc.) that actually show up on
    # this page's map and in the Category breakdown below.
    # all_health_facilities counts every row in the live
    # health_centers facility data per district, regardless of
    # Category, so this table can show that broader total
    # alongside the narrower CSV-based health_centers/doctors
    # figures rather than implying that "Health Center" is the
    # only category that exists.
    all_health_facilities = (
        health_centers
        .groupby("District")
        .size()
        .reset_index(name="All Health Facilities")
    )

    all_health_facilities["District"] = (
        "District "
        + all_health_facilities["District"]
        .astype(str)
    )

    coverage = coverage.merge(
        all_health_facilities,
        on="District",
        how="left"
    )

    coverage["All Health Facilities"] = (
        coverage["All Health Facilities"]
        .fillna(0)
        .astype(int)
    )

    coverage[
        "Population per Doctor"
    ] = (
        coverage["Total"]
        / coverage["doctors"]
    ).round(0)

    coverage[
        "Population per Health Center"
    ] = (
        coverage["Total"]
        / coverage["health_centers"]
    ).round(0)

    st.subheader(
        "Health Coverage by District"
    )

    st.caption(
        """
        "health_centers" and "doctors" reflect facilities
        specifically tagged as Health Centers in the official
        district capacity records. "All Health Facilities"
        additionally includes Super Health Centers, pharmacies,
        hospitals, and other health-related facility types
        mapped on this page.
        """
    )

    with st.container(border=True, key="qcd-chart-25"):
        st.dataframe(
            coverage[
                [
                    "District",
                    "Total",
                    "health_centers",
                    "All Health Facilities",
                    "doctors",
                    "Population per Doctor",
                    "Population per Health Center"
                ]
            ],
            width="stretch"
        )


    facility_mix = (
        health_centers["Category"]
        .value_counts()
        .reset_index()
    )

    facility_mix.columns = [
        "Facility Type",
        "Count"
    ]

    fig = px.pie(
        facility_mix,
        names="Facility Type",
        values="Count",
        title="Health Facility Composition",
        color_discrete_sequence=QCD_CATEGORICAL
    )

    with st.container(border=True, key="qcd-chart-26"):
        st.plotly_chart(
            fig
        )

elif page == "Older Persons Center Map":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Older Persons & Senior Citizens
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Explore facilities supporting older persons in Quezon City,
    including nursing care centers and Bahay Aruga facilities.
    """)

    # --------------------------------------------------
    # SENIOR CITIZEN KPIs
    # --------------------------------------------------

    # See compute_senior_summary()'s docstring and the "Why don't
    # these figures add up?" note below for why registered_seniors
    # (OSCA) and the rest (2020 Census) are expected to disagree.
    senior_summary = compute_senior_summary(demographics)

    def _senior_metric(metric):
        return int(
            senior_summary.loc[
                senior_summary["metric"] == metric,
                "value"
            ].iloc[0]
        )

    registered_seniors = _senior_metric("registered_seniors")
    female_seniors = _senior_metric("female")
    male_seniors = _senior_metric("male")
    age_60_79 = _senior_metric("age_60_79")
    age_80_plus = _senior_metric("age_80_plus")

    total_facilities = len(
        older_person_care
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    kpi_card(
        k1,
        "Registered Seniors (OSCA)",
        f"{registered_seniors:,}"
    )

    kpi_card(
        k2,
        "Female (Census)",
        f"{female_seniors:,}"
    )

    kpi_card(
        k3,
        "Male (Census)",
        f"{male_seniors:,}"
    )

    kpi_card(
        k4,
        "Age 60-79 (Census)",
        f"{age_60_79:,}"
    )

    kpi_card(
        k5,
        "Age 80+ (Census)",
        f"{age_80_plus:,}"
    )

    kpi_card(
        k6,
        "Care Facilities",
        f"{total_facilities:,}",
        "up_good"
    )

    st.info(
        "**Why don't these figures add up?** \"Registered Seniors\" comes from "
        "OSCA's administrative registry; the sex and age breakdown comes from "
        "the 2020 Census. These are two different sources collected in "
        "different years, so they won't sum to the same total — OSCA's "
        "registry is also cumulative, so seniors who have since passed away "
        "or moved away stay on the count, which is part of why it can run "
        "higher than the Census figure. Both update independently as new "
        "data comes in, so the gap between them will narrow or widen over "
        "time."
    )

    st.divider()


    seniors_per_facility = (
        registered_seniors
        / total_facilities
    )

    kpi_card(
        st,
        "Registered Seniors per Care Facility",
        f"{seniors_per_facility:,.0f}",
        "down_good"
    )

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    district_options = sorted(
        pd.concat(
            [
                older_person_care["District"]
                .dropna()
                .astype(int),
                pd.Series([3, 6])
            ]
        ).unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in district_options],
        key="opc_district"
    )

    st.info("Hover over a facility to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    opc = older_person_care.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        opc = opc[
            opc["District"].astype(int)
            == district_number
        ]

    if selected_opc_category != "All":

        # Exact match, not .str.contains(): several of the
        # reassigned eldercare categories share substrings (e.g.
        # "Residential Care Facility" is itself a substring of
        # "Residential Care Facility and Home Healthcare Service
        # Provider"), same rationale as the Schools category
        # filter above.
        opc = opc[
            opc["Category"] == selected_opc_category
        ]

    if selected_opc_sector != "All":

        opc = opc[
            opc["Sector"] == selected_opc_sector
        ]

    if selected_opc_source != "All":

        opc = opc[
            opc["data_source"] == selected_opc_source
        ]

    # --------------------------------------------------
    # MISSING COORDINATES
    # --------------------------------------------------

    missing_locations = (
        opc["latitude"].isna() |
        opc["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} facilities do not have coordinates and are not shown on the map."
        )

    opc = opc.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLORS
    # --------------------------------------------------

    colors = [
        hex_to_rgb(
            opc_color(cat)
        )
        for cat in opc["Category"].astype(str)
    ]

    opc["r"] = [c[0] for c in colors]
    opc["g"] = [c[1] for c in colors]
    opc["b"] = [c[2] for c in colors]

    # Two facilities (CGNH Nursing Care Facility Services, Wellness
    # Place & Care Homes) weren't part of the eldercare data review
    # that assigned Sector (Public/Private) to every other facility,
    # so they still carry no provider type — the Provider Type
    # line is simply omitted for those two rather than shown blank.
    opc["tooltip_html"] = build_tooltip_html(
        opc, "Name",
        [
            ("Category", "Category"),
            ("Provider Type", "Sector"),
            ("District", "District"),
            ("Barangay", "barangay"),
            ("Address", "Address"),
            ("Open", "open_hours"),
            ("Close", "close_hours"),
            ("Source", "data_source"),
        ]
    )

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # POLYGONS
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False
    )

    # --------------------------------------------------
    # FACILITIES
    # --------------------------------------------------

    facility_layer = pdk.Layer(
        "ScatterplotLayer",
        data=opc,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    tooltip = {
        "html": "{tooltip_html}",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # DECK
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            facility_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-27"):
        st.pydeck_chart(
            deck,
            height=700
        )


    # --------------------------------------------------
    # KPIS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        sex_df = pd.DataFrame(
            {
                "Sex": ["Female", "Male"],
                "Population": [
                    female_seniors,
                    male_seniors
                ]
            }
        )

        fig = px.pie(
            sex_df,
            names="Sex",
            values="Population",
            title="Senior Population Gender Distribution",
            color_discrete_sequence=QCD_CATEGORICAL
        )

        with st.container(border=True, key="qcd-chart-28"):
            st.plotly_chart(
                fig
            )

    with col2:

        age_df = pd.DataFrame(
            {
                "Age Group": [
                    "60-79",
                    "80+"
                ],
                "Population": [
                    age_60_79,
                    age_80_plus
                ]
            }
        )

        fig = px.bar(
            age_df,
            x="Age Group",
            y="Population",
            title="Senior Citizens by Age Group",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-29"):
            st.plotly_chart(
                fig
            )

    seniors_per_year = pd.read_csv(
        "processed/editable/seniors_per_year.csv"
    )

    seniors_per_year[
        "senior_citizens_registered_during_the_year"
    ] = (
        seniors_per_year[
            "senior_citizens_registered_during_the_year"
        ]
        .astype(str)
        .str.replace(",", "")
        .astype(int)
    )

    fig = px.line(
        seniors_per_year,
        x="year",
        y="senior_citizens_registered_during_the_year",
        markers=True,
        title="Registered Senior Citizens Over Time",
        color_discrete_sequence=["#7F47ED"]
    )

    with st.container(border=True, key="qcd-chart-30"):
        st.plotly_chart(
            fig
        )

    # seniors_registered here matches "Senior Citizens" from the
    # old standalone processed/seniors_per_barangay.csv exactly
    # (verified before that file was retired) — demographics is
    # the single source of truth now, one less file to keep in
    # sync.
    seniors_barangay = demographics[
        ["barangay", "district", "seniors_registered"]
    ].rename(
        columns={
            "barangay": "Barangay",
            "district": "District",
            "seniors_registered": "Senior Citizens"
        }
    )

    top_barangays = (
        seniors_barangay
        .sort_values(
            "Senior Citizens",
            ascending=False
        )
        .head(10)
    )

    st.subheader(
        "Top 10 Barangays by Number of Senior Citizens"
    )

    with st.container(border=True, key="qcd-chart-31"):
        st.dataframe(
            top_barangays[
                [
                    "Barangay",
                    "District",
                    "Senior Citizens"
                ]
            ],
            width="stretch"
        )

    district_seniors = (
        seniors_barangay
        .groupby("District")
        ["Senior Citizens"]
        .sum()
        .reset_index()
    )

    # Format district names for consistency
    district_seniors["District"] = format_district(
        district_seniors["District"]
    )

    fig = px.bar(
        district_seniors,
        x="District",
        y="Senior Citizens",
        text_auto=",",
        title="Senior Citizens by District",
        color_discrete_sequence=["#7F47ED"]
    )

    with st.container(border=True, key="qcd-chart-32"):
        st.plotly_chart(
            fig
        )

    facility_counts = (
        older_person_care
        .groupby("District")
        .size()
        .reset_index(name="Facilities")
    )

    # Use standardized format_district function for consistency
    facility_counts["District"] = format_district(
        facility_counts["District"]
    )

    coverage = district_seniors.merge(
        facility_counts,
        on="District",
        how="left"
    )

    coverage["Facilities"] = (
        coverage["Facilities"]
        .fillna(0)
    )

    coverage[
        "Seniors per Facility"
    ] = (
        coverage["Senior Citizens"]
        / coverage["Facilities"]
    ).round(0)

    st.subheader(
        "Senior Care Coverage by District"
    )

    with st.container(border=True, key="qcd-chart-33"):
        st.dataframe(
            coverage.sort_values(
                "Seniors per Facility",
                ascending=False
            ),
            width="stretch"
        )


    facility_mix = (
        older_person_care["Category"]
        .value_counts()
        .reset_index()
    )

    facility_mix.columns = [
        "Facility Type",
        "Count"
    ]

    fig = px.pie(
        facility_mix,
        names="Facility Type",
        values="Count",
        title="Diverse Senior Care Options",
        color_discrete_sequence=QCD_CATEGORICAL
    )

    with st.container(border=True, key="qcd-chart-34"):
        st.plotly_chart(
            fig
        )

    # =====================================================
    # NEW SECTION: ELDERLY VULNERABILITY PROFILE
    # =====================================================

    st.divider()
    st.markdown("### Older Persons Vulnerability Profile")

    # Load demographics
    demographics = load_demographics()
    demographics_district = load_demographics_by_district()

    # Tabs for barangay and district level
    tab_barangay, tab_district = st.tabs(["Barangay Analysis", "District Analysis"])

    with tab_barangay:
        st.markdown("#### Barangay-Level Older Persons Indicators")

        # Create elderly profile dataset
        elderly_profile = demographics[[
            'barangay',
            'district',
            'age_60plus',
            'age_60plus_m',
            'age_60plus_f',
            'age_80plus',
            'age_80plus_m',
            'age_80plus_f',
            'seniors_registered',
            'cbms_food_insecurity_prevalence_pct',
            'cbms_housing_inadequacy_index_pct'
        ]].copy()

        # Normalize district for consistent display
        elderly_profile['District'] = 'District ' + elderly_profile['district'].astype(str)

        elderly_profile['seniors_coverage_pct'] = (
            elderly_profile['seniors_registered'] /
            elderly_profile['age_60plus'] * 100
        ).replace([np.inf, -np.inf], np.nan)

        elderly_profile['pct_80plus'] = (
            elderly_profile['age_80plus'] /
            elderly_profile['age_60plus'] * 100
        ).replace([np.inf, -np.inf], np.nan)

        elderly_profile['elderly_vulnerable'] = (
            elderly_profile['cbms_food_insecurity_prevalence_pct'] +
            elderly_profile['cbms_housing_inadequacy_index_pct']
        ) / 2

        # Highlight high-need barangays
        high_need_elderly = elderly_profile.nlargest(10, 'elderly_vulnerable')

        fig = px.scatter(
            elderly_profile,
            x='age_60plus',
            y='elderly_vulnerable',
            size='age_80plus',
            color='District',
            hover_name='barangay',
            title='Older Persons Population Size vs Vulnerability (Size = 80+)',
            labels={
                'age_60plus': 'Population 60+',
                'elderly_vulnerable': 'Avg Vulnerability Index (Food + Housing)',
                'age_80plus': 'Population 80+'
            },
            color_discrete_sequence=QCD_CATEGORICAL
        )

        with st.container(border=True, key="qcd-chart-35"):
            st.plotly_chart(fig)

        # High-need barangays table
        st.markdown("##### Top 10 High-Need Barangays for Older Persons Services")

        display_table = high_need_elderly[[
            'barangay',
            'District',
            'age_60plus',
            'age_80plus',
            'seniors_registered',
            'seniors_coverage_pct',
            'cbms_food_insecurity_prevalence_pct',
            'cbms_housing_inadequacy_index_pct'
        ]].copy()

        display_table.columns = [
            'Barangay',
            'District',
            'Population 60+',
            'Population 80+',
            'Registered Seniors',
            'Coverage %',
            'Food Insecurity %',
            'Housing Inadequacy %'
        ]

        # Format for display
        for col in ['Population 60+', 'Population 80+', 'Registered Seniors']:
            display_table[col] = display_table[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")

        for col in ['Coverage %', 'Food Insecurity %', 'Housing Inadequacy %']:
            display_table[col] = display_table[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")

        with st.container(border=True, key="qcd-chart-36"):
            st.dataframe(display_table, width='stretch', hide_index=True)

    with tab_district:
        st.markdown("#### District-Level Older Persons Summary")

        elderly_district = demographics_district[[
            'district',
            'age_60plus',
            'age_60plus_m',
            'age_60plus_f',
            'age_80plus',
            'age_80plus_m',
            'age_80plus_f',
            'seniors_registered',
            'cbms_food_insecurity_prevalence_pct_hhw',
            'cbms_housing_inadequacy_index_pct_hhw'
        ]].copy()

        elderly_district['seniors_coverage_pct'] = (
            elderly_district['seniors_registered'] /
            elderly_district['age_60plus'] * 100
        ).replace([np.inf, -np.inf], np.nan)

        elderly_district['pct_80plus'] = (
            elderly_district['age_80plus'] /
            elderly_district['age_60plus'] * 100
        ).replace([np.inf, -np.inf], np.nan)

        # Three-column layout for KPIs
        col1, col2, col3 = st.columns(3)

        with col1:
            kpi_card(
                col1,
                "Total Seniors (60+)",
                f"{elderly_district['age_60plus'].sum():,.0f}",
                "up_good"
            )

        with col2:
            kpi_card(
                col2,
                "Population 80+",
                f"{elderly_district['age_80plus'].sum():,.0f}",
                "neutral"
            )

        with col3:
            avg_coverage = (
                elderly_district['seniors_registered'].sum() /
                elderly_district['age_60plus'].sum() * 100
            )
            kpi_card(
                col3,
                "Registration Coverage",
                f"{avg_coverage:.1f}%",
                "up_good"
            )

        # District comparison chart
        # (renamed columns, not just plotly's labels= param — labels=
        # only retitles the axis/legend, the individual legend entries
        # for a wide-format y=[...] chart come straight from the
        # column names themselves, e.g. "age_60plus" would still show
        # in the legend even with labels={'variable': 'Age Group'})
        fig_dist = px.bar(
            elderly_district.rename(columns={
                'age_60plus': '60+',
                'age_80plus': '80+'
            }),
            x='district',
            y=['60+', '80+'],
            barmode='group',
            title='Older Persons Population by District',
            labels={
                'value': 'Population',
                'variable': 'Age Group',
                'district': 'District'
            },
            color_discrete_map={'60+': '#7F47ED', '80+': '#FF6B6B'}
        )
        fig_dist.update_xaxes(tickformat="d")

        with st.container(border=True, key="qcd-chart-37"):
            st.plotly_chart(fig_dist)

        # Vulnerability by district
        fig_vuln = px.bar(
            elderly_district.rename(columns={
                'cbms_food_insecurity_prevalence_pct_hhw': 'Food Insecurity',
                'cbms_housing_inadequacy_index_pct_hhw': 'Housing Inadequacy'
            }),
            x='district',
            y=['Food Insecurity', 'Housing Inadequacy'],
            barmode='group',
            title='Older Persons Vulnerability Indicators by District',
            labels={
                'value': 'Percentage (%)',
                'variable': 'Indicator',
                'district': 'District'
            },
            color_discrete_map={
                'Food Insecurity': '#FF6B6B',
                'Housing Inadequacy': '#FFA500'
            }
        )
        fig_vuln.update_xaxes(tickformat="d")

        with st.container(border=True, key="qcd-chart-38"):
            st.plotly_chart(fig_vuln)

elif page == "Long-Term Care & Rehabilitation":
    
    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:0px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Long-Term Care and Rehabilitation Facilities
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Explore facilities providing long-term care,
    rehabilitation, therapy, and specialized
    recovery services in Quezon City.
    """)

    # --------------------------------------------------
    # REHABILITATION KPIs
    # --------------------------------------------------

    total_facilities = len(long_term_care)

    total_categories = (
        long_term_care["Category"]
        .nunique()
    )

    # normalize_barangay_names() first — see the same fix on the
    # Childcare page for why raw casing double-counts barangays.
    covered_barangays = (
        normalize_barangay_names(long_term_care["barangay"])
        .nunique()
    )

    covered_districts = (
        long_term_care["District"]
        .nunique()
    )

    k1, k2, k3, k4 = st.columns(4)

    kpi_card(
        k1,
        "Facilities",
        f"{total_facilities:,}",
        "up_good"
    )

    kpi_card(
        k2,
        "Service Types",
        f"{total_categories:,}",
        "up_good"
    )

    kpi_card(
        k3,
        "Barangays Served",
        f"{covered_barangays:,}",
        "up_good"
    )

    kpi_card(
        k4,
        "Districts Served",
        f"{covered_districts:,}",
        "up_good"
    )

    st.divider()

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        long_term_care["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in districts]
    )

    st.info("Hover over a facility to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    ltc = long_term_care.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        ltc = ltc[
            ltc["District"].astype(int)
            == district_number
        ]

    if selected_ltc_category != "All":

        ltc = ltc[
            ltc["Category"]
            .str.contains(
                selected_ltc_category,
                case=False,
                na=False
            )
        ]

    if selected_ltc_source != "All":

        ltc = ltc[
            ltc["data_source"] == selected_ltc_source
        ]

    # --------------------------------------------------
    # MISSING COORDINATES
    # --------------------------------------------------

    missing_locations = (
        ltc["latitude"].isna() |
        ltc["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} facilities do not have coordinates and are not shown on the map."
        )

    ltc = ltc.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLORS
    # --------------------------------------------------

    colors = [
        hex_to_rgb(
            ltc_color(cat)
        )
        for cat in ltc["Category"].astype(str)
    ]

    ltc["r"] = [c[0] for c in colors]
    ltc["g"] = [c[1] for c in colors]
    ltc["b"] = [c[2] for c in colors]

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # POLYGONS
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False
    )

    # --------------------------------------------------
    # FACILITIES
    # --------------------------------------------------

    # Provider Type is unknown for nearly all Long-Term Care
    # facilities (155/156 rows have no Sector value in
    # care_supply_facilities.csv) — the line is omitted for those
    # rows rather than shown blank.
    ltc["tooltip_html"] = build_tooltip_html(
        ltc, "Name",
        [
            ("Category", "Category"),
            ("Provider Type", "Sector"),
            ("Source", "data_source"),
            ("District", "District"),
            ("Barangay", "barangay"),
            ("Address", "Address"),
            ("Open", "open_hours"),
            ("Close", "close_hours"),
        ]
    )

    facility_layer = pdk.Layer(
        "ScatterplotLayer",
        data=ltc,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    tooltip = {
        "html": "{tooltip_html}",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # DECK
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            facility_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-35"):
        st.pydeck_chart(
            deck,
            height=700
        )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Facilities")

    _ltc_disp = ltc[["Name","Category","District","barangay","Address"]].copy()
    with st.container(border=True, key="qcd-chart-36"):
        st.dataframe(
            _ltc_disp[["Name","Category","District","Address"]],
            width='stretch'
        )
    # --------------------------------------------------
    # REHABILITATION KPIs
    # --------------------------------------------------

    elderly_population = (
        population_age[
            "60+ (Older Persons)"
        ]
        .sum()
    )

    population_total = (
        population_sex["Total"]
        .sum()
    )

    population_per_rehab = (
        population_total
        / total_facilities
    )

    elderly_per_rehab = (
        elderly_population
        / total_facilities
    )

    c1, c2, c3 = st.columns(3)

    kpi_card(
        c1,
        "Total Population",
        f"{population_total:,.0f}"
    )

    kpi_card(
        c2,
        "Population per Facility",
        f"{population_per_rehab:,.0f}",
        "down_good"
    )

    kpi_card(
        c3,
        "Older Persons per Facility",
        f"{elderly_per_rehab:,.0f}",
        "down_good"
    )

    st.divider()

    service_mix = (
        long_term_care["Category"]
        .value_counts()
        .reset_index()
    )

    service_mix.columns = [
        "Service Type",
        "Facilities"
    ]

    # Sort by facilities count for better readability
    service_mix = service_mix.sort_values(
        "Facilities",
        ascending=True
    )

    fig = px.bar(
        service_mix,
        x="Facilities",
        y="Service Type",
        orientation="h",
        title="Long-Term Care and Rehabilitation Services by Type",
        color_discrete_sequence=["#7F47ED"]
    )

    fig.update_layout(
        height=max(400, len(service_mix) * 30),
        yaxis_title="Service Type",
        xaxis_title="Number of Facilities",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Facilities: %{x}<extra></extra>"
    )

    with st.container(border=True, key="qcd-chart-37"):
        st.plotly_chart(
            fig
        )

    district_counts = (
        long_term_care
        .groupby("District")
        .size()
        .reset_index(name="Facilities")
    )

    # Format district names for consistency
    district_counts["District"] = format_district(
        district_counts["District"]
    )

    fig = px.bar(
        district_counts,
        x="District",
        y="Facilities",
        text_auto=True,
        title="Rehabilitation Facilities by District",
        color_discrete_sequence=["#7F47ED"]
    )

    with st.container(border=True, key="qcd-chart-38"):
        st.plotly_chart(
            fig
        )

    district_population = (
        population_sex
        .groupby("District")
        ["Total"]
        .sum()
        .reset_index()
    )

    district_facilities = (
        long_term_care
        .groupby("District")
        .size()
        .reset_index(name="Facilities")
    )

    coverage = district_population.merge(
        district_facilities,
        on="District",
        how="left"
    )

    coverage["Facilities"] = (
        coverage["Facilities"]
        .fillna(0)
    )

    coverage[
        "Population per Facility"
    ] = (
        coverage["Total"]
        / coverage["Facilities"]
    ).round(0)

    st.subheader(
        "Coverage by District"
    )

    with st.container(border=True, key="qcd-chart-39"):
        st.dataframe(
            coverage.sort_values(
                "Population per Facility",
                ascending=False
            ),
            width="stretch"
        )

    ranking = (
        coverage[
            [
                "District",
                "Population per Facility"
            ]
        ]
        .sort_values(
            "Population per Facility",
            ascending=False
        )
    )

    st.subheader(
        "District Priority Ranking"
    )

    with st.container(border=True, key="qcd-chart-40"):
        st.dataframe(
            ranking,
            width="stretch"
        )

elif page == "Persons with Disabilities":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Persons with Disabilities
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Registered persons with disabilities and senior
    citizens with disability across Quezon City, by sex,
    disability type, district, and barangay.
    """)

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
    # demographics, demand_city_context, and
    # demand_district_context are loaded once at app
    # startup (see top of file) from
    # processed/editable/demographics_by_barangay.csv,
    # demand_city_context.csv, and
    # demand_district_context.csv.
    # --------------------------------------------------

    pwd_by_type = demand_city_context[
        demand_city_context["category"] == "PWDs by type"
    ].copy()

    pwd_by_type = pwd_by_type.rename(
        columns={"breakdown": "Type of Disability"}
    )

    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    total_pwd = demographics["pwd_registered"].sum()

    total_male = int(math.ceil(pwd_by_type["male"].sum()))
    total_female = pwd_by_type["female"].sum()

    disability_types = pwd_by_type["Type of Disability"].nunique()

    rehab_facilities = len(long_term_care)

    barangays_covered = (
        demographics
        .loc[demographics["pwd_registered"] > 0, "barangay"]
        .nunique()
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    kpi_card(
        k1,
        "Registered Persons with Disabilities",
        f"{total_pwd:,.0f}"
    )

    kpi_card(
        k2,
        "Barangays",
        barangays_covered
    )

    kpi_card(
        k3,
        "Rehab Facilities",
        rehab_facilities,
        "up_good"
    )

    kpi_card(
        k4,
        "Male",
        f"{total_male:,.0f}"
    )

    kpi_card(
        k5,
        "Female",
        f"{total_female:,.0f}"
    )

    kpi_card(
        k6,
        "Disability Types",
        disability_types
    )

    st.divider()

    # --------------------------------------------------
    # COVERAGE KPI
    # --------------------------------------------------

    kpi_card(
        st,
        "Persons with Disabilities per Rehabilitation Facility",
        f"{(total_pwd / rehab_facilities):,.0f}",
        "down_good"
    )

    st.divider()

    # --------------------------------------------------
    # SEX DISTRIBUTION
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        sex_df = pd.DataFrame(
            {
                "Sex": [
                    "Male",
                    "Female"
                ],
                "Count": [
                    total_male,
                    total_female
                ]
            }
        )

        fig = px.pie(
            sex_df,
            names="Sex",
            values="Count",
            title="Persons with Disabilities by Sex",
            color_discrete_sequence=QCD_CATEGORICAL
        )

        with st.container(border=True, key="qcd-chart-41"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    with col2:

        fig = px.bar(
            pwd_by_type
            .sort_values(
                "total",
                ascending=False
            ),
            x="Type of Disability",
            y="total",
            title="Disability Types",
            color_discrete_sequence=["#7F47ED"]
        )

        fig.update_layout(
            yaxis_title="Registered Persons with Disabilities"
        )

        with st.container(border=True, key="qcd-chart-42"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    st.divider()

    # --------------------------------------------------
    # DISTRICT DISTRIBUTION
    # --------------------------------------------------

    st.subheader(
        "Persons with Disabilities by District"
    )

    district_display = demand_district_context.copy()

    # Use standardized format_district function for consistency
    district_display["District"] = format_district(
        district_display["district"]
    )

    fig = px.bar(
        district_display,
        x="District",
        y="pwd_registered",
        text_auto=",",
        title="Registered Persons with Disabilities by District",
        color_discrete_sequence=["#7F47ED"]
    )

    fig.update_layout(
        yaxis_title="Registered Persons with Disabilities"
    )

    with st.container(border=True, key="qcd-chart-43"):
        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.divider()

    # --------------------------------------------------
    # SENIORS WITH DISABILITY
    # (replaces the previous PWD registration trend charts
    #, no year-by-year registration history is available
    # in the current data, so this section instead surfaces
    # the senior-citizen disability context that demand_city
    # _context.csv carries: the two diverging city-level
    # counts, by registration basis, for seniors who are also
    # registered as PWDs, plus the age split of seniors overall)
    # --------------------------------------------------

    st.subheader(
        "Seniors with Disability"
    )

    st.caption(
        "OSCA and PDAO use different registration bases, so "
        "their counts of seniors also registered as persons "
        "with disabilities do "
        "not match. Both figures are shown rather than "
        "reconciled into one number. City-level only, no "
        "barangay or district breakdown is available for "
        "this indicator."
    )

    seniors_disability = demand_city_context[
        demand_city_context["category"] == "Seniors with disability"
    ].copy()

    seniors_by_age = demand_city_context[
        demand_city_context["category"] == "Seniors by age"
    ].copy()

    col3, col4 = st.columns(2)

    with col3:

        fig = px.bar(
            seniors_disability,
            x="breakdown",
            y="total",
            title="Seniors Also Registered as Persons with Disabilities",
            text_auto=",",
            color_discrete_sequence=["#7F47ED"]
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Count"
        )

        with st.container(border=True, key="qcd-chart-44"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    with col4:

        fig = px.bar(
            seniors_by_age,
            x="breakdown",
            y="total",
            title="Registered Seniors by Age Band",
            text_auto=",",
            color_discrete_sequence=["#7F47ED"]
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Registered Seniors"
        )

        with st.container(border=True, key="qcd-chart-45"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    st.divider()

    # --------------------------------------------------
    # TOP BARANGAYS
    # --------------------------------------------------

    col5, col6 = st.columns(2)

    with col5:

        st.subheader(
            "Top 10 Barangays by Population of Persons with Disabilities"
        )

        with st.container(border=True, key="qcd-chart-46"):
            st.dataframe(
                demographics[
                    [
                        "barangay",
                        "district",
                        "pwd_registered"
                    ]
                ]
                .rename(
                    columns={
                        "barangay": "Barangay",
                        "district": "District",
                        "pwd_registered": "Persons with Disabilities"
                    }
                )
                .sort_values(
                    "Persons with Disabilities",
                    ascending=False
                )
                .head(10),
                width="stretch"
            )

    with col6:

        st.subheader(
            "Highest Disability Prevalence Rate"
        )

        with st.container(border=True, key="qcd-chart-47"):
            st.dataframe(
                demographics[
                    [
                        "barangay",
                        "district",
                        "disability_prevalence_rate_pct"
                    ]
                ]
                .rename(
                    columns={
                        "barangay": "Barangay",
                        "district": "District",
                        "disability_prevalence_rate_pct":
                            "Prevalence Rate (%)"
                    }
                )
                .sort_values(
                    "Prevalence Rate (%)",
                    ascending=False
                )
                .head(10),
                width="stretch"
            )

    st.divider()

    # --------------------------------------------------
    # REHABILITATION COVERAGE
    # --------------------------------------------------

    st.subheader(
        "Persons with Disabilities vs Rehabilitation Services"
    )

    rehab_by_district = (
        long_term_care
        .groupby("District")
        .size()
        .reset_index(
            name="Facilities"
        )
    )

    rehab_by_district["District"] = (
        rehab_by_district["District"]
        .astype(int)
    )

    district_coverage = demand_district_context.merge(
        rehab_by_district,
        left_on="district",
        right_on="District",
        how="left"
    )

    district_coverage["Persons with Disabilities per Facility"] = (
        district_coverage["pwd_registered"]
        /
        district_coverage["Facilities"]
    ).round(0)

    with st.container(border=True, key="qcd-chart-48"):
        st.dataframe(
            district_coverage[
                [
                    "district",
                    "pwd_registered",
                    "Facilities",
                    "Persons with Disabilities per Facility"
                ]
            ].rename(
                columns={
                    "district": "District",
                    "pwd_registered": "Registered Persons with Disabilities in QC"
                }
            ),
            width="stretch"
        )

elif page == "Action Offices":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Quezon City Action Offices
        </h2>
        """,
        unsafe_allow_html=True
    )


    st.markdown("""
    Explore the distribution of Quezon City Action Offices providing local access
    to government services.
    """)

    st.markdown("""
    **Action Offices** are satellite government service centers that provide citizens with convenient access to
    basic transactions, information, and referrals without traveling to main city offices.
    """)

    # --------------------------------------------------
    # ACTION OFFICE KPIs
    # --------------------------------------------------

    total_offices = len(action_offices)

    covered_barangays = (
        action_offices["barangay"]
        .nunique()
    )

    covered_districts = (
        action_offices["District"]
        .nunique()
    )

    k1, k2, k3 = st.columns(3)

    kpi_card(
        k1,
        "Total Action Offices",
        f"{total_offices:,}",
        "up_good"
    )

    kpi_card(
        k2,
        "Barangays Served",
        f"{covered_barangays:,}",
        "up_good"
    )

    kpi_card(
        k3,
        "Districts Served",
        f"{covered_districts:,}",
        "up_good"
    )

    st.divider()

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        action_offices["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in districts]
    )

    st.info("Hover over an office to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    sat = action_offices.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        sat = sat[
            sat["District"].astype(int)
            == district_number
        ]

    # --------------------------------------------------
    # MISSING COORDINATES
    # --------------------------------------------------

    missing_locations = (
        sat["latitude"].isna() |
        sat["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} offices do not have coordinates and are not shown on the map."
        )

    sat = sat.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLORS BY DISTRICT
    # --------------------------------------------------

    colors = [
        hex_to_rgb(
            district_color(d)
        )
        for d in sat["District"]
    ]

    sat["r"] = [c[0] for c in colors]
    sat["g"] = [c[1] for c in colors]
    sat["b"] = [c[2] for c in colors]

    # No "District" field here — Category is the office's title
    # ("District 4", etc.), so a "District: 4" line right underneath
    # would just repeat what the title already says.
    sat["tooltip_html"] = build_tooltip_html(
        sat, "Category",
        [
            ("Barangay", "barangay"),
            ("Address", "Address"),
            ("Open", "open_hours"),
            ("Close", "close_hours"),
        ]
    )

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # POLYGONS
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False
    )

    # --------------------------------------------------
    # OFFICES
    # --------------------------------------------------

    office_layer = pdk.Layer(
        "ScatterplotLayer",
        data=sat,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    tooltip = {
        "html": """
        {tooltip_html}
        <br/><br/>
        <b>Services:</b><br/>
        • PDAO Satellite Office: ID services for persons with disabilities; purchase &amp; free movie booklets<br/>
        • OSCA Satellite Office: Senior Citizen ID; medicine, grocery &amp; movie booklets; centenarian recognition; death benefits; social pension<br/>
        • PESO Satellite Office: Job referral; employer accreditation; workers' association registration; OFW &amp; Kasambahay assistance<br/>
        • SSDD Satellite Office: Social case studies; medical &amp; burial assistance, persons with disabilities case studies, women's case management, elderly/persons with disabilities intake, training, and livelihood &amp; capital assistance
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # DECK
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            office_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-49"):
        st.pydeck_chart(
            deck,
            height=700
        )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Action Offices")

    _sat_disp = sat[["District","barangay","Address"]].copy()
    with st.container(border=True, key="qcd-chart-50"):
        st.dataframe(
            _sat_disp[["District","Address"]],
            width='stretch'
        )
elif page == "Migration Resource Center":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Migration Resource Center
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("""
    Explore facilities providing information, training,
    referral services, and support for migrant workers
    and their families in Quezon City.
    """)

    # --------------------------------------------------
    # MIGRATION RESOURCE CENTER KPIs
    # --------------------------------------------------

    total_facilities = len(migration_centers)

    covered_barangays = (
        migration_centers["barangay"]
        .nunique()
    )

    covered_districts = (
        migration_centers["District"]
        .nunique()
    )

    k1, k2, k3 = st.columns(3)

    kpi_card(
        k1,
        "Facilities",
        f"{total_facilities:,}",
        "up_good"
    )

    kpi_card(
        k2,
        "Barangays Served",
        f"{covered_barangays:,}",
        "up_good"
    )

    kpi_card(
        k3,
        "Districts Served",
        f"{covered_districts:,}",
        "up_good"
    )

    st.divider()

    st.caption(
        "**Data pairing note:** Registered migrant worker counts or OFW population data, "
        "if added to the dashboard, should live on this page rather than Population Overview, "
        "since pairing resource supply (facilities) with population demand (migrant workers) "
        "enables better coverage analysis."
    )

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        migration_centers["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "Select the district",
        ["All"] + [f"District {d}" for d in districts]
    )

    st.info("Hover over a facility to view details.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    mig = migration_centers.copy()
    if selected_district != "All":

        district_number = int(
            selected_district.replace(
                "District ",
                ""
            )
        )

        mig = mig[
            mig["District"].astype(int)
            == district_number
        ]

    # --------------------------------------------------
    # MISSING COORDINATES
    # --------------------------------------------------

    missing_locations = (
        mig["latitude"].isna() |
        mig["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} facilities do not have coordinates and are not shown on the map."
        )

    mig = mig.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLORS
    # --------------------------------------------------

    mig["r"] = 127
    mig["g"] = 71
    mig["b"] = 237

    # --------------------------------------------------
    # VIEW STATE
    # --------------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,   
        max_zoom=17, 
    )

    # --------------------------------------------------
    # POLYGONS
    # --------------------------------------------------

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo,
        stroked=True,
        filled=True,
        get_fill_color=[127, 191, 127, 38],
        get_line_color=[102, 102, 102],
        line_width_min_pixels=1,
        pickable=False
    )

    # --------------------------------------------------
    # FACILITIES
    # --------------------------------------------------

    mig["tooltip_html"] = build_tooltip_html(
        mig, "Name",
        [
            ("Provider Type", "Sector"),
            ("District", "District"),
            ("Barangay", "barangay"),
            ("Address", "Address"),
            ("Open", "open_hours"),
            ("Close", "close_hours"),
        ]
    )

    facility_layer = pdk.Layer(
        "ScatterplotLayer",
        data=mig,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color=[40, 40, 40, 200],
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=1.5,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    tooltip = {
        "html": """
        {tooltip_html}
        <br/><br/>
        <b>Services:</b><br/>
        1. Pre-Migration and Pre-Employment Trainings<br/>
        2. Pre-Departure Trainings<br/>
        3. On-Site Support and Learning Sessions<br/>
        4. Reintegration Trainings for OFW Returnees
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # --------------------------------------------------
    # DECK
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            polygon_layer,
            facility_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-51"):
        st.pydeck_chart(
            deck,
            height=700
        )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader(
        "Migration Service Facilities"
    )

    display_cols = [
        c for c in ["Name","Category","District","Address"]
        if c in mig.columns
    ]

    _mig_disp = mig[display_cols].copy()

    with st.container(border=True, key="qcd-chart-52"):
        st.dataframe(_mig_disp, width="stretch")

elif page == "Care Services Explorer":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Care Services Explorer
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        """
        Explore childcare centers, schools, health facilities,
        older persons facilities, rehabilitation centers,
        migration resource centers, bus stops, and Quezon City
        Action Offices on a single map, optionally overlaid
        with land-surface temperature, vegetation, or flood
        exposure layers.
        """
    )

    st.divider()

    # --------------------------------------------------
    # SERVICE CONFIGURATION
    # --------------------------------------------------

    service_layers = {

        "Childcare Centers": {
            "df": childcare_centers,
            "color": "#4C1D95",
            "symbol": "◆",
            "source": "Childcare Center",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Schools": {
            "df": schools,
            "color": "#4472C4",
            "symbol": "▲",
            "source": "School",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Health Centers": {
            "df": health_centers,
            "color": "#4C1D95",
            "symbol": "✚",
            "source": "Health Facility",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Older Persons Facilities": {
            "df": older_person_care,
            "color": "#055B52",
            "symbol": "●",
            "source": "Older Persons Facility",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Long-Term Care & Rehabilitation": {
            "df": long_term_care,
            "color": "#4C1D95",
            "symbol": "✦",
            "source": "Rehabilitation Facility",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Action Offices": {
            "df": action_offices,
            "color": "#055B52",
            "symbol": "■",
            "source": "Action Office",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Migration Resource Centers": {
            "df": migration_centers,
            "color": "#C4B5FD",
            "symbol": "✈",
            "source": "Migration Resource Center",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Bus Stops": {
            "df": bus_stops,
            "color": "#F97316",
            "symbol": "⊙",
            "source": "Bus Stop",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },
    }

    # --------------------------------------------------
    # LEGEND
    # --------------------------------------------------

    st.markdown("### Service Categories")

    # Phase 1 Optimization: Handle 8 service categories with 2 rows of 4 columns
    cols = st.columns(4)

    for i, (layer_name, layer) in enumerate(service_layers.items()):

        # Switch to next row after 4 items
        if i == 4:
            cols = st.columns(4)
            col_idx = 0
        else:
            col_idx = i % 4

        cols[col_idx].markdown(
            f"""
            <span style="
                color:{layer['color']};
                font-size:25px;
            ">
            {layer['symbol']}
            </span>
            <span style="color:#7F47ED;">
            {layer_name}
            </span>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # --------------------------------------------------
    # CLIMATE LAYER CONFIGURATION
    # --------------------------------------------------

    climate_overlay_layers = {
        "Land-Surface Temperature": {
            "path": "processed/reference/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
            "colormap": "YlOrRd",
            "binary": False
        },
        "Vegetation (NDVI)": {
            "path": "processed/reference/climate/ndvi_mean_2025_EPSG3123.tif",
            "colormap": "Greens",
            "binary": False
        },
        "Flood Inundation (100-yr)": {
            "path": "processed/reference/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
            "colormap": "Blues",
            "binary": True
        }
    }

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:

        selected_layers = st.multiselect(
            "Services to Display",
            list(service_layers.keys()),
            default=list(service_layers.keys())[:3]
        )

    with col2:

        district_values = sorted(
            health_centers["District"]
            .dropna()
            .astype(int)
            .unique()
        )

        district_options = {
            "All": "All"
        }

        district_options.update(
            {
                f"District {d}": d
                for d in district_values
            }
        )

        selected_district_label = st.selectbox(
            "District",
            list(district_options.keys())
        )

        selected_district = district_options[
            selected_district_label
        ]

    with col3:

        # Derived from the data (union across every facility type
        # shown on this page) rather than hardcoded — see the
        # Childcare Centers filter above for why.
        _explorer_sources = sorted(
            pd.concat([
                childcare_centers["data_source"],
                schools["data_source"],
                health_centers["data_source"],
                older_person_care["data_source"],
                long_term_care["data_source"],
                action_offices["data_source"],
                migration_centers["data_source"],
                bus_stops["data_source"],
            ]).dropna().unique()
        )

        selected_explorer_source = st.selectbox(
            "Data Source",
            ["All"] + _explorer_sources,
            key="explorer_source_filter"
        )

    # Same population-group options as the Climate Layers page's
    # Population dropdown, so the two stay in sync conceptually
    # (kept as a separate dict rather than imported, matching how
    # service_layers is already duplicated between this page and
    # build_explorer_map above). Each value is (source, column),
    # same convention as Climate Layers' CLIMATE_POP_OPTIONS:
    # "demographics" columns come from the shared `demographics`
    # table, "domestic_workers" from the separate
    # domestic_workers_barangay table.
    POP_DENSITY_OPTIONS = {
        "Child population (ages 0-5)": ("demographics", "age_0_5"),
        "Child population (ages 6-17)": ("demographics", "age_6_17"),
        "Older persons (60+)": ("demographics", "age_60plus"),
        "Persons with disabilities (registered)": ("demographics", "pwd_registered"),
        "Total population": ("demographics", "pop_census"),
        "Domestic workers (registered)": ("domestic_workers", "domestic_workers_total")
    }

    col_toggle1, col_toggle2, col_toggle3 = st.columns(3)

    with col_toggle1:
        selected_density_label = st.selectbox(
            "Population Layer",
            list(POP_DENSITY_OPTIONS.keys()),
            index=0,
            key="explorer_density_filter",
            help=(
                "Overlay population density or raw count on the map to visualize demand for care services. "
                "Darker areas indicate higher values for the selected population group."
            )
        )

        selected_density_source, selected_density_col = (
            POP_DENSITY_OPTIONS[selected_density_label]
        )

    with col_toggle2:
        selected_density_metric_label = st.radio(
            "Show as",
            ["Density (per km²)", "Raw Count"],
            index=0,
            key="explorer_density_metric",
            horizontal=True
        )

        selected_density_metric = (
            "density"
            if selected_density_metric_label == "Density (per km²)"
            else "count"
        )

    with col_toggle3:
        show_flood_risk_only = st.checkbox(
            "Show At-Flood-Risk Facilities Only",
            value=False,
            help=(
                "Display only facilities located in flood-prone areas. "
                "Helps identify vulnerable service locations that may need mitigation measures."
            )
        )

    st.caption(
        """
        **Supply × Demand Analysis:** Compare care service locations (markers) with population
        density to identify areas with high demand but limited supply.
        """
    )

    if not selected_layers:

        st.info(
            "Select at least one service layer above to see "
            "flood exposure counts."
        )

    else:

        exposure_rows = []

        for layer_name in selected_layers:

            layer_df = service_layers[layer_name]["df"]

            if selected_district != "All":

                layer_df = layer_df[
                    layer_df[
                        service_layers[layer_name]["district_col"]
                    ]
                    .astype(int)
                    == selected_district
                ]

            if selected_explorer_source != "All" and "data_source" in layer_df.columns:

                layer_df = layer_df[
                    layer_df["data_source"] == selected_explorer_source
                ]

            total_n = len(layer_df)

            at_risk_n = int(
                layer_df.get(
                    "flood_risk",
                    pd.Series(False, index=layer_df.index)
                ).sum()
            )

            exposure_rows.append({
                "Service Type": layer_name,
                "Total Facilities": total_n,
                "In Flood Zone": at_risk_n,
                "% At Risk": (
                    round(100 * at_risk_n / total_n, 1)
                    if total_n > 0 else 0.0
                )
            })

        exposure_df = pd.DataFrame(exposure_rows)

        total_facilities = exposure_df["Total Facilities"].sum()
        total_at_risk = exposure_df["In Flood Zone"].sum()

        kpi1, kpi2, kpi3 = st.columns(3)

        kpi_card(
            kpi1,
            "Facilities Selected",
            f"{total_facilities:,}"
        )

        kpi_card(
            kpi2,
            "In Flood Zone",
            f"{total_at_risk:,}",
            "down_good"
        )

        kpi_card(
            kpi3,
            "% At Risk",
            f"{(100 * total_at_risk / total_facilities):.1f}%"
            if total_facilities > 0 else "0.0%",
            "down_good"
        )

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    explorer_deck, climate_legend_info, demand_legend_info = build_explorer_map(
        tuple(selected_layers),
        selected_district,
        selected_climate_layers=(),
        flood_risk_only=show_flood_risk_only,
        show_risk_rings=False,
        demand_pop_col=selected_density_col,
        demand_pop_label=selected_density_label,
        demand_pop_source=selected_density_source,
        demand_metric=selected_density_metric,
        selected_source=selected_explorer_source
    )

    if demand_legend_info is not None:

        _density_vmin, _density_vmax, _density_label, _density_colormap = demand_legend_info

        st.markdown(
            render_colormap_legend_html(
                colormap=_density_colormap,
                vmin=_density_vmin,
                vmax=_density_vmax,
                unit="" if selected_density_metric == "count" else "/km²",
                label=_density_label
            ),
            unsafe_allow_html=True
        )

    st.pydeck_chart(
        explorer_deck,
        height=850
    )


    st.divider()

    # --------------------------------------------------
    # SUPPLY-SIDE FLOOD EXPOSURE SUMMARY (RESULTS)
    # (counts, across the *currently selected* service layers
    # and district, how many facilities sit inside the 100-yr
    # flood footprint, see flag_facilities_at_risk in
    # functions.py. The heading and caveat appear at the top
    # of the page for better visibility; this section shows
    # the detailed results table and chart.)
    # --------------------------------------------------

    st.markdown("#### Flood Exposure by Service Type")

    if not selected_layers:

        st.info(
            "Select at least one service layer above to see "
            "flood exposure counts."
        )

    else:

        fig_exposure = px.bar(
            exposure_df.sort_values(
                "In Flood Zone",
                ascending=False
            ),
            x="Service Type",
            y="In Flood Zone",
            color="% At Risk",
            color_continuous_scale="Reds",
            title="Facilities in 100-yr Flood Zone, by Service Type"
        )

        fig_exposure.update_layout(
            xaxis_title="",
            yaxis_title="Facilities in Flood Zone"
        )

        with st.container(border=True, key="qcd-chart-53"):
            st.plotly_chart(
                fig_exposure
            )

        with st.container(border=True, key="qcd-chart-54"):
            st.dataframe(
                exposure_df
            )

elif page == "Accessibility Analysis":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Accessibility Analysis
        </h2>
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # LOAD MAPS (for Socio-Economic Indicators tab)
    # ==================================================
    barangay_map = gpd.read_file(
        "processed/reference/qc_barangays.geojson"
    )

    # Normalize barangay_name for matching with demographics data
    barangay_map["barangay_name"] = (
        barangay_map["barangay_name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ==================================================
    # FACILITY-PER-1,000 RATIO INDICATORS
    # (shared with the Accessibility Map page, see
    # ACCESSIBILITY_RATIO_INDICATORS in functions.py)
    # ==================================================

    ratio_indicators = ACCESSIBILITY_RATIO_INDICATORS

    selected_ratio_label = st.selectbox(
        "Select Accessibility Ratio",
        list(ratio_indicators.keys())
    )

    selected_ratio = ratio_indicators[selected_ratio_label]

    tab_barangay, tab_district, tab_socio = st.tabs(
        [
            "Barangay Analysis",
            "District Analysis",
            "Socio-Economic Indicators"
        ]
    )


    with tab_district:

        # ==================================================
        # DISTRICT AGGREGATION (from demographics_by_barangay.csv)
        # ==================================================

        district_access = (
            demographics
            .groupby("district")
            .agg(
                Total=("pop_census", "sum"),
                Facilities=("Total", "sum"),
                Facility_Type_Count=(
                    selected_ratio["facility_col"], "sum"
                ),
                Relevant_Population=(
                    selected_ratio["pop_col"], "sum"
                )
            )
            .reset_index()
            .rename(columns={"district": "District"})
        )

        # ==================================================
        # SELECTED RATIO (recomputed at district level,         # per-1,000 ratios don't average correctly across
        # barangays of different sizes, so this is computed
        # fresh from the district totals rather than averaging
        # the barangay-level ratio_* column)
        # ==================================================

        district_access[selected_ratio_label] = (
            district_access["Facility_Type_Count"]
            /
            district_access["Relevant_Population"]
            * 1000
        )

        district_access = district_access.replace(
            [np.inf, -np.inf],
            np.nan
        )

        # ==================================================
        # FACILITY SUPPLY METRICS (all facility types,
        # from demographics_by_barangay.csv's Total facility column)
        # ==================================================

        district_access["Facilities per 10k Population"] = (
            district_access["Facilities"]
            /
            district_access["Total"]
            * 10000
        )

        district_access["Care Demand per Facility"] = (
            district_access["Total"]
            /
            district_access["Facilities"]
        )

        district_access = district_access.replace(
            [np.inf, -np.inf],
            np.nan
        )

        district_access = district_access.round(2)

        access = district_access

        # ==================================================
        # DISTRICT SUMMARY TABLE, driven by the selected
        # facility-specific ratio
        #
        # District-level choropleths and the barangay-level
        # choropleth on the next tab were computed two different
        # ways (a district-wide total vs. per-barangay values),
        # so they read as inconsistent when shown as two separate
        # colored maps next to each other — one is always a
        # smoothed-out aggregate of the other. The reference GIS
        # maps only ever color barangays (districts appear as an
        # outline for context, not their own choropleth), so this
        # tab shows the same district-level numbers as a ranked
        # table instead of a second, disagreeing map.
        # ==================================================

        st.subheader(
            f"District Summary, {selected_ratio_label}"
        )

        st.caption(
            "Ranked by lowest ratio first (most underserved). "
            "For a spatial view, see the Barangay Analysis tab — "
            "district boundaries are drawn there for context."
        )

        district_table = (
            district_access[
                [
                    "District",
                    selected_ratio_label,
                    "Facility_Type_Count",
                    "Relevant_Population",
                    "Total"
                ]
            ]
            .rename(
                columns={
                    "Facility_Type_Count": "Facilities (this type)",
                    "Relevant_Population": "Relevant Population",
                    "Total": "Total Population"
                }
            )
            .dropna(subset=[selected_ratio_label])
            .sort_values(
                [selected_ratio_label, "Relevant Population"],
                ascending=[True, False]
            )
        )

        district_table["District"] = format_district(
            district_table["District"]
        )

        with st.container(border=True, key="qcd-chart-55"):
            st.dataframe(
                district_table,
                width="stretch",
                hide_index=True
            )

        st.divider()

        # ==================================================
        # CHARTS (STACKED VERTICAL LAYOUT)
        # ==================================================

        # Format district names for consistency across all pages
        access_chart = access.copy()
        access_chart["District"] = format_district(access_chart["District"])

        # 
        # CHART 1: FACILITY RATIO BY DISTRICT
        # 

        st.subheader(f"{selected_ratio_label} by District")

        st.caption(
            f"""
            **Single-Type Indicator:** Shows the number of {selected_ratio_label.lower()}
            facilities per 1,000 people in each district. Higher bars = better availability of this specific service type.
            Use this to identify geographic gaps in specific care categories.
            """
        )

        fig1_data = access_chart.sort_values(
            selected_ratio_label,
            ascending=False
        )

        fig = px.bar(
            fig1_data,
            x="District",
            y=selected_ratio_label,
            color=selected_ratio_label,
            color_continuous_scale="Purples_r",
            title=None,
            labels={selected_ratio_label: selected_ratio_label}
        )

        # Add value labels on top of bars with white text
        fig.update_traces(
            textposition="outside",
            texttemplate="<b>%{y:.1f}</b>",
            textfont=dict(color="white", size=12),
            marker_line=dict(color="white", width=2),
            hovertemplate="<b>%{x}</b><br>" + selected_ratio_label + ": %{y:.2f}<extra></extra>"
        )

        # Improve bar styling and spacing
        fig.update_layout(
            xaxis_title="District",
            yaxis_title=selected_ratio_label,
            showlegend=False,
            height=400,
            margin=dict(t=40, b=60, l=60, r=40),
            bargap=0.25,  # Space between bars (smaller = wider bars)
            plot_bgcolor="rgba(100, 80, 140, 0.25)",  # Darker purple background for visibility in dark mode
            paper_bgcolor="#682680",
            coloraxis_colorbar=dict(
                tickfont=dict(color="white"),
                title_font=dict(color="white")
            )
        )

        fig.update_xaxes(
            showgrid=False,
            tickangle=-45,
            tickfont=dict(color="white"),
            title_font=dict(color="white")

        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(200, 200, 200, 0.2)",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        )

        with st.container(border=True, key="qcd-chart-56"):
            st.plotly_chart(fig)

        st.divider()

        # ==================================================
        # POPULATION VS FACILITIES
        # ==================================================

        fig = px.scatter(
            access_chart,
            x="Relevant_Population",
            y="Facility_Type_Count",
            size="Facility_Type_Count",
            text="District",
            color=selected_ratio_label,
            # Reversed for the same "darker = underserved"
            # convention used on the rest of this page, a lower
            # ratio should read darker, not lighter.
            color_continuous_scale="Purples_r",
            title=f"Facility Saturation Risk: Demand-to-Supply Mismatch by District"
        )

        fig.update_layout(
            xaxis_title="Relevant Population",
            yaxis_title="Facilities of this Type"
        )

        fig.update_traces(
            textposition="top center"
        )

        with st.container(border=True, key="qcd-chart-58"):
            st.plotly_chart(
                fig
            )

    with tab_barangay:

        # ==================================================
        # BARANGAY DATA (from demographics_by_barangay.csv directly,         # facility counts, population, and pre-computed
        # ratio_* columns are all already at barangay level)
        # ==================================================

        barangay_access = demographics.copy()

        barangay_access = barangay_access.rename(
            columns={
                "barangay": "Barangay",
                "district": "District",
                "pop_census": "Total",
                "Total": "Facilities"
            }
        )

        # ==================================================
        # SELECTED RATIO (already pre-computed in
        # demographics_by_barangay.csv; pulled in directly rather than
        # recalculated, since barangay-level ratios don't
        # need re-aggregation the way district ones do).
        #
        # Falls back to computing it from facility_col/pop_col
        # (same formula as the District tab) when ratio_col isn't
        # actually a column in demographics_by_barangay.csv — e.g.
        # "All Care Facilities per 1,000 PWDs" references
        # "ratio_pwd_all", which the source CSV doesn't carry, and
        # would otherwise crash this tab with a KeyError.
        # ==================================================

        if selected_ratio["ratio_col"] in barangay_access.columns:

            barangay_access[selected_ratio_label] = (
                barangay_access[selected_ratio["ratio_col"]]
            )

        else:

            # facility_col/pop_col name columns as they exist in
            # demographics_by_barangay.csv, but the rename above
            # already turned that CSV's "Total" (facility count)
            # into "Facilities" and "pop_census" into "Total"
            # (population) on this frame — so "Total" now means
            # population here, not facilities. Remap before using
            # either name, or this would silently divide by the
            # wrong column for any indicator whose facility_col is
            # "Total" (e.g. "All Care Facilities per 1,000 PWDs").
            _fallback_col_renames = {
                "Total": "Facilities",
                "pop_census": "Total"
            }

            _facility_col = _fallback_col_renames.get(
                selected_ratio["facility_col"],
                selected_ratio["facility_col"]
            )

            _pop_col = _fallback_col_renames.get(
                selected_ratio["pop_col"],
                selected_ratio["pop_col"]
            )

            barangay_access[selected_ratio_label] = (
                barangay_access[_facility_col]
                / barangay_access[_pop_col]
                * 1000
            ).replace([np.inf, -np.inf], np.nan)

        # ==================================================
        # FACILITY SUPPLY METRICS (all facility types)
        # ==================================================

        barangay_access["Facilities per 10k Population"] = (
            barangay_access["Facilities"]
            /
            barangay_access["Total"]
            * 10000
        )

        barangay_access["Care Demand per Facility"] = (
            barangay_access["Total"]
            /
            barangay_access["Facilities"]
        )

        barangay_access = barangay_access.replace(
            [np.inf, -np.inf],
            np.nan
        )

        barangay_access = (
            barangay_access
            .round(2)
        )

        # ==================================================
        # BARANGAY MAP, driven by the selected ratio
        # ==================================================

        barangay_geo = gpd.read_file(
            "processed/reference/qc_barangays.geojson"
        )

        barangay_geo["barangay_name"] = (
            barangay_geo["barangay_name"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        barangay_access["Barangay_key"] = (
            barangay_access["Barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        barangay_geo = barangay_geo.merge(
            barangay_access[
                [
                    "Barangay",
                    "Barangay_key",
                    "Facilities",
                    "Total",
                    "Facilities per 10k Population",
                    selected_ratio_label
                ]
            ],
            left_on="barangay_name",
            right_on="Barangay_key",
            how="left"
        )

        st.subheader(
            f"Barangay Map, {selected_ratio_label}"
        )

        st.caption(
            "Lighter = fewer facilities of this type relative to "
            "the population they serve (more underserved), darker "
            "= more (better served). Barangays with zero facilities "
            "of this type are shown in grey. District boundaries "
            "are drawn in black for context."
        )

        # ------------------------------------------
        # DISCRETE BINS (matches the reference GIS maps' style —
        # see compute_quantile_bins / discrete_bin_color_and_label
        # in functions.py for why these are computed from
        # quantiles rather than hand-picked per indicator).
        # ------------------------------------------

        bin_edges = compute_quantile_bins(
            barangay_geo[selected_ratio_label],
            n_bins=6
        )

        _n_colors = max(len(bin_edges) - 1, 1)
        _color_idx = np.linspace(0, len(QCD_SEQUENTIAL) - 1, _n_colors)

        bin_colors = [
            hex_to_rgb(QCD_SEQUENTIAL[int(round(i))])
            for i in _color_idx
        ]

        ZERO_FACILITY_COLOR = [225, 225, 225]

        def _bin_color_label(value):
            return discrete_bin_color_and_label(
                value, bin_edges, bin_colors, ZERO_FACILITY_COLOR
            )

        _bin_results = barangay_geo[selected_ratio_label].apply(_bin_color_label)

        barangay_geo["fill_color"] = _bin_results.apply(
            lambda pair: pair[0] + [215]
        )
        barangay_geo["bin_label"] = _bin_results.apply(
            lambda pair: pair[1]
        )

        barangay_choropleth_geojson = json.loads(
            barangay_geo.to_json()
        )

        # ------------------------------------------
        # VIEW STATE
        # ------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            min_zoom=11,
            max_zoom=17,
        )

        # ------------------------------------------
        # Barangay choropleth
        # ------------------------------------------

        barangay_choropleth_layer = pdk.Layer(
            "GeoJsonLayer",
            data=barangay_choropleth_geojson,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[120, 120, 120, 150],
            line_width_min_pixels=0.6,
            pickable=True,
            auto_highlight=True
        )

        # District boundaries drawn as a bold outline on top, for
        # context only, not a second choropleth — matching the
        # reference maps, which never color districts separately.
        district_boundary_layer = pdk.Layer(
            "GeoJsonLayer",
            data=json.loads(district_map.to_json()),
            stroked=True,
            filled=False,
            get_line_color=[20, 20, 20, 220],
            line_width_min_pixels=2.5,
            pickable=False
        )

        # ------------------------------------------
        # TOOLTIP
        # ------------------------------------------

        tooltip = {
            "html": f"""
            <b>{{Barangay}}</b><br/>
            {selected_ratio_label}: {{{selected_ratio_label}}} ({{bin_label}})<br/>
            Facilities (any type): {{Facilities}}<br/>
            Population: {{Total}}
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "12px"
            }
        }

        # ------------------------------------------
        # MAP
        # ------------------------------------------

        deck = pdk.Deck(
            layers=[
                barangay_choropleth_layer,
                district_boundary_layer,
                load_reservoir_layer()
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-61"):
            st.markdown(
                render_discrete_legend_html(
                    list(zip(bin_edges_to_labels(bin_edges), bin_colors)),
                    zero_label="No facility",
                    zero_color=ZERO_FACILITY_COLOR,
                    label=f"{selected_ratio_label} by Barangay"
                ),
                unsafe_allow_html=True
            )
            st.pydeck_chart(
                deck,
                height=750
            )

        st.divider()

        # ==================================================
        # PRIORITY BARANGAYS
        # ==================================================

        st.subheader(
            "Priority Barangays"
        )

        st.caption(
            f"Ranked by lowest {selected_ratio_label}, then by "
            "highest population (areas where the gap affects "
            "the most people). The **Dominant Zone** column shows "
            "the most common land-use designation in each barangay "
            "from QC's zoning data, a low ratio in a dense R-3 "
            "residential barangay signals a genuine care facility "
            "shortage, while the same ratio in an industrial or "
            "utility zone may reflect land-use constraints rather "
            "than unmet need."
        )

        priority_barangays = (
            barangay_access
            .dropna(subset=[selected_ratio_label])
            .sort_values(
                [selected_ratio_label, "Total"],
                ascending=[True, False]
            )
            .head(25)
        )

        #  Enrich with dominant zone 
        try:
            _zs_p = pd.read_csv(
                "processed/reference/zoning/qc_zoning_summary.csv"
            )
            _nlu_p = {"ROAD", "WATER", "X"}
            _zc_p = [
                c for c in _zs_p.columns
                if c not in (
                    "barangay_id", "barangay", "total_polygons"
                ) and c not in _nlu_p
            ]
            def _dom_p(row):
                vals = {
                    c: row[c] for c in _zc_p
                    if c in row and pd.notna(row[c])
                    and row[c] > 0
                }
                return max(vals, key=vals.get) if vals else "Unknown"
            _zs_p["Dominant Zone"] = _zs_p.apply(_dom_p, axis=1)
            _zs_p["_join"] = (
                _zs_p["barangay"].astype(str).str.strip().str.title()
            )
            priority_barangays = priority_barangays.copy()
            priority_barangays["_join"] = (
                priority_barangays["Barangay"]
                .astype(str).str.strip().str.title()
            )
            priority_barangays = priority_barangays.merge(
                _zs_p[["_join", "Dominant Zone"]],
                on="_join", how="left"
            ).drop(columns=["_join"])
            priority_cols = [
                "Barangay", "District", "Total", "Facilities",
                selected_ratio_label, "Facilities per 10k Population",
                "Dominant Zone"
            ]
        except Exception:
            priority_cols = [
                "Barangay", "District", "Total", "Facilities",
                selected_ratio_label, "Facilities per 10k Population"
            ]

        with st.container(border=True, key="qcd-chart-64"):
            st.dataframe(
                priority_barangays[
                    [c for c in priority_cols
                     if c in priority_barangays.columns]
                ],
                width="stretch"
            )

    with tab_socio:

        st.markdown("""
        Contextual socio-economic indicators at the barangay
        level, household composition, food insecurity, and
        housing conditions (2024 CBMS), plus sex ratio and the
        share of working-age women.
        """)

        st.info(
            "**CBMS coverage note.** The household-survey "
            "indicators below (household size, nuclear families "
            "per household, food insecurity, housing inadequacy) "
            "come from the 2024 Community-Based Monitoring System, "
            "which covers roughly 71% of Quezon City's census "
            "population, not a full count. They should be read "
            "as indicative of conditions in responding households, "
            "not as exact citywide totals."
        )

        with st.expander("Recommended Policy Actions: Integrated Care Planning", expanded=False):

            st.markdown("""
            **Linking Accessibility Gaps to Socio-Economic Need:**
            1. **Vulnerability-Accessibility Overlap** → Barangays with both low accessibility AND high
               socio-economic need (food insecurity, disability prevalence, housing inadequacy) require
               integrated services, not just more facilities. Design multi-service hubs rather than
               single-purpose clinics.

            2. **Prioritize Mixed-Service Centers** → In high-need barangays, co-locate childcare, health,
               and older persons care. A single multi-service center serving clustered barangays is often more
               cost-effective than separate facilities.

            3. **Climate Risk Overlay** → Check the Climate Layers page to see if
               socio-economically vulnerable barangays are also flood/heat-exposed. These areas need
               climate-resilient infrastructure (e.g., elevated facilities, emergency care caches).

            4. **Next Step: Care Planning** → Use the Care Planning & Investment Priorities page to model
               facility allocation scenarios based on these three combined factors: accessibility gaps,
               socio-economic need, and climate exposure.
            """)

        # ---------------------------------------------------
        # MAP DATA
        # ---------------------------------------------------

        # Domestic worker counts (domestic_workers_female/male/total)
        # are already plain columns on `demographics` — see
        # load_domestic_workers() in functions.py for how they got
        # there — so no separate merge is needed here anymore, just
        # the per-1,000 ratios below.
        demographics_with_dw = demographics.copy()

        demographics_with_dw["domestic_workers_per_1000_total"] = (
            demographics_with_dw["domestic_workers_total"]
            / demographics_with_dw["pop_census"]
            * 1000
        )

        demographics_with_dw["domestic_workers_per_1000_female"] = (
            demographics_with_dw["domestic_workers_female"]
            / demographics_with_dw["pop_female"]
            * 1000
        )

        demographics_with_dw["domestic_workers_per_1000_male"] = (
            demographics_with_dw["domestic_workers_male"]
            / demographics_with_dw["pop_male"]
            * 1000
        )

        socio_indicators = {
            "Population (Census)": {
                "col": "pop_census",
                "description": (
                    "Total population, by barangay (2024 "
                    "census). Standalone population "
                    "distribution map, separate from the "
                    "per-1,000 domestic worker rates above, "
                    "for seeing raw population scale on its "
                    "own, in the same map/table format as "
                    "every other indicator here."
                )
            },
            "Sex Ratio (Males per 100 Females)": {
                "col": "sex_ratio_m_per_100f",
                "description": (
                    "Males per 100 females per barangay."
                )
            },
            "Share of Working-Age Women (%)": {
                "col": "share_women_18_59_pct",
                "description": (
                    "Women aged 18–59 as a share of total "
                    "population, a proxy for female labor "
                    "available for paid work and unpaid care."
                )
            },
            "Average Household Size": {
                "col": "cbms_avg_household_size",
                "description": (
                    "Average number of persons per household. "
                    "Context on household dependency load."
                )
            },
            "Average Nuclear Families per Household": {
                "col": "cbms_avg_nuclear_families_per_hh",
                "description": (
                    "Average number of nuclear families per "
                    "household; values above 1 indicate "
                    "doubling-up or shared dwellings."
                )
            },
            "Food Insecurity Prevalence (%)": {
                "col": "cbms_food_insecurity_prevalence_pct",
                "description": (
                    "Share of households worried about not "
                    "having enough food to eat (mild / headline "
                    "food insecurity)."
                )
            },
            "Severe Food Insecurity (%)": {
                "col": "cbms_food_severe_wholeday_pct",
                "description": (
                    "Share of households that went without "
                    "eating for a whole day (most severe food "
                    "insecurity)."
                )
            },
            "Food Insecurity Intensity Score": {
                "col": "cbms_food_intensity_score",
                "description": (
                    "Severity-weighted score across all eight "
                    "food insecurity items (1 = worried, 8 = "
                    "whole day without eating)."
                )
            },
            "Housing Inadequacy Index (%)": {
                "col": "cbms_housing_inadequacy_index_pct",
                "description": (
                    "Average share of households with unimproved "
                    "(natural, light, or salvaged) roof, walls, "
                    "and floor."
                )
            },
            "Severe Housing Deprivation (%)": {
                "col": "cbms_housing_makeshift_severe_pct",
                "description": (
                    "Share of households using makeshift / "
                    "salvaged / improvised building materials."
                )
            },
            "Total Domestic Workers (Count)": {
                "col": "domestic_workers_total",
                "description": (
                    "Total registered domestic workers, by "
                    "barangay (raw count, not a rate). "
                    "Source: processed/indicators/"
                    "demographics_by_barangay.csv."
                )
            },
            "Female Domestic Workers (Count)": {
                "col": "domestic_workers_female",
                "description": (
                    "Registered female domestic workers, by "
                    "barangay (raw count, not a rate)."
                )
            },
            "Male Domestic Workers (Count)": {
                "col": "domestic_workers_male",
                "description": (
                    "Registered male domestic workers, by "
                    "barangay (raw count, not a rate)."
                )
            },
        }

        selected_socio_label = st.selectbox(
            "Select Socio-Economic Indicator",
            list(socio_indicators.keys()),
            key="socio_indicator_select"
        )

        selected_socio_col = (
            socio_indicators[selected_socio_label]["col"]
        )

        st.caption(
            socio_indicators[selected_socio_label]["description"]
        )

        # Normalize join keys defensively, same convention used
        # throughout this dashboard.
        demographics_socio = demographics_with_dw[
            ["barangay", "district", selected_socio_col]
        ].copy()

        demographics_socio["barangay"] = (
            demographics_socio["barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        socio_map = barangay_map.merge(
            demographics_socio,
            left_on="barangay_name",
            right_on="barangay",
            how="left"
        )

        socio_map = socio_map.rename(
            columns={"district": "District"}
        )

        # ---------------------------------------------------
        # KPI CARDS
        # ---------------------------------------------------

        socio_avg = socio_map[selected_socio_col].mean()
        socio_max_row = socio_map.loc[
            socio_map[selected_socio_col].idxmax()
        ]
        socio_min_row = socio_map.loc[
            socio_map[selected_socio_col].idxmin()
        ]

        sc1, sc2, sc3 = st.columns(3)

        kpi_card(
            sc1,
            "Citywide Average",
            f"{socio_avg:,.2f}"
        )

        kpi_card(
            sc2,
            "Most Vulnerable Barangay",
            f"{socio_max_row['barangay_name'].title()} "
            f"({socio_max_row[selected_socio_col]:,.2f})"
        )

        kpi_card(
            sc3,
            "Least Vulnerable Barangay",
            f"{socio_min_row['barangay_name'].title()} "
            f"({socio_min_row[selected_socio_col]:,.2f})"
        )

        st.divider()

        # ---------------------------------------------------
        # MAP
        # ---------------------------------------------------

        st.subheader(
            f"Barangay Map, {selected_socio_label}"
        )

        socio_vmin = socio_map[selected_socio_col].quantile(0.05)
        socio_vmax = socio_map[selected_socio_col].quantile(0.95)

        socio_map["fill_color"] = (
            socio_map[selected_socio_col].apply(
                lambda v: value_to_rgba(v, socio_vmin, socio_vmax)
            )
        )

        socio_geojson = json.loads(
            socio_map.to_json()
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            min_zoom=11,
            max_zoom=17,
        )

        socio_layer = pdk.Layer(
            "GeoJsonLayer",
            data=socio_geojson,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[102, 102, 102],
            line_width_min_pixels=0.5,
            pickable=True,
            auto_highlight=True
        )

        tooltip = {
            "html": f"""
            <b>{{barangay_name}}</b><br/>
            {selected_socio_label}: {{{selected_socio_col}}}
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "12px"
            }
        }

        deck = pdk.Deck(
            layers=[
                socio_layer,
                load_reservoir_layer()
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-10"):
            # pydeck draws the fill color but never explains it.
            # Unit is derived from the column name itself rather
            # than a separate hand-maintained lookup, since these
            # columns follow a consistent naming convention
            # (_pct, per_1000, per_100f) that would otherwise need
            # to be kept in sync with socio_indicators by hand.
            if selected_socio_col.endswith("_pct"):
                socio_unit = "%"
            elif "per_1000" in selected_socio_col:
                socio_unit = "per 1,000"
            elif "per_100f" in selected_socio_col:
                socio_unit = "per 100 females"
            else:
                socio_unit = ""

            st.markdown(
                render_colormap_legend_html(
                    "Purples",
                    socio_vmin,
                    socio_vmax,
                    unit=socio_unit,
                    label=f"{selected_socio_label} (darker = higher)"
                ),
                unsafe_allow_html=True
            )

            st.pydeck_chart(
                deck,
                height=650
            )

elif page == "Care Planning & Investment Priorities":


    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Care Planning & Investment Priorities
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    This section identifies barangays where future
    care-related investments may have the greatest impact.

    The analysis combines population demand,
    existing infrastructure, care demand,
    and service diversity to prioritize
    areas for intervention.
    """)

    # ==================================================
    # BARANGAY DATA - CORRECTED PRIORITY CALCULATION
    # ==================================================
    # CHANGE: Split "Facilities" by type to match research findings
    # This prevents high childcare counts from masking elderly/PWD care gaps
    # ==================================================

    barangay_access = demographics.copy()

    barangay_access = barangay_access.rename(
        columns={
            "barangay": "Barangay",
            "district": "District",
            "pop_census": "Total",
            "Total": "Total_Facilities"  # Renamed for clarity
        }
    )

    # ==================================================
    # PWD DATA
    # ==================================================
    # pwd_registered (verified identical to the old standalone
    # processed/persons_with_disability_by_barangay.csv's "PWDs"
    # column before that file was retired) is already on
    # `demographics`/barangay_access — no separate file or merge
    # needed.
    barangay_access["Persons with Disabilities"] = (
        barangay_access["pwd_registered"]
    )

    # ==================================================
    # FACILITY TYPES - SEPARATED BY CARE DOMAIN
    # (This is the key fix: don't sum all facilities together)
    # ==================================================

    # Eldercare facilities: Use ONLY "Older persons care" (elderly-specific)
    # Exclude "Health centers" and "Long-term care" which serve multiple populations
    eldercare_facility_cols = ["Older persons care"]

    # Childcare facilities (see compute_childcare_facility_counts_by_
    # barangay in functions.py): the "Childcare" major_division plus
    # Schools' "Preschool" category specifically -- not every Schools
    # row, which would pull in Elementary/Junior High/Senior High/
    # Special Education Program facilities that don't serve the 0-5
    # population Childcare_Demand is measuring.
    barangay_access["Childcare_Facilities"] = (
        barangay_access["Childcare-Relevant Facilities"]
        if "Childcare-Relevant Facilities" in barangay_access.columns else 0
    )

    barangay_access["Eldercare_Facilities"] = (
        barangay_access[eldercare_facility_cols].sum(axis=1)
    )

    # PWD Facilities (see compute_pwd_facility_counts_by_barangay in
    # functions.py): Long-term care categories with "center" but not
    # "clinic" in the name, plus Schools' "Special Education
    # Program" category.
    barangay_access["Disability_Facilities"] = (
        barangay_access["PWD Facilities"]
        if "PWD Facilities" in barangay_access.columns else 0
    )

    # Keep total facilities for display
    barangay_access["Facilities"] = barangay_access["Total_Facilities"]

    # ==================================================
    # CARE DEMAND - BY POPULATION TYPE
    # ==================================================

    barangay_access["Childcare_Demand"] = (
        barangay_access["age_0_5"]
    )

    barangay_access["Eldercare_Demand"] = (
        barangay_access["age_60plus"]
    )

    # Disability Demand: Use the merged registered-persons-with-disabilities column
    if "Persons with Disabilities" in barangay_access.columns:
        barangay_access["Disability_Demand"] = barangay_access["Persons with Disabilities"]
    else:
        barangay_access["Disability_Demand"] = 0

    # Combined metric across all three domains -- children, older
    # persons, AND persons with disabilities. Every table/chart/tooltip
    # below that shows "Care Demand" is built from this single
    # definition, so what's displayed always matches what the Priority
    # Score itself is actually driven by (previously this summed only
    # Childcare_Demand + Eldercare_Demand, so a barangay could rank
    # near the top of "Top 25 Priority Barangays" purely on a
    # disability-facility gap while its displayed "Care Demand" number
    # silently excluded the PWD population responsible for that rank).
    barangay_access["Care Demand"] = (
        barangay_access["Childcare_Demand"]
        +
        barangay_access["Eldercare_Demand"]
        +
        barangay_access["Disability_Demand"]
    )

    barangay_access["Facilities per 10k Population"] = (
        barangay_access["Facilities"]
        /
        barangay_access["Total"]
        * 10000
    )

    barangay_access["Care Demand per Facility"] = (
        barangay_access["Care Demand"]
        /
        barangay_access["Facilities"]
    )

    barangay_access = barangay_access.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # ==================================================
    # PRIORITY SCORES - THREE SEPARATE CALCULATIONS
    # ==================================================
    # Each score isolates demand/supply for ONE care type
    # This reveals Commonwealth as #1 for eldercare/disability
    # ==================================================

    n_barangays = len(barangay_access)

    # ============================================
    # CHILDCARE PRIORITY SCORE
    # ============================================
    barangay_access["Childcare_Demand_Rank"] = (
        barangay_access["Childcare_Demand"].rank(ascending=False)
    )

    # Facility gap is ranked on facilities PER 1,000 RESIDENTS, not
    # the raw facility count. Ranking on the raw count let a tiny,
    # low-population barangay with literally 0 facilities (e.g.
    # Valencia, pop. ~11k) tie for the best/scarcest rank alongside
    # -- or ahead of -- a massive barangay with dozens of facilities
    # that are nonetheless nowhere near enough for its population
    # (e.g. Holy Spirit, pop. ~112k, 46 facilities). A raw count
    # can't distinguish "scarce because tiny" from "scarce relative
    # to six figures of residents"; a per-capita rate can.
    barangay_access["Childcare_Facility_Rate"] = (
        barangay_access["Childcare_Facilities"] / barangay_access["Total"] * 1000
    )

    barangay_access["Childcare_Facility_Rank"] = (
        barangay_access["Childcare_Facility_Rate"].rank(ascending=True)
    )

    barangay_access["Childcare_Priority_Score"] = (
        (n_barangays + 1 - barangay_access["Childcare_Demand_Rank"]) * 0.50
        +
        (n_barangays + 1 - barangay_access["Childcare_Facility_Rank"]) * 0.50
    )

    # Normalize to 0-100
    max_childcare = barangay_access["Childcare_Priority_Score"].max()
    if max_childcare > 0:
        barangay_access["Childcare_Priority_Score"] = (
            barangay_access["Childcare_Priority_Score"] / max_childcare * 100
        )

    # ============================================
    # ELDERCARE PRIORITY SCORE (Commonwealth #1)
    # ============================================
    barangay_access["Eldercare_Demand_Rank"] = (
        barangay_access["Eldercare_Demand"].rank(ascending=False)
    )

    # Per-capita rate, not raw count -- see the Childcare block above
    # for why (same fix, same reasoning, applied per domain).
    barangay_access["Eldercare_Facility_Rate"] = (
        barangay_access["Eldercare_Facilities"] / barangay_access["Total"] * 1000
    )

    barangay_access["Eldercare_Facility_Rank"] = (
        barangay_access["Eldercare_Facility_Rate"].rank(ascending=True)
    )

    barangay_access["Eldercare_Priority_Score"] = (
        (n_barangays + 1 - barangay_access["Eldercare_Demand_Rank"]) * 0.40
        +
        (n_barangays + 1 - barangay_access["Eldercare_Facility_Rank"]) * 0.60  # Weight gap heavier
    )

    # Normalize to 0-100
    max_eldercare = barangay_access["Eldercare_Priority_Score"].max()
    if max_eldercare > 0:
        barangay_access["Eldercare_Priority_Score"] = (
            barangay_access["Eldercare_Priority_Score"] / max_eldercare * 100
        )

    # ============================================
    # DISABILITY PRIORITY SCORE (Commonwealth #1)
    # ============================================
    barangay_access["Disability_Demand_Rank"] = (
        barangay_access["Disability_Demand"].rank(ascending=False)
    )

    # Per-capita rate, not raw count -- see the Childcare block above
    # for why (same fix, same reasoning, applied per domain).
    barangay_access["Disability_Facility_Rate"] = (
        barangay_access["Disability_Facilities"] / barangay_access["Total"] * 1000
    )

    barangay_access["Disability_Facility_Rank"] = (
        barangay_access["Disability_Facility_Rate"].rank(ascending=True)
    )

    barangay_access["Disability_Priority_Score"] = (
        (n_barangays + 1 - barangay_access["Disability_Demand_Rank"]) * 0.40
        +
        (n_barangays + 1 - barangay_access["Disability_Facility_Rank"]) * 0.60
    )

    # Normalize to 0-100
    max_disability = barangay_access["Disability_Priority_Score"].max()
    if max_disability > 0:
        barangay_access["Disability_Priority_Score"] = (
            barangay_access["Disability_Priority_Score"] / max_disability * 100
        )

    # ============================================
    # OVERALL PRIORITY SCORE
    # (Reflects need across all three domains, not just whichever one
    # is worst -- a barangay that's moderately underserved in all
    # three should rank ahead of one that's fine in two and bad in
    # only one, which a max() can't distinguish from a barangay that's
    # bad in one and fine in the other two.)
    # ============================================
    barangay_access["Priority Score"] = barangay_access[[
        "Childcare_Priority_Score",
        "Eldercare_Priority_Score",
        "Disability_Priority_Score"
    ]].mean(axis=1)

    # Still track which single domain is the biggest driver for each
    # barangay -- useful context even though it no longer determines
    # the overall score by itself.
    priority_domains = ["Childcare_Priority_Score", "Eldercare_Priority_Score", "Disability_Priority_Score"]
    barangay_access["Primary_Priority_Domain"] = barangay_access[priority_domains].idxmax(axis=1)
    barangay_access["Primary_Priority_Domain"] = (
        barangay_access["Primary_Priority_Domain"]
        .str.replace("_Priority_Score", "")
    )

    barangay_access = (
        barangay_access
        .sort_values(
            ["Priority Score", "Total"],
            ascending=[False, False]
        )
    )

    # ==================================================
    # KPI CARDS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            st,
            "Total Barangays",
            len(barangay_access)
        )

    with col2:
        no_care_count = int((barangay_access["Facilities"] == 0).sum())
        kpi_card(
            st,
            "Barangays with No Care Facility",
            no_care_count,
            "down_good"
        )

    with col3:
        highest_priority = barangay_access.iloc[0]["Barangay"]
        kpi_card(
            st,
            "Highest Overall Priority",
            highest_priority
        )

    with col4:
        kpi_card(
            st,
            "Average Priority Score",
            round(
                barangay_access["Priority Score"].mean(),
                1
            )
        )

    with st.expander(" Methodology: How Priority Scores Work", expanded=False):
        st.markdown("""
        ### Three Separate Priority Metrics

        Rather than combining all facility types into one "Facilities" count (which masks gaps),
        this analysis calculates priority separately for each care domain:

        **Childcare Priority Score** = 50% × (Children Rank) + 50% × (Facility Gap Rank)
        - Identifies barangays with many children (age 0–5) but few childcare/school facilities
        - **What counts as a childcare facility:** the "Childcare" division (Child Development
          Centers/Supervised Play, Child Learning Centers, Day Care Centers) plus Schools rows
          categorized "Preschool" specifically — not every Schools row, which would pull in
          Elementary/Junior High/Senior High/Special Education Program facilities that don't
          serve the 0–5 population this score is measuring against

        **Older Persons Priority Score** = 40% × (Older Persons Rank) + 60% × (Facility Gap Rank)
        - Identifies barangays with many seniors (age 60+) but few eldercare facilities
        - Higher weight on facility gap because older persons care is severely underprovided
        - **What counts as an eldercare facility:** only the "Older persons care" division —
          Health centers and Long-term care/rehabilitation facilities are deliberately excluded,
          since those serve multiple populations rather than seniors specifically

        **Disability Priority Score** = 40% × (Persons with Disabilities Rank) + 60% × (Facility Gap Rank)
        - Identifies barangays with many registered persons with disabilities but few disability services
        - Higher weight on facility gap because disability services are nearly absent city-wide
        - **What counts as a disability facility:** counts only health facilities with "center" in
          the name, excluding clinics as they are more medical-related. It additionally includes
          two categories — "Special Education Program" and "Therapy Center."

        **Facility Gap Rank is per 1,000 residents, not a raw facility count.**

        **Overall Priority Score** = Average of the three domains
        """)

    # ==================================================
    # MAP
    # ==================================================

    barangay_geo = gpd.read_file(
        "processed/reference/qc_barangays.geojson"
    )
    # ==================================================
    # MAP
    # ==================================================

    barangay_geo = gpd.read_file(
        "processed/reference/qc_barangays.geojson"
    )

    # Normalize join keys defensively, both sides must
    # match exactly on the merge key, regardless of how
    # they were cleaned upstream.
    barangay_geo["barangay_name"] = (
        barangay_geo["barangay_name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    barangay_access["Barangay"] = (
        barangay_access["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    priority_map = barangay_geo.merge(
        barangay_access,
        left_on="barangay_name",
        right_on="Barangay",
        how="left"
    )

    st.subheader(
        "Priority Investment Map"
    )

    st.caption(
        "Darker = higher Priority Score = more underserved relative "
        "to need. Gray = no care facility data available for that "
        "barangay (see note above if shown)."
    )

    def purd_color(t):

        if pd.isna(t):
            return [204, 204, 204, 100]

        t = min(max(t, 0), 1)

        # Light lavender -> deep magenta/purple, approximating
        # the matplotlib "PuRd" colormap used by folium.Choropleth
        stops = [
            (0.00, (247, 244, 249)),
            (0.25, (215, 181, 216)),
            (0.50, (223, 101, 176)),
            (0.75, (174, 1, 126)),
            (1.00, (103, 0, 31))
        ]

        for i in range(len(stops) - 1):

            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]

            if t0 <= t <= t1:

                local_t = (
                    (t - t0) / (t1 - t0)
                    if t1 > t0 else 0
                )

                r = c0[0] + (c1[0] - c0[0]) * local_t
                g = c0[1] + (c1[1] - c0[1]) * local_t
                b = c0[2] + (c1[2] - c0[2]) * local_t

                return [int(r), int(g), int(b), 205]

        return [103, 0, 31, 205]

    # Colored by PERCENTILE RANK, not the raw Priority Score value.
    # Overall Priority Score is a max of three already-normalized-to-100
    # domain scores, so its distribution skews high (median ~75 across
    # the 142 barangays) -- a straight min-max color scale would then
    # put most of the city in the darker half of the gradient, making
    # the map read as "everywhere is high priority" even though the
    # barangays still differ meaningfully in relative rank. Percentile
    # rank spreads the same 142 barangays evenly across the gradient
    # regardless of how bunched the underlying scores are, so the
    # map's color differences track relative priority again.
    #
    # Colors must be computed from the numeric "Priority Score"
    # BEFORE that column gets overwritten with the "No data"
    # placeholder string below.
    score_percentile = priority_map["Priority Score"].rank(pct=True)

    priority_map["fill_color"] = score_percentile.apply(purd_color)

    tooltip_fields = [
        "Barangay",
        "Facilities",
        "Care Demand",
        "Priority Score"
    ]

    # "Barangay" comes from the right side of the left-merge above,
    # so it's NaN for any polygon with no matching row in
    # barangay_access. "barangay_name" comes from the geometry
    # itself and is always populated, so use it as the display name
    # whenever "Barangay" is missing.
    priority_map["Barangay"] = (
        priority_map["Barangay"]
        .fillna(priority_map["barangay_name"])
    )

    # Round numeric fields and substitute a clear placeholder
    # for missing values so the tooltip never shows blank.
    for col in ["Facilities", "Care Demand", "Priority Score"]:
        priority_map[col] = priority_map[col].round(1)

    priority_map[tooltip_fields] = priority_map[tooltip_fields].fillna("No data")

    priority_map_geojson = json.loads(
        priority_map.to_json()
    )

    # ------------------------------------------
    # VIEW STATE
    # ------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,
        max_zoom=17,
    )

    # ------------------------------------------
    # Priority choropleth
    # ------------------------------------------

    priority_layer = pdk.Layer(
        "GeoJsonLayer",
        data=priority_map_geojson,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[102, 102, 102, 150],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True
    )

    # ------------------------------------------
    # TOOLTIP
    # ------------------------------------------

    tooltip = {
        "html": """
        <b>{Barangay}</b><br/>
        Facilities: {Facilities}<br/>
        Care Demand (children, seniors & persons with disabilities): {Care Demand}<br/>
        Priority Score: {Priority Score}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # ------------------------------------------
    # MAP
    # ------------------------------------------

    deck = pdk.Deck(
        layers=[
            priority_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"
    )

    with st.container(border=True, key="qcd-chart-66"):
        st.pydeck_chart(
            deck,
            height=750
        )

    st.divider()

    # ==================================================
    # PRIORITY DISTRICTS FOR FUTURE INVESTMENT
    # ==================================================

    st.subheader(
        "Priority Districts for Future Investment"
    )

    st.caption(
        "Ranked by highest priority score. Higher Care Demand per Facility "
        "indicates districts requiring investment."
    )

    # Aggregate barangay data to district level for priority analysis
    district_priority = (
        barangay_access
        .groupby("District")
        .agg({
            "Total": "sum",
            "Facilities": "sum",
            "Care Demand": "sum",
            "Priority Score": "mean",
            "Care Demand per Facility": "mean"
        })
        .reset_index()
        .round(2)
    )

    # Sort by Priority Score descending
    district_priority = district_priority.sort_values(
        "Priority Score",
        ascending=False
    )

    # Get top 5 districts
    top_priority_districts = district_priority.head(5).copy()
    top_priority_districts["District"] = top_priority_districts["District"].astype(str)

    # Rename columns for display
    display_cols = top_priority_districts.rename(columns={
        "District": "District",
        "Total": "Population",
        "Facilities": "Total Facilities",
        "Care Demand": "Care Demand (0-5, 60+ & Persons with Disabilities)",
        "Priority Score": "Priority Score (0-100)",
        "Care Demand per Facility": "Avg. Population per Facility"
    })

    with st.container(border=True, key="qcd-chart-66b"):
        st.dataframe(
            display_cols[
                [
                    "District",
                    "Population",
                    "Total Facilities",
                    "Care Demand (0-5, 60+ & Persons with Disabilities)",
                    "Priority Score (0-100)",
                    "Avg. Population per Facility"
                ]
            ],
            column_config={
                "District": st.column_config.TextColumn("District", width="small"),
                "Population": st.column_config.NumberColumn("Population", width="medium", format="localized"),
                "Total Facilities": st.column_config.NumberColumn("Total Facilities", width="small", format="%d"),
                "Care Demand (0-5, 60+ & Persons with Disabilities)": st.column_config.NumberColumn("Care Demand (0-5, 60+ & Persons with Disabilities)", width="medium", format="localized"),
                "Priority Score (0-100)": st.column_config.NumberColumn("Priority Score (0-100)", width="medium", format="%.1f"),
                "Avg. Population per Facility": st.column_config.NumberColumn("Avg. Population per Facility", width="medium", format="%.0f")
            },
            hide_index=True,
            width="stretch"
        )

    # Add actionable guidance text
    st.markdown("""
    <div class="qcd-insight">
        <div class="qcd-insight-label">Policy Guidance for District Investment</div>
        <div class="qcd-insight-body">
            <strong>Districts at the top of this list require immediate attention</strong>, they
            have high care demand relative to available facilities and fewer facilities per capita. Consider:
            <ul style="margin-top: 8px; margin-bottom: 0;">
                <li><strong>New facility placement:</strong> Prioritize construction or renovation of care
                    facilities in high-priority districts</li>
                <li><strong>Service expansion:</strong> Explore whether existing nearby facilities can
                    expand service hours or reach to underserved areas</li>
                <li><strong>Community-based care:</strong> Support training and licensing of in-home or
                    community-based care providers as an interim solution</li>
                <li><strong>Infrastructure partnerships:</strong> Collaborate with schools, health centers,
                    and NGOs to co-locate or share care services</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ==================================================
    # TOP 25 PRIORITY BARANGAYS
    # ==================================================

    st.subheader(
        "Top 25 Priority Barangays"
    )

    with st.container(border=True, key="qcd-chart-67"):
        st.dataframe(
            barangay_access[
                [
                    "Barangay",
                    "District",
                    "Total",
                    "Facilities",
                    "Care Demand",
                    "Priority Score"
                ]
            ].head(25),
            width="stretch"
        )

    # ==================================================
    # CHART
    # ==================================================

    fig = px.bar(
        barangay_access.head(25),
        x="Priority Score",
        y="Barangay",
        orientation="h",
        color="Priority Score",
        title="Top 25 Critical Intervention Zones (Children, Older Persons & Persons with Disabilities Underserved)",
        color_continuous_scale=QCD_SEQUENTIAL
    )

    fig.update_layout(
        height=700
    )

    with st.container(border=True, key="qcd-chart-68"):
        st.plotly_chart(
            fig
        )

    st.divider()

    # ==================================================
    # BARANGAYS WITH NO FACILITIES
    # ==================================================

    st.subheader(
        "Barangays with No Facilities"
    )

    care_deserts = (
        barangay_access[
            barangay_access["Facilities"] == 0
        ]
        .sort_values(
            "Care Demand",
            ascending=False
        )
    )

    st.markdown("""
    These barangays currently have no registered care facilities
    in the inventory. They represent critical gaps in service coverage
    and should be prioritized for facility placement and service development.
    """)

    kpi_card(
        st,
        "Barangays with No Facilities",
        len(care_deserts),
        "down_good"
    )

    with st.container(border=True, key="qcd-chart-69"):
        st.dataframe(
            care_deserts[
                [
                    "Barangay",
                    "District",
                    "Total",
                    "Care Demand",
                    "Priority Score"
                ]
            ],
            width="stretch"
        )

    st.divider()

    # ==================================================
    # DOWNLOAD TABLE
    # ==================================================

    csv = (
        barangay_access
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "Download Priority Planning Table",
        csv,
        "priority_barangays.csv",
        "text/csv"
    )

elif page == "Barangay Clusters":


    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Barangay Clusters
        </h2>
        """,
        unsafe_allow_html=True
    )

    with st.expander("Why Cluster Barangays?", expanded=False):
        st.markdown("""
        Quezon City's 142 barangays face vastly different care challenges. Rather than
        building interventions for each barangay individually, clustering groups similar
        neighborhoods so you can **design tailored solutions by type**.

        For example:
        - **High-density, young neighborhoods** need more schools and childcare but may have
          fewer elder care facilities
        - **Sparse, aging neighborhoods** need elder care and health services within reach
        - **Well-served neighborhoods** can focus on quality improvement
        - **Underserved neighborhoods** need basic facility placement

        This page identifies these patterns automatically using K-means clustering on
        demographic, accessibility, and socio-economic data.
        """)

    with st.expander("What Defines Each Cluster?", expanded=False):
        st.markdown("""
        Barangays are grouped on:

        - **Demographic Profile**, population density, proportion of children (0–17),
          proportion of older persons (60+), and sex ratio (males per 100 females)
        - **Care Accessibility**, total facilities per 10,000 residents, and the
          mix of facility types (Childcare, Health centers, Long-Term Care & Rehabilitation,
          Schools, the four most common types)
        - **Socio-Economic Vulnerability**, disability prevalence rate, food insecurity,
          housing inadequacy (all from 2024 CBMS), and registered migrant workers
          per 1,000 residents
        """)

    with st.expander("How to Use Cluster Analysis", expanded=False):
        st.markdown("""
        1. **Understand your neighborhood type**, Find your barangay's cluster to see
           what challenges are common in similar areas
        2. **Learn from peers**, Use cluster characteristics to identify neighboring
           barangays with comparable needs (easier to coordinate shared services)
        3. **Share solutions**, If one barangay in a cluster succeeds with an intervention,
           it's likely to work in others in the same cluster
        4. **Allocate resources strategically**, Prioritize facility types and services
           based on cluster profiles
        """)

    with st.expander("Worked Example: Using Cluster Insights to Plan Interventions", expanded=False):
        st.markdown("""
        **Scenario:** You notice that three barangays in the northern districts belong to Cluster 3: "dense, young, under-served."

        **What this tells you:**
        - These barangays are **densely populated** with many young families (high proportion of children 0–17)
        - They have **relatively few care facilities** per capita (under-served)
        - They share similar demographic and vulnerability profiles

        **Policy action:**
        Instead of designing three separate interventions, you decide to:
        - **Coordinate childcare facility expansion** across all three barangays (schools, learning centers, daycares)
        - **Share a regional health clinic** that serves multiple clusters with similar age profiles
        - **Pool training programs** for community health workers and early childcare providers to serve the cluster
        - **Use one RFP (Request for Proposal)** for private partners to expand services across the cluster, reducing administrative overhead

        **Why this works:**
        Because barangays in the same cluster face similar challenges, solutions designed for one are more likely to work for others.
        A high-density, young cluster needs childcare and schools; an aging, sparse cluster needs mobile health clinics and long-term care;
        a well-served cluster might focus on quality and gaps in existing services. **Cluster-based planning saves resources and targets
        interventions where they're most needed.**
        """)

    with st.expander("Recommended Policy Actions: Cluster-Based Facility Planning", expanded=False):

        st.markdown("""
        **Use Clustering for Shared Service Models & Strategic Allocation:**
        1. **Identify Your Cluster Type** → Find your priority barangays (from Care Planning page) in the
           cluster map above. Note their cluster assignment (e.g., "dense, young, under-served"). Barangays
           in the same cluster face similar challenges.

        2. **Group Similar Barangays for Shared Centers** → Instead of building a new facility in every
           underserved barangay, identify a cluster of 3–4 peer barangays with the same profile. Place one
           well-positioned, multi-service center to serve all (easier to staff, lower cost, better quality).

        3. **Tailor Services by Cluster Type** →
           - **Dense, Young Clusters** → Emphasize childcare, schools, reproductive health
           - **Sparse, Aging Clusters** → Emphasize mobile health clinics, long-term care, elder transportation
           - **Underserved (Mixed Age)** → Build integrated primary care + basic childcare/older persons support
           - **Well-Served Clusters** → Focus on quality/specialty services and peer mentoring

        4. **Cross-Cluster Coordination** → Some services (e.g., specialty care, teaching hospitals) don't need
           to be in every cluster. Place them at boundaries between clusters so they're accessible to multiple
           cluster types. This improves efficiency and avoids duplication.
        """)


    # ==================================================
    # AGE GROUP DEFINITION (same as Population Overview)
    # ==================================================

    age_group_definition = {
        "children_0_17": [
            "0-5 (Early Childhood)",
            "6-17 (School Age Children)"
        ],
        "working_age_18_59": [
            "18-59 (Working Age Adult)"
        ],
        "elderly_60_plus": [
            "60+ (Older Persons)"
        ]
    }

    # ==================================================
    # CLEAN POPULATION
    # ==================================================

    pop = population_age.copy()

    age_cols = [
        "0-5 (Early Childhood)",
        "6-17 (School Age Children)",
        "18-59 (Working Age Adult)",
        "60+ (Older Persons)",
        "Total"
    ]

    for col in age_cols:

        pop[col] = (
            pop[col]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
        )

    pop["children_0_17"] = pop[
        age_group_definition["children_0_17"]
    ].sum(axis=1)

    pop["working_age"] = pop[
        age_group_definition["working_age_18_59"]
    ].sum(axis=1)

    pop["elderly"] = pop[
        age_group_definition["elderly_60_plus"]
    ].sum(axis=1)

    pop["children_pct"] = (
        pop["children_0_17"] / pop["Total"] * 100
    )

    pop["elderly_pct"] = (
        pop["elderly"] / pop["Total"] * 100
    )

    # ==================================================
    # POPULATION DENSITY (needs barangay geometry)
    # ==================================================

    barangay_map = gpd.read_file(
        "processed/reference/qc_barangays.geojson"
    )

    barangay_map["barangay_name"] = (
        barangay_map["barangay_name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    pop["Barangay"] = (
        pop["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    pop_geo = barangay_map.merge(
        pop,
        left_on="barangay_name",
        right_on="Barangay",
        how="left"
    )

    pop_geo_metric = pop_geo.to_crs("EPSG:32651")

    pop_geo["area_km2"] = (
        pop_geo_metric.geometry.area / 1_000_000
    )

    pop_geo["population_density"] = (
        pop_geo["Total"] / pop_geo["area_km2"]
    )

    pop_geo = pop_geo.replace([np.inf, -np.inf], np.nan)

    numeric_guard_cols = [
        "Total",
        "children_0_17",
        "working_age",
        "elderly",
        "children_pct",
        "elderly_pct",
        "population_density"
    ]

    pop_geo[numeric_guard_cols] = (
        pop_geo[numeric_guard_cols].fillna(0)
    )

    # ==================================================
    # BUILD FEATURES & RUN CLUSTERING
    # ==================================================

    n_clusters = st.slider(
        "Number of clusters",
        min_value=2,
        max_value=6,
        value=4,
        help="""
        Matches the K-means exploration range used in the
        clustering notebook (3 to 6 clusters tested there).
        """
    )

    cluster_features_df, feature_cols = build_cluster_features(
        pop_geo,
        demographics
    )

    clustered, scaled_features = run_barangay_clustering(
        cluster_features_df,
        feature_cols,
        n_clusters=n_clusters
    )

    clustered["Cluster"] = clustered["Cluster"].astype(int)

    # ==================================================
    # KPI CARDS
    # ==================================================

    cluster_sizes = (
        clustered
        .groupby("Cluster")
        .size()
        .reset_index(name="Barangays")
    )

    largest_cluster = int(
        cluster_sizes.loc[
            cluster_sizes["Barangays"].idxmax(),
            "Cluster"
        ]
    )

    # ==================================================
    # PRE-COMPUTE CLUSTER MEANS FOR TAG GENERATION
    # ==================================================

    cluster_means = (
        scaled_features
        .groupby(clustered["Cluster"])
        .mean()
    )

    feature_label_map = {
        "population_density": "Population Density",
        "children_pct": "% Children (0-17)",
        "elderly_pct": "% Older Persons (60+)",
        "facilities_per_10k": "Facilities per 10k Pop.",
        "share_childcare": "% Facilities: Childcare",
        "share_health_centers": "% Facilities: Health",
        "share_long-term_care_and_rehabilitation_services":
            "% Facilities: Long-Term Care",
        "share_schools": "% Facilities: Schools",
        "sex_ratio_m_per_100f": "Sex Ratio (M/100F)",
        "disability_prevalence_rate_pct": "Disability Prevalence",
        "cbms_food_insecurity_prevalence_pct": "Food Insecurity",
        "cbms_housing_inadequacy_index_pct": "Housing Inadequacy",
        "migrant_per_1000": "Migrant Workers per 1,000"
    }

    # Generate descriptive tags for clusters
    def generate_cluster_tag(cluster_id, cluster_means, feature_label_map):
        """
        Generate a descriptive tag for a cluster based on its most extreme features.
        Returns a short phrase like "dense, young, underserved"
        Prioritizes key features and avoids duplicates for clarity.
        """
        # Get values for this cluster
        cluster_values = cluster_means.loc[int(cluster_id)]

        # Create feature-description mapping (feature name -> positive adjective, negative adjective)
        feature_descriptions = {
            "population_density": ("dense", "sparse"),
            "children_pct": ("young", "aging"),
            "elderly_pct": ("aging", "young"),
            "facilities_per_10k": ("well-served", "underserved"),
            "disability_prevalence_rate_pct": ("high disability", "low disability"),
            "cbms_food_insecurity_prevalence_pct": ("food insecure", "food secure"),
            "cbms_housing_inadequacy_index_pct": ("inadequate housing", "adequate housing"),
            "migrant_per_1000": ("high migration", "low migration"),
            "sex_ratio_m_per_100f": ("male-skewed", "female-skewed")
        }

        # Priority order: show most policy-relevant features
        priority_features = [
            "population_density",
            "elderly_pct",  # Prioritize elderly over children_pct (avoid duplication)
            "children_pct",
            "facilities_per_10k",
            "cbms_food_insecurity_prevalence_pct",
            "disability_prevalence_rate_pct",
            "sex_ratio_m_per_100f"
        ]

        tags = []
        seen_concepts = set()  # Track concepts like "age profile" to avoid duplication

        for feature in priority_features:
            if len(tags) >= 3:  # Limit to 3 tags for clarity
                break

            if feature not in feature_descriptions:
                continue

            pos_desc, neg_desc = feature_descriptions[feature]
            value = cluster_values[feature]
            tag = pos_desc if value > 0 else neg_desc

            # Skip if we already have an age-related tag (elderly_pct/children_pct)
            if feature in ["elderly_pct", "children_pct"]:
                if "age_profile" in seen_concepts:
                    continue
                seen_concepts.add("age_profile")

            # Skip duplicate tags
            if tag not in tags:
                tags.append(tag)

        return ", ".join(tags) if tags else "mixed profile"

    # Generate tags for all clusters
    cluster_tags = {}
    for cid in sorted(clustered["Cluster"].unique()):
        cluster_tags[cid] = generate_cluster_tag(cid, cluster_means, feature_label_map)

    k1, k2, k3 = st.columns(3)

    kpi_card(
        k1,
        "Barangays Clustered",
        int(clustered["barangay_name"].nunique())
    )

    kpi_card(
        k2,
        "Clusters",
        n_clusters
    )

    kpi_card(
        k3,
        "Largest Cluster",
        f"Cluster {largest_cluster}"
    )

    st.divider()

    # ==================================================
    # MAP
    # ==================================================

    st.subheader(
        "Barangay Cluster Map"
    )

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")

        return [
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        ]

    clustered["fill_color"] = clustered["Cluster"].apply(
        lambda c: hex_to_rgb(cluster_color(c)) + [205]
    )

    cluster_map_geojson = json.loads(
        clustered.to_json()
    )

    # ------------------------------------------
    # VIEW STATE
    # ------------------------------------------

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
        min_zoom=11,
        max_zoom=17,
    )

    # ------------------------------------------
    # Cluster choropleth
    # ------------------------------------------

    cluster_layer = pdk.Layer(
        "GeoJsonLayer",
        data=cluster_map_geojson,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[102, 102, 102],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True
    )

    # ------------------------------------------
    # TOOLTIP
    # ------------------------------------------

    tooltip = {
        "html": """
        <b>{barangay_name}</b><br/>
        Cluster: {Cluster}<br/>
        Population: {Total}<br/>
        Density (per km²): {population_density}<br/>
        Children Share (%): {children_pct}<br/>
        Older Persons Share (%): {elderly_pct}<br/>
        Facilities per 10k Pop.: {facilities_per_10k}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px"
        }
    }

    # ------------------------------------------
    # MAP
    # ------------------------------------------

    deck = pdk.Deck(
        layers=[
            cluster_layer,
            load_reservoir_layer()
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"
    )

    # Generate cluster explanations for common readers
    def get_cluster_explanation(cluster_id, cluster_tag):
        """
        Provides plain-language explanation of what each cluster profile means
        for policy planning and resource allocation.
        """
        explanations = {
            1: {
                "title": "Dense Neighborhoods",
                "description": "High population density areas requiring concentrated services and infrastructure investment. Priority: expand schools, childcare facilities, and health clinics."
            },
            2: {
                "title": "Aging Communities",
                "description": "Neighborhoods with high older persons population and aging demographics. Priority: older persons care services, geriatric health centers, and age-friendly community programs."
            },
            3: {
                "title": "Food-Insecure Areas",
                "description": "Communities facing significant food insecurity challenges. Priority: nutrition programs, food assistance initiatives, and income-generating activities."
            },
            4: {
                "title": "Young Populations",
                "description": "Areas with high concentrations of children and youth. Priority: schools, educational programs, youth services, and childcare facilities."
            },
            5: {
                "title": "Mixed Profile",
                "description": "Neighborhoods with diverse characteristics requiring balanced, multi-sector service provision."
            },
            6: {
                "title": "Mixed Profile",
                "description": "Neighborhoods with diverse characteristics requiring balanced, multi-sector service provision."
            }
        }

        return explanations.get(int(cluster_id), {
            "title": f"Cluster {int(cluster_id)}",
            "description": f"Profile: {cluster_tag}. This cluster shows unique characteristics that warrant tailored service planning."
        })

    cluster_ids = sorted(clustered["Cluster"].dropna().unique())

    # Create a responsive grid layout
    if len(cluster_ids) <= 2:
        cols = st.columns(len(cluster_ids))
    else:
        cols = st.columns(min(2, len(cluster_ids)))

    col_index = 0
    for cluster_id in cluster_ids:
        col = cols[col_index % len(cols)]

        cluster_tag = cluster_tags.get(cluster_id, "mixed profile")
        cluster_info = get_cluster_explanation(cluster_id, cluster_tag)
        cluster_hex = cluster_color(cluster_id)

        with col:
            # Custom HTML card styled like KPI cards
            card_html = f'''
<div style="background: linear-gradient(135deg, {cluster_hex}CC 0%, {cluster_hex} 100%); border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <div style="font-family: 'Roboto', sans-serif; font-size: 0.85rem; font-weight: 500; color: #FFFFFF; margin-bottom: 6px;">Cluster {int(cluster_id)}</div>
    <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 1.1rem; color: #FFFFFF; margin-bottom: 8px; line-height: 1.2;">{cluster_info['title']}</div>
    <div style="font-family: 'Roboto', sans-serif; font-size: 0.8rem; color: #FFFFFF; margin-bottom: 8px; line-height: 1.4;">{cluster_info['description']}</div>
    <div style="font-family: 'Roboto', sans-serif; font-size: 0.75rem; color: rgba(255,255,255,0.8); font-style: italic;">Profile: {cluster_tag}</div>
</div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)

        col_index += 1

    with st.container(border=True, key="qcd-chart-76"):
        st.pydeck_chart(
            deck,
            height=700
        )

    st.divider()

    # ==================================================
    # CLUSTER PROFILES (WIND ROSE / RADAR)
    # ==================================================

    st.subheader(
        "Cluster Profiles"
    )

    st.markdown("""
    Each radar chart shows the average standardized value
    of each feature within a cluster (0 is the citywide
    average; positive values are above average, negative
    values are below average), the same "wind rose"
    profiling used in the clustering notebook to interpret
    what makes each cluster distinct.
    """)

    profile_cols = min(2, n_clusters)
    cluster_ids = sorted(clustered["Cluster"].dropna().unique())

    cols = st.columns(profile_cols)

    cluster_means = (
        scaled_features
        .groupby(clustered["Cluster"])
        .mean()
    )

    feature_label_map = {
        "population_density": "Population Density",
        "children_pct": "% Children (0-17)",
        "elderly_pct": "% Older Persons (60+)",
        "facilities_per_10k": "Facilities per 10k Pop.",
        "share_childcare": "% Facilities: Childcare",
        "share_health_centers": "% Facilities: Health",
        "share_long-term_care_and_rehabilitation_services":
            "% Facilities: Long-Term Care",
        "share_schools": "% Facilities: Schools",
        "sex_ratio_m_per_100f": "Sex Ratio (M/100F)",
        "disability_prevalence_rate_pct": "Disability Prevalence",
        "cbms_food_insecurity_prevalence_pct": "Food Insecurity",
        "cbms_housing_inadequacy_index_pct": "Housing Inadequacy",
        "migrant_per_1000": "Migrant Workers per 1,000"
    }

    radar_labels = [
        feature_label_map.get(
            c,
            c.replace("share_", "% ").replace("_", " ")
        )
        for c in feature_cols
    ]

    for i, cid in enumerate(cluster_ids):

        with cols[i % profile_cols]:

            values = cluster_means.loc[int(cid)].tolist()

            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=values + values[:1],
                    theta=radar_labels + radar_labels[:1],
                    fill="toself",
                    name=f"Cluster {int(cid)}",
                    line_color=cluster_color(cid)
                )
            )

            cluster_tag = cluster_tags.get(cid, "")
            fig.update_layout(
                title=f"Cluster {int(cid)}: {cluster_tag}<br><sub>{int(cluster_sizes.set_index('Cluster').loc[int(cid), 'Barangays'])} barangays</sub>",
                showlegend=False,
                height=400
            )

            with st.container(border=True, key=f"qcd-chart-77-{int(cid)}"):
                st.plotly_chart(fig)

    st.divider()

    # CLUSTER SUMMARY TABLE
    # ==================================================

    st.subheader(
        "Cluster Summary"
    )

    summary_cols = [
        "Total",
        "population_density",
        "children_pct",
        "elderly_pct",
        "facilities_per_10k",
        "disability_prevalence_rate_pct",
        "cbms_food_insecurity_prevalence_pct",
        "cbms_housing_inadequacy_index_pct",
        "migrant_per_1000"
    ]

    cluster_summary = (
        clustered
        .groupby("Cluster")[summary_cols]
        .mean()
        .round(2)
        .reset_index()
    )

    cluster_summary = cluster_summary.merge(
        cluster_sizes,
        on="Cluster"
    )

    cluster_summary = cluster_summary.rename(
        columns={
            "Total": "Avg. Population",
            "population_density": "Avg. Density (per km²)",
            "children_pct": "Avg. Children Share (%)",
            "elderly_pct": "Avg. Older Persons Share (%)",
            "facilities_per_10k": "Avg. Facilities per 10k Pop.",
            "disability_prevalence_rate_pct": "Avg. Disability Prevalence (%)",
            "cbms_food_insecurity_prevalence_pct": "Avg. Food Insecurity (%)",
            "cbms_housing_inadequacy_index_pct": "Avg. Housing Inadequacy (%)",
            "migrant_per_1000": "Avg. Migrant Workers per 1,000"
        }
    )

    with st.container(border=True, key="qcd-chart-78"):
        st.dataframe(
            cluster_summary,
            width="stretch"
        )

    st.divider()

    # ==================================================
    # BARANGAYS BY CLUSTER
    # ==================================================

    st.subheader(
        "Barangays by Cluster"
    )

    selected_cluster = st.selectbox(
        "View barangays in cluster",
        cluster_ids
    )

    with st.container(border=True, key="qcd-chart-79"):
        st.dataframe(
            clustered[
                clustered["Cluster"] == selected_cluster
            ][
                [
                    "barangay_name",
                    "District",
                    "Total",
                    "population_density",
                    "children_pct",
                    "elderly_pct",
                    "facilities_per_10k",
                    "disability_prevalence_rate_pct",
                    "cbms_food_insecurity_prevalence_pct"
                ]
            ].rename(
                columns={
                    "barangay_name": "Barangay",
                    "population_density": "Density (per km²)",
                    "children_pct": "Children Share (%)",
                    "elderly_pct": "Older Persons Share (%)",
                    "facilities_per_10k": "Facilities per 10k Pop.",
                    "disability_prevalence_rate_pct": "Disability Prevalence (%)",
                    "cbms_food_insecurity_prevalence_pct": "Food Insecurity (%)"
                }
            )
            .sort_values("Total", ascending=False),
            width="stretch"
        )

    st.divider()

    # ==================================================
    # DOWNLOAD
    # ==================================================

    cluster_csv = (
        clustered.drop(columns="geometry", errors="ignore")
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "Download Barangay Cluster Table",
        cluster_csv,
        "barangay_clusters.csv",
        "text/csv"
    )

elif page == "Climate Layers":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Climate Layers
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        """
        Interactive climate and hazard map for Quezon City:
        barangay population shading, district and barangay
        boundaries, high-risk flood areas (more than 50cm of
        inundation in a 100-year rain event), and care facility
        locations. Use the Facilities filter below to change
        which facilities are shown (the Population group filter
        is inside the Flood Inundation tab).
        """
    )

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    CLIMATE_FACILITY_OPTIONS = {
        "Childcare": childcare_centers,
        "Schools": schools,
        "Health centers": health_centers,
        "Older persons care": older_person_care,
        "Long-term care & rehabilitation": long_term_care,
        "Action offices": action_offices,
        "Migration resource centers": migration_centers,
        "Bus stops": bus_stops
    }

    # Each value is (source, column): "demographics" columns are
    # looked up on the shared `demographics` table, "domestic_workers"
    # columns on the separate domestic_workers_barangay table (see
    # load_domestic_workers() in functions.py) — kept as a tuple so
    # the render code below can pull from whichever table each
    # option actually lives in.
    CLIMATE_POP_OPTIONS = {
        "Child population (ages 0-5)": ("demographics", "age_0_5"),
        "Child population (ages 6-17)": ("demographics", "age_6_17"),
        "Older persons (60+)": ("demographics", "age_60plus"),
        "Persons with disabilities (registered)": ("demographics", "pwd_registered"),
        "Total population": ("demographics", "pop_census"),
        "Domestic workers (registered)": ("domestic_workers", "domestic_workers_total")
    }

    # School type sub-filter, only shown when "Schools" is the
    # selected facility. "Primary" is a combined bucket (not a
    # value that exists in the source data) covering both
    # Preschool and Elementary school; every other option maps 1:1
    # to an existing Category value, derived from the data rather
    # than hardcoded so a new school Category shows up here
    # automatically next time the data is refreshed.
    SCHOOL_SUBCATEGORY_OPTIONS = {"All": None}

    if {"Preschool", "Elementary school"} <= set(schools["Category"].dropna().unique()):
        SCHOOL_SUBCATEGORY_OPTIONS["Primary (Preschool + Elementary)"] = ["Preschool", "Elementary school"]

    for cat in sorted(schools["Category"].dropna().unique()):
        SCHOOL_SUBCATEGORY_OPTIONS[cat] = [cat]

    selected_school_subcat = "All"

    # Population dropdown lives inside the Flood Inundation tab
    # below (not here) — flood exposure is the one raster layer
    # where "which population group is affected" is the natural
    # follow-up question, so its selector sits with that tab
    # rather than as a page-wide filter. The population
    # choropleth map itself still renders in its usual place
    # further down the page.
    fac_filter_col, fac_source_col = st.columns(2)

    with fac_filter_col:
        selected_fac_label = st.selectbox(
            "Facilities",
            list(CLIMATE_FACILITY_OPTIONS.keys()),
            index=0,
            key="climate_fac_filter"
        )

        if selected_fac_label == "Schools":
            selected_school_subcat = st.selectbox(
                "School Type",
                list(SCHOOL_SUBCATEGORY_OPTIONS.keys()),
                index=0,
                key="climate_school_subcat_filter"
            )

    with fac_source_col:
        # Derived from the data (union across every facility type
        # in CLIMATE_FACILITY_OPTIONS) rather than hardcoded — see
        # the Childcare Centers filter for why.
        _climate_fac_sources = sorted(
            pd.concat([
                df["data_source"] for df in CLIMATE_FACILITY_OPTIONS.values()
                if "data_source" in df.columns
            ]).dropna().unique()
        )

        selected_climate_fac_source = st.radio(
            "Data Source",
            ["All"] + _climate_fac_sources,
            index=0,
            key="climate_fac_source",
            horizontal=True
        )

    selected_fac_df = CLIMATE_FACILITY_OPTIONS[selected_fac_label]

    _school_cats = SCHOOL_SUBCATEGORY_OPTIONS[selected_school_subcat]

    if selected_fac_label == "Schools" and _school_cats is not None:
        selected_fac_df = selected_fac_df[
            selected_fac_df["Category"].isin(_school_cats)
        ]

    if selected_climate_fac_source != "All" and "data_source" in selected_fac_df.columns:
        selected_fac_df = selected_fac_df[
            selected_fac_df["data_source"] == selected_climate_fac_source
        ]

    # --------------------------------------------------
    # FACILITY POINTS (shared by every map on this page —
    # built once here, right after the filters, so both the
    # raster tabs below and the population map further down
    # can reuse the exact same layer/tooltip data instead of
    # drifting out of sync with each other).
    #
    # Name/Line1/Line2/Line3 is a small generic schema (rather
    # than separate Category/District/Address/... keys) so the
    # population map's combined tooltip (see FACILITY_TOOLTIP_HTML
    # below) can use the *same* template for both this point
    # layer and the barangay choropleth beneath it, which has a
    # completely different set of source columns. Populating
    # both datasets with these same four keys means whichever
    # one is actually hovered renders cleanly, with no
    # "undefined" placeholders for the fields that don't apply.
    # --------------------------------------------------

    _FAC_TOOLTIP_COLS = [
        "Name", "Category", "District", "Address",
        "open_hours", "close_hours", "data_source", "bus_route"
    ]

    facility_points = selected_fac_df[
        ["longitude", "latitude"]
        + [c for c in _FAC_TOOLTIP_COLS if c in selected_fac_df.columns]
    ].dropna(subset=["longitude", "latitude"]).copy()

    for col in _FAC_TOOLTIP_COLS:
        if col in facility_points.columns:
            # str(v).strip().lower() == "nan" catches columns that
            # were cast to string dtype upstream (see clean_dataframe
            # in functions.py), which turns a real NaN into the
            # literal text "nan" rather than leaving it as a value
            # pd.isna() would still catch here. Missing values map
            # to "" (not "Not available") so the Line1-4 assembly
            # below can drop a field's label entirely rather than
            # show e.g. "Open: " with nothing after it.
            facility_points[col] = facility_points[col].map(
                lambda v: (
                    ""
                    if pd.isna(v) or str(v).strip().lower() == "nan"
                    else str(v)
                )
            )
        else:
            facility_points[col] = ""

    # Bus stops have no Category value in the source data — the
    # bus route number/name is the closer equivalent, so it fills
    # in for Category on this one facility type.
    if "bus_route" in facility_points.columns:
        facility_points["Category"] = facility_points["Category"].where(
            facility_points["Category"] != "",
            "Bus Route " + facility_points["bus_route"]
        )

    def _join_nonempty(parts, sep=" · "):
        return sep.join(p for p in parts if p)

    facility_points["Line1"] = [
        _join_nonempty(
            [cat, f"District {d}" if d else ""]
        )
        for cat, d in zip(
            facility_points["Category"], facility_points["District"]
        )
    ]
    facility_points["Line2"] = facility_points["Address"].map(
        lambda a: f"Address: {a}" if a else ""
    )
    facility_points["Line3"] = [
        _join_nonempty(
            [f"Open {o}" if o else "", f"Close {c}" if c else ""],
            sep=" – "
        )
        for o, c in zip(
            facility_points["open_hours"], facility_points["close_hours"]
        )
    ]
    facility_points["Line4"] = facility_points["data_source"].map(
        lambda s: f"Source: {s}" if s else ""
    )

    # Light purple, the same "generic facility" color used for
    # markers elsewhere in the app (e.g. Migration Resource Centers,
    # Day Care Center, Milk Bank), so this page's dots read as part
    # of the same visual system rather than a one-off. A fixed dark
    # outline (same as every other facility layer in the app) is
    # what actually keeps a light fill color visible against a light
    # basemap — that's the fix, not the hue. The previous pale
    # yellow, and before that this same light purple without an
    # outline, both blended into the background for the same reason:
    # no outline contrast.
    facility_layer = pdk.Layer(
        "ScatterplotLayer",
        data=facility_points,
        get_position="[longitude, latitude]",
        get_fill_color=[196, 181, 253, 235],
        get_line_color=[40, 40, 40, 200],
        line_width_min_pixels=1.2,
        stroked=True,
        get_radius=50,
        radius_min_pixels=4,
        radius_max_pixels=10,
        pickable=True
    )

    FACILITY_TOOLTIP_HTML = """
    <b>{Name}</b><br/>
    {Line1}<br/>
    {Line2}<br/>
    {Line3}<br/>
    {Line4}
    """

    FACILITY_TOOLTIP_STYLE = {
        "backgroundColor": "white",
        "color": "black",
        "fontSize": "12px"
    }

    # --------------------------------------------------
    # RASTER LAYER CONFIGURATION
    # (land-surface temperature, vegetation, and flood
    # inundation — one tab each, every tab also shows the
    # same facility dots as the population map below)
    # --------------------------------------------------

    climate_layers = {
        "Flood Inundation (100-yr)": {
            "path": "processed/reference/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
            "colormap": "Blues",
            "binary": True,
            "unit": "flooded / not flooded",
            "legend_label": "Flood depth > 50cm (100-year rain event)",
            "description": (
                "Binary flood extent (~10m resolution) showing "
                "areas expected to see more than 50cm of inundation "
                "depth in a 100-year rainfall event. This is a mask, "
                "not a depth map."
            )
        },
        "Land-Surface Temperature": {
            "path": "processed/reference/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
            "colormap": "YlOrRd",
            "binary": False,
            "unit": "°C",
            "legend_label": "Land-Surface Temperature (°C)",
            "description": (
                "7-year summer average land-surface temperature, "
                "derived from Landsat thermal imagery (~50m "
                "resolution). Higher values indicate stronger "
                "urban heat, typically dense, paved, low-vegetation "
                "areas. Color scale is clipped to the 2nd-98th "
                "percentile to avoid a handful of extreme pixels "
                "flattening the rest of the map."
            )
        },
        "Vegetation (NDVI)": {
            "path": "processed/reference/climate/ndvi_mean_2025_EPSG3123.tif",
            "colormap": "Greens",
            "binary": False,
            "unit": "NDVI",
            "legend_label": "NDVI (vegetation index)",
            "description": (
                "2025 mean Normalized Difference Vegetation Index "
                "(~10m resolution). Values range roughly from -1 to "
                "1; higher (darker green) means denser, healthier "
                "vegetation, lower (pale) means bare soil, pavement, "
                "or built-up area. Useful as a rough inverse proxy "
                "for heat exposure and a direct proxy for green "
                "space access."
            )
        }
    }

    # --------------------------------------------------
    # RENDER ONE RASTER LAYER (shared by all three tabs).
    # min_zoom == the initial zoom, matching the same
    # zoom-lock pattern used on the Childcare Centers map,
    # so the view can't be zoomed out past the point where
    # the whole city is visible.
    # --------------------------------------------------

    def _render_climate_raster_tab(layer_config, container_key):

        st.caption(layer_config["description"])

        try:

            qc_boundary = load_qc_boundary()

            png_data_uri, bounds_corners, vmin, vmax = raster_to_bitmap_layer(
                layer_config["path"],
                colormap=layer_config["colormap"],
                binary=layer_config["binary"],
                _mask_geometry=qc_boundary
            )

            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=11,
                pitch=0,
                min_zoom=11,
                max_zoom=17,
            )

            boundary_layer = pdk.Layer(
                "GeoJsonLayer",
                data=geo,
                stroked=True,
                filled=False,
                get_line_color=[80, 80, 80, 180],
                line_width_min_pixels=0.6,
                pickable=False
            )

            # png_data_uri already comes back pre-quoted (a string
            # containing literal quote characters), and bounds_corners
            # is already the 4-corner format BitmapLayer expects,             # see raster_to_bitmap_layer's docstring in functions.py.
            bitmap_layer = pdk.Layer(
                "BitmapLayer",
                image=png_data_uri,
                bounds=bounds_corners,
                opacity=1.0
            )

            deck = pdk.Deck(
                layers=[
                    bitmap_layer,
                    boundary_layer,
                    facility_layer,
                    load_reservoir_layer()
                ],
                initial_view_state=view_state,
                tooltip={
                    "html": FACILITY_TOOLTIP_HTML,
                    "style": FACILITY_TOOLTIP_STYLE
                },
                map_style="light"
            )

            with st.container(border=True, key=container_key):
                st.markdown(
                    render_colormap_legend_html(
                        colormap=layer_config["colormap"],
                        vmin=vmin,
                        vmax=vmax,
                        unit=layer_config["unit"],
                        label=layer_config["legend_label"]
                    ),
                    unsafe_allow_html=True
                )
                st.pydeck_chart(
                    deck,
                    height=700
                )

            if layer_config["binary"]:

                st.caption(
                    f"Legend: {layer_config['legend_label']}, "
                    "shaded areas indicate flooding, unshaded areas "
                    "do not."
                )

            else:

                st.caption(
                    "Color scale is clipped to the 2nd-98th percentile "
                    "of this layer's data, to avoid a handful of "
                    "extreme pixels flattening the rest of the map."
                )

        except Exception as e:

            st.error(
                f"Could not render this layer: {e}. "
                "Check that rasterio and pyproj are installed, and "
                f"that the file exists at `{layer_config['path']}`."
            )

    flood_tab, lst_tab, veg_tab = st.tabs(list(climate_layers.keys()))

    with flood_tab:
        _pop_filter_col, _pop_metric_col = st.columns(2)

        with _pop_filter_col:
            selected_pop_label = st.selectbox(
                "Population Layer",
                list(CLIMATE_POP_OPTIONS.keys()),
                index=0,
                key="climate_pop_filter"
            )

        with _pop_metric_col:
            selected_pop_metric_label = st.radio(
                "Show as",
                ["Density (per km²)", "Raw Count"],
                index=0,
                key="climate_pop_metric",
                horizontal=True
            )

            selected_pop_metric = (
                "density"
                if selected_pop_metric_label == "Density (per km²)"
                else "count"
            )

        selected_pop_source, selected_pop_col = (
            CLIMATE_POP_OPTIONS[selected_pop_label]
        )

        # --------------------------------------------------
        # BARANGAY POPULATION DENSITY CHOROPLETH (light -> dark
        # green, same "Greens" ramp and per-km² framing as the
        # Population Density Layer on the Care Services Explorer
        # page, so the two read as one consistent system).
        # Shares this tab with the flood overlay below: a
        # semi-transparent blue BitmapLayer draws on top of this
        # choropleth, and green is adjacent to blue rather than
        # its complement (orange was used here previously for
        # exactly that reason), so at high density + high flood
        # opacity the two can blend toward a muddy blue-green.
        # Kept as requested since it matches Care Services
        # Explorer, but worth knowing if that blending turns out
        # to be a problem in practice.
        # --------------------------------------------------

        clim_barangay = gpd.read_file(
            "processed/reference/qc_barangays.geojson"
        )

        clim_barangay["barangay_name"] = (
            clim_barangay["barangay_name"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        _clim_pop_source_df = (
            demographics
            if selected_pop_source == "demographics"
            else domestic_workers_barangay
        )

        clim_demo = _clim_pop_source_df[
            ["barangay", "district", selected_pop_col]
        ].copy()

        clim_demo["barangay_key"] = (
            clim_demo["barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        clim_barangay = clim_barangay.merge(
            clim_demo,
            left_on="barangay_name",
            right_on="barangay_key",
            how="left"
        )

        if selected_pop_metric == "count":

            # Raw population count for the selected group, no
            # area division — Oranges ramp so it reads as visibly
            # distinct from the density view and from the flood
            # layer's blue (rather than competing with it, as an
            # orange-adjacent green would).
            clim_barangay["population_metric"] = clim_barangay[selected_pop_col]

            _pop_colormap = "Oranges"
            _pop_unit = ""

        else:

            # Same area/density calculation as the Care Services
            # Explorer's Population Density Layer (build_explorer_map
            # in app.py): reproject to EPSG:3123 for accurate area,
            # then count / area_km2.
            clim_barangay_proj = clim_barangay.to_crs("EPSG:3123")

            clim_barangay["area_km2"] = (
                clim_barangay_proj.geometry.area / 1_000_000
            )

            clim_barangay["population_metric"] = (
                clim_barangay[selected_pop_col]
                / clim_barangay["area_km2"]
            )

            _pop_colormap = "Greens"
            _pop_unit = "/km²"

        # CONTINUOUS scale (value_to_rgba + the Greens/Oranges
        # colormap from functions.py), not discrete quantile bins.
        # Density and count are both heavily right-skewed here,
        # same rationale as the other choropleths on this page, so
        # the color range is clipped to the 2nd-98th percentile
        # rather than the raw min/max, to keep a handful of extreme
        # barangays from flattening everyone else to the light end.
        pop_values = (
            clim_barangay["population_metric"]
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
        )

        pop_vmin, pop_vmax = pop_values.quantile([0.02, 0.98])

        def pop_color_for_value(value):

            if pd.isna(value):
                return [235, 235, 235, 90]

            return value_to_rgba(
                value,
                pop_vmin,
                pop_vmax,
                colormap=_pop_colormap,
                alpha=190
            )

        clim_barangay["fill_color"] = (
            clim_barangay["population_metric"].apply(pop_color_for_value)
        )

        # Pre-formatted tooltip value (raw column may be NaN for
        # unmatched polygons, which would render as a blank).
        clim_barangay["pop_display"] = (
            clim_barangay["population_metric"]
            .map(lambda v: f"{v:,.1f}{_pop_unit}" if pd.notna(v) else "No data")
        )

        clim_barangay["district_display"] = (
            clim_barangay["district"]
            .map(lambda v: f"{v:.0f}" if pd.notna(v) else "—")
        )

        # Same generic Name/Line1/Line2/Line3 keys as facility_points
        # (see FACILITY_TOOLTIP_HTML above) so one shared tooltip
        # template works for both layers in the deck built below.
        clim_barangay["Name"] = clim_barangay["barangay_name"]
        clim_barangay["Line1"] = "District " + clim_barangay["district_display"]
        _pop_line2_label = (
            "count" if selected_pop_metric == "count" else "density"
        )

        clim_barangay["Line2"] = (
            f"{selected_pop_label} {_pop_line2_label}: " + clim_barangay["pop_display"]
        )
        clim_barangay["Line3"] = ""
        clim_barangay["Line4"] = ""

        clim_geojson = json.loads(
            clim_barangay.to_json()
        )

        # --------------------------------------------------
        # FLOOD OVERLAY (>50cm, 100-year rain event)
        # --------------------------------------------------

        flood_error = None

        try:
            qc_boundary = load_qc_boundary()

            flood_png, flood_bounds, _, _ = raster_to_bitmap_layer(
                "processed/reference/climate/flood_inundation_binary_gt50cm_EPSG3123.tif",
                colormap="Blues",
                binary=True,
                _mask_geometry=qc_boundary
            )
        except Exception as e:
            flood_png, flood_bounds = None, None
            flood_error = str(e)

        # --------------------------------------------------
        # LAYERS
        # --------------------------------------------------

        choropleth_layer = pdk.Layer(
            "GeoJsonLayer",
            data=clim_geojson,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[255, 255, 255, 160],
            line_width_min_pixels=0.5,
            pickable=True,
            auto_highlight=True
        )

        district_boundary_layer = pdk.Layer(
            "GeoJsonLayer",
            data=json.loads(district_map.to_json()),
            stroked=True,
            filled=False,
            get_line_color=[20, 20, 20, 220],
            line_width_min_pixels=2.5,
            pickable=False
        )

        map_layers = [choropleth_layer]

        if flood_png is not None:
            map_layers.append(
                pdk.Layer(
                    "BitmapLayer",
                    image=flood_png,
                    bounds=flood_bounds,
                    opacity=0.5
                )
            )

        map_layers.append(district_boundary_layer)
        map_layers.append(facility_layer)
        map_layers.append(load_reservoir_layer())

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            min_zoom=11,
            max_zoom=17,
        )

        tooltip = {
            "html": FACILITY_TOOLTIP_HTML,
            "style": FACILITY_TOOLTIP_STYLE
        }

        deck = pdk.Deck(
            layers=map_layers,
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        # --------------------------------------------------
        # LEGEND (discrete, mirrors the static reference map)
        # --------------------------------------------------

        # Every icon sits in an identical 18x18px centering box
        # regardless of its own shape (a 0-height line, a 14px
        # square, an 11px circle) so all four items line up on the
        # same vertical center instead of drifting per-icon. The
        # outer div is itself a flex row (not just each item
        # individually) — without that, sibling inline-flex spans
        # are positioned against each other by CSS's default
        # text-baseline rule, which shifts depending on each item's
        # own content height and was the actual source of the
        # misalignment, not the icon boxes themselves.
        def _legend_item(icon_html, label_text):
            return (
                '<span style="display:flex;align-items:center;margin-right:24px;">'
                '<span style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:18px;height:18px;margin-right:6px;flex-shrink:0;">{icon_html}</span>'
                f'<span style="font-size:16px;color:#1a1a1a;">{label_text}</span>'
                '</span>'
            )

        legend_html = (
            '<div style="display:flex;flex-wrap:wrap;align-items:center;row-gap:8px;">'
            + _legend_item(
                '<span style="display:inline-block;width:20px;height:0;border-top:3px solid #141414;"></span>',
                "District boundary"
            )
            + _legend_item(
                '<span style="display:inline-block;width:20px;height:0;border-top:1px solid #aaa;"></span>',
                "Barangay boundary"
            )
            + _legend_item(
                '<span style="display:inline-block;width:14px;height:14px;background:rgba(8,48,107,0.5);border:1px solid #999;"></span>',
                "High-risk flood areas (&gt;50cm, 100-yr event)"
            )
            + _legend_item(
                '<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:rgb(196,181,253);border:1px solid #282828;"></span>',
                f"{selected_fac_label} facilities"
            )
            + '</div>'
        )

        with st.container(border=True, key="qcd-climate-layers-map"):
            st.markdown(legend_html, unsafe_allow_html=True)
            st.markdown(
                render_colormap_legend_html(
                    colormap=_pop_colormap,
                    vmin=pop_vmin,
                    vmax=pop_vmax,
                    unit=_pop_unit,
                    label=(
                        f"{selected_pop_label} Density"
                        if selected_pop_metric == "density"
                        else f"{selected_pop_label} (Count)"
                    )
                ),
                unsafe_allow_html=True
            )
            st.pydeck_chart(
                deck,
                height=700
            )

        if flood_error is not None:
            st.warning(
                "Flood overlay could not be rendered: "
                f"{flood_error}. The population and facility layers "
                "are still shown."
            )

        with st.expander("Recommended Policy Actions: Facility-Level Flood Risk Mitigation", expanded=False):

            st.markdown("""
            **Protect Facilities & Ensure Continuity of Care During Flooding:**
            1. **Audit Facility Flood Risk** → On the map above, look for facilities that fall inside the
               blue high-risk flood areas (>50cm in a 100-year rain event). These are your at-risk assets.
               Use the Facilities filter to check each service type, and prioritize those serving vulnerable
               populations (childcare, older persons care, health centers).

            2. **Tiered Mitigation Strategy** →
               - **Tier 1 (Immediate):** Facilities in the flood zone → Elevate critical equipment, install
                 backflow preventers, pre-position emergency supplies.
               - **Tier 2 (Near-term):** Study relocation vs. hardening. Some facilities (e.g.,
                 open-air supervised playgrounds) may not be worth hardening; others (clinics, nurseries) are
                 critical and should be elevated or moved.
               - **Tier 3 (Long-term):** Model alternative facility locations using Barangay Clusters. Find
                 nearby clusters with low flood risk but similar care needs.

            3. **Backup Facility Network** → For flood-prone areas, coordinate with schools and community centers
               to serve as emergency care sites during flooding. Pre-position supplies and train staff.

            4. **Integrate with Accessibility Planning** → Don't just move flood-risk facilities randomly.
               Use the Care Planning page to model how relocation impacts accessibility ratios. Move them to
               locations that also improve accessibility for underserved barangays.
            """)

    with lst_tab:
        _render_climate_raster_tab(
            climate_layers["Land-Surface Temperature"],
            "qcd-chart-87-lst"
        )

    with veg_tab:
        _render_climate_raster_tab(
            climate_layers["Vegetation (NDVI)"],
            "qcd-chart-87-veg"
        )

elif page == "Zoning Map":


    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Zoning Map
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Land-use zone polygons for all Quezon City barangays, "
        "sourced from the QC Zoning Administration Unit public "
        "viewer (zaulb.quezoncity.gov.ph). Visualization only, "
        "private/restricted zone records are excluded by the source."
    )

    #  Load shared data for all tabs 
    # (loaded once here so all tabs can use it without
    # re-reading from disk on every tab switch)
    @st.cache_data(show_spinner=False)
    def _load_zoning_merged():
        _zs = pd.read_csv("processed/reference/zoning/qc_zoning_summary.csv")
        # load_demographics() rather than a direct read — this tab's
        # Facility-Zone Gap Analysis below reads ratio_childcare/
        # ratio_school_6_17/ratio_pop_health/ratio_old_60/ratio_old_80,
        # which are computed live (see compute_facility_ratios) and
        # no longer exist in the raw CSV.
        _dm = load_demographics()
        _nlu = {"ROAD", "WATER", "X"}
        _zcols = [
            c for c in _zs.columns
            if c not in ("barangay_id", "barangay", "total_polygons")
            and c not in _nlu
        ]
        def _dom(row):
            vals = {c: row[c] for c in _zcols
                    if c in row and pd.notna(row[c]) and row[c] > 0}
            return max(vals, key=vals.get) if vals else "Unknown"
        _zs["Dominant Zone"] = _zs.apply(_dom, axis=1)
        _merged = _dm.merge(
            _zs[["barangay", "Dominant Zone"]],
            left_on=_dm["barangay"].str.strip().str.title(),
            right_on=_zs["barangay"].str.strip().str.title(),
            how="left",
            suffixes=("", "_z")
        ).drop(columns=["key_0"], errors="ignore")
        if "barangay_z" in _merged.columns:
            _merged = _merged.drop(columns=["barangay_z"])
        _merged["Dominant Zone"] = _merged["Dominant Zone"].fillna("Unknown")
        return _zs, _dm, _merged

    _zoning_summary, _demographics, _zoning_merged = _load_zoning_merged()

    #  City-wide KPI summary stats
    # "QMC" (Quezon Memorial Circle) is a landmark polygon in the
    # zoning source data, not a barangay — excluded here so any
    # barangay count/list built from _zoning_summary stays at 142,
    # even though its zone polygons still render on the map.
    _nlu_kpi = {"ROAD", "WATER", "X", "Unknown"}
    _total_brgy = len(_zoning_summary[
        (~_zoning_summary["Dominant Zone"].isin(_nlu_kpi))
        & (_zoning_summary["barangay"] != "QMC")
    ])

    _zone_groups = {
        "Residential": [
            "R-3 HIGH DENSITY RESIDENTIAL ZONE",
            "R-2 MEDIUM DENSITY RESIDENTIAL ZONE",
            "R-2-A MEDIUM DENSITY RESIDENTIAL SUB-ZONE",
            "R-1 LOW DENSITY RESIDENTIAL ZONE",
            "R-1-A LOW DENSITY RESIDENTIAL SUB-ZONE",
            "SOCIALIZED HOUSING",
            "SPECIAL URBAN DEVELOPMENT ZONE",
        ],
        "Commercial": [
            "C-1 MINOR COMMERCIAL ZONE",
            "C-2 MAJOR COMMERCIAL ZONE",
            "C-3 METROPOLITAN COMMERCIAL ZONE",
        ],
        "Industrial": [
            "I-1 LIGHT INTENSITY INDUSTRIAL ZONE",
            "I-2 MEDIUM INTENSITY INDUSTRIAL ZONE",
        ],
        "Institutional / Other": [
            "INSTITUTIONAL", "CEMETERY", "UTILITY",
            "PARKS AND OPEN SPACE",
        ],
    }

    _dom_counts = _zoning_summary["Dominant Zone"].value_counts()

    def _group_count(zones):
        return sum(_dom_counts.get(z, 0) for z in zones)

    _res_n   = _group_count(_zone_groups["Residential"])
    _com_n   = _group_count(_zone_groups["Commercial"])
    _ind_n   = _group_count(_zone_groups["Industrial"])
    _oth_n   = _group_count(_zone_groups["Institutional / Other"])

    st.markdown("#### Citywide Land-Use Overview")
    st.caption(
        "Based on the dominant zone type per barangay "
        "(excluding road, water, and unclassified zones)."
    )

    _k1, _k2, _k3, _k4 = st.columns(4)
    with _k1:
        with st.container(border=True):
            st.metric(
                "Residential barangays",
                _res_n,
                help="R-1 through R-3, Socialized Housing, Special Urban Development"
            )
    with _k2:
        with st.container(border=True):
            st.metric(
                "Commercial barangays",
                _com_n,
                help="C-1, C-2, C-3 commercial zones"
            )
    with _k3:
        with st.container(border=True):
            st.metric(
                "Industrial barangays",
                _ind_n,
                help="I-1 light and I-2 medium intensity industrial zones"
            )
    with _k4:
        with st.container(border=True):
            st.metric(
                "Institutional / Other",
                _oth_n,
                help="Institutional, Cemetery, Utility, Parks"
            )

    st.divider()

    ztab1, ztab2, ztab3, ztab4 = st.tabs([
        "Zone Polygon Viewer",
        "Dominant Zone by Barangay",
        "Facility–Zone Gap Analysis",
        "Zone × Facility Cross-Table",
    ])

    with ztab1:

        #  Zone type colour palette (matches QC viewer legend) 
        ZONE_COLORS = {
            "R-3 HIGH DENSITY RESIDENTIAL ZONE":         [180, 90,  40,  180],
            "R-2-A MEDIUM DENSITY RESIDENTIAL SUB-ZONE": [220, 140, 80,  180],
            "R-1 LOW DENSITY RESIDENTIAL ZONE":          [240, 190, 130, 180],
            "C-1 MINOR COMMERCIAL ZONE":                 [220, 80,  80,  180],
            "C-2 MAJOR COMMERCIAL ZONE":                 [180, 30,  30,  180],
            "I-2 MEDIUM INTENSITY INDUSTRIAL ZONE":      [160, 80,  200, 180],
            "I-1 LIGHT INTENSITY INDUSTRIAL ZONE":       [200, 140, 230, 180],
            "INSTITUTIONAL":                             [80,  120, 200, 180],
            "CEMETERY":                                  [80,  160, 80,  180],
            "UTILITY":                                   [100, 100, 100, 180],
            "ROAD":                                      [200, 200, 200, 120],
            "WATER":                                     [80,  160, 220, 180],
            "X":                                         [180, 180, 180, 60],
        }
        DEFAULT_COLOR = [160, 160, 160, 120]

        #  Cached data loader 
        # (runs once on first load, then stays in memory across all
        # interactions, the main source of slowness was re-running
        # gpd.read_file on every selectbox change. Simplification
        # tolerance of 0.00005 degrees (~5m) is invisible at city
        # zoom levels but cuts vertex count significantly, speeding
        # up both serialisation and browser rendering.)
        @st.cache_data(show_spinner="Loading zoning data...")
        def load_zoning_data():
            zoning = gpd.read_file("processed/reference/zoning/qc_zoning.geojson")
            borders = gpd.read_file("processed/reference/qc_barangays.geojson")
            zoning["geometry"] = zoning["geometry"].simplify(
                0.00005, preserve_topology=True
            )
            borders["geometry"] = borders["geometry"].simplify(
                0.00005, preserve_topology=True
            )
            summary = pd.read_csv("processed/reference/zoning/qc_zoning_summary.csv")
            return zoning, borders, summary

        try:
            zoning_gdf, barangay_borders, summary_df = load_zoning_data()
        except Exception as e:
            st.error(
                f"Could not load zoning data: {e}\n\n"
                "Make sure the files are at:\n"
                "- `processed/reference/zoning/qc_zoning.geojson`\n"
                "- `processed/reference/zoning/qc_zoning_summary.csv`"
            )
            st.stop()

        all_zone_types = sorted(
            zoning_gdf["zone_type"].dropna().unique().tolist()
        )
        # "QMC" (Quezon Memorial Circle) is a landmark polygon in
        # the zoning source data, not a barangay — excluded from
        # the barangay picker (but its zone polygons still render
        # on the map in the "All" view; it's just not selectable
        # or counted as one of the 142 barangays).
        all_barangays = sorted(
            b for b in zoning_gdf["barangay"].dropna().unique().tolist()
            if b != "QMC"
        )

        #  Sidebar: colour legend 
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Zone Types")
        for zone in all_zone_types:
            color = ZONE_COLORS.get(zone, DEFAULT_COLOR)
            r, g, b = color[0], color[1], color[2]
            st.sidebar.markdown(
                f'<span style="color:rgba({r},{g},{b},1);font-size:22px;">■</span> '
                f'<b>{zone}</b>',
                unsafe_allow_html=True
            )

        #  Main-area: barangay filter only 
        selected_barangay = st.selectbox(
            "Select barangay",
            ["All"] + all_barangays,
            key="zoning_brgy_filter"
        )

        st.info("Hover over a zone polygon to view barangay and zone type.")

        #  Filter 
        gdf_filtered = zoning_gdf.copy()

        if selected_barangay != "All":
            gdf_filtered = gdf_filtered[
                gdf_filtered["barangay"] == selected_barangay
            ]

        if gdf_filtered.empty:
            st.warning("No zones match the current filters.")
            st.stop()

        #  Filter barangay borders 
        if selected_barangay != "All":
            name_col = next(
                (c for c in barangay_borders.columns
                 if c.lower() in (
                     "barangay_name", "barangay", "name",
                     "brgy_name", "brgy"
                 )),
                None
            )
            borders_filtered = (
                barangay_borders[
                    barangay_borders[name_col].str.strip().str.title()
                    == selected_barangay.strip().title()
                ]
                if name_col else barangay_borders
            )
        else:
            borders_filtered = barangay_borders

        #  Add fill color 
        gdf_filtered["fill_color"] = gdf_filtered["zone_type"].apply(
            lambda z: ZONE_COLORS.get(z, DEFAULT_COLOR)
        )

        #  KPI row 
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            with st.container(border=True):
                st.metric(
                    "Barangays",
                    gdf_filtered[
                        gdf_filtered["barangay"] != "QMC"
                    ]["barangay"].nunique()
                )
        with col_k2:
            with st.container(border=True):
                st.metric("Zone polygons", f"{len(gdf_filtered):,}")
        with col_k3:
            with st.container(border=True):
                st.metric("Zone types", gdf_filtered["zone_type"].nunique())

        #  Legend above map, explicit dark text for dark-mode readability 
        legend_items = "".join([
            f'<div style="display:flex;align-items:center;gap:6px;">'
            f'<span style="display:inline-block;width:14px;height:14px;'
            f'background:rgba({ZONE_COLORS.get(z, DEFAULT_COLOR)[0]},'
            f'{ZONE_COLORS.get(z, DEFAULT_COLOR)[1]},'
            f'{ZONE_COLORS.get(z, DEFAULT_COLOR)[2]},0.85);'
            f'border-radius:2px;flex-shrink:0;"></span>'
            f'<span style="font-size:12px;color:#1a1a1a;">{z}</span></div>'
            for z in all_zone_types
            if z in gdf_filtered["zone_type"].unique()
        ])

        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:10px 20px;'
            f'padding:10px 14px;background:#ffffff;border:1px solid #e0e0e0;'
            f'border-radius:6px;margin-bottom:8px;">{legend_items}</div>',
            unsafe_allow_html=True
        )

        #  Map 
        _centroids = (
            gdf_filtered.geometry
            .to_crs("EPSG:3123")
            .centroid
            .to_crs("EPSG:4326")
        )
        center_lat = float(_centroids.y.mean())
        center_lon = float(_centroids.x.mean())

        zoom = 11 if selected_barangay == "All" else 14

        zoning_layer = pdk.Layer(
            "GeoJsonLayer",
            data=json.loads(gdf_filtered.to_json()),
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[80, 80, 80, 60],
            line_width_min_pixels=0.4,
            pickable=True,
            auto_highlight=True,
        )

        border_layer = pdk.Layer(
            "GeoJsonLayer",
            data=json.loads(borders_filtered.to_json()),
            stroked=True,
            filled=False,
            get_line_color=[80, 80, 80, 120],
            line_width_min_pixels=1.0,
            pickable=False,
        )

        # Reservoir isn't one of the 142 barangays and carries no
        # zone/demographic data — shown here purely as a geographic
        # landmark (same treatment as QMC above: visible, but never
        # part of any barangay count or list). "zone_type" is set to
        # a plain description rather than left blank so the shared
        # tooltip template below doesn't show an empty "Zone: " line.
        _reservoir_gdf = gpd.read_file(
            "processed/reference/qc_reservoir.geojson",
            engine="pyogrio"
        )
        _reservoir_gdf["barangay"] = _reservoir_gdf["barangay_name"]
        _reservoir_gdf["zone_type"] = "Water body"

        reservoir_layer = pdk.Layer(
            "GeoJsonLayer",
            data=json.loads(_reservoir_gdf.to_json()),
            stroked=True,
            filled=False,
            get_line_color=[80, 80, 80, 200],
            line_width_min_pixels=1.2,
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=0,
            min_zoom=11,
            max_zoom=18,
        )

        deck = pdk.Deck(
            layers=[zoning_layer, border_layer, reservoir_layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{barangay}</b><br/>Zone: {zone_type}",
                "style": {
                    "backgroundColor": "white",
                    "color": "black",
                    "fontSize": "12px"
                }
            },
            map_style="light"
        )

        with st.container(border=True):
            st.pydeck_chart(deck, height=620)

        #  Summary table 
        st.subheader("Zone Type Breakdown by Barangay")
        st.caption(
            "Number of zone polygons per zone type per barangay "
            "(polygon count, not area). Private/restricted zone "
            "records are excluded at source."
        )

        summary_show = (
            summary_df[summary_df["barangay"] == selected_barangay]
            if selected_barangay != "All"
            else summary_df.copy()
        )

        zone_cols = [
            c for c in summary_show.columns
            if c not in ("barangay_id", "barangay", "total_polygons")
        ]

        # Reservoir is a landmark polygon with no zone data at all
        # (unlike QMC, which has real zone polygons) — leave every
        # column but the name blank rather than showing a row of
        # zeros/NaN across every zone type.
        summary_show.loc[
            summary_show["barangay"] == "Reservoir",
            ["total_polygons"] + zone_cols
        ] = np.nan

        display_cols = ["barangay", "total_polygons"] + zone_cols

        with st.container(border=True):
            st.dataframe(
                summary_show[
                    [c for c in display_cols if c in summary_show.columns]
                ].sort_values("total_polygons", ascending=False),
                width="stretch"
            )


    with ztab2:

        st.markdown("### Dominant Zone Type by Barangay")

        st.caption(
            "Each barangay is coloured by its most common "
            "land-use zone type (by polygon count, excluding "
            "ROAD, WATER, and unclassified zones). Useful for "
            "interpreting accessibility gaps, barangays with "
            "few care facilities in R-3/R-2-A residential zones "
            "represent genuine unmet demand, while gaps in "
            "industrial or utility zones may reflect land-use "
            "constraints rather than policy failures."
        )

        try:
            _zs2 = pd.read_csv(
                "processed/reference/zoning/qc_zoning_summary.csv"
            )
            _nlu2 = {"ROAD", "WATER", "X"}
            _zcols2 = [
                c for c in _zs2.columns
                if c not in (
                    "barangay_id", "barangay", "total_polygons"
                ) and c not in _nlu2
            ]

            def _dom2(row):
                vals = {
                    c: row[c] for c in _zcols2
                    if c in row and pd.notna(row[c]) and row[c] > 0
                }
                return max(vals, key=vals.get) if vals else "Unknown"

            _zs2["Dominant Zone"] = _zs2.apply(_dom2, axis=1)

            _brgy_gdf2 = barangay_borders.copy()
            # qc_barangays.geojson uses "barangay_name" column
            _name_col2 = next(
                (c for c in _brgy_gdf2.columns
                 if c.lower() in (
                     "barangay_name", "barangay", "name",
                     "brgy_name", "brgy"
                 )), None
            )

            if _name_col2:
                _brgy_gdf2["_join_key"] = (
                    _brgy_gdf2[_name_col2].astype(str).str.strip().str.title()
                )
                _zs2["_join_key"] = (
                    _zs2["barangay"].astype(str).str.strip().str.title()
                )
                _brgy_gdf2 = _brgy_gdf2.merge(
                    _zs2[["_join_key", "Dominant Zone"]],
                    on="_join_key",
                    how="left"
                ).drop(columns=["_join_key"])
                _zs2 = _zs2.drop(columns=["_join_key"])
                # expose as "barangay" so pydeck {barangay} resolves
                _brgy_gdf2["barangay"] = (
                    _brgy_gdf2[_name_col2].astype(str)
                )
            else:
                _brgy_gdf2["Dominant Zone"] = "Unknown"
                _brgy_gdf2["barangay"] = ""

            # Build colour palette from ZONE_COLORS (already defined
            # above for the polygon viewer), falling back to grey for
            # any zone name in the data not in the palette, handles
            # minor naming differences between the scraper output and
            # the hardcoded legend keys.
            _CHORO_COLORS = {
                k: [v[0], v[1], v[2], 200]
                for k, v in ZONE_COLORS.items()
            }
            _CHORO_COLORS["Unknown"] = [200, 200, 200, 120]

            _brgy_gdf2["fill_color"] = _brgy_gdf2["Dominant Zone"].apply(
                lambda z: _CHORO_COLORS.get(
                    str(z) if z else "Unknown",
                    [200, 200, 200, 120]
                )
            )

            _present = sorted(
                _brgy_gdf2["Dominant Zone"].dropna().unique()
            )
            _leg2 = "".join([
                f'<div style="display:flex;align-items:center;gap:6px;">'                f'<span style="display:inline-block;width:14px;height:14px;'                f'background:rgba({_CHORO_COLORS.get(z,[200,200,200,120])[0]},'                f'{_CHORO_COLORS.get(z,[200,200,200,120])[1]},'                f'{_CHORO_COLORS.get(z,[200,200,200,120])[2]},0.85);'                f'border-radius:2px;flex-shrink:0;"></span>'                f'<span style="font-size:12px;color:#1a1a1a;">{z}</span></div>'
                for z in _present
            ])
            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;gap:10px 20px;'                f'padding:10px 14px;background:#ffffff;'                f'border:1px solid #e0e0e0;border-radius:6px;'                f'margin-bottom:8px;">{_leg2}</div>',
                unsafe_allow_html=True
            )

            _choro_layer = pdk.Layer(
                "GeoJsonLayer",
                data=json.loads(_brgy_gdf2.to_json()),
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color=[80, 80, 80, 80],
                line_width_min_pixels=0.8,
                pickable=True,
                auto_highlight=True,
            )

            with st.container(border=True):
                st.pydeck_chart(
                    pdk.Deck(
                        layers=[_choro_layer, load_reservoir_layer()],
                        initial_view_state=pdk.ViewState(
                            latitude=14.676, longitude=121.043,
                            zoom=11, pitch=0, min_zoom=11, max_zoom=17,
                        ),
                        tooltip={
                            "html": "<b>{barangay}</b><br/>Dominant Zone: {Dominant Zone}",
                            "style": {"backgroundColor": "white",
                                      "color": "black", "fontSize": "12px"}
                        },
                        map_style="light"
                    ),
                    height=600
                )

            st.subheader("Dominant Zone per Barangay")
            st.caption(
                "Full list sorted alphabetically. Use alongside "
                "the Accessibility Analysis to interpret whether "
                "gaps reflect genuine care deficits or land-use "
                "constraints. Where two zone types tie on "
                "polygon count, the first alphabetically is used "
                ",  only Mangga and West Kamias are affected."
            )
            _dom_per_brgy = (
                _zs2[["barangay", "Dominant Zone", "total_polygons"]]
                .rename(columns={
                    "barangay": "Barangay",
                    "total_polygons": "Total Polygons"
                })
            )
            # Reservoir is a landmark, not a barangay, and has no
            # zone data at all — show its name only.
            _dom_per_brgy.loc[
                _dom_per_brgy["Barangay"] == "Reservoir",
                ["Dominant Zone", "Total Polygons"]
            ] = np.nan
            with st.container(border=True):
                st.dataframe(
                    _dom_per_brgy.sort_values("Barangay"),
                    width="stretch"
                )

        except Exception as _e2:
            st.warning(f"Could not load dominant zone data: {_e2}")

    with ztab3:

        st.markdown("### Facility–Zone Gap Analysis")

        st.caption(
            "Barangays where land use indicates genuine care demand "
            "(residential zones) but facility coverage is low. "
            "These are the most actionable locations for new facility "
            "siting, residential zoning means both that residents "
            "need services and that planning permission is likely "
            "obtainable. Sort by any column to prioritise by "
            "population size, facility type, or accessibility ratio."
        )

        _RESIDENTIAL_ZONES = [
            "R-3 HIGH DENSITY RESIDENTIAL ZONE",
            "R-2 MEDIUM DENSITY RESIDENTIAL ZONE",
            "R-2-A MEDIUM DENSITY RESIDENTIAL SUB-ZONE",
            "R-1 LOW DENSITY RESIDENTIAL ZONE",
            "R-1-A LOW DENSITY RESIDENTIAL SUB-ZONE",
            "SOCIALIZED HOUSING",
            "SPECIAL URBAN DEVELOPMENT ZONE",
        ]

        _FAC_COLS = {
            "Childcare": "ratio_childcare",
            "Schools": "ratio_school_6_17",
            "Health Centers": "ratio_pop_health",
            "Older Persons Care": "ratio_old_60",
            "Long-Term Care": "ratio_old_80",
        }

        _gap_facility = st.selectbox(
            "Facility type to analyse",
            list(_FAC_COLS.keys()),
            key="gap_facility_select"
        )

        _gap_ratio_col = _FAC_COLS[_gap_facility]

        _gap_df = _zoning_merged[
            _zoning_merged["Dominant Zone"].isin(_RESIDENTIAL_ZONES)
        ].copy()

        _gap_df = _gap_df[[
            "barangay", "district", "pop_census",
            _gap_ratio_col, "Dominant Zone"
        ]].dropna(subset=[_gap_ratio_col]).rename(columns={
            "barangay": "Barangay",
            "district": "District",
            "pop_census": "Population",
            _gap_ratio_col: f"{_gap_facility} per 1,000",
            "Dominant Zone": "Zone",
        })

        _gap_df[f"{_gap_facility} per 1,000"] = (
            _gap_df[f"{_gap_facility} per 1,000"]
        ).round(2)

        _gap_max_val = float(
            _gap_df[f"{_gap_facility} per 1,000"].quantile(0.75)
        )
        _gap_med_val = float(
            _gap_df[f"{_gap_facility} per 1,000"].median()
        )

        # If all values are 0 (e.g. no Older Persons Care
        # facilities in any residential barangay), the slider
        # min==max==0 which crashes Streamlit. Show a plain
        # number_input fallback instead, also more useful since
        # a slider with range 0–0 conveys nothing.
        if _gap_max_val <= 0:
            st.info(
                f"All residential barangays have zero "
                f"{_gap_facility} facilities, no ratio range "
                "to filter. All barangays are shown below."
            )
            _gap_threshold = 0.0
        else:
            _gap_threshold = st.slider(
                f"Show barangays below this {_gap_facility} ratio",
                min_value=0.0,
                max_value=_gap_max_val,
                value=min(_gap_med_val, _gap_max_val),
                step=round(_gap_max_val / 100, 4) or 0.01,
                key="gap_threshold_slider",
                help=(
                    "Barangays with a ratio below this value are "
                    "shown, lower = more underserved relative to "
                    "their residential zone population."
                )
            )

        _gap_filtered = (
            _gap_df[
                _gap_df[f"{_gap_facility} per 1,000"]
                <= _gap_threshold
            ]
            .sort_values(
                [f"{_gap_facility} per 1,000", "Population"],
                ascending=[True, False]
            )
        )

        _g1, _g2, _g3 = st.columns(3)
        with _g1:
            with st.container(border=True):
                st.metric(
                    "Residential barangays below threshold",
                    len(_gap_filtered)
                )
        with _g2:
            with st.container(border=True):
                st.metric(
                    "Total population in gap barangays",
                    f"{int(math.ceil(_gap_filtered['Population'].sum())):,}"
                )
        with _g3:
            with st.container(border=True):
                st.metric(
                    "Zero-facility barangays",
                    int(math.ceil((_gap_filtered[f"{_gap_facility} per 1,000"] == 0).sum()))
                )

        if _gap_filtered.empty:
            st.info(
                "No residential barangays below this threshold. "
                "Try raising the slider."
            )
        else:
            _ratio_col = f"{_gap_facility} per 1,000"
            _zero_gap  = _gap_filtered[_gap_filtered[_ratio_col] == 0]
            _nz_gap    = _gap_filtered[_gap_filtered[_ratio_col] >  0]

            if _nz_gap.empty:
                st.info(
                    "All residential barangays below the threshold "
                    "have zero facilities, see the table below."
                )
            else:
                _fig_gap = _px4.bar(
                    _nz_gap.sort_values(_ratio_col, ascending=True).head(20),
                    x=_ratio_col,
                    y="Barangay",
                    orientation="h",
                    color=_ratio_col,
                    color_continuous_scale="Reds_r",
                    title=(
                        f"Top 20 Residential Barangays with Lowest "
                        f"{_gap_facility} Coverage (excl. zero-facility)"
                    ),
                    text=_ratio_col,
                    hover_data=["District", "Zone", "Population"],
                )
                _fig_gap.update_traces(
                    texttemplate="%{text:.2f}",
                    textposition="outside"
                )
                _fig_gap.update_layout(
                    xaxis=dict(
                        range=[0, _nz_gap[_ratio_col].max() * 1.3],
                        title=f"{_gap_facility} per 1,000 population"
                    ),
                    coloraxis_showscale=False,
                    height=max(380, min(len(_nz_gap), 20) * 22 + 80),
                    margin=dict(l=160, r=80, t=60, b=40),
                )
                with st.container(border=True):
                    st.plotly_chart(_fig_gap)

        st.subheader("Full Gap Table")
        st.caption(
            "Residential barangays below the selected threshold "
            "with at least one facility, sorted by lowest ratio "
            "then highest population. Zero-facility barangays are "
            "shown separately below."
        )

        _ratio_col = f"{_gap_facility} per 1,000"
        _table_nz = _gap_filtered[
            _gap_filtered[_ratio_col] > 0
        ].reset_index(drop=True)

        with st.container(border=True):
            st.dataframe(_table_nz, width="stretch")

        st.download_button(
            label="Download gap table as CSV",
            data=_table_nz.to_csv(index=False).encode("utf-8"),
            file_name=f"qc_facility_zone_gap_{_gap_facility.lower().replace(' ','_')}.csv",
            mime="text/csv",
        )

        # # Zero-facility barangays shown separately below the table
        # _zero_table = _gap_filtered[
        #     _gap_filtered[_ratio_col] == 0
        # ].reset_index(drop=True)

        # if len(_zero_table) > 0:
        #     st.subheader("Barangays with Zero Facilities")
        #     st.caption(
        #         f"{len(_zero_table)} residential barangays have no "
        #         f"{_gap_facility} facilities at all, these represent "
        #         "the most critical gaps and should be prioritised "
        #         "for new facility siting. Sorted by population "
        #         "to surface highest-impact locations first."
        #     )
        #     with st.container(border=True):
        #         st.dataframe(
        #             _zero_table[
        #                 ["Barangay", "District", "Population", "Zone"]
        #             ].sort_values("Population", ascending=False)
        #             .reset_index(drop=True),
        #             width="stretch"
        #         )
        #     st.download_button(
        #         label="Download zero-facility barangays as CSV",
        #         data=_zero_table.to_csv(index=False).encode("utf-8"),
        #         file_name=f"qc_zero_facility_{_gap_facility.lower().replace(' ','_')}.csv",
        #         mime="text/csv",
        #     )

    with ztab4:

        st.markdown("### Zone × Facility Type Cross-Table")

        st.caption(
            "For each dominant zone type, how many facilities of "
            "each type exist across all barangays with that zone. "
            "Answers: are we placing facilities in the right zones? "
            "Residential zones should have the most childcare, "
            "schools, and health centers; institutional zones should "
            "anchor older persons care and long-term care. "
            "Gaps (0s) in residential rows for care facility types "
            "indicate potential siting opportunities."
        )

        _FAC_COLS_ALL = [
            "Childcare",
            "Schools",
            "Health centers",
            "Older persons care",
            "Long-term care and rehabilitation services",
            "Quezon City satellite offices for services",
        ]

        _cross = (
            _zoning_merged
            .groupby("Dominant Zone")[
                [c for c in _FAC_COLS_ALL
                 if c in _zoning_merged.columns]
            ]
            .sum()
            .astype(int)
            .reset_index()
        )

        # Sort by total facilities descending
        _cross["Total"] = _cross[
            [c for c in _FAC_COLS_ALL if c in _cross.columns]
        ].sum(axis=1)
        _cross = _cross.sort_values("Total", ascending=False)

        # Rename for display
        _cross = _cross.rename(columns={
            "Dominant Zone": "Zone",
            "Long-term care and rehabilitation services": "Long-Term Care",
            "Quezon City satellite offices for services": "Action Offices",
            "Health centers": "Health Centers",
            "Older persons care": "Older Persons Care",
        })

        with st.container(border=True):
            st.dataframe(
                _cross.set_index("Zone"),
                width="stretch"
            )

        st.caption(
            "Rows sorted by total facility count. "
            "Unknown = barangays where zoning data could not be matched."
        )

        # Heatmap view
        _heat_cols = [
            c for c in [
                "Childcare", "Schools", "Health Centers",
                "Older Persons Care", "Long-Term Care", "Action Offices"
            ] if c in _cross.columns
        ]

        _fig_heat = _px4.imshow(
            _cross.set_index("Zone")[_heat_cols],
            text_auto=True,
            color_continuous_scale="Purples",
            title="Care Facilities Distributed Across Zone Types",
            aspect="auto",
        )
        _fig_heat.update_layout(
            xaxis_title="Facility Type",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=300, r=40, t=60, b=40),
        )

        with st.container(border=True):
            st.plotly_chart(_fig_heat)

        st.download_button(
            label="Download cross-table as CSV",
            data=_cross.to_csv(index=False).encode("utf-8"),
            file_name="qc_zone_facility_cross_table.csv",
            mime="text/csv",
        )
