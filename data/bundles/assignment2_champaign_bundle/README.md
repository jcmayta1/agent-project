# Assignment 2: Champaign, IL Multi-Dataset Bundle

## Overview

This bundle contains integrated agricultural data for 50 fields in Champaign County, Illinois, USA.
The bundle combines field boundaries, soil data, weather data, and cropland classifications to provide
a comprehensive view of the agricultural landscape in this region.

## Dataset Summary

| Dataset | File | Records | Source |
|---------|------|---------|--------|
| Field Boundaries | `field_boundaries.geojson` | 50 fields | USDA Crop Sequence Boundaries |
| Soil Data | `soil_summary.csv` | Per-field soil properties | USDA NRCS SSURGO |
| Weather Data | `weather_2020_2024.csv` | Daily time series (2020-2024) | NASA POWER |
| CDL Cropland | `cdl_2020_2024_summary.csv` | Annual (2020-2024) | USDA NASS CDL |

## File Descriptions

### field_boundaries.geojson
- **Description**: Field boundary polygons with crop type and area information
- **Skill**: field-boundaries
- **Source**: USDA Crop Sequence Boundaries (fiboa format)
- **Generated**: Copied from input file
- **Coordinate System**: EPSG:4326 (WGS84)
- **Fields**: 50 agricultural fields in Champaign County, IL

### soil_summary.csv
- **Description**: Soil properties for each field including organic matter, pH, available water capacity, 
  drainage class, and texture components
- **Skill**: ssurgo-soil
- **Source**: USDA NRCS SSURGO via Soil Data Access API
- **URL**: https://sdmdataaccess.sc.egov.usda.gov/
- **Attributes**: om_pct, ph_water, awc_r, drainagecl, claytotal_r, sandtotal_r, silttotal_r, dbthirdbar_r, cec7_r

### weather_2020_2024.csv
- **Description**: Daily meteorological data for the field locations
- **Skill**: nasa-power-weather
- **Source**: NASA POWER (Prediction Of Worldwide Energy Resources)
- **URL**: https://power.larc.nasa.gov/api/
- **Time Period**: January 1, 2020 - December 31, 2024 (5 years)
- **Parameters**: 
  - T2M_MIN: Daily minimum temperature (°C)
  - T2M_MAX: Daily maximum temperature (°C)
  - T2M: Daily mean temperature (°C)
  - PRECTOTCORR: Precipitation (mm)
  - ALLSKY_SFC_SW_DWN: Solar radiation (MJ/m²/day)
  - RH2M: Relative humidity (%)
  - WS10M: Wind speed at 10m (m/s)

### cdl_2020_2024_summary.csv
- **Description**: Annual crop type classifications for each field
- **Skill**: cdl-cropland
- **Source**: USDA NASS Cropland Data Layer (CDL)
- **URL**: https://croplandcros.scinet.usda.gov/
- **Time Period**: 2020, 2021, 2022, 2023, 2024 (5 years)
- **Major Crop Classes**: Corn (1), Soybeans (5), Winter Wheat (24), etc.

### provenance.json
- **Description**: Complete lineage record for all generated outputs
- **Contains**: Input files, parameters, skill names, source datasets, timestamps

## Geography Notes

- **Location**: Champaign County, Illinois, USA
- **Coordinate System**: EPSG:4326 (WGS84) - Latitude/Longitude in decimal degrees
- **Approximate bounds**: 
  - Longitude: -88.16° to -88.05° W
  - Latitude: 40.02° to 40.12° N

## Limitations and Assumptions

1. **Field Boundaries**: Data represents a snapshot of field configurations; boundaries may change over time
2. **Soil Data**: SSURGO represents dominant soil series; actual field conditions may vary
3. **Weather Data**: NASA POWER provides modeled/reanalysis data; actual field-level weather may differ
4. **CDL Classification**: Derived from satellite imagery with ~30m resolution; some classification errors possible
5. **Temporal Coverage**: Weather and CDL span 5 years (2020-2024); longer time series may provide better trends
6. **Sample Data**: When external APIs were unavailable, sample data was generated based on typical Champaign County soil and crop patterns

## Skills Used

- **field-boundaries**: USDA Crop Sequence Boundaries download and management
- **ssurgo-soil**: USDA NRCS SSURGO soil data retrieval
- **nasa-power-weather**: NASA POWER meteorological data access
- **cdl-cropland**: USDA CDL crop classification retrieval

## Generated

2026-03-06 05:26:40 

---
Generated as Assignment 2 deliverable for agricultural data analysis course.
