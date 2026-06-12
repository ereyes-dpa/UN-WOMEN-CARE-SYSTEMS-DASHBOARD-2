import base64
import streamlit as st
import pandas as pd
import geopandas as gpd

def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Long Term Care Palette 
def ltc_color(category):

    category = str(category).upper()

    # Rehabilitation-focused
    if "REHABILITATION" in category:
        return "#5B21B6"

    # Physical therapy
    elif "PHYSICAL THERAPY" in category:
        return "#7F47ED"

    # Occupational therapy / schools
    elif "OCCUPATIONAL" in category:
        return "#A78BFA"

    # Psychological services
    elif "PSYCHOLOGICAL" in category:
        return "#C4B5FD"

    # Psychiatric rehabilitation
    elif "PSYCHIATRIC" in category:
        return "#8B5CF6"

    # Disability support center
    elif "KABAHAGI" in category:
        return "#DDD6FE"

    return "#EDE9FE"

def ltc_hex(category):
    return ltc_color(category)

# Satellite palette
DISTRICT_COLORS = {
    1: "#5B21B6",
    2: "#6D28D9",
    3: "#7F47ED",
    4: "#8B5CF6",
    5: "#A78BFA",
    6: "#C4B5FD"
}

def district_color(district):

    try:
        district = int(district)
        return DISTRICT_COLORS.get(
            district,
            "#DDD6FE"
        )

    except:
        return "#DDD6FE"
    
def category_color(cat):

    cat = str(cat).upper()

    if "QC LGU" in cat:
        return [76, 29, 149]      # Deep Purple

    elif "NATIONAL" in cat:
        return [91, 33, 182]      # Purple Dark

    elif "SUPER HEALTH" in cat:
        return [127, 71, 237]     # Main Purple

    elif "HEALTH CENTER" in cat:
        return [167, 139, 250]    # Light Purple

    elif "PHARMACY" in cat:
        return [196, 181, 253]    # Very Light Purple

    elif "MILK BANK" in cat:
        return [221, 214, 254]    # Pale Purple

    return [235, 230, 255]


def health_category_mapper(cat):

    cat = str(cat)

    if "National government-owned hospitals" in cat:
        return "National"

    elif "LGU-run hospitals" in cat:
        return "QC LGU"

    elif "LGU-run lying-in clinics" in cat:
        return "QC LGU"

    elif "Health center pharmacy" in cat:
        return "Pharmacy"

    elif "Super health care centers" in cat:
        return "Super Health"

    elif "Health centers" in cat:
        return "Health Center"

    elif "Human milk bank" in cat:
        return "Milk Bank"

    return "Other"

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

    care = pd.read_csv("processed/care.csv")

    childcare_centers = care[
        care["major_division"] == "Childcare"
    ].copy()

    schools = care[
        care["major_division"] == "Schools"
    ].copy()

    health_centers = (
        care[
            care["major_division"] == "Health centers"
        ]
        .copy()
    )   

    older_person_care = (
            care[
                care["major_division"] == "Older persons care"
            ]
            .copy()
        ) 
    
    long_term_care = care[
        care["major_division"]
        == "Long-term care and rehabilitation services"
        ].copy()
    
    satellite_offices = care[
        care["major_division"]
        == "Quezon City satellite offices for services"
        ].copy()

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
        older_person_care, 
        schools,
        long_term_care,
        satellite_offices
    )

# Clean Child care centers

def clean_health_centers(df) :
    df["Category"] = (
        df["category"]
        .apply(health_category_mapper)
    )

    df = df.rename(
        columns={
            "name_original": "Name of Facility",
            "address_clean": "Address",
            "district": "District"
        }
    )

    df["District"] = (
        df["District"]
        .astype(int)
        .astype(str)
    )

    df["District"] = (
        "District " +
        df["District"]
    )

    return df

# Clean Health Centers

def clean_dataframe(df) :
    df = df.rename(
    columns={
            "name_original": "Name",
            "district": "District",
            "address_clean": "Address",
            "sub_division": "Sector",
            "category": "Category"
        }
    )

    df = df.dropna(
    subset=[
        "latitude",
        "longitude"
    ]
)

    return df
