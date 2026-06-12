import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
import pydeck as pdk
from streamlit_folium import st_folium

from functions import *

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
                Quezon Caring City Dashboard
            </h1>
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
    older_person_care, 
    schools,
    long_term_care,
    satellite_offices
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
# CLEANING
# --------------------------------------------------
health_centers = clean_health_centers(health_centers)
childcare_centers = clean_dataframe(childcare_centers)
schools = clean_dataframe(schools)
long_term_care = clean_dataframe(long_term_care)
satellite_offices = clean_dataframe(satellite_offices)
# --------------------------------------------------
# KPI VALUES
# --------------------------------------------------

population = int(
    city_kpis.loc[
        city_kpis["indicator"] == "population_2024",
        "value"
    ].iloc[0]
)

child_centers = int(
    childcare_summary.loc[
        childcare_summary["metric"] == "child_development_centers",
        "value"
    ].iloc[0]
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

st.markdown("""
<style>
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color:#7F47ED !important;
}
</style>
""", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Section",
    [
        "Childcare Centers",
        "Schools", 
        "Health Centers Map",
        "Older Persons Center Map",
        "Long-Term Care & Rehabilitation",
        "Satellite Offices",
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
            "Super Health",
            "Health Center",
            "Pharmacy",
            "Milk Bank"
        ]
    )

    category_descriptions = {
        "QC LGU":
            "LGU-run hospitals and lying-in clinics.",

        "National":
            "National government-owned hospitals.",

        "Super Health":
            "Enhanced primary healthcare facilities.",

        "Health Center":
            "Community-based primary healthcare centers.",

        "Pharmacy":
            "Health center pharmacy facilities.",

        "Milk Bank":
            "Human milk bank services."
    }

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Facility Categories")

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
            ">●</span>
            <b>{cat}</b><br>
            <small>{category_descriptions[cat]}</small>
            """,
            unsafe_allow_html=True
        )

if page == "Childcare Centers":

    selected_childcare_sector = st.sidebar.radio(
        "Provider Type",
        [
            "All",
            "Public",
            "Private"
        ]
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
        category_options
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Facility Categories")

    st.sidebar.markdown(
        """
        <span style="color:#5B21B6;font-size:22px;">●</span>
        <b>Child Development Center</b><br>
        <small>Public childcare and early childhood development services.</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#7F47ED;font-size:22px;">●</span>
        <b>Child Learning Center</b><br>
        <small>Private childcare and early learning services.</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#A78BFA;font-size:22px;">●</span>
        <b>Day Care Center</b><br>
        <small>Private day care and supervision services.</small>
        """,
        unsafe_allow_html=True
    )

if page == "Older Persons Center Map":

    selected_opc_category = st.sidebar.radio(
        "Facility Type",
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
        <span style="color:#4C1D95;font-size:22px;">●</span>
        <b>Nursing Care Center</b><br>
        <small>Residential facilities providing long-term nursing and care services.</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#A78BFA;font-size:22px;">●</span>
        <b>Bahay Aruga</b><br>
        <small>Temporary accommodation and support services for vulnerable older persons.</small>
        """,
        unsafe_allow_html=True
    )

