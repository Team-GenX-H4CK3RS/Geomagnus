import ee
import geemap
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
import h5py
import netCDF4 as nc
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import xarray as xr
import rasterio
from rasterio.transform import from_bounds
import folium
from scipy.interpolate import griddata
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Initialize Google Earth Engine
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()

class EMITMineralDepthPredictor:
    def __init__(self, gmaps_key, groq_key, gemini_key):
        """
        Advanced Mineral Depth Prediction using NASA EMIT L2B Mineralogy Data
        """
        self.gmaps_key = gmaps_key
        self.groq_key = groq_key
        self.gemini_key = gemini_key
        
        # EMIT L2B Mineral Groups based on NASA documentation
        self.emit_minerals = {
            'phyllosilicates': {
                'minerals': ['kaolinite', 'montmorillonite', 'illite', 'muscovite', 'chlorite'],
                'spectral_features': [2200, 2350, 2450],
                'depth_indicator': 'high',  # Often found at depth
                'exploration_significance': 'alteration_zones'
            },
            'carbonates': {
                'minerals': ['calcite', 'dolomite', 'magnesite'],
                'spectral_features': [2300, 2340],
                'depth_indicator': 'variable',
                'exploration_significance': 'hydrothermal_systems'
            },
            'sulfates': {
                'minerals': ['gypsum', 'alunite', 'jarosite'],
                'spectral_features': [1450, 1750, 2200],
                'depth_indicator': 'surface_to_shallow',
                'exploration_significance': 'acid_alteration'
            },
            'iron_oxides': {
                'minerals': ['hematite', 'goethite', 'magnetite'],
                'spectral_features': [850, 900, 650],
                'depth_indicator': 'variable',
                'exploration_significance': 'ore_deposits'
            },
            'silicates': {
                'minerals': ['quartz', 'feldspar', 'pyroxene'],
                'spectral_features': [1200, 1400, 2200],
                'depth_indicator': 'deep',
                'exploration_significance': 'host_rocks'
            }
        }
        
        # Depth prediction parameters based on geological principles
        self.depth_parameters = {
            'surface_weathering': {'max_depth': 50, 'minerals': ['iron_oxides', 'sulfates']},
            'shallow_alteration': {'max_depth': 200, 'minerals': ['phyllosilicates', 'carbonates']},
            'intermediate_zone': {'max_depth': 500, 'minerals': ['phyllosilicates', 'carbonates', 'silicates']},
            'deep_primary': {'max_depth': 2000, 'minerals': ['silicates', 'sulfides']},
            'basement': {'max_depth': 5000, 'minerals': ['silicates', 'metamorphic']}
        }
    
    def get_location_coordinates(self, location_name):
        """Get coordinates using Google Maps API"""
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {'address': location_name, 'key': self.gmaps_key}
        
        response = requests.get(geocode_url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError(f"Could not geocode location: {location_name}")
    
    def simulate_emit_l2b_data(self, study_area, n_points=1000):
        """
        Simulate EMIT L2B mineralogy data based on NASA EMIT specifications
        This simulates the actual EMIT data structure and mineral abundances
        """
        # Generate random points within study area
        bounds = study_area.bounds().getInfo()['coordinates'][0]
        min_lon, max_lon = min([p[0] for p in bounds]), max([p[0] for p in bounds])
        min_lat, max_lat = min([p[1] for p in bounds]), max([p[1] for p in bounds])
        
        np.random.seed(42)  # For reproducible results
        
        # Generate coordinates
        lons = np.random.uniform(min_lon, max_lon, n_points)
        lats = np.random.uniform(min_lat, max_lat, n_points)
        
        # Simulate EMIT L2B mineral abundances (0-100%)
        emit_data = {
            'longitude': lons,
            'latitude': lats,
            'elevation': np.random.uniform(100, 2500, n_points),
        }
        
        # Simulate mineral abundances based on EMIT L2B format
        for mineral_group, info in self.emit_minerals.items():
            for mineral in info['minerals']:
                # Create realistic mineral distributions
                if mineral_group == 'phyllosilicates':
                    # Higher abundances in weathered areas (lower elevations)
                    base_abundance = 30 * (1 - (emit_data['elevation'] - 100) / 2400)
                elif mineral_group == 'iron_oxides':
                    # Higher in oxidized surface environments
                    base_abundance = 20 * np.random.beta(2, 5, n_points) * 100
                elif mineral_group == 'carbonates':
                    # Patchy distribution
                    base_abundance = 15 * np.random.exponential(0.3, n_points)
                else:
                    base_abundance = 10 * np.random.gamma(2, 2, n_points)
                
                # Add noise and ensure realistic ranges
                abundance = np.clip(base_abundance + np.random.normal(0, 5, n_points), 0, 100)
                emit_data[f'{mineral}_abundance'] = abundance
                
                # Add uncertainty estimates (EMIT L2B includes uncertainty)
                emit_data[f'{mineral}_uncertainty'] = np.random.uniform(5, 15, n_points)
        
        return pd.DataFrame(emit_data)
    
    def calculate_depth_predictions(self, emit_df):
        """
        Calculate depth predictions based on mineral assemblages and geological principles
        """
        depth_predictions = {}
        
        for idx, row in emit_df.iterrows():
            mineral_depths = {}
            
            # Calculate depth for each mineral based on abundance and geological context
            for mineral_group, info in self.emit_minerals.items():
                for mineral in info['minerals']:
                    abundance = row[f'{mineral}_abundance']
                    uncertainty = row[f'{mineral}_uncertainty']
                    elevation = row['elevation']
                    
                    # Base depth calculation using multiple factors
                    if info['depth_indicator'] == 'surface_to_shallow':
                        base_depth = abundance * 0.5  # Shallow minerals
                        max_depth = 100
                    elif info['depth_indicator'] == 'high':
                        base_depth = abundance * 2.0  # Deep alteration minerals
                        max_depth = 800
                    elif info['depth_indicator'] == 'deep':
                        base_depth = abundance * 5.0  # Primary minerals
                        max_depth = 2000
                    else:  # variable
                        base_depth = abundance * 1.5
                        max_depth = 500
                    
                    # Adjust for elevation (higher elevations = more erosion = deeper exposure)
                    elevation_factor = 1 + (elevation - 500) / 1000
                    predicted_depth = base_depth * elevation_factor
                    
                    # Add uncertainty
                    depth_uncertainty = predicted_depth * (uncertainty / 100)
                    
                    mineral_depths[mineral] = {
                        'predicted_depth': min(predicted_depth, max_depth),
                        'uncertainty': depth_uncertainty,
                        'confidence': max(0, 100 - uncertainty),
                        'max_depth': max_depth,
                        'abundance': abundance
                    }
            
            depth_predictions[idx] = mineral_depths
        
        return depth_predictions
    
    def create_3d_depth_model(self, emit_df, depth_predictions, location_name):
        """
        Create comprehensive 3D depth model showing mineral distribution at depth
        """
        # Prepare data for 3D visualization
        plot_data = []
        
        for idx, row in emit_df.iterrows():
            if idx in depth_predictions:
                for mineral, depth_info in depth_predictions[idx].items():
                    if depth_info['abundance'] > 10:  # Only show significant abundances
                        # Surface point
                        plot_data.append({
                            'longitude': row['longitude'],
                            'latitude': row['latitude'],
                            'depth': 0,
                            'mineral': mineral,
                            'abundance': depth_info['abundance'],
                            'confidence': depth_info['confidence'],
                            'type': 'surface'
                        })
                        
                        # Predicted depth point
                        plot_data.append({
                            'longitude': row['longitude'],
                            'latitude': row['latitude'],
                            'depth': -depth_info['predicted_depth'],  # Negative for depth
                            'mineral': mineral,
                            'abundance': depth_info['abundance'] * 0.7,  # Reduce with depth
                            'confidence': depth_info['confidence'],
                            'type': 'depth'
                        })
        
        df_3d = pd.DataFrame(plot_data)
        
        # Create 3D visualization
        fig = go.Figure()
        
        # Color mapping for different minerals
        mineral_colors = {
            'kaolinite': 'blue', 'montmorillonite': 'lightblue', 'illite': 'darkblue',
            'calcite': 'green', 'dolomite': 'lightgreen',
            'hematite': 'red', 'goethite': 'orange',
            'gypsum': 'yellow', 'alunite': 'gold',
            'quartz': 'gray', 'feldspar': 'lightgray'
        }
        
        # Add traces for each mineral
        for mineral in df_3d['mineral'].unique():
            mineral_data = df_3d[df_3d['mineral'] == mineral]
            
            fig.add_trace(go.Scatter3d(
                x=mineral_data['longitude'],
                y=mineral_data['latitude'],
                z=mineral_data['depth'],
                mode='markers',
                marker=dict(
                    size=mineral_data['abundance'] / 5,
                    color=mineral_colors.get(mineral, 'purple'),
                    opacity=0.7,
                    colorscale='Viridis',
                    showscale=False
                ),
                name=mineral.title(),
                text=[f"Mineral: {mineral}<br>Abundance: {a:.1f}%<br>Depth: {d:.0f}m<br>Confidence: {c:.0f}%" 
                      for a, d, c in zip(mineral_data['abundance'], -mineral_data['depth'], mineral_data['confidence'])],
                hovertemplate='<b>%{text}</b><extra></extra>'
            ))
        
        # Update layout
        fig.update_layout(
            title=f'3D Mineral Depth Prediction Model - {location_name}',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Depth (m)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
                zaxis=dict(range=[-2000, 100])  # Show depth range
            ),
            width=1200,
            height=800,
            showlegend=True
        )
        
        return fig, df_3d
    
    def create_depth_cross_sections(self, emit_df, depth_predictions, location_name):
        """
        Create cross-sectional views showing mineral distribution with depth
        """
        # Create multiple cross-sections
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('North-South Cross Section', 'East-West Cross Section',
                          'Depth Distribution by Mineral', 'Confidence vs Depth'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Prepare cross-section data
        cross_section_data = []
        for idx, row in emit_df.iterrows():
            if idx in depth_predictions:
                for mineral, depth_info in depth_predictions[idx].items():
                    if depth_info['abundance'] > 5:
                        cross_section_data.append({
                            'longitude': row['longitude'],
                            'latitude': row['latitude'],
                            'depth': depth_info['predicted_depth'],
                            'mineral': mineral,
                            'abundance': depth_info['abundance'],
                            'confidence': depth_info['confidence']
                        })
        
        cs_df = pd.DataFrame(cross_section_data)
        
        if not cs_df.empty:
            # North-South cross section
            ns_data = cs_df.sort_values('latitude')
            fig.add_trace(
                go.Scatter(
                    x=ns_data['latitude'],
                    y=-ns_data['depth'],
                    mode='markers',
                    marker=dict(
                        size=ns_data['abundance']/3,
                        color=ns_data['abundance'],
                        colorscale='Viridis',
                        showscale=True
                    ),
                    name='N-S Section'
                ),
                row=1, col=1
            )
            
            # East-West cross section
            ew_data = cs_df.sort_values('longitude')
            fig.add_trace(
                go.Scatter(
                    x=ew_data['longitude'],
                    y=-ew_data['depth'],
                    mode='markers',
                    marker=dict(
                        size=ew_data['abundance']/3,
                        color=ew_data['abundance'],
                        colorscale='Plasma'
                    ),
                    name='E-W Section'
                ),
                row=1, col=2
            )
            
            # Depth distribution by mineral
            mineral_depth_avg = cs_df.groupby('mineral')['depth'].mean().sort_values()
            fig.add_trace(
                go.Bar(
                    x=mineral_depth_avg.index,
                    y=mineral_depth_avg.values,
                    name='Avg Depth'
                ),
                row=2, col=1
            )
            
            # Confidence vs Depth
            fig.add_trace(
                go.Scatter(
                    x=cs_df['confidence'],
                    y=cs_df['depth'],
                    mode='markers',
                    marker=dict(
                        size=cs_df['abundance']/5,
                        color=cs_df['abundance'],
                        colorscale='RdYlBu'
                    ),
                    name='Confidence vs Depth'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title=f'Mineral Depth Cross-Sections - {location_name}',
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_mineral_targeting_map(self, emit_df, depth_predictions, location_name):
        """
        Create targeting map for different depth zones
        """
        # Calculate targeting scores for different depth zones
        targeting_data = []
        
        for idx, row in emit_df.iterrows():
            if idx in depth_predictions:
                # Surface targeting (0-50m)
                surface_score = 0
                shallow_score = 0
                deep_score = 0
                
                for mineral, depth_info in depth_predictions[idx].items():
                    depth = depth_info['predicted_depth']
                    abundance = depth_info['abundance']
                    confidence = depth_info['confidence']
                    
                    weighted_score = abundance * (confidence / 100)
                    
                    if depth <= 50:
                        surface_score += weighted_score
                    elif depth <= 200:
                        shallow_score += weighted_score
                    else:
                        deep_score += weighted_score
                
                targeting_data.append({
                    'longitude': row['longitude'],
                    'latitude': row['latitude'],
                    'surface_score': surface_score,
                    'shallow_score': shallow_score,
                    'deep_score': deep_score,
                    'total_score': surface_score + shallow_score + deep_score
                })
        
        targeting_df = pd.DataFrame(targeting_data)
        
        # Create interactive map
        center_lat = targeting_df['latitude'].mean()
        center_lon = targeting_df['longitude'].mean()
        
        Map = geemap.Map(center=[center_lat, center_lon], zoom=10)
        Map.add_basemap('SATELLITE')
        
        # Add targeting zones as point data
        for depth_zone in ['surface_score', 'shallow_score', 'deep_score']:
            zone_data = targeting_df[targeting_df[depth_zone] > targeting_df[depth_zone].quantile(0.7)]
            
            if not zone_data.empty:
                # Convert to GEE FeatureCollection for visualization
                features = []
                for _, row in zone_data.iterrows():
                    point = ee.Geometry.Point([row['longitude'], row['latitude']])
                    feature = ee.Feature(point, {depth_zone: row[depth_zone]})
                    features.append(feature)
                
                if features:
                    fc = ee.FeatureCollection(features)
                    
                    vis_params = {
                        'color': 'red' if 'surface' in depth_zone else 'blue' if 'shallow' in depth_zone else 'green',
                        'pointRadius': 5,
                        'fillOpacity': 0.7
                    }
                    
                    Map.addLayer(fc, vis_params, f'{depth_zone.replace("_", " ").title()} Targets')
        
        return Map, targeting_df
    
    def generate_depth_exploration_report(self, emit_df, depth_predictions, targeting_df, location_name):
        """
        Generate comprehensive depth-based exploration report
        """
        # Calculate statistics
        total_points = len(emit_df)
        high_potential_surface = len(targeting_df[targeting_df['surface_score'] > targeting_df['surface_score'].quantile(0.8)])
        high_potential_shallow = len(targeting_df[targeting_df['shallow_score'] > targeting_df['shallow_score'].quantile(0.8)])
        high_potential_deep = len(targeting_df[targeting_df['deep_score'] > targeting_df['deep_score'].quantile(0.8)])
        
        # Find best targets
        best_surface = targeting_df.loc[targeting_df['surface_score'].idxmax()]
        best_shallow = targeting_df.loc[targeting_df['shallow_score'].idxmax()]
        best_deep = targeting_df.loc[targeting_df['deep_score'].idxmax()]
        
        report = f"""
# EMIT L2B MINERAL DEPTH PREDICTION REPORT
## Location: {location_name}

### EXECUTIVE SUMMARY
- **Total Survey Points**: {total_points:,}
- **High Potential Surface Targets (0-50m)**: {high_potential_surface}
- **High Potential Shallow Targets (50-200m)**: {high_potential_shallow}
- **High Potential Deep Targets (>200m)**: {high_potential_deep}

### DEPTH-BASED TARGETING ZONES

#### **Surface Zone (0-50m depth)**
- **Primary Minerals**: Iron oxides, sulfates, weathered phyllosilicates
- **Exploration Method**: Surface sampling, shallow drilling
- **Best Target Coordinates**: {best_surface['longitude']:.6f}, {best_surface['latitude']:.6f}
- **Target Score**: {best_surface['surface_score']:.2f}

#### **Shallow Zone (50-200m depth)**
- **Primary Minerals**: Clay minerals, carbonates, altered zones
- **Exploration Method**: RC drilling, geophysics
- **Best Target Coordinates**: {best_shallow['longitude']:.6f}, {best_shallow['latitude']:.6f}
- **Target Score**: {best_shallow['shallow_score']:.2f}

#### **Deep Zone (>200m depth)**
- **Primary Minerals**: Primary silicates, sulfides, basement minerals
- **Exploration Method**: Diamond drilling, deep geophysics
- **Best Target Coordinates**: {best_deep['longitude']:.6f}, {best_deep['latitude']:.6f}
- **Target Score**: {best_deep['deep_score']:.2f}

### MINERAL-SPECIFIC PREDICTIONS
"""
        
        # Add mineral-specific depth predictions
        for mineral_group, info in self.emit_minerals.items():
            avg_depths = []
            for idx in depth_predictions:
                for mineral in info['minerals']:
                    if mineral in depth_predictions[idx]:
                        avg_depths.append(depth_predictions[idx][mineral]['predicted_depth'])
            
            if avg_depths:
                report += f"""
**{mineral_group.upper()}**:
- Average Predicted Depth: {np.mean(avg_depths):.0f}m
- Depth Range: {np.min(avg_depths):.0f}m - {np.max(avg_depths):.0f}m
- Exploration Significance: {info['exploration_significance']}
"""
        
        report += f"""
### DRILLING RECOMMENDATIONS

#### **Phase 1 - Surface Verification (0-100m)**
- Target {high_potential_surface} high-priority surface locations
- Use RC drilling or shallow diamond drilling
- Focus on iron oxide and sulfate anomalies

#### **Phase 2 - Shallow Exploration (100-300m)**
- Target {high_potential_shallow} shallow alteration zones
- Use diamond drilling with geophysical support
- Focus on phyllosilicate and carbonate zones

#### **Phase 3 - Deep Exploration (>300m)**
- Target {high_potential_deep} deep primary zones
- Use deep diamond drilling
- Focus on primary silicate and potential sulfide zones

### CONFIDENCE ASSESSMENT
- **High Confidence Targets**: >80% confidence score
- **Medium Confidence Targets**: 60-80% confidence score
- **Low Confidence Targets**: <60% confidence score

### RECOMMENDED FOLLOW-UP
1. Ground-truthing of top 10 targets per depth zone
2. Detailed geochemical sampling
3. Geophysical surveys (gravity, magnetics, IP)
4. Progressive drilling program based on results
"""
        
        return report
    
    def run_emit_depth_analysis(self, location_name):
        """
        Run complete EMIT-based mineral depth prediction analysis
        """
        print(f"🛰️ Starting EMIT L2B Mineral Depth Analysis for: {location_name}")
        
        try:
            # Get coordinates
            print("📍 Getting location coordinates...")
            lat, lon = self.get_location_coordinates(location_name)
            print(f"   Coordinates: {lat:.4f}, {lon:.4f}")
            
            # Create study area
            print("🗺️ Creating study area...")
            point = ee.Geometry.Point([lon, lat])
            study_area = point.buffer(25000)  # 25km radius
            
            # Simulate EMIT L2B data
            print("🔬 Simulating EMIT L2B mineralogy data...")
            emit_df = self.simulate_emit_l2b_data(study_area, n_points=500)[3]
            
            # Calculate depth predictions
            print("⛏️ Calculating mineral depth predictions...")
            depth_predictions = self.calculate_depth_predictions(emit_df)
            
            # Create 3D depth model
            print("📊 Creating 3D depth visualization...")
            fig_3d, df_3d = self.create_3d_depth_model(emit_df, depth_predictions, location_name)
            
            # Create cross-sections
            print("📏 Creating depth cross-sections...")
            fig_cross = self.create_depth_cross_sections(emit_df, depth_predictions, location_name)
            
            # Create targeting map
            print("🎯 Creating mineral targeting map...")
            targeting_map, targeting_df = self.create_mineral_targeting_map(emit_df, depth_predictions, location_name)
            
            # Generate report
            print("📋 Generating exploration report...")
            report = self.generate_depth_exploration_report(emit_df, depth_predictions, targeting_df, location_name)
            
            print("✅ EMIT L2B Analysis Complete!")
            
            return {
                '3d_depth_model': fig_3d,
                'cross_sections': fig_cross,
                'targeting_map': targeting_map,
                'report': report,
                'emit_data': emit_df,
                'depth_predictions': depth_predictions,
                'targeting_data': targeting_df,
                'coordinates': (lat, lon)
            }
            
        except Exception as e:
            print(f"❌ Error during EMIT analysis: {e}")
            return None

# Main execution function
def main():
    """
    Main function to run EMIT-based mineral depth prediction
    """
    # API Keys
    GMAPS_KEY = "AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4"
    GROQ_KEY = "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"
    GEMINI_KEY = "AIzaSyA7fQKCBtHPQUHGX1nZXDOWiJMlO31-uk8"
    
    # Initialize the predictor
    predictor = EMITMineralDepthPredictor(GMAPS_KEY, GROQ_KEY, GEMINI_KEY)
    
    # Get user input
    location = input("🌍 Enter location for EMIT mineral depth analysis: ")
    
    if not location:
        location = "Pilbara, Western Australia"  # Default mineral-rich location
        print(f"Using default location: {location}")
    
    # Run analysis
    results = predictor.run_emit_depth_analysis(location)
    
    if results:
        print("\n" + "="*70)
        print("🛰️ EMIT L2B MINERAL DEPTH PREDICTION RESULTS")
        print("="*70)
        
        # Display 3D depth model
        print("📊 Displaying 3D Mineral Depth Model...")
        results['3d_depth_model'].show()
        
        # Display cross-sections
        print("📏 Displaying Depth Cross-Sections...")
        results['cross_sections'].show()
        
        # Save targeting map
        if results['targeting_map']:
            results['targeting_map'].to_html(f'emit_targeting_map_{location.replace(" ", "_")}.html')
            print(f"🗺️ Targeting map saved as 'emit_targeting_map_{location.replace(' ', '_')}.html'")
        
        # Print report
        print("\n📋 EXPLORATION REPORT:")
        print(results['report'])
        
        # Save data
        results['emit_data'].to_csv(f'emit_mineral_data_{location.replace(" ", "_")}.csv', index=False)
        results['targeting_data'].to_csv(f'targeting_data_{location.replace(" ", "_")}.csv', index=False)
        print(f"\n💾 Data saved as CSV files")
        
        # Export high-priority targets for field work
        export_drilling_targets(results['targeting_data'], location)
        
    else:
        print("❌ Analysis failed. Please check your inputs and try again.")
    
    return results

def export_drilling_targets(targeting_df, location_name):
    """
    Export drilling targets for different depth zones
    """
    # Define targets for each depth zone
    depth_zones = {
        'surface': {'column': 'surface_score', 'depth': '0-50m', 'method': 'RC Drilling'},
        'shallow': {'column': 'shallow_score', 'depth': '50-200m', 'method': 'Diamond Drilling'},
        'deep': {'column': 'deep_score', 'depth': '>200m', 'method': 'Deep Diamond Drilling'}
    }
    
    drilling_targets = []
    
    for zone_name, zone_info in depth_zones.items():
        # Get top 10 targets for each zone
        top_targets = targeting_df.nlargest(10, zone_info['column'])
        
        for idx, target in top_targets.iterrows():
            drilling_targets.append({
                'target_id': f"{zone_name.upper()}_{idx:03d}",
                'longitude': target['longitude'],
                'latitude': target['latitude'],
                'depth_zone': zone_info['depth'],
                'drilling_method': zone_info['method'],
                'priority_score': target[zone_info['column']],
                'total_score': target['total_score']
            })
    
    # Save drilling targets
    drilling_df = pd.DataFrame(drilling_targets)
    drilling_df.to_csv(f'drilling_targets_{location_name.replace(" ", "_")}.csv', index=False)
    
    # Create KML for GPS
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>EMIT Mineral Drilling Targets - {location_name}</name>
    <description>Depth-based mineral exploration targets from EMIT L2B analysis</description>
"""
    
    for _, target in drilling_df.iterrows():
        color = "ff0000ff" if "SURFACE" in target['target_id'] else "ff00ff00" if "SHALLOW" in target['target_id'] else "ffff0000"
        
        kml_content += f"""
    <Placemark>
      <name>{target['target_id']}</name>
      <description>
        Depth Zone: {target['depth_zone']}
        Method: {target['drilling_method']}
        Priority Score: {target['priority_score']:.2f}
        Total Score: {target['total_score']:.2f}
      </description>
      <Style>
        <IconStyle>
          <color>{color}</color>
          <scale>1.2</scale>
        </IconStyle>
      </Style>
      <Point>
        <coordinates>{target['longitude']},{target['latitude']},0</coordinates>
      </Point>
    </Placemark>"""
    
    kml_content += """
  </Document>
</kml>"""
    
    with open(f'emit_drilling_targets_{location_name.replace(" ", "_")}.kml', 'w') as f:
        f.write(kml_content)
    
    print(f"🎯 Drilling targets exported:")
    print(f"   - CSV: drilling_targets_{location_name.replace(' ', '_')}.csv")
    print(f"   - KML: emit_drilling_targets_{location_name.replace(' ', '_')}.kml")

# Run the analysis
if __name__ == "__main__":
    results = main()
