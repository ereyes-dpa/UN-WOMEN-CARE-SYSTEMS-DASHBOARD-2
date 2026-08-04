import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import numpy as np
from functions import *
import pydeck as pdk
import geopandas as gpd

# PUBLIC VERSION

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Quezon Caring City Dashboard",
    layout="wide"
)

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
) = load_data()

geo, bounds = load_geo()

# --------------------------------------------------
# FLAG FACILITIES AT FLOOD RISK
# --------------------------------------------------

childcare_centers   = flag_facilities_at_risk(childcare_centers)
schools             = flag_facilities_at_risk(schools)
health_centers      = flag_facilities_at_risk(health_centers)
older_person_care   = flag_facilities_at_risk(older_person_care)
long_term_care      = flag_facilities_at_risk(long_term_care)
action_offices      = flag_facilities_at_risk(action_offices)
migration_centers   = flag_facilities_at_risk(migration_centers)

# --------------------------------------------------
# BARANGAY AND DISTRICT MAPS
# --------------------------------------------------

barangay_map = gpd.read_file(
    "processed/qc_barangays.geojson"
)

district_map = gpd.read_file(
    "processed/qc_districts.geojson"
)

# --------------------------------------------------
# POPULATION DATA
# (only the citywide total is used on this public build —
# for the Home page's headline stat badge — since the
# detailed barangay-level demographic breakdown lives on
# Population Overview, which isn't part of this version.)
# --------------------------------------------------

population_summary, population_sex, population_age = load_data_for_kpis()

# --------------------------------------------------
# BARANGAY AND DISTRICT DATAFRAMES (for KPIs and charts)
# --------------------------------------------------

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
    selected_district
):
    """
    Builds the full Care Services Explorer folium map and
    returns its rendered HTML string.

    Cached on (selected_layers, selected_district) only — the
    only two things that actually change what's drawn. Streamlit
    reruns this whole script on every widget interaction, which
    would otherwise rebuild every marker on the map from scratch
    each time even when nothing relevant changed. Caching the
    finished map means a rerun that doesn't change either
    argument returns the previously-built HTML immediately
    instead of reconstructing and re-serializing the whole map.

    Returns HTML (via m._repr_html_()) rather than the live
    folium.Map object so the cached value is a plain, easily
    hashable/picklable string. Render with st.iframe(...), not
    st_folium (st_folium's return value isn't used on this page,
    so the iframe-based render avoids that component's extra
    per-rerun overhead).
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
            "color": "#4472C4",
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

            folium.Marker(
                location=[
                    row_dict[layer["lat_col"]],
                    row_dict[layer["lon_col"]]
                ],
                icon=folium.DivIcon(
                    html=f"""
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
                    """
                ),
                tooltip=str(
                    row_dict[layer["name_col"]]
                ),
                popup=folium.Popup(
                    popup_html,
                    max_width=350,
                    lazy=True
                )
            ).add_to(m)

    return m._repr_html_()

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

    # School category options (school types)
    category_options = [
        "All",
        "Preschool",
        "Elementary school",
        "High school",
        "Senior high school"
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
        <span style="color:#2E5090;font-size:22px;">■</span>
        <b>Preschool</b><br>
        <span style="color:#4472C4;font-size:22px;">■</span>
        <b>Elementary school</b><br>
        <span style="color:#6B8FD4;font-size:22px;">■</span>
        <b>Junior high school</b><br>
        <span style="color:#8FA8E0;font-size:22px;">■</span>
        <b>Senior high school</b><br>
        <span style="color:#B5CBEE;font-size:22px;">■</span>
        <b>High school</b>
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
                    Public reference for Quezon City's
                    care-service network — childcare, schools,
                    health centers, older persons' facilities,
                    long-term care, action offices, and
                    migration resource centers.
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
    # QUICK STATS (KPI CARDS)
    # =====================================================

    total_barangays = 142
    total_districts = len(district_pop)

    k1, k2, k3 = st.columns(3)

    kpi_card(
        k1,
        "Total Population",
        f"{citywide_population:,.0f}",
        caption="residents citywide"
    )

    kpi_card(
        k2,
        "Total Barangays",
        f"{total_barangays:,}",
        caption="administrative divisions"
    )

    kpi_card(
        k3,
        "Total Districts",
        f"{total_districts}",
        caption="geographic areas"
    )

    st.divider()

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
                "Use the sidebar to open a care-service map, "
                "or the Care Services Explorer to see several "
                "service types on one map."
            ),
            (
                "Filter",
                "Each map offers filters above it — by "
                "provider type, district, or category."
            ),
            (
                "Find",
                "Click any marker on a map for the facility's "
                "name, address, and hours."
            )
        ]

        for step_title, step_body in nav_steps:

            st.markdown(
                f"""
                <div class="qcd-card" style="border: 1px solid #e0e0e0; border-radius: 8px;">
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

        st.markdown(
            """
            <div class="qcd-card-accent" style="border: 1px solid #e0e0e0; border-left: 4px solid #055B52; border-radius: 8px;">
                <div class="qcd-card-title">Care Services</div>
                <p class="qcd-card-body">
                    Childcare centers, schools, health centers,
                    older persons' facilities, long-term care
                    and rehabilitation, action offices, and
                    migration resource centers — each on its
                    own map under "Care Maps" in the sidebar.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="qcd-card-accent" style="border: 1px solid #e0e0e0; border-left: 4px solid #7F47ED; border-radius: 8px;">
                <div class="qcd-card-title">
                    Care Services Explorer
                </div>
                <p class="qcd-card-body">
                    See several service types together on a
                    single map, filterable by service and
                    district — useful for comparing coverage
                    across facility types in one place.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

elif page == "Childcare Centers":

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

    st.pydeck_chart(
        deck,
        height=700,
        width='stretch'
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

    st.pydeck_chart(
        deck,
        height=700,
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

    st.pydeck_chart(
        deck,
        height=700,
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

    st.pydeck_chart(
        deck,
        height=700,
        width='stretch'
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

    st.pydeck_chart(
        deck,
        height=700,
        width='stretch' 
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
    Explore the distribution of Quezon City
    Action offices providing local access
    to government services. 
                
    The District Action Offices serve as the City Hall’s extension, where people can raise all their concerns and grievances for proper and immediate action. They are tasked to extend maximum service to the greater number of people and to engage the active participation of the private sector.            
    """)

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

    st.pydeck_chart(
        deck,
        height=700,
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

    st.pydeck_chart(
        deck,
        height=700,
        width='stretch'
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
        migration resource centers, bus stops, and Quezon City
        Action offices on a single map.
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
            "color": "#4472C4",
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

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    map_html = build_explorer_map(
        tuple(selected_layers),
        selected_district
    )

    st.iframe(
        map_html,
        height=850,
        width="stretch"
    )
