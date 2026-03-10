"""
Visualizations Script for Champaign IL Agricultural Data
========================================================
This script creates visualizations for the agricultural analysis report.

Input:
- /workspaces/agent-project/data/EDA/data/fields_10.csv
- /workspaces/agent-project/data/EDA/data/soil_10.csv
- /workspaces/agent-project/data/EDA/data/weather_10.csv

Output:
- /workspaces/agent-project/data/EDA/figures/crop_distribution.png
- /workspaces/agent-project/data/EDA/figures/soil_ph_histogram.png
- /workspaces/agent-project/data/EDA/figures/annual_precipitation.png
- /workspaces/agent-project/data/EDA/figures/correlation_heatmap.png
- /workspaces/agent-project/data/EDA/figures/field_map.html
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

# Define paths
EDA_DIR = "/workspaces/agent-project/data/EDA"
DATA_DIR = os.path.join(EDA_DIR, "data")
FIGURES_DIR = os.path.join(EDA_DIR, "figures")

# Ensure output directory exists
os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data():
    """Load all prepared datasets."""
    print("Loading data for visualizations...")
    fields = pd.read_csv(os.path.join(DATA_DIR, "fields_10.csv"))
    soil = pd.read_csv(os.path.join(DATA_DIR, "soil_10.csv"))
    weather = pd.read_csv(os.path.join(DATA_DIR, "weather_10.csv"))
    weather['date'] = pd.to_datetime(weather['date'])
    return fields, soil, weather

def create_crop_distribution_chart(fields):
    """Create crop distribution pie chart."""
    print("\nCreating crop distribution chart...")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    crop_counts = fields['crop_name'].value_counts()
    colors = ['#FFD700', '#8B4513']  # Gold for corn, Brown for soybeans
    
    wedges, texts, autotexts = ax.pie(
        crop_counts.values, 
        labels=crop_counts.index,
        autopct='%1.0f%%',
        colors=colors[:len(crop_counts)],
        startangle=90,
        explode=[0.02] * len(crop_counts),
        shadow=True
    )
    
    ax.set_title('Crop Distribution - Top 10 Fields\n(Champaign County, IL)', 
                  fontsize=14, fontweight='bold')
    
    # Add legend with acres
    total_acres = fields['area_acres'].sum()
    legend_labels = [f"{crop}: {count} fields ({fields[fields["crop_name"]==crop]["area_acres"].sum():.0f} acres)" 
                    for crop, count in crop_counts.items()]
    ax.legend(wedges, legend_labels, title="Crops", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "crop_distribution.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: crop_distribution.png")

def create_soil_ph_histogram(soil):
    """Create soil pH distribution histogram."""
    print("\nCreating soil pH histogram...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Histogram with KDE
    n, bins, patches = ax.hist(soil['ph_water'], bins=8, color='#4CAF50', 
                                edgecolor='white', alpha=0.7)
    
    # Add mean line
    mean_ph = soil['ph_water'].mean()
    ax.axvline(mean_ph, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_ph:.2f}')
    
    # Optimal range shading (6.0-7.0 for corn/soybeans)
    ax.axvspan(6.0, 7.0, alpha=0.2, color='green', label='Optimal pH range')
    
    ax.set_xlabel('Soil pH', fontsize=12)
    ax.set_ylabel('Number of Fields', fontsize=12)
    ax.set_title('Soil pH Distribution - Top 10 Fields\n(Champaign County, IL)', 
                  fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    
    # Add stats text
    stats_text = f"Mean: {soil['ph_water'].mean():.2f}\nMin: {soil['ph_water'].min():.2f}\nMax: {soil['ph_water'].max():.2f}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "soil_ph_histogram.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: soil_ph_histogram.png")

def create_annual_precipitation_chart(weather):
    """Create annual precipitation bar chart."""
    print("\nCreating annual precipitation chart...")
    
    weather['year'] = weather['date'].dt.year
    annual_precip = weather.groupby('year')['PRECTOTCORR'].sum()
    
    # Convert to inches (1 mm = 0.03937 in)
    annual_precip_inches = annual_precip * 0.03937
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(annual_precip_inches.index, annual_precip_inches.values, 
                  color='#2196F3', edgecolor='white', alpha=0.8)
    
    # Add average line
    avg_precip = annual_precip_inches.mean()
    ax.axhline(avg_precip, color='red', linestyle='--', linewidth=2, 
               label=f'5-Year Average: {avg_precip:.1f} inches')
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Precipitation (inches)', fontsize=12)
    ax.set_title('Annual Precipitation - Top 10 Fields\n(Champaign County, IL, 2020-2024)', 
                  fontsize=14, fontweight='bold')
    ax.legend()
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}"',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "annual_precipitation.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: annual_precipitation.png")

def create_correlation_heatmap(soil):
    """Create correlation heatmap for soil properties."""
    print("\nCreating correlation heatmap...")
    
    # Select numeric columns
    numeric_cols = ['om_pct', 'ph_water', 'awc_r', 'claytotal_r', 'sandtotal_r', 
                    'silttotal_r', 'dbthirdbar_r', 'cec7_r']
    
    # Create shorter labels for display
    labels = {
        'om_pct': 'Organic Matter (%)',
        'ph_water': 'pH',
        'awc_r': 'Water Holding Cap.',
        'claytotal_r': 'Clay (%)',
        'sandtotal_r': 'Sand (%)',
        'silttotal_r': 'Silt (%)',
        'dbthirdbar_r': 'Bulk Density',
        'cec7_r': 'CEC'
    }
    
    corr_matrix = soil[numeric_cols].corr()
    corr_matrix.index = [labels.get(c, c) for c in corr_matrix.index]
    corr_matrix.columns = [labels.get(c, c) for c in corr_matrix.columns]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', center=0,
                square=True, fmt='.2f', cbar_kws={"shrink": 0.8},
                linewidths=0.5, ax=ax)
    
    ax.set_title('Soil Properties Correlation Matrix\n(Champaign County, IL)', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "correlation_heatmap.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: correlation_heatmap.png")

def create_field_map(fields, soil):
    """Create interactive Leaflet map of fields."""
    print("\nCreating interactive field map...")
    
    # Load GeoJSON
    geojson_path = os.path.join(DATA_DIR, "fields_10.geojson")
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    # Merge field and soil data
    fields_with_soil = fields.merge(soil, on='field_id')
    
    # Add soil data to GeoJSON
    for feature in geojson_data['features']:
        fid = feature['properties']['field_id']
        field_data = fields_with_soil[fields_with_soil['field_id'] == fid]
        if len(field_data) > 0:
            feature['properties']['area_acres'] = float(field_data['area_acres'].values[0])
            feature['properties']['crop'] = field_data['crop_name'].values[0]
            feature['properties']['ph'] = float(field_data['ph_water'].values[0])
            feature['properties']['om_pct'] = float(field_data['om_pct'].values[0])
    
    # Create HTML map
    geojson_str = json.dumps(geojson_data)
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Champaign County IL - Field Analysis Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        .info {{
            padding: 10px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            max-width: 250px;
        }}
        .info h4 {{ margin: 0 0 8px; }}
        .legend {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            line-height: 1.5;
        }}
        .legend i {{
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([40.07, -88.12], 12);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        var geojsonData = {geojson_str};
        
        function getColor(crop) {{
            return crop === 'Corn' ? '#FFD700' : '#8B4513';
        }}
        
        function style(feature) {{
            return {{
                fillColor: getColor(feature.properties.crop),
                weight: 2,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.6
            }};
        }}
        
        function highlightFeature(e) {{
            var layer = e.target;
            layer.setStyle({{
                weight: 3,
                color: '#666',
                fillOpacity: 0.8
            }});
            layer.bringToFront();
        }}
        
        function resetHighlight(e) {{
            geojsonLayer.resetStyle(e.target);
        }}
        
        function onEachFeature(feature, layer) {{
            layer.on({{
                mouseover: highlightFeature,
                mouseout: resetHighlight
            }});
            var props = feature.properties;
            var popupContent = '<div class="info">' +
                '<h4>Field ID: ' + props.field_id + '</h4>' +
                '<b>Area:</b> ' + props.area_acres.toFixed(1) + ' acres<br>' +
                '<b>Crop:</b> ' + props.crop + '<br>' +
                '<b>Soil pH:</b> ' + props.ph.toFixed(2) + '<br>' +
                '<b>Organic Matter:</b> ' + props.om_pct.toFixed(2) + '%' +
                '</div>';
            layer.bindPopup(popupContent);
        }}
        
        var geojsonLayer = L.geoJSON(geojsonData, {{
            style: style,
            onEachFeature: onEachFeature
        }}).addTo(map);
        
        map.fitBounds(geojsonLayer.getBounds(), {{padding: [50, 50]}});
        
        var legend = L.control({{position: 'bottomright'}});
        legend.onAdd = function(map) {{
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<h4>Crops</h4>' +
                '<i style="background: #FFD700"></i> Corn<br>' +
                '<i style="background: #8B4513"></i> Soybeans';
            return div;
        }};
        legend.addTo(map);
    </script>
</body>
</html>'''
    
    with open(os.path.join(FIGURES_DIR, "field_map.html"), 'w') as f:
        f.write(html_content)
    
    print(f"  Saved: field_map.html")

def main():
    print("=" * 60)
    print("CREATING VISUALIZATIONS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load data
    fields, soil, weather = load_data()
    
    # Create visualizations
    create_crop_distribution_chart(fields)
    create_soil_ph_histogram(soil)
    create_annual_precipitation_chart(weather)
    create_correlation_heatmap(soil)
    create_field_map(fields, soil)
    
    print("\n" + "=" * 60)
    print("✓ VISUALIZATIONS COMPLETE")
    print("=" * 60)
    print(f"Saved to: {FIGURES_DIR}")

if __name__ == "__main__":
    main()
