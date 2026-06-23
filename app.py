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

health_centers            = clean_health_centers(health_centers)
childcare_centers         = clean_dataframe(childcare_centers)
schools                   = clean_dataframe(schools)
older_person_care         = clean_dataframe(older_person_care)
long_term_care            = clean_dataframe(long_term_care)
satellite_offices         = clean_dataframe(satellite_offices)
satellite_offices["Name"] = "District " + satellite_offices["District"].astype(int).astype(str)
migration_centers         = clean_dataframe(migration_centers)

# --------------------------------------------------
# QC CENTER
# --------------------------------------------------

minx, miny, maxx, maxy = geo.total_bounds

center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2


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
    st.session_state.page = "Childcare Centers"

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

# --------------------------------------------------
# CARE MAPS
# --------------------------------------------------

st.sidebar.subheader("Care Maps")

if st.sidebar.button(
    "Childcare Centers",
    use_container_width=True
):
    st.session_state.page = "Childcare Centers"

if st.sidebar.button(
    "Schools",
    use_container_width=True
):
    st.session_state.page = "Schools"

if st.sidebar.button(
    "Health Centers Map",
    use_container_width=True
):
    st.session_state.page = "Health Centers Map"

if st.sidebar.button(
    "Older Persons Center Map",
    use_container_width=True
):
    st.session_state.page = "Older Persons Center Map"

if st.sidebar.button(
    "Long-Term Care & Rehabilitation",
    use_container_width=True
):
    st.session_state.page = "Long-Term Care & Rehabilitation"

if st.sidebar.button(
    "Satellite Offices",
    use_container_width=True
):
    st.session_state.page = "Satellite Offices"

if st.sidebar.button(
    "Migration Resource Center",
    use_container_width=True
):
    st.session_state.page = "Migration Resource Center"

# --------------------------------------------------
# TOOLS
# --------------------------------------------------

st.sidebar.subheader("Additional Tools")

if st.sidebar.button(
    "Care Services Explorer",
    use_container_width=True
):
    st.session_state.page = "Care Services Explorer"

# --------------------------------------------------
# ACTIVE PAGE
# --------------------------------------------------

