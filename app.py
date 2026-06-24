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

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOGOS ROW
# --------------------------------------------------

fcdo_logo = get_base64("assets/fcdo_logo.png")
un_logo   = get_base64("assets/unwomen_logo.png")
qc_logo   = get_base64("assets/qc_logo.png")

QC_HEIGHT   = 60
FCDO_HEIGHT = 60
UN_HEIGHT   = 40

left_col, spacer_col, right_col = st.columns([1, 3, 3])

# QC Logo (left)
with left_col:

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            height:80px;
        ">
            <a href="https://quezoncity.gov.ph/" target="_blank">
                <img src="data:image/png;base64,{qc_logo}"
                     style="height:{QC_HEIGHT}px; width:auto;
                    transform: translateY(14px);
        ">
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
            height:80px;
        ">
            <a href="https://www.gov.uk/government/organisations/foreign-commonwealth-development-office"
               target="_blank">
                <img src="data:image/webp;base64,{fcdo_logo}"
                     style="
                        height:{FCDO_HEIGHT}px;
                        width:auto;
                        transform: translateY(8px);
                     ">
            </a>
            <a href="https://www.unwomen.org/en"
               target="_blank">
                <img src="data:image/png;base64,{un_logo}"
                     style="
                        height:{UN_HEIGHT}px;
                        width:auto;
                     ">
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
    satellite_offices,
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
    st.session_state.page = "Population Overview"


@st.cache_data(show_spinner="Building map...")
def build_explorer_map(
    selected_layers,
    selected_district,
    selected_climate_layers
):
    """
    Builds the full Care Services Explorer folium map and
    returns its rendered HTML string.

    Cached on (selected_layers, selected_district,
    selected_climate_layers) only — these are the only things
    that actually change what's drawn. Streamlit reruns this
    whole script on every widget interaction, which would
    otherwise rebuild the map (re-encode every raster overlay to
    PNG, rebuild every marker) from scratch each time even though
    the underlying data and raster renders are already cached
    individually. Caching the finished map means a rerun that
    doesn't change any of these three arguments returns the
    previously-built HTML immediately instead of reconstructing
    and re-serializing the whole map.

    Returns HTML (via m._repr_html_()) rather than the live
    folium.Map object so the cached value is a plain, easily
    hashable/picklable string — st_folium can render a Map object
    directly, but caching the HTML avoids any ambiguity about
    whether a cached Map object's internal state could be
    accidentally mutated by a caller between cache hits.
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
            "color": "#5B21B6",
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
            "color": "#7F47ED",
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
            "color": "#8B5CF6",
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
            "color": "#A78BFA",
            "symbol": "▲",
            "source": "Rehabilitation Facility",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Action Offices": {
            "df": satellite_offices,
            "color": "#DDD6FE",
            "symbol": "⬢",
            "source": "Satellite Office",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Migration Resource Centers": {
            "df": migration_centers,
            "color": "#C084FC",
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
            "fillColor": "#7fbf7f",
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.10,
        }
    ).add_to(m)

    # ------------------------------------------
    # CLIMATE OVERLAYS
    # ------------------------------------------

    if selected_climate_layers:

        qc_boundary_explorer = load_qc_boundary()

        for climate_layer_name in selected_climate_layers:

            climate_layer = climate_overlay_layers[climate_layer_name]

            try:

                rgba, folium_bounds, _, _ = raster_to_image_overlay(
                    climate_layer["path"],
                    colormap=climate_layer["colormap"],
                    binary=climate_layer["binary"],
                    _mask_geometry=qc_boundary_explorer
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
                marker_color_value = "#C084FC"

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

selected_childcare_sector = "All"
selected_childcare_category = "All"

selected_school_sector = "All"
selected_school_category = "All"

selected_opc_category = "All"

selected_ltc_category = "All"

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")
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

    selected_childcare_sector = st.sidebar.radio(
        "Provider Type",
        [
            "All",
            "Public",
            "Private"
        ],
        key="childcare_sector"
    )

    if selected_childcare_sector == "Public":

        category_options = [
            "All",
            "Child Development Center"
        ]

    elif selected_childcare_sector == "Private":

        category_options = [
            "All",
            "Child Learning Center",
            "Day Care Center"
        ]

    else:

        category_options = [
            "All",
            "Child Development Center",
            "Child Learning Center",
            "Day Care Center"
        ]

    selected_childcare_category = st.sidebar.radio(
        "Facility Category",
        category_options,
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
# SATELLITE OFFICES
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
    "Climate & Hazard Exposure",
    width='stretch'
):
    st.session_state.page = "Climate & Hazard Exposure"
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
        <span style="color:#5B21B6;font-size:22px;">●</span>
        <b>Child Development Center</b><br>
        <span style="color:#7F47ED;font-size:22px;">●</span>
        <b>Child Learning Center</b><br>
        <span style="color:#A78BFA;font-size:22px;">●</span>
        <b>Day Care Center</b>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Schools")

    st.sidebar.markdown(
        """
        <span style="color:#5B21B6;font-size:22px;">■</span>
        <b>Public School</b><br>
        <span style="color:#A78BFA;font-size:22px;">■</span>
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
        <span style="color:#4C1D95;font-size:22px;">◆</span>
        <b>Nursing Care Center</b><br>
        <span style="color:#A78BFA;font-size:22px;">◆</span>
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
        <span style="color:#7F47ED;font-size:22px;">⬢</span>
        <b>District Offices</b>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Migration Services")

    st.sidebar.markdown(
        """
        <span style="color:#C084FC;font-size:22px;">✦</span>
        <b>Migration Resource Center</b>
        """,
        unsafe_allow_html=True
    )    

