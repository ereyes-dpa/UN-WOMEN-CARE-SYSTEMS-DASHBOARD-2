import base64
import json
import io
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import numpy as np
from PIL import Image

@st.cache_data
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
            "name_original": "Name",
            "address_clean": "Address",
            "district": "District"
        }
    )

    df["District"] = pd.to_numeric(
        df["District"],
        errors="coerce"
    ).astype("Int64")

    df["Name"] = df["Name"].str.title()


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

    df["District"] = (
        pd.to_numeric(df["District"], errors="coerce")
        .astype("Int64")
    )
        
    return df

@st.cache_data
def load_geo():
    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    bounds = gdf.total_bounds

    return gdf.__geo_interface__, bounds

@st.cache_data
def load_geo_explorer():

    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    gdf["geometry"] = (
        gdf.geometry
        .simplify(
            tolerance=0.0001,
            preserve_topology=True
        )
    )

    bounds = gdf.total_bounds

    return gdf.__geo_interface__, bounds


@st.cache_resource
def load_qc_boundary():
    """
    Reads the barangay-level boundaries and dissolves them into
    a single Quezon City outline (shapely geometry, EPSG:4326).
    Used to crop climate rasters to the city limits instead of
    showing their full rectangular extent.
    """

    gdf = gpd.read_file(
        "processed/qc_barangays.geojson",
        engine="pyogrio"
    )

    # union_all() replaced the unary_union property in
    # geopandas 1.0 — fall back for older installs.
    if hasattr(gdf, "union_all"):
        dissolved = gdf.union_all()
    else:
        dissolved = gdf.unary_union

    return dissolved


@st.cache_resource
def get_boundary_geojson(geo_json):
    return folium.GeoJson(
        geo_json,
        style_function=lambda x: {
            "fillColor": "#7fbf7f",
            "color": "#666666",
            "weight": 1,
            "fillOpacity": 0.15,
        }
    )

@st.cache_data
def load_data():

    care = pd.read_csv("processed/care_v3.csv")

    category_cols = [
        "major_division",
        "sub_division",
        "category"
    ]

    for col in category_cols:
        if col in care.columns:
            care[col] = care[col].astype("category")

    care["open_hours"] = (
        care["open_hours"]
        .fillna("Not available")
    )

    care["close_hours"] = (
        care["close_hours"]
        .fillna("Not available")
    )        

    # Clean coordinates
    care["latitude"] = pd.to_numeric(
        care["latitude"],
        errors="coerce"
    )

    care["longitude"] = pd.to_numeric(
        care["longitude"],
        errors="coerce"
    )

    care = care.dropna(
        subset=["latitude", "longitude"]
    )

    childcare_centers = care[
        care["major_division"] == "Childcare"
    ].copy()

    schools = care[
        care["major_division"] == "Schools"
    ].copy()

    health_centers = care[
        care["major_division"] == "Health centers"
    ].copy()

    older_person_care = care[
        care["major_division"] == "Older persons care"
    ].copy()

    long_term_care = care[
        care["major_division"]
        == "Long-term care and rehabilitation services"
    ].copy()

    satellite_offices = care[
        care["major_division"]
        == "Quezon City satellite offices for services"
    ].copy()

    migration_centers = care[
        care["major_division"] == "Trainings"
    ].copy()

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

    return (
        childcare_centers,
        schools,
        health_centers,
        older_person_care,
        long_term_care,
        satellite_offices,
        migration_centers
    )

