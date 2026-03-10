"""
Data Preparation Script for Champaign IL Agricultural Analysis
===============================================================
This script loads source data and filters to the top 10 fields by area.

Input:
- /workspaces/agent-project/data/field-boundaries/field_locations.csv
- /workspaces/agent-project/data/bundles/assignment2_champaign_bundle/soil_summary.csv
- /workspaces/agent-project/data/bundles/assignment2_champaign_bundle/weather_2020_2024.csv
- /workspaces/agent-project/data/bundles/assignment2_champaign_bundle/cdl_2020_2024_summary.csv
- /workspaces/agent-project/data/bundles/assignment2_champaign_bundle/field_boundaries.geojson

Output:
- /workspaces/agent-project/data/EDA/data/fields_10.csv
- /workspaces/agent-project/data/EDA/data/soil_10.csv
- /workspaces/agent-project/data/EDA/data/weather_10.csv
- /workspaces/agent-project/data/EDA/data/crop_summary.csv
- /workspaces/agent-project/data/EDA/data/fields_10.geojson
"""

import pandas as pd
import json
import os

# Define paths
BASE_DIR = "/workspaces/agent-project/data"
EDA_DIR = os.path.join(BASE_DIR, "EDA")
DATA_DIR = os.path.join(EDA_DIR, "data")

# Ensure output directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# USDA CDL Crop Code Mapping (Standard)
# Source: USDA NASS Cropland Data Layer
CDL_CROP_CODES = {
    1: "Corn",
    2: "Cotton",
    3: "Rice",
    4: "Sorghum",
    5: "Soybeans",
    6: "Sunflower",
    10: "Peanuts",
    21: "Barley",
    22: "Durum Wheat",
    23: "Spring Wheat",
    24: "Winter Wheat",
    36: "Alfalfa",
    61: "Fallow/Idle Cropland"
}

def load_field_locations():
    """Load field locations and select top 10 by area."""
    print("Loading field locations...")
    df = pd.read_csv(os.path.join(BASE_DIR, "field-boundaries/field_locations.csv"))
    
    # Sort by area descending and take top 10
    df_sorted = df.sort_values('area_acres', ascending=False).head(10)
    
    # Get field IDs
    top_10_field_ids = df_sorted['field_id'].tolist()
    
    print(f"Top 10 fields by area:")
    for i, row in df_sorted.iterrows():
        print(f"  {row['field_id']}: {row['area_acres']:.1f} acres - {row['crop_name']}")
    
    return df_sorted, top_10_field_ids

def load_soil_data(field_ids):
    """Load and filter soil data for selected fields."""
    print("\nLoading soil data...")
    df = pd.read_csv(os.path.join(BASE_DIR, "bundles/assignment2_champaign_bundle/soil_summary.csv"))
    df_filtered = df[df['field_id'].isin(field_ids)]
    print(f"  Filtered to {len(df_filtered)} fields")
    return df_filtered

def load_weather_data(field_ids):
    """Load and filter weather data for selected fields."""
    print("\nLoading weather data...")
    df = pd.read_csv(os.path.join(BASE_DIR, "bundles/assignment2_champaign_bundle/weather_2020_2024.csv"))
    df['date'] = pd.to_datetime(df['date'])
    df_filtered = df[df['field_id'].isin(field_ids)]
    print(f"  Filtered to {len(df_filtered)} records (2020-2024)")
    return df_filtered

def load_cdl_data(field_ids):
    """Load CDL crop data and verify crop code mapping."""
    print("\nLoading CDL crop data...")
    df = pd.read_csv(os.path.join(BASE_DIR, "bundles/assignment2_champaign_bundle/cdl_2020_2024_summary.csv"))
    df_filtered = df[df['field_id'].isin(field_ids)]
    
    # Verify crop code mapping
    print("\n  Verifying crop code mapping:")
    unique_codes = df_filtered['crop_code'].unique()
    for code in unique_codes:
        mapped_name = CDL_CROP_CODES.get(code, "Unknown")
        existing_name = df_filtered[df_filtered['crop_code'] == code]['crop_name'].iloc[0]
        match = "✓" if mapped_name == existing_name else "✗ MISMATCH"
        print(f"    Code {code}: CDL says '{mapped_name}', File has '{existing_name}' {match}")
    
    # Add standardized crop names from CDL mapping
    df_filtered = df_filtered.copy()
    df_filtered['crop_name_standardized'] = df_filtered['crop_code'].map(CDL_CROP_CODES)
    
    print(f"  Filtered to {len(df_filtered)} records (2020-2024)")
    return df_filtered

def load_geojson(field_ids):
    """Load and filter GeoJSON boundaries for selected fields."""
    print("\nLoading GeoJSON boundaries...")
    geojson_path = os.path.join(BASE_DIR, "bundles/assignment2_champaign_bundle/field_boundaries.geojson")
    
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    # Filter features - GeoJSON has string field_ids
    field_ids_str = set(str(fid) for fid in field_ids)
    features = [f for f in geojson_data['features'] if str(f['properties']['field_id']) in field_ids_str]
    
    print(f"  Matched {len(features)} features")
    filtered_geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    print(f"  Filtered to {len(features)} field polygons")
    return filtered_geojson

def save_outputs(fields_df, soil_df, weather_df, cdl_df, geojson_data):
    """Save all filtered datasets."""
    print("\nSaving filtered datasets...")
    
    # Save field locations
    fields_df.to_csv(os.path.join(DATA_DIR, "fields_10.csv"), index=False)
    print(f"  Saved: fields_10.csv ({len(fields_df)} fields)")
    
    # Save soil data
    soil_df.to_csv(os.path.join(DATA_DIR, "soil_10.csv"), index=False)
    print(f"  Saved: soil_10.csv ({len(soil_df)} records)")
    
    # Save weather data
    weather_df.to_csv(os.path.join(DATA_DIR, "weather_10.csv"), index=False)
    print(f"  Saved: weather_10.csv ({len(weather_df)} records)")
    
    # Save crop summary
    cdl_df.to_csv(os.path.join(DATA_DIR, "crop_summary.csv"), index=False)
    print(f"  Saved: crop_summary.csv ({len(cdl_df)} records)")
    
    # Save GeoJSON
    geojson_path = os.path.join(DATA_DIR, "fields_10.geojson")
    with open(geojson_path, 'w') as f:
        json.dump(geojson_data, f)
    print(f"  Saved: fields_10.geojson ({len(geojson_data['features'])} features)")
    
    print("\n✓ Data preparation complete!")

def main():
    print("=" * 60)
    print("CHAMPAIGN IL AGRICULTURAL DATA PREPARATION")
    print("=" * 60)
    
    # Load and filter data
    fields_df, field_ids = load_field_locations()
    soil_df = load_soil_data(field_ids)
    weather_df = load_weather_data(field_ids)
    cdl_df = load_cdl_data(field_ids)
    geojson_data = load_geojson(field_ids)
    
    # Save outputs
    save_outputs(fields_df, soil_df, weather_df, cdl_df, geojson_data)
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Fields analyzed: {len(field_ids)}")
    print(f"Total acreage: {fields_df['area_acres'].sum():.1f} acres")
    print(f"Weather period: 2020-2024 (5 years)")
    print(f"Soil attributes: {len(soil_df.columns) - 1}")
    print(f"CDL crop years: {cdl_df['year'].unique().tolist()}")

if __name__ == "__main__":
    main()
