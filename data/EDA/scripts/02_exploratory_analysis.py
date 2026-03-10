"""
Exploratory Analysis Script for Champaign IL Agricultural Data
================================================================
This script performs exploratory data analysis on the filtered 10 fields.

Input:
- /workspaces/agent-project/data/EDA/data/fields_10.csv
- /workspaces/agent-project/data/EDA/data/soil_10.csv
- /workspaces/agent-project/data/EDA/data/weather_10.csv
- /workspaces/agent-project/data/EDA/data/crop_summary.csv

Output:
- Console summary statistics
- CSV files with analysis results
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# Define paths
EDA_DIR = "/workspaces/agent-project/data/EDA"
DATA_DIR = os.path.join(EDA_DIR, "data")

# Ensure output directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    """Load all prepared datasets."""
    print("Loading prepared datasets...")
    fields = pd.read_csv(os.path.join(DATA_DIR, "fields_10.csv"))
    soil = pd.read_csv(os.path.join(DATA_DIR, "soil_10.csv"))
    weather = pd.read_csv(os.path.join(DATA_DIR, "weather_10.csv"))
    crop = pd.read_csv(os.path.join(DATA_DIR, "crop_summary.csv"))
    
    weather['date'] = pd.to_datetime(weather['date'])
    
    return fields, soil, weather, crop

def analyze_fields(fields):
    """Analyze field characteristics."""
    print("\n" + "=" * 60)
    print("FIELD ANALYSIS")
    print("=" * 60)
    
    print(f"\nTotal fields: {len(fields)}")
    print(f"Total acreage: {fields['area_acres'].sum():.1f} acres")
    print(f"Average field size: {fields['area_acres'].mean():.1f} acres")
    print(f"Smallest field: {fields['area_acres'].min():.1f} acres")
    print(f"Largest field: {fields['area_acres'].max():.1f} acres")
    
    # Crop distribution
    crop_dist = fields['crop_name'].value_counts()
    print(f"\nCrop Distribution:")
    for crop, count in crop_dist.items():
        pct = count / len(fields) * 100
        print(f"  {crop}: {count} fields ({pct:.0f}%)")
        acres = fields[fields['crop_name'] == crop]['area_acres'].sum()
        print(f"    Total acres: {acres:.1f} ({acres/fields['area_acres'].sum()*100:.0f}%)")
    
    return {
        'total_fields': len(fields),
        'total_acres': fields['area_acres'].sum(),
        'avg_size': fields['area_acres'].mean(),
        'crop_distribution': crop_dist.to_dict()
    }

def analyze_crops(crop):
    """Analyze crop data and rotations."""
    print("\n" + "=" * 60)
    print("CROP ROTATION ANALYSIS (2020-2024)")
    print("=" * 60)
    
    # Crop by year
    print("\nCrop distribution by year:")
    yearly = crop.groupby(['year', 'crop_name']).size().unstack(fill_value=0)
    print(yearly)
    
    # Crop rotation patterns
    print("\nCrop Rotation Patterns:")
    pivot = crop.pivot_table(index='field_id', columns='year', values='crop_name', aggfunc='first')
    print(pivot)
    
    # Check for rotation (different crops in different years)
    rotations = pivot.apply(lambda x: x.nunique() > 1, axis=1)
    rotating = rotations.sum()
    static = len(rotations) - rotating
    
    print(f"\nRotation Summary:")
    print(f"  Fields with crop rotation: {rotating}")
    print(f"  Fields with same crop: {static}")
    
    return {
        'yearly_distribution': yearly.to_dict(),
        'fields_with_rotation': int(rotating),
        'fields_static': int(static)
    }

def analyze_soil(soil):
    """Analyze soil properties."""
    print("\n" + "=" * 60)
    print("SOIL PROPERTIES ANALYSIS")
    print("=" * 60)
    
    # Numeric soil properties
    numeric_cols = ['om_pct', 'ph_water', 'awc_r', 'claytotal_r', 'sandtotal_r', 'silttotal_r', 'dbthirdbar_r', 'cec7_r']
    
    print("\nDescriptive Statistics:")
    desc = soil[numeric_cols].describe()
    print(desc.round(2))
    
    # Drainage distribution
    print("\nDrainage Class Distribution:")
    drainage = soil['drainagecl'].value_counts()
    for d, count in drainage.items():
        pct = count / len(soil) * 100
        print(f"  {d}: {count} fields ({pct:.0f}%)")
    
    # pH analysis
    print("\nSoil pH Analysis:")
    ph_avg = soil['ph_water'].mean()
    ph_min = soil['ph_water'].min()
    ph_max = soil['ph_water'].max()
    print(f"  Average pH: {ph_avg:.2f}")
    print(f"  Range: {ph_min:.2f} - {ph_max:.2f}")
    
    if ph_avg < 6.0:
        print("  → Soil tends toward acidic - consider lime application")
    elif ph_avg > 7.0:
        print("  → Soil tends toward alkaline")
    else:
        print("  → pH is in optimal range for corn/soybeans")
    
    # Organic matter
    print("\nOrganic Matter Analysis:")
    om_avg = soil['om_pct'].mean()
    print(f"  Average OM: {om_avg:.2f}%")
    if om_avg > 3.5:
        print("  → High organic matter - good soil health")
    elif om_avg > 2.5:
        print("  → Moderate organic matter")
    else:
        print("  → Consider cover crops to improve OM")
    
    return {
        'avg_ph': round(ph_avg, 2),
        'avg_om': round(om_avg, 2),
        'drainage_distribution': drainage.to_dict(),
        'descriptive_stats': desc.to_dict()
    }

def analyze_weather(weather):
    """Analyze weather patterns."""
    print("\n" + "=" * 60)
    print("WEATHER ANALYSIS (2020-2024)")
    print("=" * 60)
    
    # Overall summary
    print("\n5-Year Weather Summary:")
    print(f"  Total precipitation: {weather['PRECTOTCORR'].sum():.1f} mm")
    print(f"  Average temperature: {weather['T2M'].mean():.1f}°C")
    print(f"  Average high: {weather['T2M_MAX'].mean():.1f}°C")
    print(f"  Average low: {weather['T2M_MIN'].mean():.1f}°C")
    print(f"  Average solar radiation: {weather['ALLSKY_SFC_SW_DWN'].mean():.1f} MJ/m²/day")
    
    # Annual precipitation
    weather['year'] = weather['date'].dt.year
    print("\nAnnual Precipitation:")
    annual_precip = weather.groupby('year')['PRECTOTCORR'].sum()
    for year, precip in annual_precip.items():
        print(f"  {year}: {precip:.1f} mm")
    
    # Convert to inches for reference (1 mm = 0.03937 in)
    avg_annual_inches = annual_precip.mean() * 0.03937
    print(f"\n  Average annual: {avg_annual_inches:.1f} inches")
    
    # Temperature by year
    print("\nAverage Temperature by Year:")
    annual_temp = weather.groupby('year')['T2M'].mean()
    for year, temp in annual_temp.items():
        print(f"  {year}: {temp:.1f}°C ({temp*9/5+32:.1f}°F)")
    
    # Growing season (May-Sep) analysis
    weather['month'] = weather['date'].dt.month
    growing_season = weather[weather['month'].isin([5, 6, 7, 8, 9])]
    
    print("\nGrowing Season (May-Sep) Averages:")
    print(f"  Precipitation: {growing_season['PRECTOTCORR'].sum()/5:.1f} mm per season")
    print(f"  Avg temperature: {growing_season['T2M'].mean():.1f}°C ({growing_season['T2M'].mean()*9/5+32:.1f}°F)")
    print(f"  Avg solar radiation: {growing_season['ALLSKY_SFC_SW_DWN'].mean():.1f} MJ/m²/day")
    
    return {
        'total_precip_mm': round(weather['PRECTOTCORR'].sum(), 1),
        'avg_temp_c': round(weather['T2M'].mean(), 1),
        'annual_precip': annual_precip.to_dict(),
        'avg_temp_by_year': annual_temp.to_dict()
    }

def save_analysis_results(field_stats, crop_stats, soil_stats, weather_stats):
    """Save analysis results to CSV."""
    print("\n" + "=" * 60)
    print("SAVING ANALYSIS RESULTS")
    print("=" * 60)
    
    # Save field summary
    field_summary = pd.DataFrame([field_stats])
    field_summary.to_csv(os.path.join(DATA_DIR, "analysis_field_summary.csv"), index=False)
    print("  Saved: analysis_field_summary.csv")
    
    # Save soil summary
    soil_summary = pd.DataFrame([{
        'avg_ph': soil_stats['avg_ph'],
        'avg_om': soil_stats['avg_om'],
        'drainage': ', '.join(soil_stats['drainage_distribution'].keys())
    }])
    soil_summary.to_csv(os.path.join(DATA_DIR, "analysis_soil_summary.csv"), index=False)
    print("  Saved: analysis_soil_summary.csv")
    
    # Save weather summary
    weather_summary = pd.DataFrame([{
        'total_precip_mm': weather_stats['total_precip_mm'],
        'avg_temp_c': weather_stats['avg_temp_c']
    }])
    weather_summary.to_csv(os.path.join(DATA_DIR, "analysis_weather_summary.csv"), index=False)
    print("  Saved: analysis_weather_summary.csv")
    
    print("\n✓ Exploratory analysis complete!")

def main():
    print("=" * 60)
    print("CHAMPAIGN IL EXPLORATORY DATA ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load data
    fields, soil, weather, crop = load_data()
    
    # Run analyses
    field_stats = analyze_fields(fields)
    crop_stats = analyze_crops(crop)
    soil_stats = analyze_soil(soil)
    weather_stats = analyze_weather(weather)
    
    # Save results
    save_analysis_results(field_stats, crop_stats, soil_stats, weather_stats)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