# --------------------------------------------------
# PAGES
# --------------------------------------------------

 
# --------------------------------------------------
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

    dependency_ratio = (
        (
            early_childhood
            + school_age
            + elderly
        )
        / working_age
        * 100
    )

    sex_ratio_overall = (
        total_male
        / total_female
        * 100
    )

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    c1.metric(
        "Population",
        f"{total_population:,.0f}"
    )

    c2.metric(
        "0-5",
        f"{early_childhood:,.0f}"
    )

    c3.metric(
        "6-17",
        f"{school_age:,.0f}"
    )

    c4.metric(
        "18-59",
        f"{working_age:,.0f}"
    )

    c5.metric(
        "60+",
        f"{elderly:,.0f}"
    )

    c6.metric(
        "Dependency Ratio",
        f"{dependency_ratio:.1f}"
    )

    c7.metric(
        "Sex Ratio (M/F)",
        f"{sex_ratio_overall:.1f}"
    )

    st.divider()

    st.info(
        "📍 **Land Use layer pending.** A land use/zoning indicator "
        "(e.g., % residential, % open space per barangay) is planned "
        "for this page once Quezon City government shares the data, "
        "or a public Geoportal Philippines alternative is confirmed. "
        "See Notebooks 1–2 for status.",
        icon="ℹ️"
    )

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

        barangay_df["dependency_ratio"] = (
            (
                barangay_df["children_0_17"]
                +
                barangay_df["elderly"]
            )
            /
            barangay_df["working_age"]
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
        # to visualize spatially (dropped care_demand_index,
        # dependency_ratio and sex_ratio from the MAP since
        # they read better as ranked bar charts below)
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

        fig = px.choropleth_map(
            barangay_df,
            geojson=barangay_df.geometry.__geo_interface__,
            locations=barangay_df.index,
            color=selected_col,
            hover_name="Barangay",
            hover_data={
                selected_col: ":,.0f",
                "District": True
            },
            center={
                "lat": 14.676,
                "lon": 121.043
            },
            zoom=11,
            opacity=0.75,
            color_continuous_scale="Purples"
        )

        fig.update_coloraxes(
            cmin=barangay_df[selected_col].quantile(0.05),
            cmax=barangay_df[selected_col].quantile(0.95)
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=650
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.divider()

        # ---------------------------------------------------
        # TOP / BOTTOM BARANGAYS — DEPENDENCY RATIO
        # ---------------------------------------------------

        st.subheader("Dependency Ratio by Barangay")

        col_dep1, col_dep2 = st.columns(2)

        top_dep = (
            barangay_df[["Barangay", "District", "dependency_ratio"]]
            .dropna()
            .sort_values("dependency_ratio", ascending=False)
            .head(10)
        )

        bottom_dep = (
            barangay_df[["Barangay", "District", "dependency_ratio"]]
            .dropna()
            .sort_values("dependency_ratio", ascending=True)
            .head(10)
        )

        with col_dep1:
            fig_top_dep = px.bar(
                top_dep.sort_values("dependency_ratio"),
                x="dependency_ratio",
                y="Barangay",
                orientation="h",
                title="Top 10 — Highest Dependency Ratio",
                color_discrete_sequence=["#6A0DAD"]
            )
            fig_top_dep.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Dependency Ratio"
            )
            st.plotly_chart(fig_top_dep, width="stretch")

        with col_dep2:
            fig_bottom_dep = px.bar(
                bottom_dep.sort_values("dependency_ratio", ascending=False),
                x="dependency_ratio",
                y="Barangay",
                orientation="h",
                title="Top 10 — Lowest Dependency Ratio",
                color_discrete_sequence=["#B399D4"]
            )
            fig_bottom_dep.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Dependency Ratio"
            )
            st.plotly_chart(fig_bottom_dep, width="stretch")

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
                color_discrete_sequence=["#0D6A4A"]
            )
            fig_top_den.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Population Density"
            )
            st.plotly_chart(fig_top_den, width="stretch")

        with col_den2:
            fig_bottom_den = px.bar(
                bottom_den.sort_values("population_density", ascending=False),
                x="population_density",
                y="Barangay",
                orientation="h",
                title="Top 10 — Lowest Density (people/km²)",
                color_discrete_sequence=["#8FCBB3"]
            )
            fig_bottom_den.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Population Density"
            )
            st.plotly_chart(fig_bottom_den, width="stretch")

        st.divider()

        st.subheader(
            f"Top 15 Barangays by {indicator}"
        )

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

        district_pop["Dependency Ratio"] = (
            (
                district_pop[age_group_definition["children_0_17"]].sum(axis=1)
                + district_pop[age_group_definition["elderly_60_plus"]].sum(axis=1)
            )
            /
            district_pop[age_group_definition["working_age_18_59"]].sum(axis=1)
            * 100
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
                "Older Persons (60+)",
                "Dependency Ratio"
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
                "60+ (Elderly)",
            "Dependency Ratio":
                "Dependency Ratio"
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
                "senior care planning and health services.",
            "Dependency Ratio":
                "Children and older persons combined, divided by "
                "the working-age population (×100). Higher values "
                "mean more dependents per working-age resident."
        }

        st.caption(
            district_indicator_descriptions[district_indicator]
        )

        fig = px.choropleth_map(
            district_geo,
            geojson=district_geo.geometry.__geo_interface__,
            locations=district_geo.index,
            color=district_col,
            hover_name="District",
            hover_data={
                district_col: ":,.0f"
            },
            center={
                "lat": 14.676,
                "lon": 121.043
            },
            zoom=11,
            opacity=0.75,
            color_continuous_scale="Purples"
        )

        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),
            height=650
        )

        st.plotly_chart(
            fig,
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
            barmode="stack"
        )

        fig_age.update_layout(height=450)

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
                marker_color="#3B6FA0"
            )
        )

        fig_pyramid.add_trace(
            go.Bar(
                y=["Female"],
                x=[total_female],
                name="Female",
                orientation="h",
                marker_color="#C0567B"
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
            st.plotly_chart(fig_pyramid, width="stretch")

        with col_pyr2:
            fig_ratio = px.bar(
                district_pop.sort_values("Sex Ratio", ascending=False),
                x="District",
                y="Sex Ratio",
                title="Sex Ratio (M/F ×100) by District",
                color_discrete_sequence=["#3B6FA0"]
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

        st.dataframe(
            district_summary,
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
    including public Child Development Centers and private childcare providers.
    """)

    st.markdown(
        """
        <span style="color:#5B21B6;font-size:18px;">●</span>
        <b>Child Development Center</b> — For children aged 3–4 years and supports school readiness.<br>

        <span style="color:#7F47ED;font-size:18px;">●</span>
        <b>Child Learning Center</b> — Private childcare and early learning services.<br>

        <span style="color:#A78BFA;font-size:18px;">●</span>
        <b>Day Care Center</b> — Private day care and supervision services.
        """,
        unsafe_allow_html=True
    )

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

    public_centers = (
        childcare_centers["Sector"]
        .str.contains(
            "Public",
            case=False,
            na=False
        )
        .sum()
    )

    private_centers = (
        childcare_centers["Sector"]
        .str.contains(
            "Private",
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

    k1.metric(
        "Facilities",
        f"{total_facilities:,}"
    )

    k2.metric(
        "CDCs",
        f"{total_centers:,}"
    )

    k3.metric(
        "ECCD Enrollees",
        f"{eccd_enrollees:,}"
    )

    k4.metric(
        "Public",
        f"{public_centers:,}"
    )

    k5.metric(
        "Private",
        f"{private_centers:,}"
    )

    k6.metric(
        "Barangays Served",
        f"{covered_barangays:,}"
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

    if selected_childcare_sector != "All":

        cc = cc[
            cc["Sector"]
            .str.contains(
                selected_childcare_sector,
                case=False,
                na=False
            )
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

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.subheader("Facilities")

    st.dataframe(
        cc[
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
            title="Facilities by Category"
        )

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
            title="Facilities by District"
        )

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

    c1.metric(
        "Children (0-5)",
        f"{early_childhood_population:,.0f}"
    )

    c2.metric(
        "Children per CDC",
        f"{children_per_center:.0f}"
    )

    c3.metric(
        "ECCD Coverage",
        f"{enrollment_rate:.1f}%"
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

    st.markdown(
        """
        <span style="color:#5B21B6;">●</span>
        <b>Public School</b> — Government-operated educational institutions.<br>
        <span style="color:#A78BFA;">●</span>
        <b>Private School</b> — Privately operated educational institutions.
        """,
        unsafe_allow_html=True
    )

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

    k1.metric(
        "Total Schools",
        f"{total_schools:,}"
    )

    k2.metric(
        "Public",
        f"{public_schools:,}"
    )

    k3.metric(
        "Private",
        f"{private_schools:,}"
    )

    k4.metric(
        "Barangays Served",
        f"{covered_barangays:,}"
    )

    k5.metric(
        "Districts Served",
        f"{covered_districts:,}"
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

    c1.metric(
        "School-Age Population (6-17)",
        f"{school_age_population:,.0f}"
    )

    c2.metric(
        "Children per School",
        f"{children_per_school:,.0f}"
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

    st.pydeck_chart(
        deck,
        height=700,
        width='stretch'
    )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.subheader("Schools")

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

        category_counts = (
            schools["Category"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Schools"
        ]

        fig = px.pie(
            category_counts,
            names="Category",
            values="Schools",
            title="School Distribution"
        )

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
            title="Schools by District"
        )

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

    st.markdown(
        f"""
        <span style="color:{category_hex('QC LGU')};">●</span>
        <b>QC LGU</b> — Maternity and lying-in clinics for healthy pregnancies.<br>

        <span style="color:{category_hex('National')};">●</span>
        <b>National</b> — National government-owned hospitals.<br>

        <span style="color:{category_hex('Super Health')};">●</span>
        <b>Super Health</b> — Enhanced health centers with laboratory, dental, ambulance, breastfeeding, and lying-in services.<br>

        <span style="color:{category_hex('Health Center')};">●</span>
        <b>Health Center</b> — Community-based primary healthcare facilities.<br>

        <span style="color:{category_hex('Pharmacy')};">●</span>
        <b>Pharmacy</b> — Pharmacy services within health facilities.<br>

        <span style="color:{category_hex('Milk Bank')};">●</span>
        <b>Milk Bank</b> — Safe pasteurized human milk services for infants in need.
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # HEALTH KPIs
    # --------------------------------------------------

    health_capacity = pd.read_csv(
        "processed/health_centers_and_doctors_per_district.csv"
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

    k1.metric(
        "Facilities",
        f"{total_facilities:,}"
    )

    k2.metric(
        "Doctors",
        f"{int(total_doctors):,}"
    )

    k3.metric(
        "Health Centers",
        f"{health_centers_count:,}"
    )

    k4.metric(
        "Super Health",
        f"{super_health_centers:,}"
    )

    k5.metric(
        "Hospitals",
        f"{hospitals:,}"
    )

    k6.metric(
        "Pharmacies",
        f"{pharmacies:,}"
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

    c1.metric(
        "Population",
        f"{total_population:,.0f}"
    )

    c2.metric(
        "Population / Doctor",
        f"{population_per_doctor:,.0f}"
    )

    c3.metric(
        "Population / Health Center",
        f"{population_per_health_center:,.0f}"
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
        text_auto=True
    )

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
        title="Doctors vs Health Centers"
    )

    fig.update_traces(
        textposition="top center"
    )

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

    st.dataframe(
        coverage[
            [
                "District",
                "Total",
                "health_centers",
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
        title="Health Facility Composition"
    )

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

    st.markdown(
        """
        <span style="color:#4C1D95;">●</span>
        <b>Nursing Care Center</b> — Residential facilities providing long-term nursing and care services.<br>

        <span style="color:#A78BFA;">●</span>
        <b>Bahay Aruga</b> — Temporary residential facility for abandoned, neglected, abused, and indigent QC senior citizens aged 60 years and above.
        """,
        unsafe_allow_html=True
    )
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

    k1.metric(
        "Registered Seniors",
        f"{registered_seniors:,}"
    )

    k2.metric(
        "Female",
        f"{female_seniors:,}"
    )

    k3.metric(
        "Male",
        f"{male_seniors:,}"
    )

    k4.metric(
        "Age 60-79",
        f"{age_60_79:,}"
    )

    k5.metric(
        "Age 80+",
        f"{age_80_plus:,}"
    )

    k6.metric(
        "Care Facilities",
        f"{total_facilities:,}"
    )

    st.divider()


    seniors_per_facility = (
        registered_seniors
        / total_facilities
    )

    st.metric(
        "Registered Seniors per Care Facility",
        f"{seniors_per_facility:,.0f}"
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
            title="Senior Citizens by Sex"
        )

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
            title="Senior Citizens by Age Group"
        )

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
        title="Registered Senior Citizens Over Time"
    )

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
        title="Senior Citizens by District"
    )

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
        title="Older Persons Care Facility Types"
    )

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

    legend_html = ""

    for cat in ltc_categories:
        legend_html += (
            f'<span style="color:{ltc_color(cat)};">●</span> '
            f'<b>{cat}</b><br>'
        )

    st.markdown(
        legend_html,
        unsafe_allow_html=True
    )



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

    k1.metric(
        "Facilities",
        f"{total_facilities:,}"
    )

    k2.metric(
        "Service Types",
        f"{total_categories:,}"
    )

    k3.metric(
        "Barangays Served",
        f"{covered_barangays:,}"
    )

    k4.metric(
        "Districts Served",
        f"{covered_districts:,}"
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

    st.pydeck_chart(
        deck,
        height=700,
        width='stretch' 
    )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Facilities")

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

    c1.metric(
        "Total Population",
        f"{population_total:,.0f}"
    )

    c2.metric(
        "Population per Facility",
        f"{population_per_rehab:,.0f}"
    )

    c3.metric(
        "Older Persons per Facility",
        f"{elderly_per_rehab:,.0f}"
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
        title="Long-Term Care and Rehabilitation Services"
    )

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
        title="Rehabilitation Facilities by District"
    )

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

    st.markdown(
        """
        <span style="color:#7F47ED;">●</span>
        <b>QC Migrants Resource Center</b> — Provides support, information, training, and services for migrant workers and their families.
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    pwd_sex = pd.read_csv(
        "processed/persons_with_disability_by_sex.csv"
    )

    pwd_district = pd.read_csv(
        "processed/persons_with_disability_by_age_and_sex.csv"
    )

    pwd_barangay = pd.read_csv(
        "processed/persons_with_disability_by_barangay.csv"
    )

    pwd_type = pd.read_csv(
        "processed/persons_with_disability_per_type.csv"
    )

    pwd_year = pd.read_csv(
        "processed/persons_with_disability_per_year.csv"
    )

    # --------------------------------------------------
    # CLEANING
    # --------------------------------------------------

    def clean_num(series):

        return (
            series.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .astype(float)
        )

    pwd_sex["Male"] = clean_num(
        pwd_sex["Male"]
    )

    pwd_sex["Female"] = clean_num(
        pwd_sex["Female"]
    )

    pwd_district["Registered PWDs in QC"] = clean_num(
        pwd_district["Registered PWDs in QC"]
    )

    pwd_district["Population (2020 Census)"] = clean_num(
        pwd_district["Population (2020 Census)"]
    )

    pwd_barangay["PWDs"] = clean_num(
        pwd_barangay["PWDs"]
    )

    pwd_barangay["Population (2020 Census)"] = clean_num(
        pwd_barangay["Population (2020 Census)"]
    )

    pwd_year[
        "persons_with_disability_registered_during_the_year"
    ] = clean_num(
        pwd_year[
            "persons_with_disability_registered_during_the_year"
        ]
    )

    for col in [
        "2021",
        "2022",
        "2023",
        "2024",
        "2025",
        "2026"
    ]:

        pwd_type[col] = clean_num(
            pwd_type[col]
        )

    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    total_pwd = (
        pwd_district[
            "Registered PWDs in QC"
        ].sum()
    )

    total_male = (
        pwd_sex["Male"]
        .sum()
    )

    total_female = (
        pwd_sex["Female"]
        .sum()
    )

    disability_types = (
        pwd_sex[
            "Type of Disability"
        ].nunique()
    )

    rehab_facilities = len(
        long_term_care
    )

    barangays_covered = (
        pwd_barangay[
            "Barangay"
        ].nunique()
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric(
        "Registered PWDs",
        f"{total_pwd:,.0f}"
    )

    k2.metric(
        "Male",
        f"{total_male:,.0f}"
    )

    k3.metric(
        "Female",
        f"{total_female:,.0f}"
    )

    k4.metric(
        "Disability Types",
        disability_types
    )

    k5.metric(
        "Barangays",
        barangays_covered
    )

    k6.metric(
        "Rehab Facilities",
        rehab_facilities
    )

    st.divider()

    # --------------------------------------------------
    # COVERAGE KPI
    # --------------------------------------------------

    st.metric(
        "PWDs per Rehabilitation Facility",
        f"{(total_pwd / rehab_facilities):,.0f}"
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
            title="PWD Population by Sex"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        disability_totals = pwd_sex.copy()

        disability_totals["Total"] = (
            disability_totals["Male"]
            +
            disability_totals["Female"]
        )

        fig = px.bar(
            disability_totals
            .sort_values(
                "Total",
                ascending=False
            ),
            x="Type of Disability",
            y="Total",
            title="Disability Types"
        )

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

    fig = px.bar(
        pwd_district,
        x="District",
        y="Registered PWDs in QC",
        text_auto=",",
        title="Registered PWDs by District"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.divider()

    # --------------------------------------------------
    # REGISTRATION TREND
    # --------------------------------------------------

    st.subheader(
        "PWD Registration Trend"
    )

    fig = px.line(
        pwd_year,
        x="year",
        y="persons_with_disability_registered_during_the_year",
        markers=True
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.divider()

    # --------------------------------------------------
    # DISABILITY TYPES OVER TIME
    # --------------------------------------------------

    st.subheader(
        "Disability Registration Trends"
    )

    type_long = pwd_type.melt(
        id_vars="Type of Disability",
        var_name="Year",
        value_name="Count"
    )

    fig = px.line(
        type_long,
        x="Year",
        y="Count",
        color="Type of Disability"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.divider()

    # --------------------------------------------------
    # TOP BARANGAYS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Top 10 Barangays by PWD Population"
        )

        st.dataframe(
            pwd_barangay
            .sort_values(
                "PWDs",
                ascending=False
            )
            .head(10),
            width="stretch"
        )

    with col2:

        coverage_df = pwd_barangay.copy()

        coverage_df["Coverage_Num"] = (
            coverage_df["Coverage"]
            .astype(str)
            .str.replace(
                "%",
                ""
            )
            .astype(float)
        )

        st.subheader(
            "Highest Coverage Barangays"
        )

        st.dataframe(
            coverage_df
            .sort_values(
                "Coverage_Num",
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
        .astype(str)
    )

    district_map = {
        "I": "1",
        "II": "2",
        "III": "3",
        "IV": "4",
        "V": "5",
        "VI": "6"
    }

    district_coverage = (
        pwd_district.copy()
    )

    district_coverage["District_Num"] = (
        district_coverage["District"]
        .map(district_map)
    )

    district_coverage = (
        district_coverage.merge(
            rehab_by_district,
            left_on="District_Num",
            right_on="District",
            how="left"
        )
    )

    district_coverage[
        "PWDs per Facility"
    ] = (
        district_coverage[
            "Registered PWDs in QC"
        ]
        /
        district_coverage[
            "Facilities"
        ]
    ).round(0)

    st.dataframe(
        district_coverage[
            [
                "District_x",
                "Registered PWDs in QC",
                "Facilities",
                "PWDs per Facility"
            ]
        ].rename(
            columns={
                "District_x":
                "District"
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
        satellite offices providing local access
        to government services.
        """
    )

    # --------------------------------------------------
    # DISTRICT FILTER
    # --------------------------------------------------

    districts = sorted(
        satellite_offices["District"]
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

    sat = satellite_offices.copy()

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
    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Action Offices")

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
        satellite offices on a single map — optionally overlaid
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
            "color": "#5B21B6",
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
            "color": "#7F47ED",
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
            "color": "#8B5CF6",
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
            "color": "#A78BFA",
            "symbol": "▲",
            "source": "Rehabilitation Facility",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Action Offices": {
            "df": satellite_offices,
            "color": "#DDD6FE",
            "symbol": "⬢",
            "source": "Satellite Office",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Migration Resource Centers": {
            "df": migration_centers,
            "color": "#C084FC",
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
            "the Climate & Hazard Exposure page for a closer look "
            "at each layer individually."
        )
    )

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    map_html = build_explorer_map(
        tuple(selected_layers),
        selected_district,
        tuple(selected_climate_layers)
    )

    st.iframe(
        map_html,
        height=850,
        width="stretch"
    )


elif page == "Accessibility Analysis":
    import geopandas as gpd
 
    care = pd.read_csv(
        "processed/care_v3.csv"
    )
 
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

    with st.expander("How are these indicators calculated?"):
 
        st.markdown("""
        The indicators below are the same at both the **District**
        and **Barangay** level — only the level of aggregation
        differs between the two tabs.
 
        | Indicator | What it measures | Direction |
        |---|---|---|
        | **Facilities** | Count of registered care facilities of any kind (childcare, schools, health centers, elder care, etc.) located in the area | *Higher is better* |
        | **Facilities per 10k Population** | Facilities scaled to population, so large and small areas can be compared fairly | *Higher is better* |
        | **Care Gap Index** | Population ÷ Facilities — roughly, how many people each facility would need to serve on average if demand were spread evenly | *Lower is better* |
        | **Accessibility Index** | Facilities per 10k Population, rescaled 0–100 (0 = the least-served area in the dataset, 100 = the best-served) | *Higher is better* |
 
        **Accessibility Index and Care Gap Index point in opposite
        directions on purpose.** A high Care Gap Index and a *low*
        Accessibility Index both describe the same underserved area
        — just measured from opposite ends. Don't read "higher" as
        good for one and bad for the other without checking which
        indicator you're looking at.
 
        On the map and charts, **"Best Served"** refers to the
        highest Accessibility Index, and **"Priority"** refers to
        the lowest — i.e. the area with the fewest facilities
        relative to its population.
        """)
 
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
 
        district_population = (
            pop.groupby("District")[age_cols]
            .sum()
            .reset_index()
        )
 
        district_population["District"] = (
            district_population["District"]
            .astype(int)
        )
 
        # ==================================================
        # CARE FACILITIES
        # ==================================================
 
        care_clean = care.copy()
 
        care_clean["district"] = (
            pd.to_numeric(
                care_clean["district"],
                errors="coerce"
            )
        )
 
        care_clean = care_clean.dropna(
            subset=["district"]
        )
 
        care_clean["district"] = (
            care_clean["district"]
            .astype(int)
        )
 
        facility_counts = (
            care_clean
            .groupby("district")
            .size()
            .reset_index(name="Facilities")
            .rename(
                columns={
                    "district":"District"
                }
            )
        )
 
        # ==================================================
        # MERGE
        # ==================================================
 
        access = district_population.merge(
            facility_counts,
            on="District",
            how="left"
        )
 
        access["Facilities"] = (
            access["Facilities"]
            .fillna(0)
        )
 
        # ==================================================
        # INDICATORS
        # ==================================================
 
        access["Facilities per 10k Population"] = (
            access["Facilities"]
            /
            access["Total"]
            * 10000
        )
 
        access["Care Gap Index"] = (
            access["Total"]
            /
            access["Facilities"]
        )
 
        access = access.replace(
            [np.inf, -np.inf],
            np.nan
        )
 
        # ==================================================
        # ACCESSIBILITY INDEX
        # ==================================================
 
        min_score = (
            access["Facilities per 10k Population"]
            .min()
        )
 
        max_score = (
            access["Facilities per 10k Population"]
            .max()
        )
 
        access["Accessibility Index"] = (
            (
                access["Facilities per 10k Population"]
                - min_score
            )
            /
            (
                max_score
                - min_score
            )
        ) * 100
 
        access = access.round(2)
 
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
 
        c1.metric(
            "Accessibility Index",
            avg_score
        )
 
        c2.metric(
            "Total Facilities",
            f"{total_facilities:,}"
        )
 
        c3.metric(
            "Best Served District",
            best_district
        )
 
        c4.metric(
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
                    "Care Gap Index"
                ]
            ],
            on="District",
            how="left"
        )
 
        # ==================================================
        # MAP
        # ==================================================
 
        st.subheader(
            "District Accessibility Map"
        )
 
        st.caption(
            "Darker = higher Accessibility Index = more facilities "
            "relative to population (better served)."
        )
 
        # ------------------------------------------
        # Color ramp (PuRd-style) for Accessibility Index
        # ------------------------------------------
 
        def purd_color(value, vmin, vmax):
 
            if pd.isna(value) or vmax == vmin:
                return [217, 217, 217, 120]
 
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
 
                    return [int(r), int(g), int(b), 200]
 
            return [103, 0, 31, 200]
 
        access_min = district_geo["Accessibility Index"].min()
        access_max = district_geo["Accessibility Index"].max()
 
        district_geo["fill_color"] = district_geo["Accessibility Index"].apply(
            lambda v: purd_color(v, access_min, access_max)
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
            "html": """
            <b>District {District}</b><br/>
            Facilities: {Facilities}<br/>
            Population: {Total}<br/>
            Facilities / 10k Population: {Facilities per 10k Population}<br/>
            Accessibility Index: {Accessibility Index}
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
                    "Accessibility Index",
                    ascending=False
                ),
                x="District",
                y="Accessibility Index",
                color="Accessibility Index",
                color_continuous_scale="Purples",
                title="Accessibility Index by District"
            )
 
            st.plotly_chart(
                fig,
                width="stretch"
            )
 
        with right:
 
            fig = px.bar(
                access.sort_values(
                    "Care Gap Index",
                    ascending=False
                ),
                x="District",
                y="Care Gap Index",
                color="Care Gap Index",
                color_continuous_scale="Reds",
                title="Care Gap Index"
            )
 
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
            x="Total",
            y="Facilities",
            size="Facilities",
            text="District",
            color="Accessibility Index",
            color_continuous_scale="Purples",
            title="Population vs Care Facilities"
        )
 
        fig.update_traces(
            textposition="top center"
        )
 
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
 
        priority = (
            access.sort_values(
                [
                    "Accessibility Index",
                    "Care Gap Index"
                ],
                ascending=[
                    True,
                    False
                ]
            )
            .head(5)
        )
 
        st.dataframe(
            priority,
            width="stretch"
        )
 
        st.divider()
 
        # ==================================================
        # FULL TABLE
        # ==================================================
 
        st.subheader(
            "District Accessibility Indicators"
        )
 
        st.dataframe(
            access,
            width="stretch"
        )
 
    with tab2:
 
        st.subheader(
            "Barangay-Level Accessibility"
        )
 
        # ==================================================
        # POPULATION
        # ==================================================
 
        barangay_pop = population_age.copy()
 
        age_cols = [
            "0-5 (Early Childhood)",
            "6-17 (School Age Children)",
            "18-59 (Working Age Adult)",
            "60+ (Elderly)",
            "Total"
        ]
 
        for col in age_cols:
 
            barangay_pop[col] = (
                barangay_pop[col]
                .astype(str)
                .str.replace(",", "")
                .astype(float)
            )
 
        barangay_pop["Barangay"] = (
            barangay_pop["Barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )
 
        # ==================================================
        # CARE FACILITY COUNTS
        # ==================================================
 
        barangay_facilities = (
            care_clean
            .groupby("barangay")
            .size()
            .reset_index(name="Facilities")
        )
 
        barangay_facilities["barangay"] = (
            barangay_facilities["barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )
 
        # ==================================================
        # MERGE
        # ==================================================
 
        barangay_access = barangay_pop.merge(
            barangay_facilities,
            left_on="Barangay",
            right_on="barangay",
            how="left"
        )
 
        barangay_access["Facilities"] = (
            barangay_access["Facilities"]
            .fillna(0)
        )
 
        # ==================================================
        # INDICATORS
        # ==================================================
 
        barangay_access[
            "Facilities per 10k Population"
        ] = (
            barangay_access["Facilities"]
            /
            barangay_access["Total"]
            * 10000
        )
 
        barangay_access[
            "Care Gap Index"
        ] = (
            barangay_access["Total"]
            /
            barangay_access["Facilities"]
        )
 
        barangay_access = barangay_access.replace(
            [np.inf, -np.inf],
            np.nan
        )
 
        # ==================================================
        # ACCESSIBILITY INDEX
        # ==================================================
 
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
 
        c1.metric(
            "Average Accessibility",
            avg_access
        )
 
        c2.metric(
            "Barangays Without Facilities",
            int(no_facilities)
        )
 
        c3.metric(
            "Best Served Barangay",
            str(top_barangay)
        )
 
        st.divider()
 
        # ==================================================
        # BARANGAY MAP
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
 
        barangay_geo = barangay_geo.merge(
            barangay_access[
                [
                    "Barangay",
                    "Facilities",
                    "Total",
                    "Accessibility Index"
                ]
            ],
            left_on="barangay_name",
            right_on="Barangay",
            how="left"
        )
 
        st.subheader(
            "Barangay Accessibility Map"
        )
 
        st.caption(
            "Darker = higher Accessibility Index = more facilities "
            "relative to population (better served)."
        )
 
        def purd_color(value, vmin, vmax):
 
            if pd.isna(value) or vmax == vmin:
                return [217, 217, 217, 120]
 
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
 
                    return [int(r), int(g), int(b), 215]
 
            return [103, 0, 31, 215]
 
        access_min = barangay_geo["Accessibility Index"].min()
        access_max = barangay_geo["Accessibility Index"].max()
 
        barangay_geo["fill_color"] = barangay_geo["Accessibility Index"].apply(
            lambda v: purd_color(v, access_min, access_max)
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
            "html": """
            <b>{Barangay}</b><br/>
            Facilities: {Facilities}<br/>
            Population: {Total}<br/>
            Accessibility Index: {Accessibility Index}
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
 
        st.pydeck_chart(
            deck,
            height=750,
            width='stretch'
        )
 
        st.divider()
 
        # ==================================================
        # MOST UNDERSERVED BARANGAYS
        # ==================================================
 
        underserved = (
            barangay_access
            .sort_values(
                "Accessibility Index"
            )
            .head(20)
        )
 
        fig = px.bar(
            underserved,
            x="Accessibility Index",
            y="Barangay",
            orientation="h",
            color="Accessibility Index",
            color_continuous_scale="Reds",
            title="Most Underserved Barangays"
        )
 
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
            color_continuous_scale="Purples",
            title="Population vs Facilities"
        )
 
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
 
        priority_barangays = (
            barangay_access
            .sort_values(
                [
                    "Accessibility Index",
                    "Total"
                ],
                ascending=[
                    True,
                    False
                ]
            )
            .head(25)
        )
 
        st.dataframe(
            priority_barangays[
                [
                    "Barangay",
                    "District",
                    "Total",
                    "Facilities",
                    "Facilities per 10k Population",
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
 
        st.dataframe(
            barangay_access,
            width="stretch"
        )

elif page == "Care Planning & Investment Priorities":

    import geopandas as gpd

    care = pd.read_csv(
        "processed/care_v3.csv"
    )

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
    existing infrastructure, care burden,
    and service diversity to prioritize
    areas for intervention.
    """)

    with st.expander("How is the Priority Score calculated?"):

        st.markdown("""
        **Higher Priority Score = higher priority for investment**
        (i.e. the barangay appears more underserved relative to
        its need). Scores are scaled 0–100, with 100 assigned to
        the single most underserved barangay in the dataset.

        The score blends four indicators, each barangay first
        ranked against all others on that indicator, then combined
        with the weights below:

        | Indicator | What it measures | Direction | Weight |
        |---|---|---|---|
        | **Population** | Total residents in the barangay | Larger population → higher priority | 35% |
        | **Care Burden** | Children (0–5) + older persons (60+) — the age groups that rely most on care services | Larger care burden → higher priority | 35% |
        | **Facilities** | Number of registered care facilities of any kind (childcare, schools, health centers, elder care, etc.) | Fewer facilities → higher priority | 20% |
        | **Service Diversity** | Number of *distinct types* of care service present (e.g. having both a school and a health center counts as more diverse than two schools) | Less diversity → higher priority | 10% |

        A barangay with a large, care-dependent population and few or
        no facilities will score near 100. A barangay with a small
        population and many varied facilities will score near 0.

        **Other indicators on this page, for reference:**
        - **Facilities per 10k Population** — facility count normalized
          by population, so large and small barangays can be compared
          fairly. *Higher is better* (more facilities relative to people).
        - **Care Burden per Facility** — how many children + older
          persons each facility would need to serve on average if
          demand were spread evenly. *Lower is better.*
        - **Children per Facility / Elderly per Facility** — the same
          idea, split by age group (children 0–5; older persons 60+)
          and divided only by facilities that actually serve that
          group (Childcare + Schools for children; Older Persons Care
          + Long-Term Care for the elderly). *Lower is better* for both.
        - **Care Desert** — a barangay with **zero** registered care
          facilities of any kind. This is a flag, not a score.
        """)

    # ==================================================
    # CLEAN POPULATION
    # ==================================================

    pop = population_age.copy()

    # apply_barangay_mapping() pulls the final "Barangay"
    # value from barangay_district_mapping.csv's BARANGAY
    # column, which is title-case (e.g. "Greater Lagro"),
    # not uppercase. Every merge key on this page (care_clean,
    # barangay_geo["barangay_name"]) is uppercased, so this
    # must be normalized too or barangays like Greater Lagro
    # silently fail to match and show as 0 facilities.
    pop["Barangay"] = (
        pop["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

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

    # ==================================================
    # CLEAN CARE DATA
    # ==================================================

    care_clean = care.copy()

    care_clean["barangay"] = (
        care_clean["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    care_clean = care_clean[
        care_clean["barangay"].notna()
    ]

    # ==================================================
    # FACILITY COUNTS
    # ==================================================

    facility_counts = (
        care_clean
        .groupby("barangay")
        .size()
        .reset_index(name="Facilities")
    )

    # ==================================================
    # DIVERSITY INDEX
    # ==================================================

    diversity = (
        care_clean
        .groupby("barangay")["major_division"]
        .nunique()
        .reset_index(name="Service Diversity")
    )

    # ==================================================
    # POPULATION
    # ==================================================

    barangay_access = (
        pop.merge(
            facility_counts,
            left_on="Barangay",
            right_on="barangay",
            how="left"
        )
    )

    barangay_access = barangay_access.merge(
        diversity,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    )

    barangay_access["Facilities"] = (
        barangay_access["Facilities"]
        .fillna(0)
    )

    barangay_access["Service Diversity"] = (
        barangay_access["Service Diversity"]
        .fillna(0)
    )

    # ==================================================
    # CARE BURDEN
    # ==================================================

    barangay_access["Care Burden"] = (
        barangay_access["0-5 (Early Childhood)"]
        +
        barangay_access["60+ (Elderly)"]
    )

    barangay_access["Facilities per 10k Population"] = (
        barangay_access["Facilities"]
        /
        barangay_access["Total"]
        * 10000
    )

    barangay_access["Care Burden per Facility"] = (
        barangay_access["Care Burden"]
        /
        barangay_access["Facilities"]
    )

    barangay_access = barangay_access.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # ==================================================
    # CHILDREN / ELDERLY PER FACILITY
    # (adapted from the supply & cluster indicator
    # notebooks, which compute child_per_facility and
    # elderly_per_facility separately rather than as
    # a single combined "Care Burden" — useful to see
    # whether a barangay's gap is specifically in
    # childcare/school capacity or in elder care capacity)
    # ==================================================

    barangay_access = compute_population_per_facility(
        barangay_access,
        care_clean
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

    barangay_access["Burden Rank"] = (
        barangay_access["Care Burden"]
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
    # metric (rank(ascending=False) for Population/Burden puts
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
        (n_barangays + 1 - barangay_access["Burden Rank"]) * 0.35
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

        st.metric(
            "Total Barangays",
            len(barangay_access)
        )

    with col2:

        st.metric(
            "Care Desert Barangays",
            int(
                (
                    barangay_access["Facilities"] == 0
                ).sum()
            )
        )

    with col3:

        st.metric(
            "Highest Priority Barangay",
            barangay_access.iloc[0]["Barangay"]
        )

    with col4:

        st.metric(
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

    unmatched = int(priority_map["Priority Score"].isna().sum())

    if unmatched > 0:
        st.warning(
            f"{unmatched} barangay polygon(s) didn't match any "
            "row in the priority table and will show as gray "
            "with no score — check spelling/casing of barangay "
            "names in the source data."
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
        "Care Burden",
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
    for col in ["Facilities", "Care Burden", "Service Diversity", "Priority Score"]:
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
        Care Burden: {Care Burden}<br/>
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

    st.dataframe(
        barangay_access[
            [
                "Barangay",
                "District",
                "Total",
                "Facilities",
                "Care Burden",
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
        title="Highest Priority Barangays"
    )

    fig.update_layout(
        height=700
    )

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
            "Care Burden",
            ascending=False
        )
    )

    st.markdown("""
    Barangays classified as care deserts currently have
    no registered care facilities in the inventory.
    These areas may require additional assessment to
    identify service gaps and potential investment needs.
    """)

    st.metric(
        "Care Desert Barangays",
        len(care_deserts)
    )

    st.dataframe(
        care_deserts[
            [
                "Barangay",
                "District",
                "Total",
                "Care Burden",
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
            x="Care Burden",
            y="Priority Score",
            hover_name="Barangay",
            title="Care Burden vs Priority Score",
            color="Priority Score"
        )

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
            color="Priority Score"
        )

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
        title="Barangays with the Most Diverse Care Services"
    )

    fig.update_layout(
        height=700
    )

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
    "Care Burden" above combines young children and
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

        st.metric(
            "Median Children per Facility",
            f"{barangay_access['Children per Facility'].median():,.0f}"
        )

    with cpf_col2:

        st.metric(
            "Median Elderly per Facility",
            f"{barangay_access['Elderly per Facility'].median():,.0f}"
        )

    with cpf_col3:

        st.metric(
            "Barangays with No Child-Serving Facility",
            int((barangay_access["Child-Serving Facilities"] == 0).sum())
        )

    with cpf_col4:

        st.metric(
            "Barangays with No Elderly-Serving Facility",
            int((barangay_access["Elderly-Serving Facilities"] == 0).sum())
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
            title="Highest Elderly per Facility (60+ yrs)"
        )

        fig.update_layout(height=550)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.dataframe(
        barangay_access[
            [
                "Barangay",
                "District",
                "0-5 (Early Childhood)",
                "Child-Serving Facilities",
                "Children per Facility",
                "60+ (Elderly)",
                "Elderly-Serving Facilities",
                "Elderly per Facility"
            ]
        ].sort_values("Children per Facility", ascending=False),
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

    care = pd.read_csv(
        "processed/care_v3.csv"
    )

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
    similar demographic and care-service profiles —
    adapted from the project's clustering methodology
    (K-means on standardized indicators). Clustering
    helps surface neighborhoods that face comparable
    pressures (e.g. dense and young vs. sparse and
    older, or service-rich vs. service-poor) so that
    interventions can be tailored by *type* of
    barangay rather than one at a time.

    **Features used:** population density, share of
    children (0-17), share of older persons (60+),
    dependency ratio, and the mix of care services
    present locally (e.g. share of facilities that are
    Childcare, Schools, Health centers, Older Persons
    Care, etc.) — standing in for the land-use mix used
    in the original notebooks, since Quezon City's data
    is facility-based rather than raster-based.
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

    pop["dependency_ratio"] = (
        (pop["children_0_17"] + pop["elderly"])
        / pop["working_age"]
        * 100
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
        "dependency_ratio",
        "population_density"
    ]

    pop_geo[numeric_guard_cols] = (
        pop_geo[numeric_guard_cols].fillna(0)
    )

    # ==================================================
    # CARE DATA
    # ==================================================

    care_clean = care.copy()

    care_clean["barangay"] = (
        care_clean["barangay"]
        .astype(str)
        .str.strip()
    )

    care_clean = care_clean[
        care_clean["barangay"].notna()
    ]

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
        care_clean
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

    k1.metric(
        "Barangays Clustered",
        int(clustered["barangay_name"].notna().sum())
    )

    k2.metric(
        "Clusters",
        n_clusters
    )

    k3.metric(
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
        Dependency Ratio: {dependency_ratio}
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

    radar_labels = [
        c.replace("share_", "% ").replace("_", " ")
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
        "dependency_ratio"
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
            "dependency_ratio": "Avg. Dependency Ratio"
        }
    )

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
                "dependency_ratio"
            ]
        ].rename(columns={"barangay_name": "Barangay"})
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
elif page == "Climate & Hazard Exposure":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Climate & Hazard Exposure
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        """
        Explore climate and hazard layers for Quezon City one at
        a time: land-surface temperature, vegetation cover, and
        100-year flood inundation. Select a layer below.
        """
    )

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

            st.caption(
                f"Legend: {active_layer['legend_label']} — "
                f"color scale spans {vmin:.1f} to {vmax:.1f} "
                f"{active_layer['unit']} (2nd-98th percentile "
                "of this layer's data)."
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