if page == "Schools":

    selected_school_sector = st.sidebar.radio(
        "Provider Type",
        [
            "All",
            "Public",
            "Private"
        ]
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
        category_options
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### School Categories")

    st.sidebar.markdown(
        """
        <span style="color:#5B21B6;font-size:22px;">●</span>
        <b>Public School</b><br>
        <small>Government-operated educational institutions.</small>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <span style="color:#A78BFA;font-size:22px;">●</span>
        <b>Private School</b><br>
        <small>Privately operated educational institutions.</small>
        """,
        unsafe_allow_html=True
    )

if page == "Long-Term Care & Rehabilitation":

    ltc_categories = sorted(
        long_term_care["Category"]
        .dropna()
        .unique()
    )

    selected_ltc_category = st.sidebar.radio(
        "Facility Category",
        ["All"] + list(ltc_categories)
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Facility Categories")

    for cat in ltc_categories:

        st.sidebar.markdown(
            f"""
            <span style="
                color:{ltc_color(cat)};
                font-size:22px;
            ">●</span>
            <b>{cat}</b>
            """,
            unsafe_allow_html=True
        )

if page == "Satellite Offices":

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        Satellite offices provide decentralized access
        to city government services across Quezon City.
        """
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

# --------------------------------------------------
# PAGES
# --------------------------------------------------

elif page == "Childcare Centers":

    st.title("Child Care Facilities")

    st.markdown("""
    Explore the spatial distribution of childcare facilities in Quezon City,
    including public Child Development Centers and private childcare providers.
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
        "District",
        ["All"] + list(districts)
    )

    # --------------------------------------------------
    # DATA FILTERING
    # --------------------------------------------------

    cc = childcare_centers.copy()

    if selected_district != "All":

        cc = cc[
            cc["District"].astype(int)
            == selected_district
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
    # COLORS
    # --------------------------------------------------

    def childcare_color(category):

        category = str(category).upper()

        if "CHILD DEVELOPMENT" in category:
            return "#5B21B6"

        elif "CHILD LEARNING" in category:
            return "#7F47ED"

        elif "DAY CARE" in category:
            return "#A78BFA"

        return "#DDD6FE"

    # --------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "selected_childcare_facility" not in st.session_state:

        st.session_state.selected_childcare_facility = None

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
    # MARKERS
    # --------------------------------------------------

    for _, row in cc.iterrows():

        popup_html = f"""
        <b>{row['Name']}</b><br>
        Sector: {row['Sector']}<br>
        Category: {row['Category']}<br>
        District: {int(row['District'])}<br>
        Address: {row['Address']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=4,
            color=childcare_color(row["Category"]),
            fill=True,
            fill_color=childcare_color(row["Category"]),
            fill_opacity=0.9,
            weight=2,
            popup=popup_html,
            tooltip=row["Name"]
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

    if (
        map_data
        and map_data.get("last_object_clicked")
    ):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        tmp = cc.copy()

        tmp["distance"] = (
            (tmp["latitude"] - clicked_lat) ** 2 +
            (tmp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_childcare_facility = (
            tmp.loc[
                tmp["distance"].idxmin()
            ]
        )

    # --------------------------------------------------
    # INFO PANEL
    # --------------------------------------------------

    with info_col:

        st.subheader("Facility Details")

        if st.session_state.selected_childcare_facility is not None:

            facility = (
                st.session_state.selected_childcare_facility
            )

            st.markdown(
                f"### {facility['Name']}"
            )

            st.write(
                f"**Sector:** {facility['Sector']}"
            )

            st.write(
                f"**Category:** {facility['Category']}"
            )

            st.write(
                f"**District:** {int(facility['District'])}"
            )

            st.write(
                f"**Address:** {facility['Address']}"
            )

            if (
                "open_hours" in facility.index
                and "close_hours" in facility.index
                and pd.notna(facility["open_hours"])
                and pd.notna(facility["close_hours"])
            ):

                st.write(
                    f"**Hours:** {facility['open_hours']} – {facility['close_hours']}"
                )

            elif (
                "open_hours" in facility.index
                and pd.notna(facility["open_hours"])
            ):

                st.write(
                    f"**Opens:** {facility['open_hours']}"
                )

            elif (
                "close_hours" in facility.index
                and pd.notna(facility["close_hours"])
            ):

                st.write(
                    f"**Closes:** {facility['close_hours']}"
                )

        else:

            st.info(
                "Click a facility on the map."
            )

    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Facilities",
        len(cc)
    )

    c2.metric(
        "Public",
        len(
            cc[
                cc["Sector"]
                .str.contains(
                    "Public",
                    case=False,
                    na=False
                )
            ]
        )
    )

    c3.metric(
        "Private",
        len(
            cc[
                cc["Sector"]
                .str.contains(
                    "Private",
                    case=False,
                    na=False
                )
            ]
        )
    )

    # --------------------------------------------------
    # CATEGORY SUMMARY
    # --------------------------------------------------

    st.subheader("Facilities by Category")

    category_summary = (
        cc.groupby("Category")
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
    )

    TEAL_SCALE = [
        "#DDD6FE",
        "#C4B5FD",
        "#A78BFA",
        "#7F47ED",
        "#5B21B6"
    ]

    fig = px.bar(
        category_summary,
        x="count",
        y="Category",
        orientation="h",
        text="count",
        color="count",
        color_continuous_scale=TEAL_SCALE
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
        cc[
            [
                "Name",
                "Sector",
                "Category",
                "District",
                "Address"
            ]
        ],
        use_container_width=True
    )

# --------------------------------------------------
# SCHOOLS
# --------------------------------------------------

if page == "Schools":

    st.title("Schools")

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
        .astype(str)
        .unique()
    )

    selected_district = st.selectbox(
        "District",
        ["All"] + list(districts)
    )

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    sch = schools.copy()

    if selected_district != "All":

        sch = sch[
            sch["District"].astype(int)
            == selected_district
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

    sch_map = sch.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # COLORS
    # --------------------------------------------------

    def school_color(category):

        category = str(category).upper()

        if "PUBLIC SCHOOL" in category:
            return "#5B21B6"

        elif "PRIVATE SCHOOL" in category:
            return "#A78BFA"

        return "#DDD6FE"

    # --------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "selected_school" not in st.session_state:

        st.session_state.selected_school = None

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
    # MARKERS
    # --------------------------------------------------

    for _, row in sch_map.iterrows():

        popup_html = f"""
        <b>{row['Name']}</b><br>
        Sector: {row['Sector']}<br>
        Category: {row['Category']}<br>
        District: {int(row['District'])}<br>
        Address: {row['Address']}
        """

        if pd.notna(row.get("open_hours")):
            popup_html += f"<br>Open: {row['open_hours']}"

        if pd.notna(row.get("close_hours")):
            popup_html += f"<br>Close: {row['close_hours']}"

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=4,
            color=school_color(row["Category"]),
            fill=True,
            fill_color=school_color(row["Category"]),
            fill_opacity=0.9,
            weight=2,
            popup=popup_html,
            tooltip=row["Name"]
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

    if (
        map_data
        and map_data.get("last_object_clicked")
    ):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        tmp = sch_map.copy()

        tmp["distance"] = (
            (tmp["latitude"] - clicked_lat) ** 2 +
            (tmp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_school = (
            tmp.loc[
                tmp["distance"].idxmin()
            ]
        )

    # --------------------------------------------------
    # INFO PANEL
    # --------------------------------------------------

    with info_col:

        st.subheader("School Details")

        if st.session_state.selected_school is not None:

            facility = st.session_state.selected_school

            st.markdown(
                f"### {facility['Name']}"
            )

            st.write(
                f"**Sector:** {facility['Sector']}"
            )

            st.write(
                f"**Category:** {facility['Category']}"
            )

            st.write(
                f"**District:** {int(facility['District'])}"
            )

            st.write(
                f"**Address:** {facility['Address']}"
            )

            if pd.notna(facility.get("open_hours")):
                st.write(
                    f"**Open:** {facility['open_hours']}"
                )

            if pd.notna(facility.get("close_hours")):
                st.write(
                    f"**Close:** {facility['close_hours']}"
                )

        else:

            st.info(
                "Click a school on the map."
            )

    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Schools",
        len(sch)
    )

    c2.metric(
        "Public",
        len(
            sch[
                sch["Sector"]
                .str.contains(
                    "Public",
                    case=False,
                    na=False
                )
            ]
        )
    )

    c3.metric(
        "Private",
        len(
            sch[
                sch["Sector"]
                .str.contains(
                    "Private",
                    case=False,
                    na=False
                )
            ]
        )
    )

    # --------------------------------------------------
    # CATEGORY SUMMARY
    # --------------------------------------------------

    PURPLE_SCALE = [
        "#DDD6FE",
        "#C4B5FD",
        "#A78BFA",
        "#7F47ED",
        "#5B21B6"
    ]

    st.subheader("Schools by Category")

    category_summary = (
        sch.groupby("Category")
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
    )

    color_map = {
    cat: ltc_color(cat)
    for cat in category_summary["Category"]
    }

    fig = px.bar(
            category_summary,
            x="count",
            y="Category",
            orientation="h",
            text="count",
            color="Category",
            color_discrete_map=color_map
    )


    fig.update_layout(
        height=400,
        yaxis_title="",
        xaxis_title="Schools"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
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
        use_container_width=True
    )

elif page == "Health Centers Map":

    st.title("Health Centers & Hospitals") 
    
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

        hc = hc[
                hc["Category"]
                .str.contains(
                    selected_category,
                    case=False,
                    na=False
                )
            ]

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
            return "#4C1D95"

        elif "NATIONAL" in category:
            return "#5B21B6"

        elif "SUPER HEALTH" in category:
            return "#7F47ED"

        elif "HEALTH CENTER" in category:
            return "#A78BFA"

        elif "PHARMACY" in category:
            return "#C4B5FD"

        elif "MILK BANK" in category:
            return "#DDD6FE"

        return "#EDE9FE"


    # --------------------------------------------------
    # MARKERS
    # --------------------------------------------------

    for _, row in hc.iterrows():

        popup_html = f"""
        <b>{row['Name of Facility']}</b><br>
        Category: {row['Category']}<br>
        District: {row['District'].split(" ")[1]}<br>
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
                f"**District:** {int(facility['District'])}"
            )

            if "barangay" in facility.index:
                st.write(
                    f"**Barangay:** {facility['barangay']}"
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

    c1, c2 = st.columns(2)

    c1.metric(
        "Facilities",
        len(hc)
    )

    c2.metric(
        "Categories",
        hc["Category"].nunique()
    )

    # --------------------------------------------------
    # CATEGORY SUMMARY
    # --------------------------------------------------

    PURPLE_SCALE = [
    "#DDD6FE",
    "#C4B5FD",
    "#A78BFA",
    "#7F47ED",
    "#5B21B6"
    ]

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
    text="count",
    color="count",
    color_continuous_scale=PURPLE_SCALE
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
                "Address"
            ]
        ],
        use_container_width=True
    )

