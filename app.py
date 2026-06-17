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


population_summary, population_sex, population_age = load_data_for_kpis()

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
    "Available Pages",
    [
        "Population Overview",
        "Childcare Centers",
        "Schools", 
        "Health Centers Map",
        "Older Persons Center Map",
        "Long-Term Care & Rehabilitation",
        "Persons with Disabilities",
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

elif page == "Population Overview":

    st.title("Population Overview")

    st.markdown("""
    Demographic profile of Quezon City to support planning,
    resource allocation, and care service delivery decisions.
    """)

    # --------------------------------------------------
    # CLEANING
    # --------------------------------------------------

    for col in ["Male", "Female", "Total"]:

        if col in population_sex.columns:

            population_sex[col] = (
                population_sex[col]
                .astype(str)
                .str.replace(",", "")
                .astype(float)
            )

    age_columns = [
        c for c in population_age.columns
        if c not in ["Barangay", "District"]
    ]

    for col in age_columns:

        population_age[col] = (
            population_age[col]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
        )

    # --------------------------------------------------
    # SUMMARY VALUES
    # --------------------------------------------------

    total_population_2024 = (
        population_sex["Total"]
        .sum()
    )

    total_male = (
        population_sex["Male"]
        .sum()
    )

    total_female = (
        population_sex["Female"]
        .sum()
    )

    male_pct = (
        total_male
        / total_population_2024
        * 100
    )

    female_pct = (
        total_female
        / total_population_2024
        * 100
    )

    total_barangays = (
        population_sex["Barangay"]
        .nunique()
    )

    total_districts = (
        population_sex["District"]
        .nunique()
    )

    # --------------------------------------------------
    # POPULATION GROWTH
    # --------------------------------------------------

    pop_2020 = 2960048
    pop_2024 = total_population_2024

    growth_rate = (
        (pop_2024 - pop_2020)
        / pop_2020
        * 100
    )

    # --------------------------------------------------
    # KPI ROW
    # --------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Population (2024)",
        f"{pop_2024:,.0f}"
    )

    k2.metric(
        "Population (2020)",
        f"{pop_2020:,.0f}"
    )

    k3.metric(
        "Growth Rate",
        f"{growth_rate:.1f}%"
    )

    k4.metric(
        "Barangays",
        f"{total_barangays}"
    )

    k5.metric(
        "Districts",
        f"{total_districts}"
    )

    st.divider()

    # --------------------------------------------------
    # SEX + AGE DISTRIBUTION
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        sex_df = pd.DataFrame(
            {
                "Sex": [
                    "Male",
                    "Female"
                ],
                "Population": [
                    total_male,
                    total_female
                ]
            }
        )

        fig = px.pie(
            sex_df,
            names="Sex",
            values="Population",
            title="Population by Sex"
        )

        st.plotly_chart(
            fig,
            width='stretch'
        )

        st.caption(
            f"Male: {male_pct:.1f}% | Female: {female_pct:.1f}%"
        )

    with col2:

        age_df = pd.DataFrame(
            {
                "Age Group": [
                    "0-5",
                    "6-17",
                    "18-59",
                    "60+"
                ],
                "Population": [
                    population_age[
                        "0-5 \n(Early Childhood)"
                    ].sum(),

                    population_age[
                        "6-17 \n(School Age Children)"
                    ].sum(),

                    population_age[
                        "18-59 \n(Working Age Adult)"
                    ].sum(),

                    population_age[
                        "60+ \n(Elderly)"
                    ].sum()
                ]
            }
        )

        fig = px.bar(
            age_df,
            x="Age Group",
            y="Population",
            title="Population by Age Group"
        )

        st.plotly_chart(
            fig,
            width='stretch'
        )

    st.divider()

    # --------------------------------------------------
    # DISTRICT POPULATION
    # --------------------------------------------------

    st.subheader(
        "Population by District"
    )

    district_population = (
        population_sex
        .groupby("District", as_index=False)
        ["Total"]
        .sum()
        .sort_values(
            "Total",
            ascending=False
        )
    )

    fig = px.bar(
        district_population,
        x="District",
        y="Total",
        title="Population by District",
        text_auto=","
    )

    st.plotly_chart(
        fig,
        width='stretch'
    )

    st.divider()

    # --------------------------------------------------
    # AGE STRUCTURE BY DISTRICT
    # --------------------------------------------------

    st.subheader(
        "Age Structure by District"
    )

    district_age = (
        population_age
        .groupby("District")
        [
            [
                "0-5 \n(Early Childhood)",
                "6-17 \n(School Age Children)",
                "18-59 \n(Working Age Adult)",
                "60+ \n(Elderly)"
            ]
        ]
        .sum()
        .reset_index()
    )

    district_age_long = district_age.melt(
        id_vars="District",
        var_name="Age Group",
        value_name="Population"
    )

    fig = px.bar(
        district_age_long,
        x="District",
        y="Population",
        color="Age Group",
        title="Population Structure by District"
    )

    st.plotly_chart(
        fig,
        width='stretch'
    )

    st.divider()

    # --------------------------------------------------
    # TOP BARANGAYS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Top 10 Most Populated Barangays"
        )

        top_barangays = (
            population_sex
            .sort_values(
                "Total",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            top_barangays[
                [
                    "Barangay",
                    "District",
                    "Total"
                ]
            ],
            width='stretch'
        )

    with col2:

        st.subheader(
            "Least Populated Barangays"
        )

        smallest_barangays = (
            population_sex
            .sort_values(
                "Total",
                ascending=True
            )
            .head(10)
        )

        st.dataframe(
            smallest_barangays[
                [
                    "Barangay",
                    "District",
                    "Total"
                ]
            ],
            width='stretch'
        )

    st.divider()

    # --------------------------------------------------
    # DISTRICT SUMMARY TABLE
    # --------------------------------------------------

    st.subheader(
        "District Demographic Summary"
    )

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

    district_summary[
        "Male %"
    ] = (
        district_summary["Male"]
        / district_summary["Population"]
        * 100
    ).round(1)

    district_summary[
        "Female %"
    ] = (
        district_summary["Female"]
        / district_summary["Population"]
        * 100
    ).round(1)

    st.dataframe(
        district_summary,
        width='stretch'
    )

if page == "Childcare Centers":

    st.title("Child Care Facilities")

    st.markdown("""
    Explore the spatial distribution of childcare facilities in Quezon City,
    including public Child Development Centers and private childcare providers.
                
                
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
            "0-5 \n(Early Childhood)"
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

    st.title("Schools")

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
            "6-17 \n(School Age Children)"
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
            "6-17 \n(School Age Children)"
        ]
        .sum()
        .reset_index()
    )

    district_population = district_population.rename(
        columns={
            "6-17 \n(School Age Children)":
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

    st.title("Health Centers & Hospitals") 
    
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

    st.title("Older Persons & Senior Citizens")

    st.caption(
        """
        Interactive map of facilities supporting older persons in Quezon City,
        including nursing care centers and Bahay Aruga facilities.
        """
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

    st.title(
        "Long-Term Care & Rehabilitation Services"
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

    # --------------------------------------------------
    # REHABILITATION KPIs
    # --------------------------------------------------

    elderly_population = (
        population_age[
            "60+ \n(Elderly)"
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

    st.title("Persons with Disabilities (PWD)")

    st.markdown("""
    Overview of registered persons with disabilities in Quezon City,
    including disability types, registration trends,
    district distribution, and rehabilitation service coverage.
    """)

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
