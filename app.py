import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
import pydeck as pdk
from streamlit_folium import st_folium
import base64

def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_icon_url(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    return f"data:image/png;base64,{encoded}"

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def get_icon(category):

    category = str(category).upper()

    if "QC LGU" in category:
        return "hospital"

    elif "NATIONAL" in category:
        return "plus-square"

    elif "SUPER HEALTH" in category:
        return "heartbeat"

    elif "HEALTH CENTER" in category:
        return "clinic-medical"

    return "hospital"
    
# --------------------------------------------------
# CATEGORY COLORS
# --------------------------------------------------
def category_color(cat):

    cat = str(cat).upper()

    if "QC LGU" in cat:
        return [228, 26, 28]

    elif "NATIONAL" in cat:
        return [55, 126, 184]

    elif "SUPER HEALTH" in cat:
        return [255, 204, 0]

    elif "HEALTH CENTER" in cat:
        return [77, 175, 74]

    return [255, 127, 0]

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Quezon City Caring Cities Dashboard",
    page_icon="🏙️",
    layout="wide"
)

un_logo = get_base64("assets/unwomen_logo.png")
qc_logo = get_base64("assets/qc_logo.png")

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.markdown(
        f"""
        <a href="https://www.unwomen.org/en" target="_blank">
            <img src="data:image/png;base64,{un_logo}" width="180">
        </a>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="text-align:center;">
            <h1 style="color:#003B5C;">
                Quezon City Caring Cities Dashboard
            </h1>
            <p>
                Urban Care Systems & Accessibility Analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <a href="https://quezoncity.gov.ph/" target="_blank">
            <img src="data:image/png;base64,{qc_logo}" width="100">
        </a>
        """,
        unsafe_allow_html=True
    )

st.divider()

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data():

    city_kpis = pd.read_csv("processed/city_kpis.csv")
    health = pd.read_csv("processed/health.csv")
    district_summary = pd.read_csv("processed/district_summary.csv")
    senior_summary = pd.read_csv("processed/senior_summary.csv")
    senior_by_district = pd.read_csv("processed/senior_by_district.csv")
    pwd_summary = pd.read_csv("processed/pwd_summary.csv")
    pwd_types = pd.read_csv("processed/pwd_types.csv")
    businesses = pd.read_csv("processed/businesses.csv")
    childcare_summary = pd.read_csv("processed/childcare_summary.csv")
    childcare_centers = pd.read_csv("processed/childcare_centers.csv")
    facilities = pd.read_csv("processed/facilities.csv")
    barangays = pd.read_csv("processed/barangays.csv")

    population_sex = pd.read_csv(
    "processed/population/2024_population_by_sex.csv"
    )

    population_age = pd.read_csv(
        "processed/population/2024_population_by_age_group.csv"
    )

    geo = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    health_centers = pd.read_csv(
    "processed/health_centers.csv"
    )

    health_centers["Has Pharmacy"] = (
    health_centers["Has Pharmacy"]
    .astype(str)
    .str.strip()
    .str.upper()
    .map({
        "TRUE": True,
        "FALSE": False
    })
    )


    older_person_care = pd.read_csv(
        "processed/olders_person_care.csv"
    )

    print(health_centers) 

    return (
        city_kpis,
        health,
        district_summary,
        senior_summary,
        senior_by_district,
        pwd_summary,
        pwd_types,
        businesses,
        childcare_summary,
        childcare_centers,
        facilities,
        barangays,
        geo, 
        population_sex,
        population_age,
        health_centers,
        older_person_care
    )

(
    city_kpis,
    health,
    district_summary,
    senior_summary,
    senior_by_district,
    pwd_summary,
    pwd_types,
    businesses,
    childcare_summary,
    childcare_centers,
    facilities,
    barangays,
    geo,
    population_sex,
    population_age,
    health_centers,
    older_person_care
) = load_data()

# --------------------------------------------------
# CLEANING
# --------------------------------------------------

