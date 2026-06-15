import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import numpy as np
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

# --------------------------------------------------
# LOGOS ROW
# --------------------------------------------------

fcdo_logo = get_base64("assets/fcdo_logo.webp")
un_logo   = get_base64("assets/unwomen_logo.png")
qc_logo   = get_base64("assets/qc_logo.png")

left_col, spacer_col, right_col = st.columns([3, 6, 1])

with left_col:

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:20px;
            height:70px;
        ">
        <a href="https://www.gov.uk/government/organisations/foreign-commonwealth-development-office"
               target="_blank">
                <img src="data:image/webp;base64,{fcdo_logo}" height="75">
        </a>
        <a href="https://www.unwomen.org/en"
               target="_blank">
                <img src="data:image/png;base64,{un_logo}" height="60">
        </a>

        </div>
        """,
        unsafe_allow_html=True
    )

with right_col:

    st.markdown(
        f"""
        <div style="
            display:flex;
            justify-content:flex-end;
            align-items:center;
            height:70px;
        ">
            <a href="https://quezoncity.gov.ph/" target="_blank">
                <img src="data:image/png;base64,{qc_logo}" height="50">
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
        font-size:3.0rem;
        margin-top:5px;
        margin-bottom:15px;
        line-height:1.1;
    ">
        Quezon Caring City Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

(
    geo, 
    childcare_centers,
    schools,
    health_centers,
    older_person_care, 
    long_term_care,
    satellite_offices,
    migration_centers
) = load_data()

# --------------------------------------------------
# CLEANING
# --------------------------------------------------

health_centers    = clean_health_centers(health_centers)
childcare_centers = clean_dataframe(childcare_centers)
schools           = clean_dataframe(schools)
older_person_care    = clean_dataframe(older_person_care)
long_term_care    = clean_dataframe(long_term_care)
satellite_offices = clean_dataframe(satellite_offices)
satellite_offices["Name"] = "District " + satellite_offices["District"].astype(int).astype(str)
migration_centers = clean_dataframe(migration_centers)

# --------------------------------------------------
# QC CENTER
# --------------------------------------------------

minx, miny, maxx, maxy = geo.total_bounds

center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2

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
    "Available Care Maps",
    [
        "Childcare Centers",
        "Schools", 
        "Health Centers Map",
        "Older Persons Center Map",
        "Long-Term Care & Rehabilitation",
        "Satellite Offices",
        "Migration Resource Center",
        "Care Services Explorer"
    ]
)

selected_category = "All"

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
        <small>For children aged 3 to 4 years. The program focuses on providing children with early childhood education to support their growth and readiness for more formal education. 
        </small>
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
            "Lying–in Clinics are maternity clinics for healthy pregnant women as an option for an affordable, if not free, cost of pregnancy and childbirth. If a pregnant woman is at high risk, however, she will be referred to deliver the child at a hospital.",

        "National":
            "National government-owned hospitals located in Quezon City.",

        "Super Health":
            "These facilities serve both as a Health Center and a 24-hour operating Lying–in clinic and also provide basic health services.  Super Health Centers possess the necessary equipment for medical needs such as laboratory, dental services, breastfeeding services, lying-in clinic, and an ambulance.",

        "Health Center":
            "Health Centers are community patient-directed establishments that deliver comprehensive culturally competent, high-quality, primary healthcare services to the nation’s most vulnerable individuals and families, including people experiencing homelessness, agricultural workers, and residents of public housing and veterans.",

        "Pharmacy":
            "Health center pharmacy facilities.",

        "Milk Bank":
            "provides safe, pasteurized human milk to infants in need, especially premature babies and those whose mothers struggle with lactation or medical issues. Under the program, QCitizens may donate and receive milk at designated milk depots in the city."
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

