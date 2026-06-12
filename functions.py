import base64
import streamlit as st
import pandas as pd
import geopandas as gpd

def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    

# --------------------------------------------------
# CHILDCARE FUNCTIONS
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
# SCHOOLS FUNCTIONS
# --------------------------------------------------
def school_color(category):

    category = str(category).upper()

    if "PUBLIC SCHOOL" in category:
        return "#5B21B6"

    elif "PRIVATE SCHOOL" in category:
        return "#A78BFA"

    return "#DDD6FE"

# --------------------------------------------------
# OLDERS CARE FUCNTIONS
# --------------------------------------------------
def opc_color(category):

    category = str(category).upper()

    if "NURSING" in category:
        return "#5B21B6"

    elif "BAHAY ARUGA" in category:
        return "#A78BFA"

    return "#DDD6FE"


# --------------------------------------------------
# HEALTHCARE FUNCTIONS
# --------------------------------------------------
def category_hex(cat):

    rgb = category_color(cat)

    return "#{:02X}{:02X}{:02X}".format(
        rgb[0],
        rgb[1],
        rgb[2]
    )

def marker_color(category):

    category = str(category).upper()

    if "QC LGU" in category:
        return "#4C1D95"   # dark purple

    elif "NATIONAL" in category:
        return "#5B21B6"

    elif "SUPER HEALTH" in category:
        return "#6D28D9"

    elif "HEALTH CENTER" in category:
        return "#7C3AED"

    elif "PHARMACY" in category:
        return "#8B5CF6"

    elif "MILK BANK" in category:
        return "#9333EA"   # much darker

    return "#6D28D9"

# --------------------------------------------------
# LONGTERM CARE FUNCTIONS
# --------------------------------------------------
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

# --------------------------------------------------
# SATELLITE OFFICES FUNCTIONS
# --------------------------------------------------
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
        return [76, 29, 149]

    elif "NATIONAL" in cat:
        return [91, 33, 182]

    elif "SUPER HEALTH" in cat:
        return [109, 40, 217]

    elif "HEALTH CENTER" in cat:
        return [124, 58, 237]

    elif "PHARMACY" in cat:
        return [139, 92, 246]

    elif "MILK BANK" in cat:
        return [147, 51, 234]

    return [109, 40, 217]


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
        geo, 
        childcare_centers,
        schools,
        health_centers,
        older_person_care, 
        long_term_care,
        satellite_offices
    )

# --------------------------------------------------
# CLEANNING
# --------------------------------------------------
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

    df["Name of Facility"] = df["Name of Facility"].str.title()


    return df

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

    df["Name"] = df["Name"].str.title()
    

    return df
