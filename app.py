import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium

from streamlit_folium import st_folium

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Quezon City Caring Cities Dashboard",
    page_icon="🏙️",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
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

    geo = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

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
        geo
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
    geo
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

eccd = int(
    childcare_summary.loc[
        childcare_summary["metric"] == "eccd_enrollees",
        "value"
    ].iloc[0]
)

# --------------------------------------------------
# BUILD GIS DATASET
# --------------------------------------------------

childcare_by_barangay = (
    childcare_centers
    .groupby("barangay")
    .size()
    .reset_index(name="childcare_centers")
)

map_df = (
    geo.merge(
        barangays,
        left_on="barangay_name",
        right_on="barangay",
        how="left"
    )
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

map_df["care_gap"] = (
    map_df["senior_citizens"]
    /
    map_df["health_centers"]
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Section",
    [
        "Overview",
        "Care Supply",
        "Care Demand",
        "Facilities",
        "GIS Explorer"
    ]
)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.title("🏙️ Quezon City Caring Cities Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Population",
        f"{population:,}"
    )

    c2.metric(
        "Senior Citizens",
        f"{seniors:,}"
    )

    c3.metric(
        "PWDs",
        f"{pwds:,}"
    )

    c4.metric(
        "Child Centers",
        f"{child_centers:,}"
    )

    st.divider()

    indicator = st.selectbox(
        "Map Indicator",
        [
            "childcare_centers",
            "senior_citizens",
            "health_centers",
            "care_gap"
        ]
    )

    m = folium.Map(
        location=[14.67, 121.05],
        zoom_start=11,
        tiles="CartoDB positron"
    )

    folium.Choropleth(
        geo_data=map_df,
        data=map_df,
        columns=[
            "barangay_name",
            indicator
        ],
        key_on="feature.properties.barangay_name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=indicator
    ).add_to(m)

    folium.GeoJson(
        map_df,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "barangay_name",
                "district",
                "childcare_centers",
                "health_centers",
                "senior_citizens"
            ]
        )
    ).add_to(m)

    st_folium(
        m,
        height=700,
        width=None
    )

# --------------------------------------------------
# CARE SUPPLY
# --------------------------------------------------

elif page == "Care Supply":

    st.title("🏥 Care Supply")

    fig = px.bar(
        health,
        x="district",
        y="health_centers",
        title="Health Centers by District"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        health,
        x="district",
        y="doctors",
        title="Doctors by District"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    business_long = businesses.melt(
        id_vars=["service"],
        value_vars=[
            "district_1",
            "district_2",
            "district_3",
            "district_4",
            "district_5",
            "district_6"
        ]
    )

    fig = px.bar(
        business_long,
        x="service",
        y="value",
        color="variable"
    )

    fig.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# CARE DEMAND
# --------------------------------------------------

elif page == "Care Demand":

    st.title("👥 Care Demand")

    fig = px.bar(
        senior_by_district,
        x="district",
        y="senior_citizens",
        title="Senior Citizens by District"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    pwd_long = pwd_types.melt(
        id_vars="disability_type",
        var_name="year",
        value_name="count"
    )

    fig = px.line(
        pwd_long,
        x="year",
        y="count",
        color="disability_type",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# FACILITIES
# --------------------------------------------------

elif page == "Facilities":

    st.title("🏛️ Facilities")

    sector_counts = (
        facilities
        .groupby("sector")
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        sector_counts,
        x="sector",
        y="count"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        facilities,
        use_container_width=True,
        height=500
    )

# --------------------------------------------------
# GIS EXPLORER
# --------------------------------------------------

elif page == "GIS Explorer":

    st.title("🗺️ GIS Explorer")

    layer = st.selectbox(
        "Layer",
        [
            "childcare_centers",
            "health_centers",
            "senior_citizens",
            "care_gap"
        ]
    )

    m = folium.Map(
        location=[14.67, 121.05],
        zoom_start=11,
        tiles="CartoDB positron"
    )

    folium.Choropleth(
        geo_data=map_df,
        data=map_df,
        columns=[
            "barangay_name",
            layer
        ],
        key_on="feature.properties.barangay_name",
        fill_color="YlGnBu",
        fill_opacity=0.8,
        line_opacity=0.2,
        legend_name=layer
    ).add_to(m)

    folium.GeoJson(
        map_df,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "barangay_name",
                "district",
                "childcare_centers",
                "health_centers",
                "senior_citizens",
                "care_gap"
            ]
        )
    ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(
        m,
        height=800,
        width=None
    )