if page == "Older Persons Center Map":

    selected_opc_category = st.sidebar.radio(
        "Facility Type",
        [
            "All",
            "Nursing Care Center",
            "Bahay Aruga for Abandoned Elderly"
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
        <small>Temporary residential facility for abandoned, neglected, abused, and indigent QC senior citizens aged 60 years and above. </small>
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

if page == "Migration Resource Center":

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Facility Type")

    st.sidebar.markdown(
        """
        <span style="color:#7F47ED;font-size:22px;">●</span>
        <b>QC Migrants Resource Center</b><br>
        <small>
        Provides support, information, training, and services for migrant workers and their families.
        </small>
        """,
        unsafe_allow_html=True
    )

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
    st.sidebar.markdown("## Satellite Offices")

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

if page == "Childcare Centers":

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
    # SESSION STATE
    # --------------------------------------------------

    if "selected_childcare_facility" not in st.session_state:

        st.session_state.selected_childcare_facility = None

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    map_col, info_col = st.columns([2, 1])

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
            popup=folium.Popup(popup_html, max_width=350),
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

elif page == "Schools":

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
        .astype(int)
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
    # SESSION STATE
    # --------------------------------------------------

    if "selected_school" not in st.session_state:

        st.session_state.selected_school = None

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    map_col, info_col = st.columns([2, 1])

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
            popup=folium.Popup(popup_html, max_width=350),
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
    # SESSION STATE
    # --------------------------------------------------

    if "selected_facility" not in st.session_state:
        st.session_state.selected_facility = None

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    map_col, info_col = st.columns([2, 1])

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
    # MARKERS
    # --------------------------------------------------

    for _, row in hc.iterrows():

        popup_html = f"""
        <b>{row['Name of Facility']}</b><br>
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
            color=marker_color(row["Category"]),
            fill=True,
            fill_color=marker_color(row["Category"]),
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(popup_html, max_width=350),
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
        width = 'stretch'
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
        "District",
        ["All"] + district_options,
        key="opc_district"
    )

    opc = older_person_care.copy()

    if selected_district != "All":

        opc = opc[
            opc["District"].astype(int)
            == selected_district
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
    # SESSION STATE
    # --------------------------------------------------

    if "selected_senior_facility" not in st.session_state:

        st.session_state.selected_senior_facility = None

    map_col, info_col = st.columns([2, 1])

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
        <b>{row['Name']}</b><br>
        Category: {row['Category']}<br>
        District: {int(row['District'])}<br>
        Barangay: {row['barangay']}<br>
        Address: {row['Address']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=5,
            color=opc_color(row["Category"]),
            fill=True,
            fill_color=opc_color(row["Category"]),
            fill_opacity=0.9,
            weight=5,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=row["Name"]
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
                f"### {facility['Name']}"
            )

            st.write(
                f"**Category:** {facility['Category']}"
            )

            st.write(
                f"**District:** {int(facility['District'])}"
            )

            st.write(
                f"**Barangay:** {facility['barangay']}"
            )

            st.write(
                f"**Address:** {facility['Address']}"
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
                "Name",
                "District",
                "Category",
                "Address"
            ]
        ],
        width = 'stretch'
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
    # SESSION STATE
    # ----------------------------------

    if "selected_ltc" not in st.session_state:

        st.session_state.selected_ltc = None

    map_col, info_col = st.columns([2, 1])

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
            popup=folium.Popup(popup_html, max_width=350),
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
        .astype(int)
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
    # SESSION STATE
    # ----------------------------------

    if "selected_satellite_office" not in st.session_state:

        st.session_state.selected_satellite_office = None

    map_col, info_col = st.columns([2, 1])

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
            popup=folium.Popup(popup_html, max_width=350),
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
    # TABLE
    # ----------------------------------

    st.subheader("Satellite Offices")

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

    st.title("Migration Resource Center")

    st.markdown("""
    Explore facilities providing information, training,
    referral services, and support for migrant workers
    and their families in Quezon City.
    """)

    # ----------------------------------
    # DISTRICT FILTER
    # ----------------------------------

    districts = sorted(
        migration_centers["District"]
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

    mig = migration_centers.copy()

    if selected_district != "All":

        mig = mig[
            mig["District"].astype(int)
            == selected_district
        ]

    st.divider()

    # ----------------------------------
    # SESSION STATE
    # ----------------------------------

    if "selected_migration_center" not in st.session_state:

        st.session_state.selected_migration_center = None

    # ----------------------------------
    # LAYOUT
    # ----------------------------------

    map_col, info_col = st.columns([2, 1])

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

    for _, row in mig.iterrows():

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
            radius=6,
            color="#7F47ED",
            fill=True,
            fill_color="#7F47ED",
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Name"]
        ).add_to(m)

    # ----------------------------------
    # MAP DISPLAY
    # ----------------------------------

    with map_col:

        map_data = st_folium(
            m,
            height=700,
            returned_objects=[
                "last_object_clicked"
            ]
        )

    # ----------------------------------
    # CLICK DETECTION
    # ----------------------------------

    if (
        map_data
        and map_data.get(
            "last_object_clicked"
        )
    ):

        clicked_lat = (
            map_data["last_object_clicked"]["lat"]
        )

        clicked_lon = (
            map_data["last_object_clicked"]["lng"]
        )

        tmp = mig.copy()

        tmp["distance"] = (
            (tmp["latitude"] - clicked_lat) ** 2 +
            (tmp["longitude"] - clicked_lon) ** 2
        )

        st.session_state.selected_migration_center = (
            tmp.loc[
                tmp["distance"].idxmin()
            ]
        )

    # ----------------------------------
    # INFO PANEL
    # ----------------------------------

    with info_col:

        st.subheader("Facility Details")

        if (
            st.session_state.selected_migration_center
            is not None
        ):

            facility = (
                st.session_state.selected_migration_center
            )

            st.markdown(
                f"### {facility['Name']}"
            )

            st.write(
                f"**Category:** {facility['Category']}"
            )

            st.write(
                f"**District:** {int(facility['District'])}"
            )

            if (
                "barangay" in facility.index
                and pd.notna(
                    facility["barangay"]
                )
            ):

                st.write(
                    f"**Barangay:** {facility['barangay']}"
                )

            st.write(
                f"**Address:** {facility['Address']}"
            )

            if (
                "open_hours" in facility.index
                and pd.notna(
                    facility["open_hours"]
                )
            ):

                st.write(
                    f"**Open:** {facility['open_hours']}"
                )

            if (
                "close_hours" in facility.index
                and pd.notna(
                    facility["close_hours"]
                )
            ):

                st.write(
                    f"**Close:** {facility['close_hours']}"
                )

        else:

            st.info(
                "Click the facility on the map."
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

    st.title("Care Services Explorer")

    st.caption(
        """
        Explore childcare centers, schools, health facilities,
        older persons facilities, rehabilitation centers,
        migration resource centers, and Quezon City
        satellite offices on a single map.
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
            "name_col": "Name of Facility",
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

        "Satellite Offices": {
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
                font-size:22px;
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

        districts = sorted(
            health_centers["District"]
            .dropna()
            .astype(int)
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
    # LAYOUT
    # --------------------------------------------------

    map_col, info_col = st.columns([2, 1])

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

    filtered_layers = {}

    # --------------------------------------------------
    # ADD MARKERS
    # --------------------------------------------------

    for layer_name in selected_layers:

        layer = service_layers[layer_name]

        df = layer["df"].copy()

        if selected_district != "All":

            df = df[
                df[layer["district_col"]]
                .astype(int)
                == selected_district
            ]

        filtered_layers[layer_name] = df

        for _, row in df.iterrows():

            popup_html = f"""
            <b>{row[layer['name_col']]}</b><br>
            Type: {layer['source']}<br>
            District: {int(row[layer['district_col']])}
            """

            # determine color based on the same rules used in each page
            if layer_name == "Childcare Centers":
                marker_color_value = childcare_color(row["Category"])

            elif layer_name == "Schools":
                marker_color_value = school_color(row["Category"])

            elif layer_name == "Health Centers":
                marker_color_value = marker_color(row["Category"])

            elif layer_name == "Older Persons Facilities":
                marker_color_value = opc_color(row["Category"])

            elif layer_name == "Long-Term Care & Rehabilitation":
                marker_color_value = ltc_color(row["Category"])

            elif layer_name == "Satellite Offices":
                marker_color_value = district_color(row["District"])
            elif layer_name == "Migration Resource Centers":
                marker_color_value = "#C084FC"

            else:
                marker_color_value = "#7F47ED"

            folium.Marker(
                location=[
                    row[layer["lat_col"]],
                    row[layer["lon_col"]]
                ],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                        color:{marker_color_value};
                        font-size:18px;
                        font-weight:bold;
                        text-align:center;
                    ">
                        {layer['symbol']}
                    </div>
                    """
                ),
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=str(row[layer["name_col"]])
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
    # DETAILS PANEL
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

            # --------------------------
            # DISTRICT
            # --------------------------

            district_value = item[item["district_field"]]

            if pd.notna(district_value):

                try:
                    st.write(
                        f"**District:** {int(district_value)}"
                    )

                except:
                    st.write(
                        f"**District:** {district_value}"
                    )

            # --------------------------
            # ADDRESS
            # --------------------------

            if (
                item["address_field"] in item.index
                and pd.notna(item[item["address_field"]])
            ):

                st.write(
                    f"**Address:** {item[item['address_field']]}"
                )

            # --------------------------
            # BARANGAY
            # --------------------------

            if (
                "barangay" in item.index
                and pd.notna(item["barangay"])
                and str(item["barangay"]).strip() != ""
            ):

                st.write(
                    f"**Barangay:** {item['barangay']}"
                )

            # --------------------------
            # CATEGORY
            # --------------------------

            if (
                "Category" in item.index
                and pd.notna(item["Category"])
            ):

                st.write(
                    f"**Category:** {item['Category']}"
                )

        else:

            st.info(
                "Click a facility on the map."
            )