elif page == "Older Persons Center Map":

    st.title("Older Persons & Senior Citizens")

    st.caption(
        """
        Interactive map of facilities supporting older persons in Quezon City,
        including nursing care centers and Bahay Aruga facilities.
        """
    )

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
            return "#5B21B6"

        elif "BAHAY ARUGA" in category:
            return "#A78BFA"

        return "#DDD6FE"

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
        <b>{row['name_original']}</b><br>
        Category: {row['category']}<br>
        District: {int(row['district'])}<br>
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
            tooltip=row["name_original"]
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
                f"### {facility['name_original']}"
            )

            st.write(
                f"**Category:** {facility['category']}"
            )

            st.write(
                f"**District:** {int(facility['district'])}"
            )

            st.write(
                f"**Barangay:** {facility['barangay']}"
            )

            st.write(
                f"**Address:** {facility['address']}"
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
                "name_original",
                "district",
                "barangay",
                "category",
                "address"
            ]
        ],
        use_container_width=True
    )

elif page == "Long-Term Care & Rehabilitation":

    st.title(
        "Long-Term Care & Rehabilitation Services"
    )

    st.markdown("""
    Explore facilities providing long-term care,
    rehabilitation, therapy, and specialized
    recovery services in Quezon City.
    """)

    # ----------------------------------
    # DISTRICT FILTER
    # ----------------------------------

    districts = sorted(
        long_term_care["District"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_district = st.selectbox(
        "District",
        ["All"] + list(districts)
    )

    # ----------------------------------
    # FILTERING
    # ----------------------------------

    ltc = long_term_care.copy()

    if selected_district != "All":

        ltc = ltc[
            ltc["District"].astype(int)
            == selected_district
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

    # ----------------------------------
    # COORDINATES
    # ----------------------------------

    missing_locations = (
        ltc["latitude"].isna() |
        ltc["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} facilities do not have coordinates and are not shown on the map."
        )

    ltc_map = ltc.dropna(
        subset=["latitude", "longitude"]
    )

    # ----------------------------------
    # MAP CENTER
    # ----------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # ----------------------------------
    # SESSION STATE
    # ----------------------------------

    if "selected_ltc" not in st.session_state:

        st.session_state.selected_ltc = None

    map_col, info_col = st.columns([4, 1])

    # ----------------------------------
    # MAP
    # ----------------------------------

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

    # ----------------------------------
    # MARKERS
    # ----------------------------------

    for _, row in ltc_map.iterrows():

        popup_html = f"""
        <b>{row['Name']}</b><br>
        Category: {row['Category']}<br>
        District: {int(row['District'])}<br>
        Address: {row['Address']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=4,
            color=ltc_color(row["Category"]),
            fill=True,
            fill_color=ltc_color(row["Category"]),
            fill_opacity=0.9,
            weight=2,
            popup=popup_html,
            tooltip=row["Name"]
        ).add_to(m)

    with map_col:

        map_data = st_folium(
            m,
            height=700,
            returned_objects=["last_object_clicked"]
        )

    # ----------------------------------
    # CLICK DETECTION
    # ----------------------------------

    if (
        map_data
        and map_data.get("last_object_clicked")
    ):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        tmp = ltc_map.copy()

        tmp["distance"] = (
            (tmp["latitude"] - clicked_lat) ** 2 +
            (tmp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_ltc = (
            tmp.loc[
                tmp["distance"].idxmin()
            ]
        )

    # ----------------------------------
    # INFO PANEL
    # ----------------------------------

    with info_col:

        st.subheader("Facility Details")

        if st.session_state.selected_ltc is not None:

            facility = st.session_state.selected_ltc

            st.markdown(
                f"### {facility['Name']}"
            )

            st.write(
                f"**Category:** {facility['Category']}"
            )

            st.write(
                f"**District:** {int(facility['District'])}"
            )

            st.write(
                f"**Address:** {facility['Address']}"
            )

        else:

            st.info(
                "Click a facility on the map."
            )

    # ----------------------------------
    # KPIs
    # ----------------------------------

    st.divider()

    c1, c2 = st.columns(2)

    c1.metric(
        "Facilities",
        len(ltc)
    )

    c2.metric(
        "Facility Types",
        ltc["Category"].nunique()
    )

    # ----------------------------------
    # CATEGORY SUMMARY
    # ----------------------------------

    PURPLE_SCALE = [
        "#DDD6FE",
        "#C4B5FD",
        "#A78BFA",
        "#7F47ED",
        "#5B21B6"
    ]

    st.subheader(
        "Facilities by Category"
    )

    category_summary = (
        ltc.groupby("Category")
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
        text="count",
        color="count",
        color_continuous_scale=PURPLE_SCALE
    )

    st.plotly_chart(
        fig,
        use_container_width=True
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
        use_container_width=True
    )

elif page == "Satellite Offices":

    st.title(
        "Quezon City Satellite Offices"
    )

    st.caption(
        """
        Explore the distribution of Quezon City
        satellite offices providing local access
        to government services.
        """
    )

    # ----------------------------------
    # DISTRICT FILTER
    # ----------------------------------

    districts = sorted(
        satellite_offices["District"]
        .dropna()
        .unique()
    )

    selected_district = st.selectbox(
        "District",
        ["All"] + list(districts)
    )

    # ----------------------------------
    # FILTERING
    # ----------------------------------

    sat = satellite_offices.copy()

    if selected_district != "All":

        sat = sat[
            sat["District"]
            == selected_district
        ]

    # ----------------------------------
    # COORDINATES
    # ----------------------------------

    missing_locations = (
        sat["latitude"].isna() |
        sat["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} offices do not have coordinates and are not shown on the map."
        )

    sat_map = sat.dropna(
        subset=["latitude", "longitude"]
    )

    # ----------------------------------
    # MAP CENTER
    # ----------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # ----------------------------------
    # SESSION STATE
    # ----------------------------------

    if "selected_satellite_office" not in st.session_state:

        st.session_state.selected_satellite_office = None

    map_col, info_col = st.columns([4, 1])

    # ----------------------------------
    # MAP
    # ----------------------------------

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

    # ----------------------------------
    # MARKERS
    # ----------------------------------

    for _, row in sat_map.iterrows():

        popup_html = f"""
        {row['Category']}<br>
        Address: {row['Address']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=5,
            color=district_color(row["District"]),
            fill=True,
            fill_color=district_color(row["District"]),
            fill_opacity=0.9,
            weight=2,
            popup=popup_html,
            tooltip=row["Category"]
        ).add_to(m)

    with map_col:

        map_data = st_folium(
            m,
            height=700,
            returned_objects=["last_object_clicked"]
        )

    # ----------------------------------
    # CLICK DETECTION
    # ----------------------------------

    if (
        map_data
        and map_data.get("last_object_clicked")
    ):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        tmp = sat_map.copy()

        tmp["distance"] = (
            (tmp["latitude"] - clicked_lat) ** 2 +
            (tmp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_satellite_office = (
            tmp.loc[
                tmp["distance"].idxmin()
            ]
        )

    # ----------------------------------
    # INFO PANEL
    # ----------------------------------

    with info_col:

        st.subheader("Office Details")

        if (
            st.session_state.selected_satellite_office
            is not None
        ):

            office = (
                st.session_state.selected_satellite_office
            )

            st.write(
                f"**District:** {int(office['District'])}"
            )

            st.write(
                f"**Address:** {office['Address']}"
            )

        else:

            st.info(
                "Click an office on the map."
            )

    # ----------------------------------
    # KPIs
    # ----------------------------------

    st.divider()

    c1, c2 = st.columns(2)

    c1.metric(
        "Satellite Offices",
        len(sat)
    )

    c2.metric(
        "Districts Covered",
        sat["District"].nunique()
    )

    # ----------------------------------
    # TABLE
    # ----------------------------------

    st.subheader("Satellite Offices")

    st.dataframe(
        sat[
            [
                "Name",
                "District",
                "Address"
            ]
        ],
        use_container_width=True
    )

elif page == "Care Services Explorer":

    st.title("🗺️ Care Services Explorer")

    st.caption(
        """
        Explore childcare centers, schools, health facilities,
        older persons facilities, rehabilitation centers, and
        Quezon City satellite offices on a single map.
        """
    )

    st.write("Childcare:", len(childcare_centers))
    st.write("Schools:", len(schools))
    st.write("Long Term Care:", len(long_term_care))
    st.write("Satellite:", len(satellite_offices))
    st.write("Health:", len(health_centers))
    st.write("Older Persons:", len(older_person_care))

    # --------------------------------------------------
    # SERVICE CONFIGURATION
    # --------------------------------------------------

    service_layers = {

        "Childcare Centers": {
            "df": childcare_centers,
            "color": "#E41A1C",
            "source": "Childcare Center",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Schools": {
            "df": schools,
            "color": "#377EB8",
            "source": "School",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Health Centers": {
            "df": health_centers,
            "color": "#4DAF4A",
            "source": "Health Facility",
            "name_col": "Name of Facility",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Older Persons Facilities": {
            "df": older_person_care,
            "color": "#984EA3",
            "source": "Older Persons Facility",
            "name_col": "name_original",
            "district_col": "district",
            "address_col": "address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Long-Term Care & Rehabilitation": {
            "df": long_term_care,
            "color": "#FF7F00",
            "source": "Rehabilitation Facility",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        },

        "Satellite Offices": {
            "df": satellite_offices,
            "color": "#A65628",
            "source": "Satellite Office",
            "name_col": "Name",
            "district_col": "District",
            "address_col": "Address",
            "lat_col": "latitude",
            "lon_col": "longitude"
        }
    }

    # --------------------------------------------------
    # LEGEND
    # --------------------------------------------------

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown("🔴 Childcare")

    with c2:
        st.markdown("🔵 Schools")

    with c3:
        st.markdown("🟢 Health")

    with c4:
        st.markdown("🟣 Older Persons")

    with c5:
        st.markdown("🟠 Rehab")

    with c6:
        st.markdown("🟤 Satellite")

    st.divider()

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    col1, col2 = st.columns([2, 1])

    with col1:

        selected_layers = st.multiselect(
            "Services to Display",
            list(service_layers.keys()),
            default=[
                "Health Centers",
                "Older Persons Facilities"
            ]
        )

    with col2:

        districts = sorted(
            health_centers["District"]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_district = st.selectbox(
            "District",
            ["All"] + list(districts)
        )

    # --------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------

    if "selected_explorer_item" not in st.session_state:
        st.session_state.selected_explorer_item = None

    # --------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------

    minx, miny, maxx, maxy = geo.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

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
            "fillOpacity": 0.10,
        }
    ).add_to(m)

    # --------------------------------------------------
    # STORE FILTERED DATA
    # --------------------------------------------------

    filtered_layers = {}

    # --------------------------------------------------
    # PLOT LAYERS
    # --------------------------------------------------

    for layer_name in selected_layers:

        layer = service_layers[layer_name]

        df = layer["df"].copy()

        if selected_district != "All":

            district_col = layer["district_col"]

            df = df[
                df[district_col]
                .astype(str)
                == selected_district
            ]

        filtered_layers[layer_name] = df

        for _, row in df.iterrows():

            popup_html = f"""
            <b>{row[layer['name_col']]}</b><br>
            Type: {layer['source']}<br>
            District: {row[layer['district_col']]}
            """

            folium.CircleMarker(
                location=[
                    row[layer["lat_col"]],
                    row[layer["lon_col"]]
                ],
                radius=6,
                color=layer["color"],
                fill=True,
                fill_color=layer["color"],
                fill_opacity=0.9,
                weight=2,
                popup=popup_html,
                tooltip=str(
                    row[layer["name_col"]]
                )
            ).add_to(m)

    # --------------------------------------------------
    # DISPLAY MAP
    # --------------------------------------------------

    with map_col:

        map_data = st_folium(
            m,
            height=750,
            returned_objects=["last_object_clicked"]
        )

    # --------------------------------------------------
    # CLICK DETECTION
    # --------------------------------------------------

    if map_data and map_data.get("last_object_clicked"):

        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        candidates = []

        for layer_name in selected_layers:

            layer = service_layers[layer_name]

            df = filtered_layers[layer_name].copy()

            if len(df) == 0:
                continue

            df["source"] = layer["source"]
            df["name_field"] = layer["name_col"]
            df["address_field"] = layer["address_col"]
            df["district_field"] = layer["district_col"]

            df["distance"] = (
                (df[layer["lat_col"]] - clicked_lat) ** 2 +
                (df[layer["lon_col"]] - clicked_lon) ** 2
            )

            candidates.append(df)

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

        st.subheader("Details")

        item = st.session_state.selected_explorer_item

        if item is not None:

            st.markdown(
                f"### {item[item['name_field']]}"
            )

            st.write(
                f"**Type:** {item['source']}"
            )

            st.write(
                f"**District:** {item[item['district_field']]}"
            )

            if item["address_field"] in item.index:

                st.write(
                    f"**Address:** {item[item['address_field']]}"
                )

            if "barangay" in item.index:

                st.write(
                    f"**Barangay:** {item['barangay']}"
                )

            if "Category" in item.index:

                st.write(
                    f"**Category:** {item['Category']}"
                )

            if "category" in item.index:

                st.write(
                    f"**Category:** {item['category']}"
                )

        else:

            st.info(
                "Click a facility on the map."
            )

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    st.divider()

    cols = st.columns(
        max(1, len(selected_layers))
    )

    for i, layer_name in enumerate(selected_layers):

        cols[i].metric(
            layer_name,
            len(filtered_layers[layer_name])
        )
