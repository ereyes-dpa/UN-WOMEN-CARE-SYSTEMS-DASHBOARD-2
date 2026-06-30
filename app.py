import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import numpy as np
from functions import *
import pydeck as pdk
from pydeck.types import String
import numpy as np
import json

# PRIVATE VERSION

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Quezon Caring City Dashboard",
    layout="wide"
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
   than introducing a second palette — soft purple-tinted
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
    background: #F7F5FC;
    border: 1px solid #E4DEF7;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
}

.qcd-card-accent {
    border-left: 4px solid #7F47ED;
    background: #F7F5FC;
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
    color: #2B2A33;
    margin-bottom: 2px;
}

.qcd-card-body {
    font-size: 0.86rem;
    color: #5B5868;
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

/* Reusable "takeaway" box for under a chart — states the
   one-sentence insight in plain language, the way the PBIX
   reference dashboard does. Not yet applied to any page;
   ready to drop under a chart with:
   st.markdown('<div class="qcd-insight"><div class="qcd-insight-label">Insight</div>...</div>', unsafe_allow_html=True) */

.qcd-insight {
    background: #F0EBFB;
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
    color: #2B2A33;
    line-height: 1.45;
    margin: 0;
}

/* --------------------------------------------------
   KPI CARDS
   (replaces bare st.metric with a boxed, elevated card —
   purple gradient surface, white text — matching the
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
   st.container(border=True, key="qcd-chart-...") — the
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
   limitation, not a CSS bug here) — this tint colors the
   panel and padding around a table, but individual table
   cells may still show through as white/default underneath.
   Plotly charts render as inline SVG, so they pick up this
   background cleanly.)
   -------------------------------------------------- */

div[class*="st-key-qcd-chart-"] {
    background: #F3EFFC;
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

# Heights are chosen for consistent *visual weight*, not
# identical pixel height: QC is a dense, near-square seal,
# while FCDO and UN Women are wide wordmark+icon banners
# with a lot of thin strokes, whitespace, and small caption
# text. At equal pixel height the seal reads as too small
# and the wordmark captions become illegible, so QC is sized
# up relative to the banners until the three read as
# comparably "heavy" on the page. All three sit in one
# shared flex row so they share a single vertical-center
# alignment — no per-logo nudging needed.
LOGO_ROW_HEIGHT = 80

FCDO_HEIGHT = 56
UN_HEIGHT   = 56
QC_HEIGHT   = 72

left_col, spacer_col, right_col = st.columns([1, 3, 3])

# QC Logo (left)
with left_col:

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            height:{LOGO_ROW_HEIGHT}px;
        ">
            <a href="https://quezoncity.gov.ph/" target="_blank">
                <img src="data:image/png;base64,{qc_logo}"
                     style="height:{QC_HEIGHT}px; width:auto;">
            </a>
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
    migration_centers
) = load_data()

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
climate_context = load_climate_context()
demand_city_context, demand_district_context = load_demand_context()
domestic_workers_barangay, domestic_workers_district = (
    load_domestic_workers()
)

# --------------------------------------------------
# SUPPLY-SIDE CLIMATE EXPOSURE
# (flags each facility as inside/outside the 100-yr flood
# inundation footprint — see flag_facilities_at_risk in
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
    selected_climate_layers,
    flood_risk_only=False,
    show_risk_rings=True
):
    """
    Builds the full Care Services Explorer folium map and
    returns (html, climate_legend_info).

    Cached on (selected_layers, selected_district,
    selected_climate_layers, flood_risk_only, show_risk_rings)
    only — these are the only things that actually change what's
    drawn. Streamlit reruns this whole script on every widget
    interaction, which would otherwise rebuild the map (re-encode
    every raster overlay to PNG, rebuild every marker) from
    scratch each time even though the underlying data and raster
    renders are already cached individually. Caching the
    finished map means a rerun that doesn't change any of these
    arguments returns the previously-built HTML immediately
    instead of reconstructing and re-serializing the whole map.

    flood_risk_only — when True, only facilities flagged by
    flag_facilities_at_risk (i.e. df["flood_risk"] == True) are
    drawn as markers. This is the supply-side exposure filter:
    "which facilities sit inside the 100-yr flood footprint?" —
    computed once for every facility type up top (see
    flag_facilities_at_risk calls near DATA LOADING), not
    recomputed here. Only offered as a UI control on the Care
    Services Explorer tab inside Climate, Hazard and Population
    Analysis; the main Care Services Explorer page always passes
    False, since that page is meant to stay a plain facility map
    with no flood-risk framing.

    show_risk_rings — when True (used by the Care Services
    Explorer tab inside Climate, Hazard and Population
    Analysis), flood-exposed
    facilities get an extra red ring around their marker and a
    "⚠ flood risk" tag on the tooltip, so they stand out even
    with flood_risk_only off and the climate overlay off. When
    False (used by the main Care Services Explorer page), markers
    render with their normal symbol/color only — no ring, no
    tooltip tag — since that page is meant to read as a plain
    facility map, with flood-risk framing left to the
    Vulnerability Index tab next to the duplicated map. The
    flood-risk note inside each marker's popup is unaffected
    either way; it's behind a click, not a default-visible cue.

    html is the rendered map (via m._repr_html_()) rather than
    the live folium.Map object, so the cached value is a plain,
    easily hashable/picklable string — st_folium can render a
    Map object directly, but caching the HTML avoids any
    ambiguity about whether a cached Map object's internal state
    could be accidentally mutated by a caller between cache hits.

    climate_legend_info is a dict of
    {layer_name: (vmin, vmax)} for every selected *non-binary*
    climate layer (Land-Surface Temperature, NDVI) — used by the
    caller to render a color-scale legend outside this function,
    since folium's rendered HTML is opaque to Streamlit and can't
    host a native st widget itself. Binary layers (Flood
    Inundation) are intentionally excluded since they're a
    flooded/not-flooded mask, not a continuous scale.
    """

    service_layers = {

        "Childcare Centers": {
            "df": childcare_centers,
            "color": "#4C1D95",
            "symbol": "●",
            "source": "Childcare Center",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Schools": {
            "df": schools,
            "color": "#055B52",
            "symbol": "■",
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
            "symbol": "★",
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
            "symbol": "◆",
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
            "symbol": "▲",
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
            "symbol": "⬢",
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
            "symbol": "✦",
            "source": "Migration Resource Center",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },
    }

    climate_overlay_layers = {
        "Land-Surface Temperature": {
            "path": "processed/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
            "colormap": "YlOrRd",
            "binary": False
        },
        "Vegetation (NDVI)": {
            "path": "processed/climate/ndvi_mean_2025_EPSG3123.tif",
            "colormap": "Greens",
            "binary": False
        },
        "Flood Inundation (100-yr)": {
            "path": "processed/climate/flood_inundation_binary_gt30cm_EPSG3123.tif",
            "colormap": "Blues",
            "binary": True
        }
    }

    # A small padding around the QC extent (in degrees) so the
    # city boundary doesn't sit flush against the edge of the
    # area the user can pan/zoom into.
    bounds_padding = 0.03

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=12,
        max_zoom=18,
        tiles="CartoDB positron",
        max_bounds=True,
        min_lat=miny - bounds_padding,
        max_lat=maxy + bounds_padding,
        min_lon=minx - bounds_padding,
        max_lon=maxx + bounds_padding
    )

    geo_json, _ = load_geo_explorer()

    folium.GeoJson(
        geo_json,
        style_function=lambda x: {
            "fillColor": "#A6CFC1",
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.10,
        }
    ).add_to(m)

    # ------------------------------------------
    # CLIMATE OVERLAYS
    # ------------------------------------------

    climate_legend_info = {}

    if selected_climate_layers:

        qc_boundary_explorer = load_qc_boundary()

        for climate_layer_name in selected_climate_layers:

            climate_layer = climate_overlay_layers[climate_layer_name]

            try:

                rgba, folium_bounds, layer_vmin, layer_vmax = (
                    raster_to_image_overlay(
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

                folium.raster_layers.ImageOverlay(
                    image=rgba,
                    bounds=folium_bounds,
                    origin="upper",
                    opacity=1.0,
                    name=climate_layer_name
                ).add_to(m)

            except Exception:
                # Surfaced to the user outside this cached function
                # (see the explorer page body), since st commands
                # inside cached functions only show on the first,
                # uncached run.
                pass

    # ------------------------------------------
    # ADD MARKERS
    # ------------------------------------------

    for layer_name in selected_layers:

        layer = service_layers[layer_name]

        df = layer["df"]

        if selected_district != "All":

            df = df[
                df[layer["district_col"]]
                .astype(int)
                == selected_district
            ]

        if flood_risk_only:

            df = df[
                df.get(
                    "flood_risk",
                    pd.Series(False, index=df.index)
                )
            ]

        df = df.dropna(
            subset=[
                layer["lat_col"],
                layer["lon_col"]
            ]
        )

        has_sector = "Sector" in df.columns
        has_category = "Category" in df.columns
        has_barangay = "barangay" in df.columns
        has_open = "open_hours" in df.columns
        has_close = "close_hours" in df.columns
        has_district = layer["district_col"] in df.columns
        has_address = layer["address_col"] in df.columns

        records = df.to_dict("records")

        for row_dict in records:
            popup_html = f"""
            <b>{row_dict[layer['name_col']]}</b><br>
            Type: {layer['source']}
            """

            if has_sector and pd.notna(row_dict["Sector"]):
                popup_html += f"<br>Sector: {row_dict['Sector']}"

            if has_category and pd.notna(row_dict["Category"]):
                popup_html += f"<br>Category: {row_dict['Category']}"

            if has_district and pd.notna(row_dict[layer["district_col"]]):
                popup_html += (
                    f"<br>District: "
                    f"{int(row_dict[layer['district_col']])}"
                )

            if (
                has_barangay
                and pd.notna(row_dict["barangay"])
                and str(row_dict["barangay"]).strip() != ""
            ):
                popup_html += f"<br>Barangay: {row_dict['barangay']}"

            if has_address and pd.notna(row_dict[layer["address_col"]]):
                popup_html += (
                    f"<br>Address: "
                    f"{row_dict[layer['address_col']]}"
                )

            if has_open and pd.notna(row_dict["open_hours"]):
                popup_html += f"<br>Open: {row_dict['open_hours']}"

            if has_close and pd.notna(row_dict["close_hours"]):
                popup_html += f"<br>Close: {row_dict['close_hours']}"

            is_flood_risk = bool(row_dict.get("flood_risk", False))

            if is_flood_risk:
                popup_html += (
                    "<br><span style=\"color:#B91C1C;"
                    "font-weight:600;\">"
                    "⚠ In 100-yr flood inundation zone"
                    "</span>"
                )

            category = row_dict.get("Category")
            district = row_dict.get("District")

            if layer_name == "Childcare Centers":
                marker_color_value = childcare_color(category)

            elif layer_name == "Schools":
                marker_color_value = school_color(category)

            elif layer_name == "Health Centers":
                marker_color_value = marker_color(category)

            elif layer_name == "Older Persons Facilities":
                marker_color_value = opc_color(category)

            elif layer_name == "Long-Term Care & Rehabilitation":
                marker_color_value = ltc_color(category)

            elif layer_name == "Action Offices":
                marker_color_value = district_color(district)

            elif layer_name == "Migration Resource Centers":
                marker_color_value = "#C4B5FD"

            else:
                marker_color_value = "#7F47ED"

            if is_flood_risk and show_risk_rings:
                risk_ring_html = (
                    '<div style="'
                    "position:absolute;"
                    "width:24px;"
                    "height:24px;"
                    "border:2.5px solid #B91C1C;"
                    "border-radius:50%;"
                    "box-sizing:border-box;"
                    '"></div>'
                )
            else:
                risk_ring_html = ""

            folium.Marker(
                location=[
                    row_dict[layer["lat_col"]],
                    row_dict[layer["lon_col"]]
                ],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                        position:relative;
                        width:26px;
                        height:26px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                    ">
                        {risk_ring_html}
                        <div style="
                            color:{marker_color_value};
                            font-size:16px;
                            font-weight:bold;
                            text-align:center;
                            text-shadow:
                                -1px -1px 0 white,
                                1px -1px 0 white,
                                -1px  1px 0 white,
                                1px  1px 0 white;
                        ">
                            {layer['symbol']}
                        </div>
                    </div>
                    """
                ),
                tooltip=str(
                    row_dict[layer["name_col"]]
                ) + (
                    " ⚠ flood risk"
                    if is_flood_risk and show_risk_rings
                    else ""
                ),
                popup=folium.Popup(
                    popup_html,
                    max_width=350,
                    lazy=True
                )
            ).add_to(m)

    return m._repr_html_(), climate_legend_info

# Default values so variables always exist
selected_category = "All"

selected_childcare_category = "All"

selected_school_sector = "All"
selected_school_category = "All"

selected_opc_category = "All"

selected_ltc_category = "All"

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

st.sidebar.subheader("Care Maps")


# --------------------------------------------------
# POPULATION
# --------------------------------------------------

if st.sidebar.button(
    "Population Overview",
    width="stretch"
):
    st.session_state.page = "Population Overview"
    st.rerun()


# --------------------------------------------------
# CHILDCARE
# --------------------------------------------------

if st.sidebar.button(
    "Childcare Centers",
    width='stretch'
):
    st.session_state.page = "Childcare Centers"
    st.rerun()

if st.session_state.page == "Childcare Centers":

    st.sidebar.markdown("##### Filters")

    selected_childcare_category = st.sidebar.radio(
        "Facility Category",
        [
            "All",
            "Child Development Center",
            "Child Learning Center",
            "Day Care Center",
            "Supervised Neighborhood Play"
        ],
        key="childcare_category"
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

    if selected_school_sector == "Public":

        category_options = [
            "All",
            "Public School"
        ]

    elif selected_school_sector == "Private":

        category_options = [
            "All",
            "Private School"
        ]

    else:

        category_options = [
            "All",
            "Public School",
            "Private School"
        ]

    selected_school_category = st.sidebar.radio(
        "School Category",
        category_options,
        key="school_category"
    )

# --------------------------------------------------
# HEALTH CENTERS
# --------------------------------------------------

if st.sidebar.button(
    "Health Centers Map",
    width='stretch'
):
    st.session_state.page = "Health Centers Map"
    st.rerun()

if st.session_state.page == "Health Centers Map":

    st.sidebar.markdown("##### Filters")

    selected_category = st.sidebar.radio(
        "Facility Type",
        [
            "All",
            "QC LGU",
            "National",
            "Super Health",
            "Health Center",
            "Pharmacy",
            "Milk Bank"
        ],
        key="health_category"
    )

# --------------------------------------------------
# OLDER PERSONS
# --------------------------------------------------

if st.sidebar.button(
    "Older Persons Center Map",
    width='stretch'
):
    st.session_state.page = "Older Persons Center Map"
    st.rerun()

if st.session_state.page == "Older Persons Center Map":

    st.sidebar.markdown("##### Filters")

    selected_opc_category = st.sidebar.radio(
        "Facility Type",
        [
            "All",
            "Nursing Care Center",
            "Bahay Aruga for Abandoned Elderly"
        ],
        key="opc_category"
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

st.sidebar.subheader("Additional Tools")

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
    "Climate, Hazard and Population Analysis",
    width='stretch'
):
    st.session_state.page = "Climate, Hazard and Population Analysis"
    st.rerun()

# --------------------------------------------------
# ACTIVE PAGE
# --------------------------------------------------

page = st.session_state.page

if page == "Care Services Explorer":

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Child Care")

    st.sidebar.markdown(
        """
        <span style="color:#4C1D95;font-size:22px;">●</span>
        <b>Child Development Center</b><br>
        <span style="color:#8869C9;font-size:22px;">●</span>
        <b>Child Learning Center</b><br>
        <span style="color:#C4B5FD;font-size:22px;">●</span>
        <b>Day Care Center</b><br>
        <span style="color:#E0D4FD;font-size:22px;">●</span>
        <b>Supervised Neighborhood Play</b>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Schools")

    st.sidebar.markdown(
        """
        <span style="color:#055B52;font-size:22px;">■</span>
        <b>Public School</b><br>
        <span style="color:#A6CFC1;font-size:22px;">■</span>
        <b>Private School</b>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Health Services")

    ordered_categories = [
        "QC LGU",
        "National",
        "Super Health",
        "Health Center",
        "Pharmacy",
        "Milk Bank"
    ]

    for cat in ordered_categories:

        st.sidebar.markdown(
            f"""
            <span style="
                color:{category_hex(cat)};
                font-size:22px;
            ">★</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Older Persons")

    st.sidebar.markdown(
        """
        <span style="color:#055B52;font-size:22px;">◆</span>
        <b>Nursing Care Center</b><br>
        <span style="color:#A6CFC1;font-size:22px;">◆</span>
        <b>Bahay Aruga</b>
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
            ">▲</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )


    st.sidebar.markdown("---")
    st.sidebar.markdown("## Action Offices")

    st.sidebar.markdown(
        """
        <span style="color:#055B52;font-size:22px;">⬢</span>
        <b>District Offices</b>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Migration Services")

    st.sidebar.markdown(
        """
        <span style="color:#C4B5FD;font-size:22px;">✦</span>
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
                    Central reference for Quezon City's care-service
                    network — population, facilities, accessibility,
                    and climate exposure — to support planning,
                    resource allocation, and program design.
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
    # HOW TO NAVIGATE  /  WHAT'S INSIDE
    # =====================================================

    nav_col, contents_col = st.columns([1, 1.3])

    with nav_col:

        st.markdown(
            '<div class="qcd-section-label">How to Navigate</div>',
            unsafe_allow_html=True
        )

        nav_steps = [
            (
                "Explore",
                "Use the sidebar to move between care-service "
                "maps, analysis tools, and climate pages."
            ),
            (
                "Filter",
                "Most pages offer district, category, or layer "
                "filters above the map or chart."
            ),
            (
                "Decide",
                "Use the accessibility ratios, planning "
                "priorities, and vulnerability index to inform "
                "resource allocation."
            )
        ]

        for step_title, step_body in nav_steps:

            st.markdown(
                f"""
                <div class="qcd-card">
                    <div class="qcd-card-title">{step_title}</div>
                    <p class="qcd-card-body">{step_body}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    with contents_col:

        st.markdown(
            '<div class="qcd-section-label">What\'s Inside</div>',
            unsafe_allow_html=True
        )

        content_groups = [
            (
                "#055B52",
                "Care Services",
                "Childcare, schools, health centers, older "
                "persons' facilities, long-term care, action "
                "offices, and migration resource centers."
            ),
            (
                "#7F47ED",
                "Analysis Tools",
                "Care Services Explorer, Accessibility Analysis, "
                "Care Planning & Investment Priorities, and "
                "Barangay Clusters."
            ),
            (
                "#B91C1C",
                "Climate & Vulnerability",
                "Climate, Hazard and Population Analysis — which "
                "facilities and population groups are most at "
                "risk from flooding and heat, and where."
            )
        ]

        for accent_color, group_title, group_body in content_groups:

            st.markdown(
                f"""
                <div class="qcd-card-accent"
                     style="border-left-color:{accent_color};">
                    <div class="qcd-card-title">{group_title}</div>
                    <p class="qcd-card-body">{group_body}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "Population Overview":

    import geopandas as gpd
    import plotly.express as px
    import plotly.graph_objects as go

    st.title("Population Overview")

    st.markdown("""
    Demographic profile of Quezon City to support planning,
    resource allocation, and care service delivery decisions.
    """)

    # =====================================================
    # AGE GROUP DEFINITION — ⚠️ PENDING CONFIRMATION WITH MARIAN
    # (same definition documented in Notebook 2, Section 2.1.0)
    # Source data arrives pre-aggregated into these four bands,
    # so a different elderly/children cutoff (e.g. 65+ instead
    # of 60+) cannot be derived from what we have — it would
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
            "60+ (Elderly)"
        ]
    }

    # =====================================================
    # LOAD MAPS
    # =====================================================

    barangay_map = gpd.read_file(
        "processed/qc_barangays.geojson"
    )

    district_map = gpd.read_file(
        "processed/qc_districts.geojson"
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
        "60+ (Elderly)"
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
    total_female = population_sex["Female"].sum()

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

    top1, top2 = st.columns(2)

    kpi_card(
        top1,
        "Population",
        f"{total_population:,.0f}"
    )

    kpi_card(
        top2,
        "Sex Ratio (M/F)",
        f"{sex_ratio_overall:.1f}"
    )

    st.markdown(
        '<div class="qcd-section-label">Age Ranges — % of Total Population</div>',
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

    st.info(
        "**Land Use layer pending.** A land use/zoning indicator "
        "(e.g., % residential, % open space per barangay) is planned "
        "for this page once Quezon City government shares the data, "
        "or a public Geoportal Philippines alternative is confirmed. "
        "See Notebooks 1–2 for status."
    )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "Barangay Analysis",
            "District Analysis",
            "Socio-Economic Indicators"
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
        # on that isn't safe — explicitly uppercase both sides,
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
        # age_group_definition above — update there, not here,
        # once confirmed with Marian)
        # ---------------------------------------------------

        barangay_df["children_0_17"] = barangay_df[
            age_group_definition["children_0_17"]
        ].sum(axis=1)

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
        # MAP — only the indicators that are genuinely useful
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
                "Working Age Population",
                "Older Persons Population",
                "Children Share (%)",
                "Older Persons Share (%)",
                "Population Density"
            ]
        )

        indicator_map = {
            "Total Population": "Total",
            "Male Population": "Male",
            "Female Population": "Female",
            "Children Population (0-17)":
                "children_0_17",
            "Working Age Population":
                "working_age",
            "Older Persons Population":
                "elderly",
            "Children Share (%)":
                "children_pct",
            "Older Persons Share (%)":
                "elderly_pct",
            "Population Density":
                "population_density"
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
                "Combined count of residents aged 0–5 and 6–17 — "
                "the population segment most dependent on schools, "
                "childcare, and pediatric health services.",
            "Working Age Population":
                "Residents aged 18–59, the segment that typically "
                "supports the local economy and tax base.",
            "Older Persons Population":
                "Residents aged 60 and above — a key group for "
                "senior care planning and health services.",
            "Children Share (%)":
                "Percentage of the barangay's population aged 0–17. "
                "Higher values signal greater demand for schools "
                "and child-focused services.",
            "Older Persons Share (%)":
                "Percentage of the barangay's population aged 60+. "
                "Higher values signal greater demand for elderly "
                "care and health services.",
            "Population Density":
                "Residents per square kilometer. Higher density "
                "areas typically need more concentrated infrastructure "
                "and service delivery points."
        }

        st.caption(indicator_descriptions[indicator])

        # ---------------------------------------------------
        # CHOROPLETH FILL COLORS (continuous, Purples ramp,
        # clipped to 5th-95th percentile — same clipping the
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
        # VIEW STATE — locked to the same zoom range as the
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
                choropleth_layer
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-1"):
            st.pydeck_chart(
                deck,
                height=650,
                width="stretch"
            )

            # pydeck has no built-in colorbar (unlike Plotly's
            # automatic color_continuous_scale legend), so the
            # fill color here would otherwise be unexplained —
            # render_colormap_legend_html builds the same kind of
            # gradient-bar legend already used for the climate
            # raster layers elsewhere in this app, reusing the
            # same vmin/vmax (5th-95th percentile clip) that was
            # used to compute fill_color above, so the legend
            # matches what's actually drawn on the map.
            indicator_units = {
                "Children Share (%)": "%",
                "Older Persons Share (%)": "%",
                "Population Density": "people/km²"
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

        st.divider()

        # ---------------------------------------------------
        # TOP / BOTTOM BARANGAYS — POPULATION DENSITY
        # ---------------------------------------------------

        st.subheader("Population Density by Barangay")

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
                title="Top 10 — Highest Density (people/km²)",
                color_discrete_sequence=["#7F47ED"]
            )
            fig_top_den.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Population Density"
            )
            with st.container(border=True, key="qcd-chart-2"):
                st.plotly_chart(fig_top_den, width="stretch")

        with col_den2:
            fig_bottom_den = px.bar(
                bottom_den.sort_values("population_density", ascending=False),
                x="population_density",
                y="Barangay",
                orientation="h",
                title="Top 10 — Lowest Density (people/km²)",
                color_discrete_sequence=["#80AA31"]
            )
            fig_bottom_den.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Population Density"
            )
            with st.container(border=True, key="qcd-chart-3"):
                st.plotly_chart(fig_bottom_den, width="stretch")

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
        # DISTRICT MAP — kept to the indicators that matter
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
                "60+ (Elderly)"
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
                "Residents aged 60 and above — a key group for "
                "senior care planning and health services."
        }

        st.caption(
            district_indicator_descriptions[district_indicator]
        )

        # ---------------------------------------------------
        # CHOROPLETH FILL COLORS (continuous, Purples ramp,
        # full min/max range — this map had no percentile
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
        # VIEW STATE — locked to the same zoom range as the
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
                district_choropleth_layer
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-5"):
            st.pydeck_chart(
                deck,
                height=650,
                width="stretch"
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

        fig_age = px.bar(
            district_age_long,
            x="District",
            y="Population",
            color="Age Group",
            title="Population Structure by District",
            barmode="stack",
            color_discrete_sequence=QCD_CATEGORICAL
        )

        fig_age.update_layout(height=450)

        with st.container(border=True, key="qcd-chart-6"):
            st.plotly_chart(
                fig_age,
                width="stretch"
            )

        st.divider()

        # ---------------------------------------------------
        # POPULATION PYRAMID (City-wide, Male vs Female)
        # ---------------------------------------------------

        st.subheader("Population Pyramid — Male vs Female")

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
            title="Citywide Population by Sex",
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
                st.plotly_chart(fig_pyramid, width="stretch")

        with col_pyr2:
            fig_ratio = px.bar(
                district_pop.sort_values("Sex Ratio", ascending=False),
                x="District",
                y="Sex Ratio",
                title="Sex Ratio (M/F ×100) by District",
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
                st.plotly_chart(fig_ratio, width="stretch")

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

    # =====================================================
    # SOCIO-ECONOMIC TAB
    # =====================================================
    with tab3:

        st.markdown("""
        Contextual socio-economic indicators at the barangay
        level — household composition, food insecurity, and
        housing conditions (2024 CBMS), plus sex ratio and the
        share of working-age women.
        """)

        st.info(
            "**CBMS coverage note.** The household-survey "
            "indicators below (household size, nuclear families "
            "per household, food insecurity, housing inadequacy) "
            "come from the 2024 Community-Based Monitoring System, "
            "which covers roughly 71% of Quezon City's census "
            "population — not a full count. They should be read "
            "as indicative of conditions in responding households, "
            "not as exact citywide totals."
        )

        # ---------------------------------------------------
        # MAP DATA
        # ---------------------------------------------------

        # Domestic worker counts live in a separate source
        # (domestic_workers_barangay, from
        # load_domestic_workers() in functions.py) rather than
        # demographics.csv, so they're merged in here, once,
        # before the indicator dict below — everything
        # downstream (KPIs, map, top-15 table) just sees three
        # more plain numeric columns and treats them exactly
        # like every other socio-economic indicator.
        demographics_with_dw = demographics.copy()

        demographics_with_dw["barangay_key"] = (
            demographics_with_dw["barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        demographics_with_dw = demographics_with_dw.merge(
            domestic_workers_barangay[
                [
                    "barangay_key",
                    "domestic_workers_female",
                    "domestic_workers_male",
                    "domestic_workers_total"
                ]
            ],
            on="barangay_key",
            how="left"
        )

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
                    "per-1,000 domestic worker rates above — "
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
                    "population — a proxy for female labor "
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
                    "domestic_workers.csv."
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
            "Population Distribution vs. Total Domestic Workers": {
                "col": "domestic_workers_per_1000_total",
                "description": (
                    "Registered domestic workers per 1,000 "
                    "residents, by barangay. Source: "
                    "processed/indicators/domestic_workers.csv "
                    "(separate from the CBMS indicators below)."
                )
            },
            "Population Distribution vs. Female Domestic Workers": {
                "col": "domestic_workers_per_1000_female",
                "description": (
                    "Registered female domestic workers per "
                    "1,000 female residents, by barangay."
                )
            },
            "Population Distribution vs. Male Domestic Workers": {
                "col": "domestic_workers_per_1000_male",
                "description": (
                    "Registered male domestic workers per "
                    "1,000 male residents, by barangay."
                )
            }
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
            "Highest Barangay",
            f"{socio_max_row['barangay_name'].title()} "
            f"({socio_max_row[selected_socio_col]:,.2f})"
        )

        kpi_card(
            sc3,
            "Lowest Barangay",
            f"{socio_min_row['barangay_name'].title()} "
            f"({socio_min_row[selected_socio_col]:,.2f})"
        )

        st.divider()

        # ---------------------------------------------------
        # MAP
        # ---------------------------------------------------

        st.subheader(
            f"Barangay Map — {selected_socio_label}"
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
                socio_layer
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-10"):
            st.pydeck_chart(
                deck,
                height=650,
                width="stretch"
            )

            # Same gap as the Barangay/District Analysis maps —
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

        st.divider()

        # ---------------------------------------------------
        # TOP / BOTTOM BARANGAYS
        # ---------------------------------------------------

        st.subheader(
            f"Top 15 Barangays by {selected_socio_label}"
        )

        with st.container(border=True, key="qcd-chart-11"):
            st.dataframe(
                socio_map[
                    ["barangay_name", "District", selected_socio_col]
                ]
                .rename(
                    columns={
                        "barangay_name": "Barangay",
                        selected_socio_col: selected_socio_label
                    }
                )
                .dropna(subset=[selected_socio_label])
                .sort_values(selected_socio_label, ascending=False)
                .head(15),
                width="stretch"
            )

        st.divider()

        # ---------------------------------------------------
        # POPULATION vs. DOMESTIC WORKERS (SIDE BY SIDE)
        # (Cecilia's original ask, per Zainab's Slack
        # clarification: population distribution shown
        # alongside domestic worker counts as two separate
        # values per barangay — not blended into the per-1,000
        # rate used by the "Population Distribution vs.
        # Domestic Workers" choropleths above. Both views stay
        # on the dashboard per Zainab's "we can keep both".
        # Uses the same demographics_with_dw frame already
        # merged with domestic worker counts earlier in this
        # tab, so no second data load/merge is needed here.)
        # ---------------------------------------------------

        st.subheader("Domestic Worker Concentration")

        st.caption(
            "Barangays ranked by raw domestic worker count "
            "(not population, and not a per-1,000 rate) — for "
            "resource and outreach planning where what matters "
            "is where domestic workers are physically "
            "concentrated, regardless of barangay population "
            "size. The full table below also includes "
            "population for reference, alongside the per-1,000 "
            "rate charts above."
        )

        dw_compare_sex = st.radio(
            "Domestic worker count to compare",
            ["Total", "Female", "Male"],
            horizontal=True,
            key="dw_compare_sex"
        )

        dw_compare_col_map = {
            "Total": (
                "domestic_workers_total", "pop_census",
                "Total Population"
            ),
            "Female": (
                "domestic_workers_female", "pop_female",
                "Female Population"
            ),
            "Male": (
                "domestic_workers_male", "pop_male",
                "Male Population"
            ),
        }

        dw_col, pop_col, pop_label = (
            dw_compare_col_map[dw_compare_sex]
        )

        dw_compare_df = demographics_with_dw[
            ["barangay", "district", pop_col, dw_col]
        ].dropna(subset=[pop_col, dw_col]).copy()

        dw_compare_df = dw_compare_df.rename(
            columns={
                "barangay": "Barangay",
                "district": "District",
                pop_col: pop_label,
                dw_col: f"{dw_compare_sex} Domestic Workers"
            }
        )

        # Ranked purely by domestic worker count, not
        # population — the question this chart answers is
        # "where are domestic workers concentrated", a
        # resource-planning/headcount question, not a rate or
        # correlation question. Population is intentionally left
        # off this chart; it doesn't help answer that question
        # and was the source of the earlier scale-mismatch issue
        # (population in the hundreds of thousands flattening
        # domestic worker bars to near-invisible). Horizontal
        # orientation since up to 15 barangay names are easier
        # to read as y-axis labels than rotated/crowded x-axis
        # labels.
        dw_top15 = (
            dw_compare_df
            .sort_values(
                f"{dw_compare_sex} Domestic Workers",
                ascending=False
            )
            .head(15)
        )

        fig_dw_compare = px.bar(
            dw_top15.sort_values(
                f"{dw_compare_sex} Domestic Workers",
                ascending=True
            ),
            x=f"{dw_compare_sex} Domestic Workers",
            y="Barangay",
            orientation="h",
            color=f"{dw_compare_sex} Domestic Workers",
            color_continuous_scale="Purples",
            title=(
                f"Top 15 Barangays by {dw_compare_sex} "
                "Domestic Worker Count"
            )
        )

        fig_dw_compare.update_layout(
            yaxis_title="",
            xaxis_title=(
                f"{dw_compare_sex} Domestic Workers (count)"
            ),
            coloraxis_showscale=False
        )

        with st.container(border=True, key="qcd-chart-88"):
            st.plotly_chart(
                fig_dw_compare,
                width="stretch"
            )

        with st.expander(
            "Full barangay table — population vs. domestic "
            "workers"
        ):
            with st.container(border=True, key="qcd-chart-89"):
                st.dataframe(
                    dw_compare_df.sort_values(
                        pop_label, ascending=False
                    ),
                    width="stretch"
                )

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

    # --------------------------------------------------
    # CHILDCARE KPIs
    # --------------------------------------------------

    childcare_summary = pd.read_csv(
        "processed/childcare_summary.csv"
    )

    total_centers = int(
        childcare_summary.loc[
            childcare_summary["metric"]
            == "child_development_centers",
            "value"
        ].iloc[0]
    )

    eccd_enrollees = int(
        childcare_summary.loc[
            childcare_summary["metric"]
            == "eccd_enrollees",
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

    covered_barangays = (
        childcare_centers["barangay"]
        .nunique()
    )

    covered_districts = (
        childcare_centers["District"]
        .nunique()
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

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
        "ECCD Enrollees",
        f"{eccd_enrollees:,}",
        "up_good"
    )

    kpi_card(
        k4,
        "CDCs",
        f"{total_centers:,}",
        "up_good"
    )

    kpi_card(
        k5,
        "Day Care Centers",
        f"{day_care_centers:,}"
    )

    kpi_card(
        k6,
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
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
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
        Close: {close_hours}
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
            childcare_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"

    )

    with st.container(border=True, key="qcd-chart-12"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch'
        )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.subheader("Facilities")

    with st.container(border=True, key="qcd-chart-13"):
        st.dataframe(
            cc[
                [
                    "Name",
                    "Category",
                    "Sector",
                    "District",
                    "Address"
                ]
            ].rename(
                columns={"Sector": "Provider Type"}
            ),
            width = 'stretch'
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
            title="Facilities by Category",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-14"):
            st.plotly_chart(
                fig,
                width='stretch'
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

        fig = px.bar(
            district_counts,
            x="District",
            y="Facilities",
            title="Facilities by District",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-15"):
            st.plotly_chart(
                fig,
                width='stretch'
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

    enrollment_rate = (
        eccd_enrollees
        / early_childhood_population
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
        f"{enrollment_rate:.1f}%",
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
    total_schools = len(schools)

    public_schools = (
        schools["Category"]
        .str.contains(
            "Public",
            case=False,
            na=False
        )
        .sum()
    )

    private_schools = (
        schools["Category"]
        .str.contains(
            "Private",
            case=False,
            na=False
        )
        .sum()
    )

    covered_barangays = (
        schools["barangay"]
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

    school_age_population = (
        population_age[
            "6-17 (School Age Children)"
        ]
        .sum()
    )

    children_per_school = (
        school_age_population
        / total_schools
    )

    c1, c2 = st.columns(2)

    kpi_card(
        c1,
        "School-Age Population (6-17)",
        f"{school_age_population:,.0f}"
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

        sch = sch[
            sch["Category"]
            .str.contains(
                selected_school_category,
                case=False,
                na=False
            )
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

    school_layer = pdk.Layer(
        "ScatterplotLayer",
        data=sch,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
        get_radius=40,
        radius_min_pixels=4,
        radius_max_pixels=4,
        pickable=True,
    )

    # --------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------

    

    tooltip = {
        "html": """
        <b>{Name}</b><br/>
        Sector: {Sector}<br/>
        Category: {Category}<br/>
        District: {District}<br/>
        Address: {Address}<br/>
        Open: {open_hours}<br/>
        Close: {close_hours}
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
            school_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"

    )

    with st.container(border=True, key="qcd-chart-16"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch'
        )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.subheader("Schools")

    with st.container(border=True, key="qcd-chart-17"):
        st.dataframe(
            sch[
                [
                    "Name",
                    "Sector",
                    "Category",
                    "District",
                    "Address"
                ]
            ],
            width = 'stretch'
        )


    # --------------------------------------------------
    # SCHOOL KPIs
    # --------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:

        # Defensive filter: schools is already scoped to
        # major_division == "Schools" upstream (see load_data()
        # in functions.py), so every row here should carry a
        # "Public School" / "Private School" Category value. If
        # a stray row with an unrelated Category slips through
        # (e.g. mislabeled in the source CSV), drop it here
        # rather than let it show up as a phantom slice with an
        # unrelated color in this chart.
        valid_school_categories = (
            schools["Category"]
            .astype(str)
            .str.contains(
                "PUBLIC SCHOOL|PRIVATE SCHOOL",
                case=False,
                na=False
            )
        )

        category_counts = (
            schools.loc[valid_school_categories, "Category"]
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
            title="School Distribution",
            color_discrete_sequence=school_colors
        )

        # Pull percentage labels outside the slices and hide
        # labels for any near-zero slice. With only two real
        # categories (Public/Private School) this mostly just
        # keeps spacing clean, but it also guards against label
        # crowding if a future data refresh reintroduces a tiny
        # third slice.
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
                fig,
                width='stretch'
            )

    with col2:

        district_counts = (
            schools
            .groupby("District")
            .size()
            .reset_index(name="Schools")
            .sort_values(
                "Schools",
                ascending=False
            )
        )

        fig = px.bar(
            district_counts,
            x="District",
            y="Schools",
            text_auto=True,
            title="Schools by District",
            color_discrete_sequence=["#7F47ED"]
        )

        with st.container(border=True, key="qcd-chart-19"):
            st.plotly_chart(
                fig,
                width='stretch'
            )
 

    district_schools = (
        schools
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
        schools
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
        "processed/health_centers_and_doctors_per_district.csv"
    )

    # The district column in this CSV has inconsistent spacing
    # between "District" and the number (e.g. "District  2" with
    # two spaces vs. "District 1" with one) — collapse it once
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

    health_centers_count = (
        health_centers["Category"]
        .eq("Health Center")
        .sum()
    )

    super_health_centers = (
        health_centers["Category"]
        .eq("Super Health")
        .sum()
    )

    pharmacies = (
        health_centers["Category"]
        .eq("Pharmacy")
        .sum()
    )

    hospitals = (
        health_centers["Category"]
        .isin(["National", "QC LGU"])
        .sum()
    )

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

        hc = hc[
            hc["Category"]
            .str.contains(
                selected_category,
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------
    # REMOVE MISSING COORDINATES
    # --------------------------------------------------

    hc = hc.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # HOURS DISPLAY
    # --------------------------------------------------

    if "open_hours" in hc.columns:
        hc["open_display"] = (
            hc["open_hours"]
            .fillna("Not available")
        )
    else:
        hc["open_display"] = "Not available"

    if "close_hours" in hc.columns:
        hc["close_display"] = (
            hc["close_hours"]
            .fillna("Not available")
        )
    else:
        hc["close_display"] = "Not available"

    # --------------------------------------------------
    # BARANGAY DISPLAY
    # --------------------------------------------------

    if "barangay" in hc.columns:
        hc["barangay_display"] = (
            hc["barangay"]
            .fillna("Not available")
        )
    else:
        hc["barangay_display"] = "Not available"

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

    health_layer = pdk.Layer(
        "ScatterplotLayer",
        data=hc,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
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
        District: {District}<br/>
        Barangay: {barangay_display}<br/>
        Address: {Address}<br/>
        Open: {open_display}<br/>
        Close: {close_display}
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
            health_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-22"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch'
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

    fig = px.bar(
        district_capacity,
        x="district",
        y="health_centers",
        title="Health Centers by District",
        text_auto=True,
        color_discrete_sequence=["#7F47ED"]
    )

    with st.container(border=True, key="qcd-chart-23"):
        st.plotly_chart(
            fig,
            width='stretch'
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
            fig,
            width='stretch'
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
    # CSV — it doesn't reflect the full range of health-related
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
            fig,
            width='stretch'
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

    senior_summary = pd.read_csv(
        "processed/senior_summary.csv"
    )

    registered_seniors = int(
        senior_summary.loc[
            senior_summary["metric"] ==
            "registered_seniors_2026",
            "value"
        ].iloc[0]
    )

    female_seniors = int(
        senior_summary.loc[
            senior_summary["metric"] ==
            "female",
            "value"
        ].iloc[0]
    )

    male_seniors = int(
        senior_summary.loc[
            senior_summary["metric"] ==
            "male",
            "value"
        ].iloc[0]
    )

    age_60_79 = int(
        senior_summary.loc[
            senior_summary["metric"] ==
            "age_60_79",
            "value"
        ].iloc[0]
    )

    age_80_plus = int(
        senior_summary.loc[
            senior_summary["metric"] ==
            "age_80_plus",
            "value"
        ].iloc[0]
    )

    total_facilities = len(
        older_person_care
    )

    nursing_centers = (
        older_person_care["Category"]
        .str.contains(
            "Nursing",
            case=False,
            na=False
        )
        .sum()
    )

    bahay_aruga = (
        older_person_care["Category"]
        .str.contains(
            "Bahay",
            case=False,
            na=False
        )
        .sum()
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    kpi_card(
        k1,
        "Registered Seniors",
        f"{registered_seniors:,}"
    )

    kpi_card(
        k2,
        "Female",
        f"{female_seniors:,}"
    )

    kpi_card(
        k3,
        "Male",
        f"{male_seniors:,}"
    )

    kpi_card(
        k4,
        "Age 60-79",
        f"{age_60_79:,}"
    )

    kpi_card(
        k5,
        "Age 80+",
        f"{age_80_plus:,}"
    )

    kpi_card(
        k6,
        "Care Facilities",
        f"{total_facilities:,}",
        "up_good"
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

        opc = opc[
            opc["Category"]
            .str.contains(
                selected_opc_category,
                case=False,
                na=False
            )
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
    # DISPLAY COLUMNS
    # --------------------------------------------------

    if "barangay" in opc.columns:

        opc["barangay_display"] = (
            opc["barangay"]
            .fillna("Not available")
        )

    else:

        opc["barangay_display"] = (
            "Not available"
        )

    if "open_hours" in opc.columns:

        opc["open_display"] = (
            opc["open_hours"]
            .fillna("Not available")
        )

    else:

        opc["open_display"] = (
            "Not available"
        )

    if "close_hours" in opc.columns:

        opc["close_display"] = (
            opc["close_hours"]
            .fillna("Not available")
        )

    else:

        opc["close_display"] = (
            "Not available"
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
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
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
        District: {District}<br/>
        Barangay: {barangay_display}<br/>
        Address: {Address}<br/>
        Open: {open_display}<br/>
        Close: {close_display}
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
            facility_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-27"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch'
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
            title="Senior Citizens by Sex",
            color_discrete_sequence=QCD_CATEGORICAL
        )

        with st.container(border=True, key="qcd-chart-28"):
            st.plotly_chart(
                fig,
                width='stretch'
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
                fig,
                width='stretch'
            )

    seniors_per_year = pd.read_csv(
        "processed/seniors_per_year.csv"
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
            fig,
            width='stretch'
        )

    seniors_barangay = pd.read_csv(
        "processed/seniors_per_barangay.csv"
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
            fig,
            width="stretch"
        )

    facility_counts = (
        older_person_care
        .groupby("District")
        .size()
        .reset_index(name="Facilities")
    )

    facility_counts["District"] = (
        "District "
        + facility_counts["District"]
        .astype(int)
        .astype(str)
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
        title="Older Persons Care Facility Types",
        color_discrete_sequence=QCD_CATEGORICAL
    )

    with st.container(border=True, key="qcd-chart-34"):
        st.plotly_chart(
            fig,
            width="stretch"
        )

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
            Long-Term Care & Rehabilitation Services
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

    covered_barangays = (
        long_term_care["barangay"]
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
    # DISPLAY COLUMNS
    # --------------------------------------------------

    if "barangay" in ltc.columns:

        ltc["barangay_display"] = (
            ltc["barangay"]
            .fillna("Not available")
        )

    else:

        ltc["barangay_display"] = (
            "Not available"
        )

    if "open_hours" in ltc.columns:

        ltc["open_display"] = (
            ltc["open_hours"]
            .fillna("Not available")
        )

    else:

        ltc["open_display"] = (
            "Not available"
        )

    if "close_hours" in ltc.columns:

        ltc["close_display"] = (
            ltc["close_hours"]
            .fillna("Not available")
        )

    else:

        ltc["close_display"] = (
            "Not available"
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

    facility_layer = pdk.Layer(
        "ScatterplotLayer",
        data=ltc,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
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
        District: {District}<br/>
        Barangay: {barangay_display}<br/>
        Address: {Address}<br/>
        Open: {open_display}<br/>
        Close: {close_display}
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
            facility_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-35"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch' 
        )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Facilities")

    with st.container(border=True, key="qcd-chart-36"):
        st.dataframe(
            ltc[
                [
                    "Name",
                    "Category",
                    "District",
                    "Address"
                ]
            ],
            width = 'stretch'
        )

    # --------------------------------------------------
    # REHABILITATION KPIs
    # --------------------------------------------------

    elderly_population = (
        population_age[
            "60+ (Elderly)"
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

    fig = px.bar(
        service_mix,
        x="Service Type",
        y="Facilities",
        title="Long-Term Care and Rehabilitation Services",
        color_discrete_sequence=["#7F47ED"]
    )

    with st.container(border=True, key="qcd-chart-37"):
        st.plotly_chart(
            fig,
            width="stretch"
        )

    district_counts = (
        long_term_care
        .groupby("District")
        .size()
        .reset_index(name="Facilities")
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
            fig,
            width="stretch"
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

    top_categories = (
        long_term_care["Category"]
        .value_counts()
    )

    st.info(
        f"""
        Quezon City currently has
        {total_facilities:,} rehabilitation and long-term care facilities
        covering {covered_barangays:,} barangays.

        The most common service type is
        {top_categories.index[0]}
        ({top_categories.iloc[0]} facilities).
        """
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
    Registered persons with disability (PWD) and senior
    citizens with disability across Quezon City, by sex,
    disability type, district, and barangay.
    """)

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
    # demographics, demand_city_context, and
    # demand_district_context are loaded once at app
    # startup (see top of file) from
    # processed/indicators/demographics.csv,
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

    total_male = pwd_by_type["male"].sum()
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
        "Registered PWDs",
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
        "PWDs per Rehabilitation Facility",
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
            title="PWD Population by Sex",
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
            yaxis_title="Registered PWDs"
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
        "PWD Population by District"
    )

    district_display = demand_district_context.copy()

    district_display["District"] = (
        "District "
        + district_display["district"].astype(str)
    )

    fig = px.bar(
        district_display,
        x="District",
        y="pwd_registered",
        text_auto=",",
        title="Registered PWDs by District",
        color_discrete_sequence=["#7F47ED"]
    )

    fig.update_layout(
        yaxis_title="Registered PWDs"
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
    # — no year-by-year registration history is available
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
        "their counts of seniors also registered as PWD do "
        "not match. Both figures are shown rather than "
        "reconciled into one number. City-level only — no "
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
            title="Seniors Also Registered as PWD",
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
            "Top 10 Barangays by PWD Population"
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
                        "pwd_registered": "PWDs"
                    }
                )
                .sort_values(
                    "PWDs",
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
        "PWD Population vs Rehabilitation Services"
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

    district_coverage["PWDs per Facility"] = (
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
                    "PWDs per Facility"
                ]
            ].rename(
                columns={
                    "district": "District",
                    "pwd_registered": "Registered PWDs in QC"
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


    st.caption(
        """
        Explore the distribution of Quezon City
        Action Offices providing local access
        to government services.
        """
    )

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
    # DISPLAY COLUMNS
    # --------------------------------------------------

    if "barangay" in sat.columns:

        sat["barangay_display"] = (
            sat["barangay"]
            .fillna("Not available")
        )

    else:

        sat["barangay_display"] = (
            "Not available"
        )

    if "open_hours" in sat.columns:

        sat["open_display"] = (
            sat["open_hours"]
            .fillna("Not available")
        )

    else:

        sat["open_display"] = (
            "Not available"
        )

    if "close_hours" in sat.columns:

        sat["close_display"] = (
            sat["close_hours"]
            .fillna("Not available")
        )

    else:

        sat["close_display"] = (
            "Not available"
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
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
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
        <b>{Category}</b><br/>
        District: {District}<br/>
        Barangay: {barangay_display}<br/>
        Address: {Address}<br/>
        Open: {open_display}<br/>
        Close: {close_display}
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
            office_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-49"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch'
        )
    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Action Offices")

    with st.container(border=True, key="qcd-chart-50"):
        st.dataframe(
            sat[
                [
                    "District",
                    "Address"
                ]
            ],
            width = 'stretch'
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
    # DISPLAY COLUMNS
    # --------------------------------------------------

    if "barangay" in mig.columns:

        mig["barangay_display"] = (
            mig["barangay"]
            .fillna("Not available")
        )

    else:

        mig["barangay_display"] = (
            "Not available"
        )

    if "open_hours" in mig.columns:

        mig["open_display"] = (
            mig["open_hours"]
            .fillna("Not available")
        )

    else:

        mig["open_display"] = (
            "Not available"
        )

    if "close_hours" in mig.columns:

        mig["close_display"] = (
            mig["close_hours"]
            .fillna("Not available")
        )

    else:

        mig["close_display"] = (
            "Not available"
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

    facility_layer = pdk.Layer(
        "ScatterplotLayer",
        data=mig,
        get_position="[longitude, latitude]",
        get_fill_color="[r, g, b]",
        get_line_color="[r, g, b]",
        stroked=True,
        filled=True,
        opacity=0.9,
        line_width_min_pixels=2,
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
        District: {District}<br/>
        Barangay: {barangay_display}<br/>
        Address: {Address}<br/>
        Open: {open_display}<br/>
        Close: {close_display}<br/>
        <br/>
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
            facility_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    with st.container(border=True, key="qcd-chart-51"):
        st.pydeck_chart(
            deck,
            height=700,
            width='stretch'
        )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader(
        "Migration Service Facilities"
    )

    display_cols = [
        c for c in [
            "Name",
            "Category",
            "District",
            "Address"
        ]
        if c in mig.columns
    ]

    with st.container(border=True, key="qcd-chart-52"):
        st.dataframe(
            mig[display_cols],
            width="stretch"
        )

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
        migration resource centers, and Quezon City
        Action Offices on a single map — optionally overlaid
        with land-surface temperature, vegetation, or flood
        exposure layers.
        """
    )

    # --------------------------------------------------
    # SERVICE CONFIGURATION
    # --------------------------------------------------

    service_layers = {

        "Childcare Centers": {
            "df": childcare_centers,
            "color": "#4C1D95",
            "symbol": "●",
            "source": "Childcare Center",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Schools": {
            "df": schools,
            "color": "#055B52",
            "symbol": "■",
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
            "symbol": "★",
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
            "symbol": "◆",
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
            "symbol": "▲",
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
            "symbol": "⬢",
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
            "symbol": "✦",
            "source": "Migration Resource Center",
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

    cols = st.columns(7)

    for i, (layer_name, layer) in enumerate(service_layers.items()):

        cols[i].markdown(
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
            "path": "processed/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
            "colormap": "YlOrRd",
            "binary": False
        },
        "Vegetation (NDVI)": {
            "path": "processed/climate/ndvi_mean_2025_EPSG3123.tif",
            "colormap": "Greens",
            "binary": False
        },
        "Flood Inundation (100-yr)": {
            "path": "processed/climate/flood_inundation_binary_gt30cm_EPSG3123.tif",
            "colormap": "Blues",
            "binary": True
        }
    }

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    col1, col2 = st.columns([2, 1])

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

    selected_climate_layers = st.multiselect(
        "Climate & Hazard Layers (optional)",
        list(climate_overlay_layers.keys()),
        default=[],
        help=(
            "Overlay land-surface temperature, vegetation, or "
            "flood extent under the service markers above. See "
            "the Climate, Hazard and Population Analysis page "
            "for a closer look at each layer individually."
        )
    )

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    map_html, climate_legend_info = build_explorer_map(
        tuple(selected_layers),
        selected_district,
        tuple(selected_climate_layers),
        False,
        show_risk_rings=False
    )

    st.iframe(
        map_html,
        height=850,
        width="stretch"
    )

    # --------------------------------------------------
    # CLIMATE LAYER LEGEND(S)
    # (folium's rendered HTML is opaque to Streamlit, so any
    # continuous-scale climate layer overlaid above gets its
    # color-scale legend rendered here instead, just below the
    # map. Binary layers like Flood Inundation aren't included
    # here — they're a flooded/not-flooded mask, not a scale.)
    # --------------------------------------------------

    if climate_legend_info:

        legend_cols = st.columns(len(climate_legend_info))

        legend_units = {
            "Land-Surface Temperature": "°C",
            "Vegetation (NDVI)": ""
        }

        for col, (layer_name, (layer_vmin, layer_vmax)) in zip(
            legend_cols,
            climate_legend_info.items()
        ):

            with col:

                st.markdown(
                    render_colormap_legend_html(
                        climate_overlay_layers[layer_name]["colormap"],
                        layer_vmin,
                        layer_vmax,
                        unit=legend_units.get(layer_name, ""),
                        label=layer_name
                    ),
                    unsafe_allow_html=True
                )

    st.divider()

    # --------------------------------------------------
    # SUPPLY-SIDE FLOOD EXPOSURE SUMMARY
    # (counts, across the *currently selected* service layers
    # and district, how many facilities sit inside the 100-yr
    # flood footprint — see flag_facilities_at_risk in
    # functions.py. The map above no longer offers an at-risk-
    # only filter or red rings on this page — see the Care
    # Services Explorer tab inside Climate, Hazard and
    # Population Analysis for that view — but this summary
    # stays here since it's a useful count regardless of how
    # the map is displayed.)
    # --------------------------------------------------

    st.markdown("### Facilities at Risk of Flooding")

    st.caption(
        """
        Facilities whose location falls inside the 100-year
        flood inundation footprint (>30cm depth), among the
        service layers and district currently selected above.
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
                fig_exposure,
                width="stretch"
            )

        with st.container(border=True, key="qcd-chart-54"):
            st.dataframe(
                exposure_df,
                width="stretch"
            )


elif page == "Accessibility Analysis":
    import geopandas as gpd

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
    # FACILITY-PER-1,000 RATIO INDICATORS
    # (shared with the Accessibility Map page — see
    # ACCESSIBILITY_RATIO_INDICATORS in functions.py)
    # ==================================================

    ratio_indicators = ACCESSIBILITY_RATIO_INDICATORS

    selected_ratio_label = st.selectbox(
        "Select Accessibility Ratio",
        list(ratio_indicators.keys())
    )

    selected_ratio = ratio_indicators[selected_ratio_label]

    tab1, tab2 = st.tabs(
        [
            "District Analysis",
            "Barangay Analysis"
        ]
    )


    with tab1:
        st.markdown("""
        This section examines the spatial distribution of care-related
        services across Quezon City and identifies districts where
        population needs may exceed available infrastructure.
        """)

        # ==================================================
        # DISTRICT AGGREGATION (from demographics.csv)
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
        # SELECTED RATIO (recomputed at district level —
        # per-1,000 ratios don't average correctly across
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
        # OVERALL ACCESSIBILITY INDEX (all facility types,
        # from demographics.csv's Total facility column)
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

        min_score = (
            district_access["Facilities per 10k Population"]
            .min()
        )

        max_score = (
            district_access["Facilities per 10k Population"]
            .max()
        )

        district_access["Accessibility Index"] = (
            (
                district_access["Facilities per 10k Population"]
                - min_score
            )
            /
            (
                max_score
                - min_score
            )
        ) * 100

        district_access = district_access.round(2)

        access = district_access

        # ==================================================
        # KPI CARDS
        # ==================================================

        avg_score = round(
            access["Accessibility Index"].mean(),
            1
        )

        best_district = int(
            access.loc[
                access["Accessibility Index"].idxmax(),
                "District"
            ]
        )

        worst_district = int(
            access.loc[
                access["Accessibility Index"].idxmin(),
                "District"
            ]
        )

        total_facilities = int(
            access["Facilities"].sum()
        )

        c1, c2, c3, c4 = st.columns(4)

        kpi_card(
            c1,
            "Accessibility Index",
            avg_score,
            "up_good"
        )

        kpi_card(
            c2,
            "Total Facilities",
            f"{total_facilities:,}",
            "up_good"
        )

        kpi_card(
            c3,
            "Best Served District",
            best_district
        )

        kpi_card(
            c4,
            "Priority District",
            worst_district
        )

        st.divider()

        # ==================================================
        # DISTRICT GEOMETRY
        # ==================================================

        district_geo = gpd.read_file(
            "processed/qc_districts.geojson"
        )

        district_geo["district"] = (
            district_geo["district"]
            .astype(str)
            .str.extract(r"(\d+)")[0]
            .astype(int)
        )

        district_geo = district_geo.rename(
            columns={"district": "District"}
        )

        district_geo = district_geo.merge(
            access[
                [
                    "District",
                    "Accessibility Index",
                    "Facilities",
                    "Total",
                    "Facilities per 10k Population",
                    "Care Demand per Facility",
                    selected_ratio_label
                ]
            ],
            on="District",
            how="left"
        )

        # ==================================================
        # MAP — driven by the selected facility-specific ratio
        # ==================================================

        st.subheader(
            f"District Map — {selected_ratio_label}"
        )

        st.caption(
            "Darker = lower ratio = fewer facilities of this "
            "type relative to the population they serve "
            "(more underserved)."
        )

        # ------------------------------------------
        # Color ramp (PuRd-style) for the selected ratio
        # ------------------------------------------

        def purd_color(value, vmin, vmax):

            if pd.isna(value) or vmax == vmin:
                return [217, 217, 217, 120]

            t = (value - vmin) / (vmax - vmin)
            t = min(max(t, 0), 1)

            # Inverted so darker shading marks the *lower* end of
            # the ratio (fewer facilities per capita = more
            # underserved), matching the "darker = underserved"
            # convention used elsewhere in this dashboard (e.g.
            # the Priority Investment Map) rather than "darker =
            # better served".
            t = 1 - t

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

                    return [int(r), int(g), int(b), 200]

            return [103, 0, 31, 200]

        ratio_min = district_geo[selected_ratio_label].min()
        ratio_max = district_geo[selected_ratio_label].max()

        district_geo["fill_color"] = district_geo[selected_ratio_label].apply(
            lambda v: purd_color(v, ratio_min, ratio_max)
        )

        district_geojson = json.loads(
            district_geo.to_json()
        )

        # ------------------------------------------
        # District label points (centroids)
        # ------------------------------------------

        district_labels = district_geo.copy()

        # Reproject to a metric CRS before computing centroids —
        # centroids computed directly on geographic (lat/lon)
        # coordinates can be skewed for irregular polygons, since
        # degrees of longitude aren't constant-width distances.
        # Same EPSG:32651 (UTM Zone 51N) convention used for the
        # area_km2 calculation on the Barangay Clusters page.
        district_labels_metric = district_labels.to_crs("EPSG:32651")
        district_centroids_metric = district_labels_metric.geometry.centroid

        district_centroids = (
            gpd.GeoSeries(district_centroids_metric, crs="EPSG:32651")
            .to_crs(district_labels.crs)
        )

        district_labels["lon"] = district_centroids.x
        district_labels["lat"] = district_centroids.y
        district_labels["label"] = (
            "District " + district_labels["District"].astype(str)
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
        # Barangay boundaries (background)
        # ------------------------------------------

        barangay_layer = pdk.Layer(
            "GeoJsonLayer",
            data=geo,
            stroked=True,
            filled=False,
            get_line_color=[136, 136, 136],
            line_width_min_pixels=0.5,
            pickable=False
        )

        # ------------------------------------------
        # District choropleth
        # ------------------------------------------

        district_layer = pdk.Layer(
            "GeoJsonLayer",
            data=district_geojson,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[55, 65, 81],
            line_width_min_pixels=2.5,
            pickable=True,
            auto_highlight=True
        )

        # ------------------------------------------
        # District labels
        # ------------------------------------------

        label_layer = pdk.Layer(
            "TextLayer",
            data=district_labels,
            get_position="[lon, lat]",
            get_text="label",
            get_size=14,
            get_color=[17, 24, 39],
            get_background_color=[255, 255, 255, 180],
            background=True,
            get_alignment_baseline=String("center"),
            pickable=False
        )

        # ------------------------------------------
        # TOOLTIP
        # ------------------------------------------

        tooltip = {
            "html": f"""
            <b>District {{District}}</b><br/>
            {selected_ratio_label}: {{{selected_ratio_label}}}<br/>
            Facilities (any type): {{Facilities}}<br/>
            Population: {{Total}}<br/>
            Accessibility Index: {{Accessibility Index}}
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
                barangay_layer,
                district_layer,
                label_layer
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-55"):
            st.pydeck_chart(
                deck,
                height=700,
                width='stretch'
            )

        st.divider()

        # ==================================================
        # CHARTS
        # ==================================================

        left, right = st.columns(2)

        with left:

            fig = px.bar(
                access.sort_values(
                    selected_ratio_label,
                    ascending=False
                ),
                x="District",
                y=selected_ratio_label,
                color=selected_ratio_label,
                # Reversed ("_r") so a lower ratio (fewer
                # facilities per capita = more underserved) gets
                # the darker shade, matching the "darker =
                # underserved" convention used on the rest of
                # this page rather than "darker = better served".
                color_continuous_scale="Purples_r",
                title=f"{selected_ratio_label} by District"
            )

            with st.container(border=True, key="qcd-chart-56"):
                st.plotly_chart(
                    fig,
                    width="stretch"
                )

        with right:

            fig = px.bar(
                access.sort_values(
                    "Accessibility Index",
                    ascending=False
                ),
                x="District",
                y="Accessibility Index",
                color="Accessibility Index",
                # Reversed for the same reason as the chart on
                # the left — a lower Accessibility Index means
                # more underserved, so it should read darker, not
                # lighter.
                color_continuous_scale="Purples_r",
                title="Overall Accessibility Index by District"
            )

            with st.container(border=True, key="qcd-chart-57"):
                st.plotly_chart(
                    fig,
                    width="stretch"
                )

        st.divider()

        # ==================================================
        # POPULATION VS FACILITIES
        # ==================================================

        fig = px.scatter(
            access,
            x="Relevant_Population",
            y="Facility_Type_Count",
            size="Facility_Type_Count",
            text="District",
            color=selected_ratio_label,
            # Reversed for the same "darker = underserved"
            # convention used on the rest of this page — a lower
            # ratio should read darker, not lighter.
            color_continuous_scale="Purples_r",
            title=f"Relevant Population vs Facilities — {selected_ratio_label}"
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
                fig,
                width="stretch"
            )

        st.divider()

        # ==================================================
        # PRIORITY DISTRICTS
        # ==================================================

        st.subheader(
            "Priority Districts for Future Investment"
        )

        st.caption(
            f"Ranked by lowest {selected_ratio_label}, then by "
            "lowest overall Accessibility Index."
        )

        priority = (
            access.sort_values(
                [
                    selected_ratio_label,
                    "Accessibility Index"
                ],
                ascending=[
                    True,
                    True
                ]
            )
            .head(5)
        )

        with st.container(border=True, key="qcd-chart-59"):
            st.dataframe(
                priority[
                    [
                        "District",
                        selected_ratio_label,
                        "Facilities",
                        "Total",
                        "Accessibility Index",
                        "Care Demand per Facility"
                    ]
                ],
                width="stretch"
            )

        st.divider()

        # ==================================================
        # FULL TABLE
        # ==================================================

        st.subheader(
            "District Accessibility Indicators"
        )

        with st.container(border=True, key="qcd-chart-60"):
            st.dataframe(
                access[
                    [
                        "District",
                        selected_ratio_label,
                        "Facilities",
                        "Total",
                        "Facilities per 10k Population",
                        "Accessibility Index",
                        "Care Demand per Facility"
                    ]
                ],
                width="stretch"
            )
 
    with tab2:

        st.subheader(
            f"Barangay-Level Accessibility — {selected_ratio_label}"
        )

        # ==================================================
        # BARANGAY DATA (from demographics.csv directly —
        # facility counts, population, and pre-computed
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
        # demographics.csv; pulled in directly rather than
        # recalculated, since barangay-level ratios don't
        # need re-aggregation the way district ones do)
        # ==================================================

        barangay_access[selected_ratio_label] = (
            barangay_access[selected_ratio["ratio_col"]]
        )

        # ==================================================
        # OVERALL ACCESSIBILITY INDEX (all facility types)
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

        min_score = (
            barangay_access[
                "Facilities per 10k Population"
            ].min()
        )

        max_score = (
            barangay_access[
                "Facilities per 10k Population"
            ].max()
        )

        barangay_access[
            "Accessibility Index"
        ] = (
            (
                barangay_access[
                    "Facilities per 10k Population"
                ]
                - min_score
            )
            /
            (
                max_score
                - min_score
            )
        ) * 100

        barangay_access = (
            barangay_access
            .round(2)
        )

        # ==================================================
        # KPI CARDS
        # ==================================================

        no_facilities = (
            barangay_access["Facilities"] == 0
        ).sum()

        avg_access = round(
            barangay_access[
                "Accessibility Index"
            ].mean(),
            1
        )

        top_barangay = (
            barangay_access.loc[
                barangay_access[
                    "Accessibility Index"
                ].idxmax(),
                "Barangay"
            ]
        )

        c1, c2, c3 = st.columns(3)

        kpi_card(
            c1,
            "Average Accessibility",
            avg_access,
            "up_good"
        )

        kpi_card(
            c2,
            "Barangays Without Facilities",
            int(no_facilities),
            "down_good"
        )

        kpi_card(
            c3,
            "Best Served Barangay",
            str(top_barangay)
        )

        st.divider()

        # ==================================================
        # BARANGAY MAP — driven by the selected ratio
        # ==================================================

        barangay_geo = gpd.read_file(
            "processed/qc_barangays.geojson"
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
                    "Accessibility Index",
                    selected_ratio_label
                ]
            ],
            left_on="barangay_name",
            right_on="Barangay_key",
            how="left"
        )

        st.subheader(
            f"Barangay Map — {selected_ratio_label}"
        )

        st.caption(
            "Darker = lower ratio = fewer facilities of this "
            "type relative to the population they serve "
            "(more underserved)."
        )

        def purd_color(value, vmin, vmax):

            if pd.isna(value) or vmax == vmin:
                return [217, 217, 217, 120]

            t = (value - vmin) / (vmax - vmin)
            t = min(max(t, 0), 1)

            # Inverted so darker shading marks the *lower* end of
            # the ratio (fewer facilities per capita = more
            # underserved), matching the "darker = underserved"
            # convention used elsewhere in this dashboard (e.g.
            # the Priority Investment Map) rather than "darker =
            # better served".
            t = 1 - t

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

                    return [int(r), int(g), int(b), 215]

            return [103, 0, 31, 215]

        ratio_min = barangay_geo[selected_ratio_label].min()
        ratio_max = barangay_geo[selected_ratio_label].max()

        barangay_geo["fill_color"] = barangay_geo[selected_ratio_label].apply(
            lambda v: purd_color(v, ratio_min, ratio_max)
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

        # ------------------------------------------
        # TOOLTIP
        # ------------------------------------------

        tooltip = {
            "html": f"""
            <b>{{Barangay}}</b><br/>
            {selected_ratio_label}: {{{selected_ratio_label}}}<br/>
            Facilities (any type): {{Facilities}}<br/>
            Population: {{Total}}<br/>
            Accessibility Index: {{Accessibility Index}}
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
                barangay_choropleth_layer
            ],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-61"):
            st.pydeck_chart(
                deck,
                height=750,
                width='stretch'
            )

        st.divider()

        # ==================================================
        # MOST UNDERSERVED BARANGAYS (by the selected ratio)
        # ==================================================

        underserved = (
            barangay_access
            .dropna(subset=[selected_ratio_label])
            .sort_values(
                selected_ratio_label
            )
            .head(20)
        )

        fig = px.bar(
            underserved,
            x=selected_ratio_label,
            y="Barangay",
            orientation="h",
            color=selected_ratio_label,
            # Reversed ("_r") so the lowest ratio in this
            # already-worst-20 subset — the most underserved
            # barangay — gets the darkest red, matching the
            # "darker = underserved" convention used elsewhere on
            # this page, instead of the default where the least-
            # bad barangay in the list would appear darkest.
            color_continuous_scale="Reds_r",
            title=f"Most Underserved Barangays — {selected_ratio_label}"
        )

        with st.container(border=True, key="qcd-chart-62"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

        # ==================================================
        # POPULATION VS FACILITIES
        # ==================================================

        fig = px.scatter(
            barangay_access,
            x="Total",
            y="Facilities",
            size="Facilities",
            hover_name="Barangay",
            color="Accessibility Index",
            # Reversed for the same "darker = underserved"
            # convention used on the rest of this page — a lower
            # Accessibility Index should read darker, not lighter.
            color_continuous_scale="Purples_r",
            title="Population vs Facilities (All Types)"
        )

        with st.container(border=True, key="qcd-chart-63"):
            st.plotly_chart(
                fig,
                width="stretch"
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
            "the most people)."
        )

        priority_barangays = (
            barangay_access
            .dropna(subset=[selected_ratio_label])
            .sort_values(
                [
                    selected_ratio_label,
                    "Total"
                ],
                ascending=[
                    True,
                    False
                ]
            )
            .head(25)
        )

        with st.container(border=True, key="qcd-chart-64"):
            st.dataframe(
                priority_barangays[
                    [
                        "Barangay",
                        "District",
                        "Total",
                        "Facilities",
                        selected_ratio_label,
                        "Accessibility Index"
                    ]
                ],
                width="stretch"
            )

        st.divider()

        # ==================================================
        # FULL TABLE
        # ==================================================

        st.subheader(
            "Barangay Accessibility Indicators"
        )

        with st.container(border=True, key="qcd-chart-65"):
            st.dataframe(
                barangay_access[
                    [
                        "Barangay",
                        "District",
                        "Total",
                        "Facilities",
                        selected_ratio_label,
                        "Facilities per 10k Population",
                        "Accessibility Index",
                        "Care Demand per Facility"
                    ]
                ],
                width="stretch"
            )

elif page == "Care Planning & Investment Priorities":

    import geopandas as gpd

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
    # BARANGAY DATA (from demographics.csv — facility
    # counts by type, age/sex population, and PWD/senior
    # registrations are all already at barangay level, so
    # no merge against care_v3.csv or population_age is
    # needed for this page anymore)
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
    # SERVICE DIVERSITY
    # (count of distinct facility types present — Childcare,
    # Health centers, Long-term care and rehabilitation
    # services, Older persons care, Action Offices, Schools,
    # Trainings — mirrors the old major_division.nunique()
    # from care_v3.csv, since these are the same seven
    # categories)
    # ==================================================

    facility_type_cols = [
        "Childcare",
        "Health centers",
        "Long-term care and rehabilitation services",
        "Older persons care",
        "Quezon City satellite offices for services",
        "Schools",
        "Trainings"
    ]

    barangay_access["Service Diversity"] = (
        (barangay_access[facility_type_cols] > 0)
        .sum(axis=1)
    )

    # ==================================================
    # CARE DEMAND
    # ==================================================

    barangay_access["Care Demand"] = (
        barangay_access["age_0_5"]
        +
        barangay_access["age_60plus"]
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
    # CHILDREN / ELDERLY PER FACILITY
    # (split out from the combined "Care Demand" figure —
    # useful to see whether a barangay's gap is specifically
    # in childcare/school capacity or in elder care capacity.
    # Computed directly from demographics.csv's per-type
    # facility columns rather than via
    # compute_population_per_facility(), which needed a
    # major_division column from care_v3.csv that no longer
    # backs this page.)
    # ==================================================

    barangay_access["Child-Serving Facilities"] = (
        barangay_access["Childcare"]
        +
        barangay_access["Schools"]
    )

    barangay_access["Elderly-Serving Facilities"] = (
        barangay_access["Older persons care"]
        +
        barangay_access["Long-term care and rehabilitation services"]
    )

    barangay_access["Children per Facility"] = np.where(
        barangay_access["Child-Serving Facilities"] != 0,
        barangay_access["age_0_5"]
        / barangay_access["Child-Serving Facilities"],
        np.nan
    )

    barangay_access["Elderly per Facility"] = np.where(
        barangay_access["Elderly-Serving Facilities"] != 0,
        barangay_access["age_60plus"]
        / barangay_access["Elderly-Serving Facilities"],
        np.nan
    )

    # ==================================================
    # RANKS
    # ==================================================

    barangay_access["Population Rank"] = (
        barangay_access["Total"]
        .rank(
            ascending=False
        )
    )

    barangay_access["Demand Rank"] = (
        barangay_access["Care Demand"]
        .rank(
            ascending=False
        )
    )

    barangay_access["Facility Rank"] = (
        barangay_access["Facilities"]
        .rank(
            ascending=True
        )
    )

    barangay_access["Diversity Rank"] = (
        barangay_access["Service Diversity"]
        .rank(
            ascending=True
        )
    )

    # ==================================================
    # PRIORITY SCORE
    # ==================================================

    # Each *_Rank column above uses rank 1 = "worst off" on that
    # metric (rank(ascending=False) for Population/Demand puts
    # the largest value at rank 1; rank(ascending=True) for
    # Facilities/Diversity puts the smallest value, e.g. 0
    # facilities, at rank 1). Summing those raw ranks directly
    # would mean LOWER totals (rank 1 across the board) score
    # LOWEST after the /max*100 step below — the opposite of
    # "higher score = higher priority." Inverting each rank
    # first (n_barangays + 1 - rank) makes "worst off" contribute
    # the most, so the final score correctly increases with need.
    n_barangays = len(barangay_access)

    barangay_access["Priority Score"] = (
        (n_barangays + 1 - barangay_access["Population Rank"]) * 0.35
        +
        (n_barangays + 1 - barangay_access["Demand Rank"]) * 0.35
        +
        (n_barangays + 1 - barangay_access["Facility Rank"]) * 0.20
        +
        (n_barangays + 1 - barangay_access["Diversity Rank"]) * 0.10
    )

    max_score = (
        barangay_access["Priority Score"]
        .max()
    )

    barangay_access["Priority Score"] = (
        barangay_access["Priority Score"]
        /
        max_score
        * 100
    )

    barangay_access = (
        barangay_access
        .sort_values(
            "Priority Score",
            ascending=False
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

        kpi_card(
            st,
            "Care Desert Barangays",
            int(
                (
                    barangay_access["Facilities"] == 0
                ).sum()
            ),
            "down_good"
        )

    with col3:

        kpi_card(
            st,
            "Highest Priority Barangay",
            barangay_access.iloc[0]["Barangay"]
        )

    with col4:

        kpi_card(
            st,
            "Average Priority Score",
            round(
                barangay_access[
                    "Priority Score"
                ].mean(),
                1
            )
        )

    st.divider()

    # ==================================================
    # MAP
    # ==================================================

    barangay_geo = gpd.read_file(
        "processed/qc_barangays.geojson"
    )

    # Normalize join keys defensively — both sides must
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

    def purd_color(value, vmin, vmax):

        if pd.isna(value) or vmax == vmin:
            return [204, 204, 204, 100]

        t = (value - vmin) / (vmax - vmin)
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

    # Colors must be computed from the numeric "Priority Score"
    # BEFORE that column gets overwritten with the "No data"
    # placeholder string below.
    score_min = priority_map["Priority Score"].min()
    score_max = priority_map["Priority Score"].max()

    priority_map["fill_color"] = priority_map["Priority Score"].apply(
        lambda v: purd_color(v, score_min, score_max)
    )

    tooltip_fields = [
        "Barangay",
        "Facilities",
        "Care Demand",
        "Service Diversity",
        "Priority Score"
    ]

    # "Barangay" comes from the right side of the left-merge above,
    # so it's NaN for any polygon with no matching row in
    # barangay_access (e.g. Damar, Reservoir — barangays with no
    # care_v3 records at all). "barangay_name" comes from the
    # geometry itself and is always populated, so use it as the
    # display name whenever "Barangay" is missing.
    priority_map["Barangay"] = (
        priority_map["Barangay"]
        .fillna(priority_map["barangay_name"])
    )

    # Round numeric fields and substitute a clear placeholder
    # for missing values so the tooltip never shows blank.
    for col in ["Facilities", "Care Demand", "Service Diversity", "Priority Score"]:
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
        Care Demand: {Care Demand}<br/>
        Service Diversity: {Service Diversity}<br/>
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
            priority_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"
    )

    with st.container(border=True, key="qcd-chart-66"):
        st.pydeck_chart(
            deck,
            height=750,
            width='stretch'
        )

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
                    "Service Diversity",
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
        title="Highest Priority Barangays",
        color_continuous_scale=QCD_SEQUENTIAL
    )

    fig.update_layout(
        height=700
    )

    with st.container(border=True, key="qcd-chart-68"):
        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.divider()

    # ==================================================
    # CARE DESERTS
    # ==================================================

    st.subheader(
        "Care Desert Barangays"
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
    Barangays classified as care deserts currently have
    no registered care facilities in the inventory.
    These areas may require additional assessment to
    identify service gaps and potential investment needs.
    """)

    kpi_card(
        st,
        "Care Desert Barangays",
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
    # PRIORITY DRIVERS
    # ==================================================

    st.subheader(
        "What Drives Priority Scores?"
    )

    driver_col1, driver_col2 = st.columns(2)

    with driver_col1:

        fig = px.scatter(
            barangay_access,
            x="Care Demand",
            y="Priority Score",
            hover_name="Barangay",
            title="Care Demand vs Priority Score",
            color="Priority Score",
            color_continuous_scale=QCD_SEQUENTIAL
        )

        with st.container(border=True, key="qcd-chart-70"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    with driver_col2:

        fig = px.scatter(
            barangay_access,
            x="Facilities",
            y="Priority Score",
            hover_name="Barangay",
            title="Facilities vs Priority Score",
            color="Priority Score",
            color_continuous_scale=QCD_SEQUENTIAL
        )

        with st.container(border=True, key="qcd-chart-71"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    st.divider()

    # ==================================================
    # SERVICE DIVERSITY
    # ==================================================

    st.subheader(
        "Service Diversity by Barangay"
    )

    diversity_top = (
        barangay_access
        .sort_values(
            "Service Diversity",
            ascending=False
        )
        .head(20)
    )

    fig = px.bar(
        diversity_top,
        x="Service Diversity",
        y="Barangay",
        orientation="h",
        color="Service Diversity",
        title="Barangays with the Most Diverse Care Services",
        color_continuous_scale=QCD_SEQUENTIAL
    )

    fig.update_layout(
        height=700
    )

    with st.container(border=True, key="qcd-chart-72"):
        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.divider()

    # ==================================================
    # CHILDREN / ELDERLY PER FACILITY
    # ==================================================

    st.subheader(
        "Children & Elderly Demand per Facility"
    )

    st.markdown("""
    "Care Demand" above combines young children and
    older persons into a single figure. The indicators
    below separate the two groups, dividing each
    population by the number of facilities that
    specifically serve it (Childcare + Schools for
    children; Older Persons Care + Long-Term Care for
    the elderly). This shows whether a barangay's gap
    is concentrated in childcare/school capacity,
    elder care capacity, or both.
    """)

    cpf_col1, cpf_col2, cpf_col3, cpf_col4 = st.columns(4)

    with cpf_col1:

        kpi_card(
            st,
            "Median Children per Facility",
            f"{barangay_access['Children per Facility'].median():,.0f}",
            "down_good"
        )

    with cpf_col2:

        kpi_card(
            st,
            "Median Elderly per Facility",
            f"{barangay_access['Elderly per Facility'].median():,.0f}",
            "down_good"
        )

    with cpf_col3:

        kpi_card(
            st,
            "Barangays with No Child-Serving Facility",
            int((barangay_access["Child-Serving Facilities"] == 0).sum()),
            "down_good"
        )

    with cpf_col4:

        kpi_card(
            st,
            "Barangays with No Elderly-Serving Facility",
            int((barangay_access["Elderly-Serving Facilities"] == 0).sum()),
            "down_good"
        )

    cpf_left, cpf_right = st.columns(2)

    with cpf_left:

        top_children = (
            barangay_access
            .dropna(subset=["Children per Facility"])
            .sort_values("Children per Facility", ascending=False)
            .head(15)
        )

        fig = px.bar(
            top_children,
            x="Children per Facility",
            y="Barangay",
            orientation="h",
            color="Children per Facility",
            color_continuous_scale="Purples",
            title="Highest Children per Facility (0-5 yrs)"
        )

        fig.update_layout(height=550)

        with st.container(border=True, key="qcd-chart-73"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    with cpf_right:

        top_elderly = (
            barangay_access
            .dropna(subset=["Elderly per Facility"])
            .sort_values("Elderly per Facility", ascending=False)
            .head(15)
        )

        fig = px.bar(
            top_elderly,
            x="Elderly per Facility",
            y="Barangay",
            orientation="h",
            color="Elderly per Facility",
            color_continuous_scale="Purples",
            title="Highest Senior Citizens per Facility (60+ yrs)"
        )

        fig.update_layout(height=550)

        with st.container(border=True, key="qcd-chart-74"):
            st.plotly_chart(
                fig,
                width="stretch"
            )

    with st.container(border=True, key="qcd-chart-75"):
        st.dataframe(
            barangay_access[
                [
                    "Barangay",
                    "District",
                    "age_0_5",
                    "Child-Serving Facilities",
                    "Children per Facility",
                    "age_60plus",
                    "Elderly-Serving Facilities",
                    "Elderly per Facility"
                ]
            ].rename(
                columns={
                    "age_0_5": "Children (0-5)",
                    "age_60plus": "Older Persons (60+)"
                }
            ).sort_values("Children per Facility", ascending=False),
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

    import geopandas as gpd
    import plotly.graph_objects as go

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

    st.markdown("""
    This page groups barangays into clusters that share
    similar demographic, accessibility, and socio-economic
    profiles — adapted from the project's clustering
    methodology (K-means on standardized indicators).
    Clustering helps surface neighborhoods that face
    comparable pressures (e.g. dense and young vs. sparse
    and older, well-served vs. underserved, or higher vs.
    lower deprivation) so that interventions can be
    tailored by *type* of barangay rather than one at a
    time.

    **Features used:**
    - **Demographic** — population density, share of
      children (0–17), share of older persons (60+), sex
      ratio (males per 100 females)
    - **Accessibility** — facilities of any kind per 10,000
      residents, plus the mix of facility types present
      locally (share that are Childcare, Health centers,
      Long-Term Care & Rehabilitation, or Schools — the
      four types common enough across barangays to carry
      real signal)
    - **Socio-economic** — disability prevalence rate, food
      insecurity prevalence, housing inadequacy index
      (all from the 2024 CBMS), and registered migrant
      workers per 1,000 residents
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
            "60+ (Elderly)"
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
        "60+ (Elderly)",
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
        "processed/qc_barangays.geojson"
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

    k1, k2, k3 = st.columns(3)

    kpi_card(
        k1,
        "Barangays Clustered",
        int(clustered["barangay_name"].notna().sum())
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
            cluster_layer
        ],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"
    )

    legend_items = "".join(
        f"""
        <span style="color:{cluster_color(c)};font-size:18px;">●</span>
        Cluster {c}&nbsp;&nbsp;
        """
        for c in sorted(clustered["Cluster"].dropna().unique())
    )

    st.markdown(legend_items, unsafe_allow_html=True)

    with st.container(border=True, key="qcd-chart-76"):
        st.pydeck_chart(
            deck,
            height=700,
            width="stretch"
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
    values are below average) — the same "wind rose"
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

            fig.update_layout(
                title=f"Cluster {int(cid)} ({int(cluster_sizes.set_index('Cluster').loc[int(cid), 'Barangays'])} barangays)",
                showlegend=False,
                height=400
            )

            with st.container(border=True, key=f"qcd-chart-77-{int(cid)}"):
                st.plotly_chart(
                    fig,
                    width="stretch"
                )

    st.divider()

    # ==================================================
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
            "elderly_pct": "Avg. Elderly Share (%)",
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
                    "elderly_pct": "Elderly Share (%)",
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

elif page == "Climate, Hazard and Population Analysis":


    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Climate, Hazard and Population Analysis
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        """
        Which segments of the population are most at risk, and
        where. The Vulnerability Index tab below combines
        barangay-level flood exposure with one vulnerable
        population group you choose, into a single Climate
        Vulnerability Index — the demand-side counterpart to
        the facility-level flood flagging on the Care Services
        Explorer tab. Further down this page, city-wide
        flood-risk figures by population group and the
        interactive climate/hazard raster layers (heat,
        vegetation, flood) are also available.
        """
    )


    tab1, tab2 = st.tabs([
        "Vulnerability Index",
        "Services, Climate & Hazard Explorer"
    ])

    with tab1:

        # --------------------------------------------------
        # SELECTABLE VULNERABLE GROUPS
        # (each entry maps a dropdown label to a real column in
        # demographics.csv. "rate_col" is what actually goes into
        # the index — already a rate/share, not a raw count, so
        # combining groups doesn't just reward populous barangays.
        # Raw-count columns (e.g. age_60plus, age_0_5) are
        # deliberately not offered directly for this reason; where
        # demographics.csv didn't already have a per-1,000 or %
        # version of a group, one is derived on the fly below from
        # the raw count and pop_census instead of being precomputed
        # here, since that derivation is a single line either way.
        # --------------------------------------------------

        VULNERABILITY_GROUPS = {
            "Seniors (registered, per 1,000)": {
                "rate_col": "seniors_per_1000_census",
                "derive": None
            },
            "Seniors (census 60+, % of population)": {
                "rate_col": "_pct_age_60plus",
                "derive": ("age_60plus", "pop_census")
            },
            "Oldest old (80+, % of population)": {
                "rate_col": "_pct_age_80plus",
                "derive": ("age_80plus", "pop_census")
            },
            "Registered PWDs (per 1,000)": {
                "rate_col": "pwd_per_1000_census",
                "derive": None
            },
            "Disability prevalence (% of population)": {
                "rate_col": "disability_prevalence_rate_pct",
                "derive": None
            },
            "Young children (0-5, % of population)": {
                "rate_col": "_pct_age_0_5",
                "derive": ("age_0_5", "pop_census")
            },
            "Food insecurity (CBMS, %)": {
                "rate_col": "cbms_food_insecurity_prevalence_pct",
                "derive": None
            },
            "Severe food insecurity (CBMS, %)": {
                "rate_col": "cbms_food_severe_wholeday_pct",
                "derive": None
            },
            "Housing inadequacy (CBMS, %)": {
                "rate_col": "cbms_housing_inadequacy_index_pct",
                "derive": None
            },
            "Severe housing deprivation (CBMS, %)": {
                "rate_col": "cbms_housing_makeshift_severe_pct",
                "derive": None
            },
            "Migrant worker households (per 1,000)": {
                "rate_col": "_per1000_migrant_workers",
                "derive": ("migrant_workers_total", "pop_census")
            }
        }

        selected_group = st.selectbox(
            "Vulnerable population group to combine with flood "
            "exposure",
            list(VULNERABILITY_GROUPS.keys()),
            index=0,
            help=(
                "The index is an equal-weighted average of flood "
                "exposure and this one group, so a high score has "
                "one clear explanation: high flood exposure, a "
                "high concentration of this group, or both — "
                "rather than several groups blended into a single "
                "number you'd have to unpack."
            )
        )

        selected_groups = [selected_group]

        try:

            # ==================================================
            # BARANGAY FLOOD EXPOSURE (AREA-BASED)
            # ==================================================

            flood_exposure = compute_barangay_flood_exposure()

            flood_exposure["barangay_key"] = (
                flood_exposure["barangay_name"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            vuln_barangay = demographics.copy()

            vuln_barangay["barangay_key"] = (
                vuln_barangay["barangay"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            vuln_barangay = vuln_barangay.merge(
                flood_exposure[
                    ["barangay_key", "flood_area_pct"]
                ],
                on="barangay_key",
                how="left"
            )

            # --------------------------------------------------
            # ESTIMATED POPULATION EXPOSED
            # (area% x pop_census — uniform-density assumption;
            # see compute_barangay_flood_exposure's docstring.
            # Repeated as a visible caption below, not just here
            # in code, since it reads like a precise headcount
            # if seen on its own.)
            # --------------------------------------------------

            vuln_barangay["est_population_exposed"] = (
                vuln_barangay["pop_census"]
                * vuln_barangay["flood_area_pct"]
                / 100
            )

            # --------------------------------------------------
            # DERIVE ANY ON-THE-FLY RATE COLUMNS
            # (only for groups the user actually selected, so
            # an unused derive doesn't risk a divide-by-zero or
            # NaN column nobody asked for)
            # --------------------------------------------------

            for label in selected_groups:

                group = VULNERABILITY_GROUPS[label]

                if group["derive"] is not None:

                    count_col, denom_col = group["derive"]

                    vuln_barangay[group["rate_col"]] = (
                        vuln_barangay[count_col]
                        / vuln_barangay[denom_col]
                        * 1000
                    )

            # --------------------------------------------------
            # VULNERABILITY INDEX
            # (flood area% rescaled 0-100, averaged with the one
            # selected group's rate — also rescaled 0-100 — so
            # both components contribute equally regardless of
            # their raw units, and the index updates live as the
            # group selection changes above. Simple, transparent
            # average of exactly two components (not a weighted/
            # PCA-based index of many), so a high score always has
            # one clear explanation: "this barangay scores high
            # because of high flood exposure, a high concentration
            # of the selected group, or both" — not a blended
            # number that needs unpacking to interpret.)
            # --------------------------------------------------

            def rescale_0_100(series):

                min_v = series.min()
                max_v = series.max()

                if (
                    pd.isna(min_v)
                    or pd.isna(max_v)
                    or max_v == min_v
                ):
                    return pd.Series(0, index=series.index)

                return (
                    (series - min_v)
                    / (max_v - min_v)
                    * 100
                )

            score_cols = ["exposure_score"]

            vuln_barangay["exposure_score"] = rescale_0_100(
                vuln_barangay["flood_area_pct"]
            )

            for label in selected_groups:

                group = VULNERABILITY_GROUPS[label]
                score_col = f"score__{group['rate_col']}"

                vuln_barangay[score_col] = rescale_0_100(
                    vuln_barangay[group["rate_col"]]
                )

                score_cols.append(score_col)

            vuln_barangay["vulnerability_index"] = (
                vuln_barangay[score_cols].sum(
                    axis=1,
                    skipna=False
                )
                / len(score_cols)
            )

            st.caption(
                "⚠ \"Estimated population exposed\" assumes each "
                "barangay's population is spread evenly across "
                "its land area — a planning estimate, not a "
                "measured headcount. The Vulnerability Index is "
                "an equal-weighted average of flood exposure and "
                f"\"{selected_group}\", each rescaled 0-100; it is "
                "a relative ranking tool, not an absolute risk "
                "score."
            )

            # ==================================================
            # KPIs
            # ==================================================

            total_exposed_est = int(
                vuln_barangay["est_population_exposed"].sum()
            )

            top_exposed_barangay = (
                vuln_barangay
                .dropna(subset=["est_population_exposed"])
                .sort_values(
                    "est_population_exposed",
                    ascending=False
                )
                .iloc[0]
            )

            top_vulnerable_barangay = (
                vuln_barangay
                .dropna(subset=["vulnerability_index"])
                .sort_values(
                    "vulnerability_index",
                    ascending=False
                )
                .iloc[0]
            )

            v1, v2, v3 = st.columns(3)

            kpi_card(
                v1,
                "Est. Citywide Population Exposed",
                f"{total_exposed_est:,}",
                "down_good"
            )

            kpi_card(
                v2,
                "Most Exposed Barangay",
                str(top_exposed_barangay["barangay"]),
                caption=f"{top_exposed_barangay['est_population_exposed']:,.0f} est. residents"
            )

            kpi_card(
                v3,
                "Most Vulnerable Barangay",
                str(top_vulnerable_barangay["barangay"]),
                caption=f"Index: {top_vulnerable_barangay['vulnerability_index']:.0f}/100"
            )

            st.divider()

            # ==================================================
            # CHOROPLETH MAP
            # ==================================================

            barangay_geo_vuln = gpd.read_file(
                "processed/qc_barangays.geojson",
                engine="pyogrio"
            )

            barangay_geo_vuln["barangay_name"] = (
                barangay_geo_vuln["barangay_name"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            merge_cols = (
                [
                    "barangay_key",
                    "barangay",
                    "flood_area_pct",
                    "est_population_exposed",
                    "vulnerability_index"
                ]
                + [
                    VULNERABILITY_GROUPS[label]["rate_col"]
                    for label in selected_groups
                ]
            )

            barangay_geo_vuln = barangay_geo_vuln.merge(
                vuln_barangay[merge_cols],
                left_on="barangay_name",
                right_on="barangay_key",
                how="left"
            )

            def reds_color(value, vmin, vmax):

                if pd.isna(value) or vmax == vmin:
                    return [217, 217, 217, 120]

                t = (value - vmin) / (vmax - vmin)
                t = min(max(t, 0), 1)

                stops = [
                    (0.00, (255, 245, 240)),
                    (0.25, (252, 187, 161)),
                    (0.50, (252, 146, 114)),
                    (0.75, (222, 45, 38)),
                    (1.00, (103, 0, 13))
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

                        return [int(r), int(g), int(b), 215]

                return [103, 0, 13, 215]

            metric_min = barangay_geo_vuln["vulnerability_index"].min()
            metric_max = barangay_geo_vuln["vulnerability_index"].max()

            barangay_geo_vuln["fill_color"] = (
                barangay_geo_vuln["vulnerability_index"]
                .apply(
                    lambda v: reds_color(v, metric_min, metric_max)
                )
            )

            vuln_choropleth_geojson = json.loads(
                barangay_geo_vuln.to_json()
            )

            vuln_view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=11,
                pitch=0,
                min_zoom=11,
                max_zoom=17,
            )

            vuln_choropleth_layer = pdk.Layer(
                "GeoJsonLayer",
                data=vuln_choropleth_geojson,
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color=[120, 120, 120, 150],
                line_width_min_pixels=0.6,
                pickable=True,
                auto_highlight=True
            )

            group_tooltip_lines = "<br/>".join(
                f"{label}: {{{VULNERABILITY_GROUPS[label]['rate_col']}}}"
                for label in selected_groups
            )

            vuln_tooltip = {
                "html": f"""
                <b>{{barangay}}</b><br/>
                Vulnerability Index: {{vulnerability_index}}<br/>
                Flood Area: {{flood_area_pct}}%<br/>
                {group_tooltip_lines}
                """,
                "style": {
                    "backgroundColor": "white",
                    "color": "black",
                    "fontSize": "12px"
                }
            }

            vuln_deck = pdk.Deck(
                layers=[vuln_choropleth_layer],
                initial_view_state=vuln_view_state,
                tooltip=vuln_tooltip,
                map_style="light"
            )

            with st.container(border=True, key="qcd-chart-80"):
                st.pydeck_chart(
                    vuln_deck,
                    height=700,
                    width="stretch"
                )

            st.caption(
                "Darker red = higher Climate Vulnerability Index."
            )

            st.divider()

            # ==================================================
            # TOP 15 BARANGAYS BY VULNERABILITY INDEX
            # ==================================================

            top15 = (
                vuln_barangay
                .dropna(subset=["vulnerability_index"])
                .sort_values("vulnerability_index", ascending=False)
                .head(15)
            )

            fig_vuln = px.bar(
                top15,
                x="vulnerability_index",
                y="barangay",
                orientation="h",
                color="vulnerability_index",
                color_continuous_scale="Reds",
                title="Top 15 Barangays — Climate Vulnerability Index"
            )

            fig_vuln.update_layout(
                yaxis_title="",
                xaxis_title="Vulnerability Index (0-100)",
                yaxis=dict(autorange="reversed")
            )

            with st.container(border=True, key="qcd-chart-81"):
                st.plotly_chart(
                    fig_vuln,
                    width="stretch"
                )

            with st.expander(
                "Full barangay table (exposure & vulnerability)"
            ):

                display_cols = (
                    [
                        "barangay",
                        "district",
                        "pop_census",
                        "flood_area_pct",
                        "est_population_exposed"
                    ]
                    + [
                        VULNERABILITY_GROUPS[label]["rate_col"]
                        for label in selected_groups
                    ]
                    + ["vulnerability_index"]
                )

                rename_map = {
                    "barangay": "Barangay",
                    "district": "District",
                    "pop_census": "Population (Census)",
                    "flood_area_pct": "Flood Area (%)",
                    "est_population_exposed":
                        "Est. Population Exposed",
                    "vulnerability_index":
                        "Vulnerability Index (0-100)"
                }

                for label in selected_groups:
                    rename_map[
                        VULNERABILITY_GROUPS[label]["rate_col"]
                    ] = label

                with st.container(border=True, key="qcd-chart-82"):
                    st.dataframe(
                        vuln_barangay[display_cols]
                        .rename(columns=rename_map)
                        .round(1)
                        .sort_values(
                            "Vulnerability Index (0-100)",
                            ascending=False
                        ),
                        width="stretch"
                    )

        except Exception as e:

            st.error(
                f"Could not build the vulnerability index: {e}. "
                "Check that processed/qc_barangays.geojson and "
                "the flood raster both exist and share "
                "overlapping coverage."
            )

    with tab2:

        st.markdown(
            """
            <h3 style="
                color:#7F47ED;
                font-size:1.6rem;
                margin-top:-10px;
                margin-bottom:10px;
                padding-top:0px;
            ">
                Services, Climate & Hazard Explorer
            </h3>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            """
            Same map and flood-exposure filtering as the Care
            Services Explorer page, shown here alongside the
            population vulnerability view so supply (facilities)
            and demand (at-risk population) can be compared
            side by side without leaving this page.
            """
        )

        # --------------------------------------------------
        # SERVICE CONFIGURATION
        # --------------------------------------------------

        service_layers = {

            "Childcare Centers": {
                "df": childcare_centers,
                "color": "#4C1D95",
                "symbol": "●",
                "source": "Childcare Center",
                "name_col": "Name",
                "district_col": "District",
                "address_col": "Address",
                "lat_col": "latitude",
                "lon_col": "longitude"
            },

            "Schools": {
                "df": schools,
                "color": "#055B52",
                "symbol": "■",
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
                "symbol": "★",
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
                "symbol": "◆",
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
                "symbol": "▲",
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
                "symbol": "⬢",
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
                "symbol": "✦",
                "source": "Migration Resource Center",
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

        cols = st.columns(7)

        for i, (layer_name, layer) in enumerate(service_layers.items()):

            cols[i].markdown(
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
                "path": "processed/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
                "colormap": "YlOrRd",
                "binary": False
            },
            "Vegetation (NDVI)": {
                "path": "processed/climate/ndvi_mean_2025_EPSG3123.tif",
                "colormap": "Greens",
                "binary": False
            },
            "Flood Inundation (100-yr)": {
                "path": "processed/climate/flood_inundation_binary_gt30cm_EPSG3123.tif",
                "colormap": "Blues",
                "binary": True
            }
        }

        # --------------------------------------------------
        # FILTERS
        # --------------------------------------------------

        col1, col2 = st.columns([2, 1])

        with col1:

            selected_layers = st.multiselect(
                "Services to Display",
                list(service_layers.keys()),
                default=list(service_layers.keys())[:3],
                key="popvuln_explorer_services"
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
                list(district_options.keys()),
                key="popvuln_explorer_district"
            )

            selected_district = district_options[
                selected_district_label
            ]

        selected_climate_layers = st.multiselect(
            "Climate & Hazard Layers (optional)",
            list(climate_overlay_layers.keys()),
            default=[],
            help=(
                "Overlay land-surface temperature, vegetation, or "
                "flood extent under the service markers above. See "
                "the Climate, Hazard and Population Analysis "
                "section further down this page for a closer look "
                "at each layer individually."
            ),
            key="popvuln_explorer_climate_layers"
        )

        flood_risk_only = st.checkbox(
            "⚠ Show only facilities at risk of flooding",
            value=False,
            help=(
                "Filters the map to facilities whose location falls "
                "inside the 100-year flood inundation footprint "
                "(>30cm depth). Flood-risk status for each facility "
                "is still noted in its popup; for a visual flood-risk "
                "map with ringed markers, see the main Care Services "
                "Explorer page."
            ),
            key="popvuln_explorer_flood_only"
        )

        # --------------------------------------------------
        # MAP DISPLAY
        # --------------------------------------------------

        map_html, climate_legend_info = build_explorer_map(
            tuple(selected_layers),
            selected_district,
            tuple(selected_climate_layers),
            flood_risk_only,
            show_risk_rings=True
        )

        st.iframe(
            map_html,
            height=850,
            width="stretch"
        )

        # --------------------------------------------------
        # CLIMATE LAYER LEGEND(S)
        # (folium's rendered HTML is opaque to Streamlit, so any
        # continuous-scale climate layer overlaid above gets its
        # color-scale legend rendered here instead, just below the
        # map. Binary layers like Flood Inundation aren't included
        # here — they're a flooded/not-flooded mask, not a scale.)
        # --------------------------------------------------

        if climate_legend_info:

            legend_cols = st.columns(len(climate_legend_info))

            legend_units = {
                "Land-Surface Temperature": "°C",
                "Vegetation (NDVI)": ""
            }

            for col, (layer_name, (layer_vmin, layer_vmax)) in zip(
                legend_cols,
                climate_legend_info.items()
            ):

                with col:

                    st.markdown(
                        render_colormap_legend_html(
                            climate_overlay_layers[layer_name]["colormap"],
                            layer_vmin,
                            layer_vmax,
                            unit=legend_units.get(layer_name, ""),
                            label=layer_name
                        ),
                        unsafe_allow_html=True
                    )

        st.divider()

        # --------------------------------------------------
        # SUPPLY-SIDE FLOOD EXPOSURE SUMMARY
        # (counts, across the *currently selected* service layers
        # and district, how many facilities sit inside the 100-yr
        # flood footprint — see flag_facilities_at_risk in
        # functions.py. Independent of flood_risk_only: shown
        # whether or not the map is currently filtered to at-risk
        # facilities only, so the counts are visible even when
        # browsing the full set of markers.)
        # --------------------------------------------------

        st.markdown("### Facilities at Risk of Flooding")

        st.caption(
            """
            Facilities whose location falls inside the 100-year
            flood inundation footprint (>30cm depth), among the
            service layers and district currently selected above.
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

            with st.container(border=True, key="qcd-chart-83"):
                st.plotly_chart(
                    fig_exposure,
                    width="stretch"
                )

            with st.container(border=True, key="qcd-chart-84"):
                st.dataframe(
                    exposure_df,
                    width="stretch"
                )




    st.divider()

    # =====================================================
    # CLIMATE & HAZARD LAYERS
    # (moved here from the former standalone "Climate &
    # Hazard Exposure" page — merged in since both pages
    # covered overlapping ground: flood exposure and which
    # population groups/areas are most affected. This
    # section is the city-wide / raster-layer view; the
    # Vulnerability Index tab above is the barangay-level
    # view.)
    # =====================================================

    st.subheader("Climate & Hazard Layers")

    st.caption(
        """
        Explore climate and hazard layers for Quezon City one at
        a time: land-surface temperature, vegetation cover, and
        100-year flood inundation. Select a layer below.
        """
    )

    # --------------------------------------------------
    # CITY-WIDE FLOOD RISK CONTEXT (WorldPop)
    # --------------------------------------------------

    st.subheader(
        "Citywide Flood Risk by Population Group (WorldPop)"
    )

    st.warning(
        "**Preliminary — pending verification.** These "
        "flood-risk estimates are still being reviewed "
        "and have not yet been confirmed."
    )

    st.markdown("""
    These figures come from a separate WorldPop-based
    analysis estimating what share of each population group lives inside the
    high flood-risk zone shown in the "Flood Inundation
    (100-yr)" layer below. Groups covered: total population,
    by sex, children (0-4), and elderly (60+) — each also
    split by sex.

    **This is city-wide only — there is no barangay or
    district breakdown for these specific figures.** They
    can't be added to the barangay/district maps elsewhere
    in this dashboard, or to the Care Planning Priority
    Score, until a barangay-level version of this analysis
    exists (see the note in Care Planning & Investment
    Priorities for what that would require).

    Every population group shows almost exactly the same
    ~25% flood-risk share — including children (0-4), added
    in the most recent update to this dataset. This isn't a
    coincidence in the data — WorldPop's age/sex breakdowns
    are built by applying the same demographic ratios across
    the population grid, so each subgroup inherits nearly the
    same spatial distribution as the total population, and
    therefore nearly the same exposure rate.
    """)

    # Official indicator names from indicators_codebook.csv —
    # the "(2020, constrained)" qualifier refers to WorldPop's
    # constrained population product (population restricted to
    # known built-up areas) for the total/female/male rows;
    # the elderly rows don't carry that qualifier in the
    # codebook, so it's intentionally omitted for those three.
    climate_label_map = {
        "Total Population under High Flood Risk (%)":
            "Total Population (2020, constrained) "
            "under High Flood Risk (%)",
        "Female Population under High Flood Risk (%)":
            "Female Population (2020, constrained) "
            "under High Flood Risk (%)",
        "Male Population under High Flood Risk (%)":
            "Male Population (2020, constrained) "
            "under High Flood Risk (%)",
        "Children (0-4) under High Flood Risk (%)":
            "Children (0-4) under High Flood Risk (%)",
        "Female Children (0-4) under High Flood Risk (%)":
            "Female Children (0-4) under High Flood Risk (%)",
        "Male Children (0-4) under High Flood Risk (%)":
            "Male Children (0-4) under High Flood Risk (%)",
        "Seniors (60+) under High Flood Risk (%)":
            "Seniors Population (60+) under High Flood Risk (%)",
        "Female Seniors(60+) under High Flood Risk (%)":
            "Female Seniors (60+) under High Flood Risk (%)",
        "Male Seniors (60+) under High Flood Risk (%)":
            "Male Seniors (60+) under High Flood Risk (%)"
    }

    climate_context_display = climate_context.copy()

    climate_context_display["Indicator"] = (
        climate_context_display["Indicator"]
        .map(climate_label_map)
        .fillna(climate_context_display["Indicator"])
    )

    flood_total = climate_context[
        climate_context["Indicator"]
        == "Total Population under High Flood Risk (%)"
    ].iloc[0]

    fc1, fc2, fc3 = st.columns(3)

    kpi_card(
        fc1,
        "Total Population in High Flood Risk Zone",
        f"{flood_total['Population in Flood Zone']:,.0f}",
        "down_good"
    )

    kpi_card(
        fc2,
        "Share of Citywide Population",
        f"{flood_total['% under flood risk']:.1f}%",
        "down_good"
    )

    kpi_card(
        fc3,
        "Total Population (WorldPop)",
        f"{flood_total['Total (WorldPop)']:,.0f}"
    )

    st.divider()

    flood_chart_df = climate_context_display.copy()

    flood_chart_df["Population Group"] = (
        flood_chart_df["Indicator"]
        .str.replace(
            " under High Flood Risk (%)",
            "",
            regex=False
        )
        .str.replace(
            " (2020, constrained)",
            "",
            regex=False
        )
        
    )

    fig = px.bar(
        flood_chart_df.sort_values(
            "Population in Flood Zone",
            ascending=False
        ),
        x="Population Group",
        y="Population in Flood Zone",
        color="% under flood risk",
        color_continuous_scale="Blues",
        title="Population in High Flood Risk Zone, by Group"
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Population in Flood Zone"
    )

    with st.container(border=True, key="qcd-chart-85"):
        st.plotly_chart(
            fig,
            width="stretch"
        )

    with st.container(border=True, key="qcd-chart-86"):
        st.dataframe(
            climate_context_display.rename(
                columns={
                    "Total (WorldPop)": "Total Population",
                    "Population in Flood Zone":
                        "Population in High Flood Risk Zone",
                    "% under flood risk": "% Under Flood Risk"
                }
            ),
            width="stretch"
        )

    st.divider()

    # --------------------------------------------------
    # LAYER CONFIGURATION
    # --------------------------------------------------

    climate_layers = {
        "Land-Surface Temperature": {
            "path": "processed/climate/landsat_lst_summer_avg_7yr_EPSG3123_filled.tif",
            "colormap": "YlOrRd",
            "binary": False,
            "unit": "°C",
            "legend_label": "Land-Surface Temperature (°C)",
            "description": (
                "7-year summer average land-surface temperature, "
                "derived from Landsat thermal imagery (~30m "
                "resolution). Higher values indicate stronger "
                "urban heat — typically dense, paved, low-vegetation "
                "areas. Color scale is clipped to the 2nd-98th "
                "percentile to avoid a handful of extreme pixels "
                "flattening the rest of the map."
            )
        },
        "Vegetation (NDVI)": {
            "path": "processed/climate/ndvi_mean_2025_EPSG3123.tif",
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
        },
        "Flood Inundation (100-yr)": {
            "path": "processed/climate/flood_inundation_binary_gt30cm_EPSG3123.tif",
            "colormap": "Blues",
            "binary": True,
            "unit": "flooded / not flooded",
            "legend_label": "Flood depth > 30cm (100-year rain event)",
            "description": (
                "Binary flood extent (~10m resolution) showing "
                "areas expected to see more than 30cm of inundation "
                "depth in a 100-year rainfall event. This is a mask, "
                "not a depth map — for full depth classes (0.2-0.5m, "
                "0.5-1.5m, 1.5-3m, >3m), see the static reference map "
                "below."
            )
        }
    }

    if "climate_layer" not in st.session_state:
        st.session_state.climate_layer = "Land-Surface Temperature"

    # --------------------------------------------------
    # LAYER TOGGLE BUTTONS
    # --------------------------------------------------

    toggle_cols = st.columns(len(climate_layers))

    for i, layer_name in enumerate(climate_layers.keys()):

        is_active = (
            st.session_state.climate_layer == layer_name
        )

        if toggle_cols[i].button(
            layer_name,
            width="stretch",
            type="primary" if is_active else "secondary"
        ):
            st.session_state.climate_layer = layer_name
            st.rerun()

    st.divider()

    active_layer_name = st.session_state.climate_layer
    active_layer = climate_layers[active_layer_name]

    st.subheader(active_layer_name)
    st.caption(active_layer["description"])

    # --------------------------------------------------
    # RENDER ACTIVE RASTER LAYER
    # --------------------------------------------------

    try:

        qc_boundary = load_qc_boundary()

        png_data_uri, bounds_corners, vmin, vmax = raster_to_bitmap_layer(
            active_layer["path"],
            colormap=active_layer["colormap"],
            binary=active_layer["binary"],
            _mask_geometry=qc_boundary
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            min_zoom=9,
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
        # is already the 4-corner format BitmapLayer expects —
        # see raster_to_bitmap_layer's docstring in functions.py.
        bitmap_layer = pdk.Layer(
            "BitmapLayer",
            image=png_data_uri,
            bounds=bounds_corners,
            opacity=1.0
        )

        deck = pdk.Deck(
            layers=[
                bitmap_layer,
                boundary_layer
            ],
            initial_view_state=view_state,
            map_style="light"
        )

        with st.container(border=True, key="qcd-chart-87"):
            st.pydeck_chart(
                deck,
                height=700,
                width="stretch"
            )

        if active_layer["binary"]:

            st.caption(
                f"Legend: {active_layer['legend_label']} — "
                "shaded areas indicate flooding, unshaded areas "
                "do not."
            )

        else:

            st.markdown(
                render_colormap_legend_html(
                    active_layer["colormap"],
                    vmin,
                    vmax,
                    unit=active_layer["unit"],
                    label=active_layer["legend_label"]
                ),
                unsafe_allow_html=True
            )

            st.caption(
                "Color scale is clipped to the 2nd-98th percentile "
                "of this layer's data, to avoid a handful of "
                "extreme pixels flattening the rest of the map."
            )

    except Exception as e:

        st.error(
            f"Could not render this layer: {e}. "
            "Check that rasterio and pyproj are installed, and "
            f"that the file exists at `{active_layer['path']}`."
        )

    st.divider()

    # --------------------------------------------------
    # STATIC REFERENCE MAPS
    # --------------------------------------------------

    with st.expander("Static reference maps (full legend detail)"):

        st.markdown("""
        These are the original, fully-styled reference maps used
        to produce the layers above. The flood map in particular
        shows depth classes that the binary mask above doesn't
        capture (0.2-0.5m, 0.5-1.5m, 1.5-3m, more than 3m).
        """)

        ref_col1, ref_col2 = st.columns(2)

        with ref_col1:
            st.image(
                "processed/climate/Flood_QC.png",
                caption="100-year rain flood map in Quezon City",
                width="stretch"
            )

        with ref_col2:
            st.image(
                "processed/climate/Heatwaves.png",
                caption="Land-surface temperature reference map",
                width="stretch"
            )