page = st.session_state.page


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

    st.info("Click a facility on the map.")

    # --------------------------------------------------
    # DATA FILTERING
    # --------------------------------------------------

    cc = childcare_centers.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
        )

        cc = cc[
            cc["District"].astype(int)
            == district_number
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
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
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

        if (
            "open_hours" in row.index
            and pd.notna(row["open_hours"])
        ):
            popup_html += f"<br>Open: {row['open_hours']}"

        if (
            "close_hours" in row.index
            and pd.notna(row["close_hours"])
        ):
            popup_html += f"<br>Close: {row['close_hours']}"

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
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Name"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
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

    st.info("Click a school on the map.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    sch = schools.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
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

    sch_map = sch.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
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

    bounds = geo.total_bounds
    southwest = [bounds[1], bounds[0]]
    northeast = [bounds[3], bounds[2]]

    m.fit_bounds([southwest, northeast])

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
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Name"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
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

    st.info("Click a facility on the map.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    hc = health_centers.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
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

    hc["color"] = hc["Category"].apply(category_color)

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
        tiles="CartoDB positron"
    )

    # Optional: always focus on QC
    bounds = geo.total_bounds
    southwest = [bounds[1], bounds[0]]
    northeast = [bounds[3], bounds[2]]
    m.fit_bounds([southwest, northeast])

    # --------------------------------------------------
    # BARANGAY BOUNDARIES
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

        if (
            "barangay" in row.index
            and pd.notna(row["barangay"])
        ):
            popup_html += f"<br>Barangay: {row['barangay']}"

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
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Name of Facility"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
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

    st.info("Click a facility on the map.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    opc = older_person_care.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
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
    # REMOVE MISSING COORDINATES
    # --------------------------------------------------

    missing_locations = (
        opc["latitude"].isna() |
        opc["longitude"].isna()
    ).sum()

    if missing_locations > 0:

        st.warning(
            f"{missing_locations} facilities do not have coordinates and are not shown on the map."
        )

    opc_map = opc.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
        tiles="CartoDB positron"
    )

    bounds = geo.total_bounds
    southwest = [bounds[1], bounds[0]]
    northeast = [bounds[3], bounds[2]]

    m.fit_bounds([southwest, northeast])

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

    for _, row in opc_map.iterrows():

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
            weight=2,
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Name"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
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

    st.info("Click a facility on the map.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    ltc = long_term_care.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
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

    ltc_map = ltc.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
        tiles="CartoDB positron"
    )

    bounds = geo.total_bounds
    southwest = [bounds[1], bounds[0]]
    northeast = [bounds[3], bounds[2]]

    m.fit_bounds([southwest, northeast])

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
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Name"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
    )

elif page == "Satellite Offices":

    st.markdown(
        """
        <h2 style="
            color:#7F47ED;
            font-size:2.0rem;
            margin-top:-25px;
            margin-bottom:10px;
            padding-top:0px;
        ">
            Quezon City Satellite Offices
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Explore the distribution of Quezon City
    satellite offices providing local access
    to government services.
    """)

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

    st.info("Click an office on the map.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    sat = satellite_offices.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
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

    sat_map = sat.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
        tiles="CartoDB positron"
    )

    bounds = geo.total_bounds
    southwest = [bounds[1], bounds[0]]
    northeast = [bounds[3], bounds[2]]

    m.fit_bounds([southwest, northeast])

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

    for _, row in sat_map.iterrows():

        popup_html = f"""
        <b>{row['Category']}</b><br>
        District: {int(row['District'])}<br>
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
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=row["Category"]
        ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
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

    st.info("Click a facility on the map.")

    # --------------------------------------------------
    # FILTERING
    # --------------------------------------------------

    mig = migration_centers.copy()

    if selected_district != "All":

        district_number = int(
            selected_district.replace("District ", "")
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

    mig_map = mig.dropna(
        subset=["latitude", "longitude"]
    )

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        min_zoom=11,
        max_zoom=17,
        max_bounds=True,
        tiles="CartoDB positron"
    )

    bounds = geo.total_bounds
    southwest = [bounds[1], bounds[0]]
    northeast = [bounds[3], bounds[2]]

    m.fit_bounds([southwest, northeast])

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

    for _, row in mig_map.iterrows():

        popup_html = f"""
        <b>{row['Name']}</b><br>
        Category: {row['Category']}<br>
        District: {int(row['District'])}<br>
        Address: {row['Address']}
        """

        if (
            "barangay" in row.index
            and pd.notna(row["barangay"])
        ):
            popup_html += f"<br>Barangay: {row['barangay']}"

        if (
            "open_hours" in row.index
            and pd.notna(row["open_hours"])
        ):
            popup_html += f"<br>Open: {row['open_hours']}"

        if (
            "close_hours" in row.index
            and pd.notna(row["close_hours"])
        ):
            popup_html += f"<br>Close: {row['close_hours']}"

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

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=800,
        width=None
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

        df = df.dropna(
            subset=[
                layer["lat_col"],
                layer["lon_col"]
            ]
        )

        for _, row in df.iterrows():
            popup_html = f"""
            <b>{row[layer['name_col']]}</b><br>
            Type: {layer['source']}
            """

            # Sector
            if (
                "Sector" in row.index
                and pd.notna(row["Sector"])
            ):
                popup_html += f"<br>Sector: {row['Sector']}"

            # Category
            if (
                "Category" in row.index
                and pd.notna(row["Category"])
            ):
                popup_html += f"<br>Category: {row['Category']}"

            # District
            if (
                layer["district_col"] in row.index
                and pd.notna(row[layer["district_col"]])
            ):
                popup_html += (
                    f"<br>District: "
                    f"{int(row[layer['district_col']])}"
                )

            # Barangay
            if (
                "barangay" in row.index
                and pd.notna(row["barangay"])
                and str(row["barangay"]).strip() != ""
            ):
                popup_html += f"<br>Barangay: {row['barangay']}"

            # Address
            if (
                layer["address_col"] in row.index
                and pd.notna(row[layer["address_col"]])
            ):
                popup_html += (
                    f"<br>Address: "
                    f"{row[layer['address_col']]}"
                )

            # Opening hours
            if (
                "open_hours" in row.index
                and pd.notna(row["open_hours"])
            ):
                popup_html += (
                    f"<br>Open: {row['open_hours']}"
                )

            # Closing hours
            if (
                "close_hours" in row.index
                and pd.notna(row["close_hours"])
            ):
                popup_html += (
                    f"<br>Close: {row['close_hours']}"
                )

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
                popup=folium.Popup(
                    popup_html,
                    max_width=350
                ),
                tooltip=str(
                    row[layer["name_col"]]
                )
            ).add_to(m)

    # --------------------------------------------------
    # MAP DISPLAY
    # --------------------------------------------------

    st_folium(
        m,
        height=850,
        width="stretch"
    )