@st.cache_data
def load_data_for_kpis():

    import pandas as pd

    # ==================================================
    # LOAD FILES
    # ==================================================

    population_summary = pd.read_csv(
        "processed/population_summary.csv"
    )

    population_sex = pd.read_csv(
        "processed/population_2024_by_sex.csv"
    )

    population_age = pd.read_csv(
        "processed/population_2024_by_age_group.csv"
    )

    mapping = pd.read_csv(
        "processed/barangay_district_mapping.csv"
    )

    # ==================================================
    # CLEAN MAPPING
    # ==================================================

    mapping.columns = mapping.columns.str.strip()

    mapping["BARANGAY_original"] = (
        mapping["BARANGAY_original"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    mapping["BARANGAY"] = (
        mapping["BARANGAY"]
        .astype(str)
        .str.strip()
    )

    mapping["DISTRICT"] = (
        mapping["DISTRICT"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(int)
    )

    # ==================================================
    # CLEAN NUMERIC COLUMNS
    # ==================================================

    for col in ["Male", "Female", "Total"]:

        if col in population_sex.columns:

            population_sex[col] = (
                population_sex[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .astype(int)
            )

    age_cols = [
        "0-5 (Early Childhood)",
        "6-17 (School Age Children)",
        "18-59 (Working Age Adult)",
        "60+ (Elderly)",
        "Total"
    ]

    for col in age_cols:

        if col in population_age.columns:

            population_age[col] = (
                population_age[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .astype(int)
            )

    # ==================================================
    # APPLY BARANGAY MAPPING
    # ==================================================

    def apply_barangay_mapping(df, name=""):

        df = df.copy()

        df["Barangay_key"] = (
            df["Barangay"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        df = df.merge(
            mapping,
            left_on="Barangay_key",
            right_on="BARANGAY_original",
            how="left"
        )

        # ------------------------------------
        # SHOW UNMATCHED BARANGAYS
        # ------------------------------------

        missing = (
            df[df["BARANGAY"].isna()]
            [["Barangay", "Barangay_key"]]
            .drop_duplicates()
            .sort_values("Barangay")
        )

        if len(missing) > 0:

            print(f"\n{name} - UNMATCHED BARANGAYS")
            print("-" * 50)

            for b in missing["Barangay"]:
                print(b)

            print(f"\nTotal missing: {len(missing)}")

        # ------------------------------------
        # REPLACE VALUES
        # ------------------------------------

        df["Barangay"] = (
            df["BARANGAY"]
            .fillna(df["Barangay"])
        )

        df["District"] = (
            df["DISTRICT"]
            .fillna(df["District"])
        )

        df = df.drop(
            columns=[
                "Barangay_key",
                "BARANGAY_original",
                "BARANGAY",
                "DISTRICT"
            ],
            errors="ignore"
        )

        return df

    population_age = apply_barangay_mapping(
        population_age
    )

    population_sex = apply_barangay_mapping(
        population_sex
    )


    # ==================================================
    # RETURN
    # ==================================================

    return (
        population_summary,
        population_sex,
        population_age
    )
    

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return [
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    ]


# --------------------------------------------------
# DEMAND-PER-FACILITY INDICATORS
# (methodology adapted from the supply/cluster
# indicator notebooks: population in a target age
# group divided by the number of facilities serving
# that age group — computed per group, not combined)
# --------------------------------------------------
def compute_population_per_facility(
    barangay_pop,
    care_clean,
    children_divisions=None,
    elderly_divisions=None
):
    """
    Computes children-per-facility and elderly-per-facility
    at the barangay level.

    barangay_pop must contain:
        "Barangay", "0-5 (Early Childhood)", "60+ (Elderly)"

    care_clean must contain:
        "barangay", "major_division"

    children_divisions / elderly_divisions let the caller
    decide which major_division values count as serving
    children vs. older persons. Defaults match the QC
    care_v3.csv major_division values.
    """

    if children_divisions is None:
        children_divisions = [
            "Childcare",
            "Schools"
        ]

    if elderly_divisions is None:
        elderly_divisions = [
            "Older persons care",
            "Long-term care and rehabilitation services"
        ]

    care_clean = care_clean.copy()

    care_clean["barangay"] = (
        care_clean["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    child_facilities = (
        care_clean[
            care_clean["major_division"].isin(children_divisions)
        ]
        .groupby("barangay")
        .size()
        .reset_index(name="Child-Serving Facilities")
    )

    elderly_facilities = (
        care_clean[
            care_clean["major_division"].isin(elderly_divisions)
        ]
        .groupby("barangay")
        .size()
        .reset_index(name="Elderly-Serving Facilities")
    )

    out = barangay_pop.copy()

    out["Barangay"] = (
        out["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    out = out.merge(
        child_facilities,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    ).drop(columns=["barangay"], errors="ignore")

    out = out.merge(
        elderly_facilities,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    ).drop(columns=["barangay"], errors="ignore")

    out["Child-Serving Facilities"] = (
        out["Child-Serving Facilities"].fillna(0)
    )

    out["Elderly-Serving Facilities"] = (
        out["Elderly-Serving Facilities"].fillna(0)
    )

    # children per facility — np.nan when there are no
    # facilities, rather than infinity, so it reads cleanly
    # in tables/charts (mirrors the notebooks' np.where guard)
    out["Children per Facility"] = np.where(
        out["Child-Serving Facilities"] != 0,
        out["0-5 (Early Childhood)"] / out["Child-Serving Facilities"],
        np.nan
    )

    out["Elderly per Facility"] = np.where(
        out["Elderly-Serving Facilities"] != 0,
        out["60+ (Elderly)"] / out["Elderly-Serving Facilities"],
        np.nan
    )

    return out


# --------------------------------------------------
# BARANGAY CLUSTERING
# (methodology adapted from Clustering Exploration &
# Cluster Indicators notebooks: standardize a feature
# set describing demographics + service mix, then
# K-means to group barangays into comparable zones)
# --------------------------------------------------
def build_cluster_features(
    barangay_df,
    care_clean,
    feature_cols=None
):
    """
    Builds the standardized feature matrix used for
    barangay clustering.

    barangay_df is expected to already carry, per
    barangay: Total, population_density, children_pct,
    elderly_pct (as produced on the Population Overview
    page).

    care_clean must contain "barangay" and "major_division"
    so a facility-mix share can be added per barangay
    (share of local facilities that are Childcare, Schools,
    Health centers, Older persons care, etc.) — this stands
    in for the land-use mix used in the original notebooks,
    since QC's data is facility-based rather than raster-based.
    """

    care_clean = care_clean.copy()

    care_clean["barangay"] = (
        care_clean["barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    facility_mix = (
        care_clean
        .groupby(["barangay", "major_division"])
        .size()
        .reset_index(name="count")
    )

    facility_totals = (
        facility_mix
        .groupby("barangay")["count"]
        .sum()
        .reset_index(name="total")
    )

    facility_mix = facility_mix.merge(
        facility_totals,
        on="barangay",
        how="left"
    )

    facility_mix["share"] = (
        facility_mix["count"] / facility_mix["total"]
    )

    mix_wide = (
        facility_mix
        .pivot(
            index="barangay",
            columns="major_division",
            values="share"
        )
        .fillna(0)
        .reset_index()
    )

    mix_wide.columns = [
        "barangay"
    ] + [
        f"share_{str(c).lower().replace(' ', '_')}"
        for c in mix_wide.columns[1:]
    ]

    out = barangay_df.copy()

    out["Barangay"] = (
        out["Barangay"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    out = out.merge(
        mix_wide,
        left_on="Barangay",
        right_on="barangay",
        how="left"
    ).drop(columns=["barangay"], errors="ignore")

    share_cols = [
        c for c in out.columns if c.startswith("share_")
    ]

    out[share_cols] = out[share_cols].fillna(0)

    if feature_cols is None:
        feature_cols = [
            "population_density",
            "children_pct",
            "elderly_pct"
        ] + share_cols

    feature_cols = [
        c for c in feature_cols if c in out.columns
    ]

    return out, feature_cols


def run_barangay_clustering(
    df,
    feature_cols,
    n_clusters=4,
    random_state=0
):
    """
    Standardizes features and runs K-means, mirroring
    Section 1 of the Clustering Exploration notebook
    (sklearn StandardScaler + KMeans). Returns the
    dataframe with a "Cluster" column added (1-indexed,
    to match the original notebooks' cluster numbering)
    plus the scaled feature matrix, for profiling.
    """

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    work = df.copy()

    feat = (
        work[feature_cols]
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    scaler = StandardScaler()
    scaled = scaler.fit_transform(feat)

    km = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10
    ).fit(scaled)

    work["Cluster"] = km.labels_ + 1

    scaled_df = pd.DataFrame(
        scaled,
        columns=feature_cols,
        index=work.index
    )

    return work, scaled_df


CLUSTER_PALETTE = [
    "#5B21B6",
    "#7F47ED",
    "#A78BFA",
    "#C4B5FD",
    "#DDD6FE",
    "#EDE9FE"
]


def cluster_color(cluster_id):

    try:
        cluster_id = int(cluster_id)
        return CLUSTER_PALETTE[
            (cluster_id - 1) % len(CLUSTER_PALETTE)
        ]

    except (TypeError, ValueError):
        return "#DDD6FE"


# --------------------------------------------------
# CLIMATE RASTER RENDERING
# (converts a GeoTIFF in any CRS into an RGBA PNG +
# lat/lon bounding box, suitable for pydeck's
# BitmapLayer. Color ramps are applied client-side
# here rather than relying on the raster's own
# values, since pydeck has no native raster-colormap
# support — it only draws pre-rendered images.)
# --------------------------------------------------
import base64
import io


def _lerp_color(stops, t):
    """Linearly interpolate an RGB color from a list of
    (t, (r,g,b)) stops, for t in [0, 1]."""

    t = min(max(t, 0.0), 1.0)

    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]

        if t0 <= t <= t1:
            local_t = (t - t0) / (t1 - t0) if t1 > t0 else 0
            r = c0[0] + (c1[0] - c0[0]) * local_t
            g = c0[1] + (c1[1] - c0[1]) * local_t
            b = c0[2] + (c1[2] - c0[2]) * local_t
            return int(r), int(g), int(b)

    return stops[-1][1]


# Approximations of common matplotlib colormaps, as
# (t, (r,g,b)) stops, t in [0, 1]
COLORMAPS = {
    # YlOrRd — used for Land-Surface Temperature
    "YlOrRd": [
        (0.00, (255, 255, 178)),
        (0.25, (254, 204, 92)),
        (0.50, (253, 141, 60)),
        (0.75, (227, 26, 28)),
        (1.00, (128, 0, 38))
    ],
    # Greens — used for NDVI (vegetation)
    "Greens": [
        (0.00, (247, 252, 245)),
        (0.25, (199, 233, 192)),
        (0.50, (116, 196, 118)),
        (0.75, (35, 139, 69)),
        (1.00, (0, 68, 27))
    ],
    # Blues — used for flood inundation
    "Blues": [
        (0.00, (247, 251, 255)),
        (0.50, (107, 174, 214)),
        (1.00, (8, 48, 107))
    ],
    # Purples — used for barangay/district choropleths
    # on the Population Overview and District pages
    "Purples": [
        (0.00, (252, 251, 253)),
        (0.25, (218, 218, 235)),
        (0.50, (158, 154, 200)),
        (0.75, (106, 81, 163)),
        (1.00, (63, 0, 125))
    ]
}


def value_to_rgba(
    value,
    vmin,
    vmax,
    colormap="Purples",
    alpha=190
):
    """
    Maps a single numeric value to an [r, g, b, a] list using
    one of the COLORMAPS ramps, given a (vmin, vmax) range.

    Used for pydeck GeoJsonLayer choropleths (e.g. the
    Population Overview barangay map and District map), as a
    polygon-fill equivalent of Plotly's color_continuous_scale
    + cmin/cmax — vmin/vmax are expected to already be clipped
    (e.g. to the 5th-95th percentile) by the caller, the same
    way the Plotly version clips via update_coloraxes.
    """

    if vmax <= vmin or pd.isna(value):
        t = 0.0
    else:
        t = (value - vmin) / (vmax - vmin)

    r, g, b = _lerp_color(COLORMAPS[colormap], t)

    return [r, g, b, alpha]


def _render_raster_rgba(
    path,
    colormap="YlOrRd",
    clip_percentiles=(2, 98),
    opacity=180,
    binary=False,
    mask_geometry=None
):
    """
    Shared core for rendering a GeoTIFF (any CRS) into a colored
    RGBA array. Returns (rgba, bounds_latlon, vmin, vmax) where
    bounds_latlon is the flat (west, south, east, north) tuple in
    EPSG:4326. Used by both raster_to_bitmap_layer (pydeck) and
    raster_to_image_overlay (folium), which each reformat
    bounds_latlon differently for their respective map libraries.

    See raster_to_bitmap_layer's docstring for the meaning of
    binary and mask_geometry.
    """

    import rasterio
    from rasterio.warp import transform_bounds, transform_geom
    from rasterio.mask import mask as rio_mask

    with rasterio.open(path) as src:

        src_crs = src.crs
        nodata = src.nodata

        if mask_geometry is not None:

            # Reproject the mask boundary (EPSG:4326) into the
            # raster's native CRS before clipping, then read only
            # the masked window. rasterio.mask.mask sets pixels
            # outside the geometry to `nodata` (or NaN if no
            # nodata value is defined on the source).
            geom_native = transform_geom(
                "EPSG:4326",
                src_crs,
                mask_geometry.__geo_interface__
            )

            fill_value = (
                nodata
                if nodata is not None
                else np.nan
            )

            clipped, clipped_transform = rio_mask(
                src,
                [geom_native],
                crop=True,
                nodata=fill_value,
                filled=True
            )

            arr = clipped[0].astype("float64")

            if nodata is not None and not np.isnan(nodata):
                arr = np.where(arr == nodata, np.nan, arr)

            height, width = arr.shape

            bounds_native = rasterio.transform.array_bounds(
                height,
                width,
                clipped_transform
            )

            left, bottom, right, top = bounds_native

        else:

            arr = src.read(1).astype("float64")

            if nodata is not None and not np.isnan(nodata):
                arr = np.where(arr == nodata, np.nan, arr)

            bounds_native = src.bounds
            left, bottom, right, top = (
                bounds_native.left,
                bounds_native.bottom,
                bounds_native.right,
                bounds_native.top
            )

        bounds_latlon = transform_bounds(
            src_crs,
            "EPSG:4326",
            left,
            bottom,
            right,
            top
        )

    stops = COLORMAPS.get(colormap, COLORMAPS["YlOrRd"])

    if binary:

        vmin, vmax = 0, 1
        top_color = stops[-1][1]

        rgba = np.zeros(
            (arr.shape[0], arr.shape[1], 4),
            dtype="uint8"
        )

        mask = arr == 1

        rgba[..., 0] = np.where(mask, top_color[0], 0)
        rgba[..., 1] = np.where(mask, top_color[1], 0)
        rgba[..., 2] = np.where(mask, top_color[2], 0)
        rgba[..., 3] = np.where(mask, opacity, 0)

    else:

        finite = arr[np.isfinite(arr)]

        vmin, vmax = np.percentile(
            finite,
            clip_percentiles
        )

        if vmax <= vmin:
            vmax = vmin + 1e-6

        t = (arr - vmin) / (vmax - vmin)
        valid = np.isfinite(arr)

        # NaN positions get masked out via `valid` below anyway,
        # but np.nan_to_num avoids an "invalid cast" warning when
        # converting NaN to the int32 LUT index.
        t = np.nan_to_num(t, nan=0.0)
        t = np.clip(t, 0, 1)

        rgba = np.zeros(
            (arr.shape[0], arr.shape[1], 4),
            dtype="uint8"
        )

        # Vectorized colormap lookup via a fine-grained LUT,
        # rather than per-pixel Python interpolation (which
        # would be far too slow for million-pixel rasters)
        lut_size = 256

        lut = np.array(
            [_lerp_color(stops, i / (lut_size - 1)) for i in range(lut_size)],
            dtype="uint8"
        )

        idx = np.clip(
            (t * (lut_size - 1)).astype("int32"),
            0,
            lut_size - 1
        )

        rgba[..., 0] = np.where(valid, lut[idx, 0], 0)
        rgba[..., 1] = np.where(valid, lut[idx, 1], 0)
        rgba[..., 2] = np.where(valid, lut[idx, 2], 0)
        rgba[..., 3] = np.where(valid, opacity, 0)

    return rgba, bounds_latlon, vmin, vmax


@st.cache_data(show_spinner=False)
def raster_to_bitmap_layer(
    path,
    colormap="YlOrRd",
    clip_percentiles=(2, 98),
    opacity=180,
    binary=False,
    _mask_geometry=None
):
    """
    Reads a GeoTIFF (any CRS) and returns:
      (png_data_uri, bounds_corners, vmin, vmax)

    For use with pydeck's BitmapLayer:
        pdk.Layer("BitmapLayer", image=png_data_uri, bounds=bounds_corners, ...)

    png_data_uri   — a string already wrapped in literal quote
                      characters (e.g. '"data:image/png;base64,..."')
                      so pydeck's JSON layer renders it as a string
                      constant rather than trying to evaluate it as
                      a JS expression. Pass directly as the `image`
                      argument — do NOT wrap it in another layer of
                      quotes.
    bounds_corners — [[west, south], [west, north], [east, north],
                      [east, south]] in EPSG:4326 — the 4-corner
                      quadrilateral format pydeck's BitmapLayer
                      `bounds` expects (NOT a flat
                      [west, south, east, north] tuple).
    vmin, vmax     — the data range actually used for the color
                      scale (after percentile clipping), so a
                      legend can be drawn to match

    binary=True treats the raster as a 0/1 mask (e.g. flood
    extent) instead of a continuous color ramp: 0 is fully
    transparent, 1 is drawn as a flat color from the colormap's
    top stop.

    _mask_geometry — optional shapely geometry (e.g. the dissolved
    Quezon City boundary) in EPSG:4326. When provided, pixels
    outside this geometry are set to transparent/nodata before
    rendering, so the bitmap is cropped to the boundary rather
    than showing the raster's full rectangular extent. The
    raster's own bounds/resolution are unchanged — only pixel
    values outside the boundary are masked.

    The leading underscore on _mask_geometry tells Streamlit's
    @st.cache_data to skip hashing it (shapely geometries aren't
    hashable). This is safe as long as callers always pass the
    same boundary object for the same city/dataset — e.g. the
    cached return value of load_qc_boundary() — rather than a
    geometry that legitimately changes between calls with
    otherwise-identical arguments, which would silently return a
    stale cached bitmap.

    This function is itself cached: rendering a multi-million-
    pixel raster (reading, masking, building the colormap LUT,
    PNG-encoding, base64-encoding) is expensive enough that
    re-running it on every Streamlit widget interaction makes the
    page noticeably slow. Caching keys on (path, colormap,
    clip_percentiles, opacity, binary) — change any of those and
    the cache misses correctly.

    Requires rasterio + pyproj (both already dependencies of
    geopandas, used elsewhere in this app).
    """

    rgba, bounds_latlon, vmin, vmax = _render_raster_rgba(
        path,
        colormap=colormap,
        clip_percentiles=clip_percentiles,
        opacity=opacity,
        binary=binary,
        mask_geometry=_mask_geometry
    )

    img = Image.fromarray(rgba, mode="RGBA")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    png_b64 = base64.b64encode(png_bytes).decode()

    # pydeck serializes Layer properties through deck.gl's JSON
    # converter, which treats plain strings as JS expressions to
    # evaluate (this is how accessor strings like
    # "properties.fill_color" work). A literal string value must
    # itself be wrapped in quote characters, or the parser tries
    # to evaluate "data:image/png;base64,..." as an expression and
    # fails on the colon. See visgl/deck.gl issues #4977 and #5151.
    png_data_uri = (
        '"data:image/png;base64,' + png_b64 + '"'
    )

    west, south, east, north = bounds_latlon

    # pydeck's BitmapLayer expects `bounds` as a quadrilateral of
    # 4 [lng, lat] corners, not a flat [west, south, east, north]
    # tuple. Order matches the official pydeck BitmapLayer example.
    bounds_corners = [
        [west, south],
        [west, north],
        [east, north],
        [east, south]
    ]

    return png_data_uri, bounds_corners, vmin, vmax


@st.cache_data(show_spinner=False)
def raster_to_image_overlay(
    path,
    colormap="YlOrRd",
    clip_percentiles=(2, 98),
    opacity=180,
    binary=False,
    _mask_geometry=None
):
    """
    Reads a GeoTIFF (any CRS) and returns:
      (rgba_array, folium_bounds, vmin, vmax)

    For use with folium's ImageOverlay:
        folium.raster_layers.ImageOverlay(
            image=rgba_array, bounds=folium_bounds, origin="upper"
        ).add_to(m)

    rgba_array    — numpy uint8 array of shape (height, width, 4).
                     folium converts this to PNG internally — no
                     base64/quoting handling needed (unlike the
                     pydeck path in raster_to_bitmap_layer).
    folium_bounds — [[lat_min, lon_min], [lat_max, lon_max]] in
                     EPSG:4326 — folium's own bounds convention,
                     which is [lat, lon] order, NOT [lon, lat]
                     like pydeck uses. Don't mix the two up.
    vmin, vmax    — the data range actually used for the color
                     scale, for drawing a matching legend.

    See raster_to_bitmap_layer's docstring for the meaning of
    binary and _mask_geometry (including the caching/hashing
    note) — both behave identically here. This function is
    cached for the same reason: re-rendering a multi-million-
    pixel raster on every widget interaction is slow.
    """

    rgba, bounds_latlon, vmin, vmax = _render_raster_rgba(
        path,
        colormap=colormap,
        clip_percentiles=clip_percentiles,
        opacity=opacity,
        binary=binary,
        mask_geometry=_mask_geometry
    )

    west, south, east, north = bounds_latlon

    folium_bounds = [
        [south, west],
        [north, east]
    ]

    return rgba, folium_bounds, vmin, vmax