barangays["barangay"] = barangays["barangay"].str.strip()
geo["barangay_name"] = geo["barangay_name"].str.strip()

district_summary["district"] = (
    district_summary["district"]
    .str.replace("  ", " ")
    .str.strip()
)

barangays["district"] = (
    barangays["district"]
    .str.replace("DISTRICT ", "District ")
)

# Population cleanning
population_sex["Barangay"] = (
    population_sex["Barangay"]
    .str.strip()
)

population_age["Barangay"] = (
    population_age["Barangay"]
    .str.strip()
)

sex_numeric_cols = [
    "Male",
    "Female",
    "Total"
]

for col in sex_numeric_cols:
    population_sex[col] = (
        population_sex[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

age_cols = [
    "0-5 \n(Early Childhood)",
    "6-17 \n(School Age Children)",
    "18-59 \n(Working Age Adult)",
    "60+ \n(Elderly)",
    "Total"
]

for col in age_cols:
    population_age[col] = (
        population_age[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

# --------------------------------------------------
# KPI VALUES
# --------------------------------------------------

population = int(
    city_kpis.loc[
        city_kpis["indicator"] == "population_2024",
        "value"
    ].iloc[0]
)

seniors = int(
    senior_summary.loc[
        senior_summary["metric"] == "registered_seniors_2026",
        "value"
    ].iloc[0]
)

pwds = int(
    pwd_summary["value"].iloc[0]
)

child_centers = int(
    childcare_summary.loc[
        childcare_summary["metric"] == "child_development_centers",
        "value"
    ].iloc[0]
)

doctors_total = int(
    health["doctors"].sum()
)

health_centers_total = int(
    health["health_centers"].sum()
)

# --------------------------------------------------
# GIS DATASET
# --------------------------------------------------

childcare_by_barangay = (
    childcare_centers
    .groupby("barangay")
    .size()
    .reset_index(name="childcare_centers")
)

map_df = geo.merge(
    barangays,
    left_on="barangay_name",
    right_on="barangay",
    how="left"
)

map_df = map_df.merge(
    childcare_by_barangay,
    left_on="barangay_name",
    right_on="barangay",
    how="left"
) 

map_df = map_df.merge(
    district_summary,
    on="district",
    how="left"
)

map_df["childcare_centers"] = (
    map_df["childcare_centers"]
    .fillna(0)
)

demo_map = geo.merge(
    population_sex,
    left_on="barangay_name",
    right_on="Barangay",
    how="left"
)

demo_map = demo_map.merge(
    population_age,
    left_on="barangay_name",
    right_on="Barangay",
    how="left",
    suffixes=("", "_age")
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Section",
    [
        "Childcare Centers",
        "Health Centers Map",
        "Older Persons & Senior Citizens",
        "Care Services Explorer"
    ]
)

selected_category = "All"

def category_hex(cat):

    rgb = category_color(cat)

    return "#{:02X}{:02X}{:02X}".format(
        rgb[0],
        rgb[1],
        rgb[2]
    )

if page == "Health Centers Map":

    selected_category = st.sidebar.radio(
        "Facility Type",
        [
            "All",
            "QC LGU",
            "National",
            "Health Center",
            "Super Health",
            "Pharmacy"
        ]
    )

    category_descriptions = {
        "QC LGU": "Local government-managed facilities",
        "National": "National government hospitals and facilities",
        "Health Center": "Primary healthcare facilities",
        "Super Health": "Enhanced facilities with expanded services"
    }

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Facility Categories")

    for cat in category_descriptions:

        st.sidebar.markdown(
            f"""
            <span style="
                color:{category_hex(cat)};
                font-size:22px;
            ">●</span>
            <b>{cat}</b><br>
            <small>{category_descriptions[cat]}</small>
            """,
            unsafe_allow_html=True
        )
    
if page == "Older Persons & Senior Citizens":

    selected_opc_category = st.sidebar.radio(
        "Facility Category",
        [
            "All",
            "Nursing Care Center",
            "Bahay Aruga"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Facility Categories")

    st.sidebar.markdown(
        """
        <span style="color:#377EB8;font-size:22px;">●</span>
        <b>Nursing Care Center</b><br>
        <small>Residential and nursing care services for older persons.</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#4DAF4A;font-size:22px;">●</span>
        <b>Bahay Aruga</b><br>
        <small>Temporary accommodation and support services.</small>
        """,
        unsafe_allow_html=True
    )


if page == "Care Services Explorer":

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Health Centers Legends")

    st.sidebar.markdown(
        """
        <span style="color:#E41A1C;font-size:22px;">●</span>
        <b>QC LGU</b><br>
        <small>Local government-managed facilities</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#377EB8;font-size:22px;">●</span>
        <b>National</b><br>
        <small>National government facilities</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#4DAF4A;font-size:22px;">●</span>
        <b>Health Center</b><br>
        <small>Primary healthcare facilities</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#FFCC00;font-size:22px;">●</span>
        <b>Super Health</b><br>
        <small>Expanded health facilities</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Seniors Centers Legends")


    st.sidebar.markdown(
        """
        <span style="color:#984EA3;font-size:22px;">●</span>
        <b>Nursing Care Center</b><br>
        <small>Residential and nursing care services</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#FF7F00;font-size:22px;">●</span>
        <b>Bahay Aruga</b><br>
        <small>Temporary accommodation and support services</small>
        """,
        unsafe_allow_html=True
    )
# ------------------------------------------
# Childcare page
# ------------------------------------------

if page == "Childcare Centers":

    st.title("👶 Childcare Centers")

    # =========================
    # KPIs
    # =========================

    metrics = dict(
        zip(
            childcare_summary["metric"],
            childcare_summary["value"]
        )
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Child Development Centers",
            f"{int(metrics.get('child_development_centers', 0)):,}"
        )

    with c2:
        st.metric(
            "ECCD Enrollees",
            f"{int(metrics.get('eccd_enrollees', 0)):,}"
        )

    st.divider()

    # =========================
    # MAP DATA
    # =========================

    childcare_by_barangay = (
        childcare_centers
        .groupby("barangay")
        .size()
        .reset_index(name="childcare_centers")
    )

    childcare_map = geo.merge(
        childcare_by_barangay,
        left_on="barangay_name",
        right_on="barangay",
        how="left"
    )

    childcare_map["childcare_centers"] = (
        childcare_map["childcare_centers"]
        .fillna(0)
    )

    # =========================
    # DISTRICT FILTER
    # =========================

    districts = sorted(
        childcare_centers["district"]
        .dropna()
        .unique()
    )

    selected_district = st.selectbox(
        "District",
        ["All"] + list(districts)
    )

    centers_filtered = childcare_centers.copy()
    map_filtered = childcare_map.copy()

    if selected_district != "All":

        centers_filtered = centers_filtered[
            centers_filtered["district"] == selected_district
        ]

        map_filtered = map_filtered[
            map_filtered["district"] == selected_district
        ]

    # =========================
    # DECK.GL MAP
    # =========================

    district_layer = pdk.Layer(
        "GeoJsonLayer",
        map_filtered.__geo_interface__,
        pickable=True,
        stroked=True,
        filled=True,
        get_fill_color="[255 - childcare_centers*8, 150, childcare_centers*8, 180]",
        get_line_color=[80, 80, 80],
        line_width_min_pixels=1,
    )

    centers_layer = pdk.Layer(
        "ScatterplotLayer",
        centers_filtered,
        get_position='[longitude, latitude]',
        get_radius=80,
        get_fill_color=[220, 30, 30, 220],
        pickable=True
    )

    center_lat = centers_filtered["latitude"].mean()
    center_lon = centers_filtered["longitude"].mean()

    deck = pdk.Deck(
        map_style="light",
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
        ),
        layers=[
            district_layer,
            centers_layer,
        ],
        tooltip={
            "html": """
            <b>{center_name}</b><br/>
            Barangay: {barangay}<br/>
            District: {district}<br/>
            Address: {address}
            """
        }
    )

    st.pydeck_chart(
        deck,
        use_container_width=True
    )

    # =========================
    # TABLE
    # =========================

    st.subheader("Childcare Centers")

    st.dataframe(
        centers_filtered[
            [
                "center_name",
                "barangay",
                "district",
                "address"
            ]
        ],
        use_container_width=True
    )

# --------------------------------------------------
# HEALTH CENTERS MAP
# --------------------------------------------------

elif page == "Health Centers Map":

    st.title("🏥 Health Centers & Hospitals") 
    
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
        .unique()
    )

    selected_district = st.selectbox(
        "District",
        ["All"] + list(districts)
    )

    # --------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------

    category_options = [
        "All",
        "QC LGU",
        "National",
        "Health Center",
        "Super Health",
        "Pharmacy"
    ]

    hc = health_centers.copy()

    # District filter
    if selected_district != "All":
        hc = hc[
            hc["District"] == selected_district
        ]

    # Category filter
    if selected_category != "All":

        if selected_category == "Pharmacy":

            hc = hc[
                hc["Has Pharmacy"] == True
            ]

        else:

            hc = hc[
                hc["Category"]
                .str.contains(
                    selected_category,
                    case=False,
                    na=False
                )
            ]
    # --------------------------------------------------
    # PHARMACY BOOLEAN CLEANING
    # --------------------------------------------------

    hc["Has Pharmacy"] = (
        hc["Has Pharmacy"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map({
            "TRUE": True,
            "FALSE": False
        })
        .fillna(False)
    )

    hc["color"] = hc["Category"].apply(category_color)

    # --------------------------------------------------
    # QC CENTER
    # --------------------------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "selected_facility" not in st.session_state:
        st.session_state.selected_facility = None

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    map_col, info_col = st.columns([4, 1])

    # --------------------------------------------------
    # FOLIUM MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # --------------------------------------------------
    # BARANGAYS
    # --------------------------------------------------

    folium.GeoJson(
        geo,
        style_function=lambda x: {
            "fillColor": "#7fbf7f",
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.15,
        }
    ).add_to(m)

    # --------------------------------------------------
    # CATEGORY COLORS
    # --------------------------------------------------

    def marker_color(category):

        category = str(category).upper()

        if "QC LGU" in category:
            return "#E41A1C"      # red

        elif "NATIONAL" in category:
            return "#377EB8"      # blue

        elif "SUPER HEALTH" in category:
            return "#FFCC00"      # yellow

        elif "HEALTH CENTER" in category:
            return "#4DAF4A"      # green

        return "#999999"          # gray


    # --------------------------------------------------
    # MARKERS
    # --------------------------------------------------

    for _, row in hc.iterrows():

        popup_html = f"""
        <b>{row['Name of Facility']}</b><br>
        Category: {row['Category']}<br>
        District: {row['District']}<br>
        Has Pharmacy: {'Yes' if row['Has Pharmacy'] else 'No'}<br>
        Address: {row['Address']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=4,
            color=marker_color(row["Category"]),
            fill=True,
            fill_color=marker_color(row["Category"]),
            fill_opacity=0.9,
            weight=2,
            popup=popup_html,
            tooltip=row["Name of Facility"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP RENDER
    # --------------------------------------------------

    with map_col:

        map_data = st_folium(
            m,
            height=700,
            width=None,
            returned_objects=[
                "last_object_clicked"
            ]
        )

    # --------------------------------------------------
    # DETECT CLICK
    # --------------------------------------------------

    if (
        map_data
        and map_data.get("last_object_clicked")
    ):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        hc_temp = hc.copy()

        hc_temp["distance"] = (
            (hc_temp["latitude"] - clicked_lat) ** 2 +
            (hc_temp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_facility = (
            hc_temp.loc[
                hc_temp["distance"].idxmin()
            ]
        )

    # --------------------------------------------------
    # INFO PANEL
    # --------------------------------------------------

    with info_col:

        st.subheader("Facility Details")

        if st.session_state.selected_facility is not None:

            facility = st.session_state.selected_facility

            st.markdown(
                f"### {facility['Name of Facility']}"
            )

            st.write(
                f"**Category:** {facility['Category']}"
            )

            st.write(
                f"**District:** {facility['District']}"
            )

            st.write(
                f"**Has Pharmacy:** {'Yes' if facility['Has Pharmacy'] else 'No'}"
            )

            st.write(
                f"**Address:** {facility['Address']}"
            )

        else:

            st.info(
                "Click a facility marker on the map."
            )
    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Facilities",
        len(hc)
    )

    c2.metric(
        "With Pharmacy",
        int(hc["Has Pharmacy"].sum())
    )

    c3.metric(
        "Categories",
        hc["Category"].nunique()
    )

    # --------------------------------------------------
    # CATEGORY SUMMARY
    # --------------------------------------------------

    st.subheader("Facilities by Category")

    category_summary = (
        hc.groupby("Category")
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
    )

    fig = px.bar(
        category_summary,
        x="count",
        y="Category",
        orientation="h",
        text="count"
    )

    fig.update_layout(
        height=400,
        yaxis_title="",
        xaxis_title="Facilities"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.subheader("Facilities")

    st.dataframe(
        hc[
            [
                "Name of Facility",
                "District",
                "Category",
                "Has Pharmacy",
                "Address"
            ]
        ],
        use_container_width=True
    )


elif page == "Older Persons & Senior Citizens":

    st.title("Older Persons & Senior Citizens")

    st.caption(
        """
        Interactive map of facilities supporting older persons in Quezon City,
        including nursing care centers and Bahay Aruga facilities.
        """
    )

    # --------------------------------------------------
    # METRICS
    # --------------------------------------------------

    metrics = dict(
        zip(
            senior_summary["metric"],
            senior_summary["value"]
        )
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Registered Seniors",
        f"{int(metrics['registered_seniors_2026']):,}"
    )

    c2.metric(
        "Female",
        f"{int(metrics['female']):,}"
    )

    c3.metric(
        "Male",
        f"{int(metrics['male']):,}"
    )

    c4.metric(
        "Age 60–79",
        f"{int(metrics['age_60_79']):,}"
    )

    c5.metric(
        "Age 80+",
        f"{int(metrics['age_80_plus']):,}"
    )

    st.divider()

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    district_options = sorted(
        older_person_care["district"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_district = st.selectbox(
        "District",
        ["All"] + district_options,
        key="opc_district"
    )

    opc = older_person_care.copy()

    if selected_district != "All":

        opc = opc[
            opc["district"].astype(str)
            == selected_district
        ]

    if selected_opc_category != "All":

        opc = opc[
            opc["category"]
            .str.contains(
                selected_opc_category,
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------
    # CATEGORY COLORS
    # --------------------------------------------------

    def opc_color(category):

        category = str(category).upper()

        if "NURSING" in category:
            return "#377EB8"

        elif "BAHAY ARUGA" in category:
            return "#4DAF4A"

        return "#999999"

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "selected_senior_facility" not in st.session_state:

        st.session_state.selected_senior_facility = None

    # --------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------

    center_lat = opc["latitude"].mean()
    center_lon = opc["longitude"].mean()

    map_col, info_col = st.columns([4, 1])

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    folium.GeoJson(
        geo,
        style_function=lambda x: {
            "fillColor": "#7fbf7f",
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.15,
        }
    ).add_to(m)

    # --------------------------------------------------
    # FACILITY MARKERS
    # --------------------------------------------------

    for _, row in opc.iterrows():

        popup_html = f"""
        <b>{row['name']}</b><br>
        Category: {row['category']}<br>
        District: {row['district']}<br>
        Barangay: {row['barangay']}<br>
        Address: {row['address']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=5,
            color=opc_color(row["category"]),
            fill=True,
            fill_color=opc_color(row["category"]),
            fill_opacity=0.9,
            weight=2,
            popup=popup_html,
            tooltip=row["name"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    with map_col:

        map_data = st_folium(
            m,
            height=700,
            width=None,
            returned_objects=["last_object_clicked"]
        )

    # --------------------------------------------------
    # CLICK DETECTION
    # --------------------------------------------------

    if (
        map_data
        and map_data.get("last_object_clicked")
    ):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        tmp = opc.copy()

        tmp["distance"] = (
            (tmp["latitude"] - clicked_lat) ** 2 +
            (tmp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_senior_facility = (
            tmp.loc[
                tmp["distance"].idxmin()
            ]
        )

    # --------------------------------------------------
    # INFO PANEL
    # --------------------------------------------------

    with info_col:

        st.subheader("Facility Details")

        if st.session_state.selected_senior_facility is not None:

            facility = st.session_state.selected_senior_facility

            st.markdown(
                f"### {facility['name']}"
            )

            st.write(
                f"**Category:** {facility['category']}"
            )

            st.write(
                f"**District:** {facility['district']}"
            )

            st.write(
                f"**Barangay:** {facility['barangay']}"
            )

            st.write(
                f"**Address:** {facility['address']}"
            )

            st.write(
                f"**Major Division:** {facility['major_division']}"
            )

        else:

            st.info(
                "Click a facility on the map."
            )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "Older Persons Care Facilities"
    )

    st.dataframe(
        opc[
            [
                "name",
                "district",
                "barangay",
                "category",
                "address"
            ]
        ],
        use_container_width=True
    )

# --------------------------------------------------
# CARE SERVICE EXPLORER
# --------------------------------------------------

elif page == "Care Services Explorer":

    st.title("🗺️ Care Services Explorer")

    st.caption(
        """
        Explore and compare care-related facilities across Quezon City,
        including health facilities and older persons care services.
        """
    )

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        show_health = st.checkbox(
            "Health Facilities",
            value=True
        )

        show_senior = st.checkbox(
            "Older Persons Facilities",
            value=True
        )

    with col2:

        districts = sorted(
            health_centers["District"]
            .dropna()
            .unique()
        )

        selected_district = st.selectbox(
            "District",
            ["All"] + list(districts)
        )

    with col3:

        health_filter = st.selectbox(
            "Health Category",
            [
                "All",
                "QC LGU",
                "National",
                "Health Center",
                "Super Health"
            ]
        )

    # --------------------------------------------------
    # DATA FILTERING
    # --------------------------------------------------

    hc = health_centers.copy()
    opc = older_person_care.copy()

    if selected_district != "All":

        hc = hc[
            hc["District"] == selected_district
        ]

        opc = opc[
            opc["district"].astype(str)
            == selected_district
        ]

    if health_filter != "All":

        hc = hc[
            hc["Category"]
            .str.contains(
                health_filter,
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------
    # COLOR FUNCTIONS
    # --------------------------------------------------

    def health_color(category):

        category = str(category).upper()

        if "QC LGU" in category:
            return "#E41A1C"

        elif "NATIONAL" in category:
            return "#377EB8"

        elif "SUPER HEALTH" in category:
            return "#FFCC00"

        elif "HEALTH CENTER" in category:
            return "#4DAF4A"

        return "#999999"


    def senior_color(category):

        category = str(category).upper()

        if "NURSING" in category:
            return "#984EA3"

        elif "BAHAY ARUGA" in category:
            return "#FF7F00"

        return "#999999"

    # --------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "selected_explorer_item" not in st.session_state:

        st.session_state.selected_explorer_item = None

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    map_col, info_col = st.columns([4, 1])

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    folium.GeoJson(
        geo,
        style_function=lambda x: {
            "fillColor": "#7fbf7f",
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.15,
        }
    ).add_to(m)

    # --------------------------------------------------
    # HEALTH FACILITIES
    # --------------------------------------------------

    if show_health:

        for _, row in hc.iterrows():

            popup_html = f"""
            <b>{row['Name of Facility']}</b><br>
            Category: {row['Category']}<br>
            District: {row['District']}<br>
            Pharmacy: {'Yes' if row['Has Pharmacy'] else 'No'}
            """

            folium.CircleMarker(
                location=[
                    row["latitude"],
                    row["longitude"]
                ],
                radius=5,
                color=health_color(row["Category"]),
                fill=True,
                fill_color=health_color(row["Category"]),
                fill_opacity=0.9,
                weight=2,
                popup=popup_html,
                tooltip=row["Name of Facility"]
            ).add_to(m)

    # --------------------------------------------------
    # OLDER PERSONS FACILITIES
    # --------------------------------------------------

    if show_senior:

        for _, row in opc.iterrows():

            popup_html = f"""
            <b>{row['name']}</b><br>
            Category: {row['category']}<br>
            District: {row['district']}<br>
            Barangay: {row['barangay']}
            """

            folium.CircleMarker(
                location=[
                    row["latitude"],
                    row["longitude"]
                ],
                radius=5,
                color=senior_color(row["category"]),
                fill=True,
                fill_color=senior_color(row["category"]),
                fill_opacity=0.9,
                weight=2,
                popup=popup_html,
                tooltip=row["name"]
            ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    with map_col:

        map_data = st_folium(
            m,
            height=700,
            returned_objects=["last_object_clicked"]
        )

    # --------------------------------------------------
    # CLICK DETECTION
    # --------------------------------------------------

    if map_data and map_data.get("last_object_clicked"):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        candidates = []

        if show_health:

            tmp = hc.copy()
            tmp["source"] = "Health Facility"

            tmp["distance"] = (
                (tmp["latitude"] - clicked_lat) ** 2 +
                (tmp["longitude"] - clicked_lon) ** 2
            )

            candidates.append(tmp)

        if show_senior:

            tmp = opc.copy()
            tmp["source"] = "Older Persons Facility"

            tmp["distance"] = (
                (tmp["latitude"] - clicked_lat) ** 2 +
                (tmp["longitude"] - clicked_lon) ** 2
            )

            candidates.append(tmp)

        if len(candidates):

            all_points = pd.concat(
                candidates,
                ignore_index=True
            )

            st.session_state.selected_explorer_item = (
                all_points.loc[
                    all_points["distance"].idxmin()
                ]
            )

    # --------------------------------------------------
    # INFO PANEL
    # --------------------------------------------------

    with info_col:

        st.subheader("Facility Details")

        item = st.session_state.selected_explorer_item

        if item is not None:

            if item["source"] == "Health Facility":

                st.markdown(
                    f"### {item['Name of Facility']}"
                )

                st.write(
                    f"**Category:** {item['Category']}"
                )

                st.write(
                    f"**District:** {item['District']}"
                )

                st.write(
                    f"**Address:** {item['Address']}"
                )

            else:

                st.markdown(
                    f"### {item['name']}"
                )

                st.write(
                    f"**Category:** {item['category']}"
                )

                st.write(
                    f"**District:** {item['district']}"
                )

                st.write(
                    f"**Barangay:** {item['barangay']}"
                )

                st.write(
                    f"**Address:** {item['address']}"
                )

        else:

            st.info(
                "Click a facility on the map."
            )

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    st.divider()

    c1, c2 = st.columns(2)

    c1.metric(
        "Health Facilities",
        len(hc) if show_health else 0
    )

    c2.metric(
        "Older Persons Facilities",
        len(opc) if show_senior else 0
    )
