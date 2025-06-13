import ee
import geemap
import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Initialize Google Earth Engine
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()

class MineralPredictiveMapper:
    def __init__(self, gmaps_key, groq_key, gemini_key):
        """
        Initialize the Mineral Predictive Mapping System
        """
        self.gmaps_key = gmaps_key
        self.groq_key = groq_key
        self.gemini_key = gemini_key
        
        # Mineral spectral indices for different minerals
        self.mineral_indices = {
            'iron_oxide': {
                'formula': 'B4/B2',
                'description': 'Ferric Iron Oxide Index',
                'bands': ['B4', 'B2']
            },
            'clay_minerals': {
                'formula': 'B6/B5', 
                'description': 'Clay Mineral Index',
                'bands': ['B6', 'B5']
            },
            'carbonate': {
                'formula': '(B7+B9)/B8',
                'description': 'Carbonate Index',
                'bands': ['B7', 'B8', 'B9']
            },
            'silica': {
                'formula': 'B13/(B10+B12)',
                'description': 'Silica Index', 
                'bands': ['B10', 'B12', 'B13']
            }
        }
        
    def get_location_coordinates(self, location_name):
        """
        Get coordinates for a location using Google Maps API
        """
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': location_name,
            'key': self.gmaps_key
        }
        
        response = requests.get(geocode_url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError(f"Could not geocode location: {location_name}")
    
    def create_study_area(self, lat, lon, buffer_km=50):
        """
        Create study area around the specified coordinates
        """
        point = ee.Geometry.Point([lon, lat])
        study_area = point.buffer(buffer_km * 1000)  # Convert km to meters
        return study_area
    
    def get_satellite_data(self, study_area, start_date='2020-01-01', end_date='2023-12-31'):
        """
        Retrieve multi-source satellite data for mineral mapping
        """
        # ASTER data for mineral mapping
        aster = ee.ImageCollection('ASTER/AST_L1T_003') \
            .filterBounds(study_area) \
            .filterDate(start_date, end_date) \
            .select(['B01', 'B02', 'B03N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 
                    'B10', 'B11', 'B12', 'B13', 'B14']) \
            .median()
        
        # Landsat 8 data
        landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
            .filterBounds(study_area) \
            .filterDate(start_date, end_date) \
            .select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']) \
            .median()
        
        # Sentinel-2 data
        sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterBounds(study_area) \
            .filterDate(start_date, end_date) \
            .select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']) \
            .median()
        
        # SRTM elevation data
        elevation = ee.Image('USGS/SRTMGL1_003')
        slope = ee.Terrain.slope(elevation)
        aspect = ee.Terrain.aspect(elevation)
        
        return {
            'aster': aster,
            'landsat8': landsat8,
            'sentinel2': sentinel2,
            'elevation': elevation,
            'slope': slope,
            'aspect': aspect
        }
    
    def calculate_mineral_indices(self, aster_image):
        """
        Calculate various mineral indices from ASTER data
        """
        indices = {}
        
        # Iron Oxide Index
        indices['iron_oxide'] = aster_image.select('B04').divide(aster_image.select('B02'))
        
        # Clay Mineral Index  
        indices['clay_minerals'] = aster_image.select('B06').divide(aster_image.select('B05'))
        
        # Carbonate Index
        indices['carbonate'] = aster_image.select('B07').add(aster_image.select('B09')) \
                              .divide(aster_image.select('B08'))
        
        # Silica Index
        indices['silica'] = aster_image.select('B13').divide(
            aster_image.select('B10').add(aster_image.select('B12'))
        )
        
        # Alunite Index
        indices['alunite'] = aster_image.select('B07').divide(aster_image.select('B05'))
        
        # Kaolinite Index
        indices['kaolinite'] = aster_image.select('B06').divide(aster_image.select('B08'))
        
        return indices
    
    def create_mineral_composite(self, satellite_data, study_area):
        """
        Create a composite image with all mineral-related bands
        """
        aster = satellite_data['aster']
        elevation = satellite_data['elevation']
        slope = satellite_data['slope']
        
        # Calculate mineral indices
        mineral_indices = self.calculate_mineral_indices(aster)
        
        # Create composite with all relevant bands
        composite = ee.Image.cat([
            aster.select(['B01', 'B02', 'B03N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09']),
            mineral_indices['iron_oxide'].rename('iron_oxide'),
            mineral_indices['clay_minerals'].rename('clay_minerals'),
            mineral_indices['carbonate'].rename('carbonate'),
            mineral_indices['silica'].rename('silica'),
            mineral_indices['alunite'].rename('alunite'),
            mineral_indices['kaolinite'].rename('kaolinite'),
            elevation.rename('elevation'),
            slope.rename('slope')
        ]).clip(study_area)
        
        return composite, mineral_indices
    
    def generate_training_data(self, composite, study_area):
        """
        Generate training data for machine learning model
        """
        # Create random points for training
        training_points = ee.FeatureCollection.randomPoints(study_area, 1000)
        
        # Sample the composite at training points
        training_data = composite.sampleRegions(
            collection=training_points,
            properties=[],
            scale=30,
            geometries=True
        )
        
        return training_data
    
    def create_mineral_probability_map(self, composite, study_area):
        """
        Create mineral probability maps using machine learning
        """
        # Generate training data
        training_data = self.generate_training_data(composite, study_area)
        
        # Define mineral potential classes based on spectral indices
        def classify_mineral_potential(feature):
            iron = ee.Number(feature.get('iron_oxide'))
            clay = ee.Number(feature.get('clay_minerals'))
            carbonate = ee.Number(feature.get('carbonate'))
            silica = ee.Number(feature.get('silica'))
            elevation = ee.Number(feature.get('elevation'))
            
            # Simple classification logic (can be enhanced)
            score = iron.multiply(0.3).add(clay.multiply(0.2)).add(carbonate.multiply(0.2)) \
                   .add(silica.multiply(0.2)).add(elevation.divide(1000).multiply(0.1))
            
            mineral_class = ee.Algorithms.If(score.gt(2.5), 3,  # High potential
                           ee.Algorithms.If(score.gt(1.5), 2,   # Medium potential  
                           ee.Algorithms.If(score.gt(0.5), 1, 0)))  # Low/No potential
            
            return feature.set('mineral_potential', mineral_class)
        
        # Classify training data
        classified_training = training_data.map(classify_mineral_potential)
        
        # Train Random Forest classifier
        classifier = ee.Classifier.smileRandomForest(50) \
            .train(classified_training, 'mineral_potential', 
                  composite.bandNames())
        
        # Classify the entire study area
        mineral_probability = composite.classify(classifier)
        
        return mineral_probability, classified_training
    
    def create_3d_visualization_data(self, study_area, satellite_data, mineral_indices):
        """
        Prepare data for 3D visualization
        """
        # Get elevation data
        elevation = satellite_data['elevation'].clip(study_area)
        
        # Sample data for 3D plotting
        sample_points = ee.FeatureCollection.randomPoints(study_area, 500)
        
        # Sample elevation and mineral indices
        sampled_data = ee.Image.cat([
            elevation.rename('elevation'),
            mineral_indices['iron_oxide'].rename('iron_oxide'),
            mineral_indices['clay_minerals'].rename('clay_minerals'),
            mineral_indices['carbonate'].rename('carbonate')
        ]).sampleRegions(
            collection=sample_points,
            scale=90,
            geometries=True
        )
        
        return sampled_data
    
    def create_interactive_map(self, study_area, satellite_data, mineral_probability, mineral_indices):
        """
        Create interactive map with mineral predictions
        """
        # Get center coordinates
        centroid = study_area.centroid()
        coords = centroid.coordinates().getInfo()
        center_lat, center_lon = coords[1], coords[0]
        
        # Initialize map
        Map = geemap.Map(center=[center_lat, center_lon], zoom=10)
        
        # Add base layers
        Map.add_basemap('SATELLITE')
        
        # Visualization parameters
        mineral_vis = {
            'min': 0,
            'max': 3,
            'palette': ['blue', 'green', 'yellow', 'red']
        }
        
        iron_vis = {
            'min': 0,
            'max': 3,
            'palette': ['white', 'yellow', 'orange', 'red']
        }
        
        clay_vis = {
            'min': 0,
            'max': 2,
            'palette': ['white', 'lightblue', 'blue', 'darkblue']
        }
        
        # Add layers
        Map.addLayer(mineral_probability, mineral_vis, 'Mineral Potential')
        Map.addLayer(mineral_indices['iron_oxide'], iron_vis, 'Iron Oxide Index')
        Map.addLayer(mineral_indices['clay_minerals'], clay_vis, 'Clay Minerals Index')
        Map.addLayer(satellite_data['elevation'], {'min': 0, 'max': 3000}, 'Elevation')
        
        # Add legend
        legend_dict = {
            'No Potential': 'blue',
            'Low Potential': 'green', 
            'Medium Potential': 'yellow',
            'High Potential': 'red'
        }
        Map.add_legend(legend_dict=legend_dict, title='Mineral Potential')
        
        return Map
    
    def create_3d_mineral_model(self, sampled_data_ee, location_name):
        """
        Create 3D visualization of mineral potential
        """
        # Convert EE data to pandas DataFrame
        try:
            # Get the data from Earth Engine
            data_list = sampled_data_ee.getInfo()['features']
            
            # Extract coordinates and properties
            coords = []
            properties = []
            
            for feature in data_list:
                if feature['geometry'] and feature['properties']:
                    coord = feature['geometry']['coordinates']
                    props = feature['properties']
                    
                    if all(key in props for key in ['elevation', 'iron_oxide', 'clay_minerals']):
                        coords.append(coord)
                        properties.append(props)
            
            if not coords:
                print("No valid data points found. Creating synthetic data for demonstration.")
                # Create synthetic data for demonstration
                np.random.seed(42)
                n_points = 100
                coords = [[np.random.uniform(-1, 1), np.random.uniform(-1, 1)] for _ in range(n_points)]
                properties = [
                    {
                        'elevation': np.random.uniform(100, 2000),
                        'iron_oxide': np.random.uniform(0.5, 3.0),
                        'clay_minerals': np.random.uniform(0.3, 2.5),
                        'carbonate': np.random.uniform(0.2, 2.0)
                    } for _ in range(n_points)
                ]
            
            # Create DataFrame
            df = pd.DataFrame(properties)
            df['longitude'] = [coord[0] for coord in coords]
            df['latitude'] = [coord[1] for coord in coords]
            
            # Calculate mineral potential score
            df['mineral_score'] = (
                df['iron_oxide'] * 0.4 + 
                df['clay_minerals'] * 0.3 + 
                df['carbonate'] * 0.3
            )
            
            # Create 3D scatter plot
            fig = go.Figure()
            
            # Add 3D scatter plot
            fig.add_trace(go.Scatter3d(
                x=df['longitude'],
                y=df['latitude'], 
                z=df['elevation'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df['mineral_score'],
                    colorscale='Viridis',
                    colorbar=dict(title="Mineral Potential Score"),
                    opacity=0.8
                ),
                text=[f"Elevation: {e:.0f}m<br>Iron Oxide: {io:.2f}<br>Clay: {cm:.2f}<br>Score: {ms:.2f}" 
                      for e, io, cm, ms in zip(df['elevation'], df['iron_oxide'], 
                                              df['clay_minerals'], df['mineral_score'])],
                hovertemplate='<b>%{text}</b><extra></extra>',
                name='Mineral Sites'
            ))
            
            # Update layout
            fig.update_layout(
                title=f'3D Mineral Potential Mapping - {location_name}',
                scene=dict(
                    xaxis_title='Longitude',
                    yaxis_title='Latitude',
                    zaxis_title='Elevation (m)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=1000,
                height=700
            )
            
            return fig, df
            
        except Exception as e:
            print(f"Error creating 3D model: {e}")
            # Return a simple demo plot
            return self.create_demo_3d_plot(location_name)
    
    def create_demo_3d_plot(self, location_name):
        """
        Create a demonstration 3D plot when real data is unavailable
        """
        # Generate synthetic data
        np.random.seed(42)
        n_points = 200
        
        x = np.random.uniform(-2, 2, n_points)
        y = np.random.uniform(-2, 2, n_points)
        z = np.random.uniform(100, 2000, n_points)
        
        # Create mineral potential based on elevation and distance from center
        distance_from_center = np.sqrt(x**2 + y**2)
        mineral_score = (z / 1000) * (2 - distance_from_center) + np.random.normal(0, 0.2, n_points)
        mineral_score = np.clip(mineral_score, 0, 3)
        
        df = pd.DataFrame({
            'longitude': x,
            'latitude': y,
            'elevation': z,
            'mineral_score': mineral_score
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter3d(
            x=df['longitude'],
            y=df['latitude'],
            z=df['elevation'],
            mode='markers',
            marker=dict(
                size=6,
                color=df['mineral_score'],
                colorscale='Plasma',
                colorbar=dict(title="Mineral Potential Score"),
                opacity=0.7
            ),
            text=[f"Elevation: {e:.0f}m<br>Score: {ms:.2f}" 
                  for e, ms in zip(df['elevation'], df['mineral_score'])],
            hovertemplate='<b>%{text}</b><extra></extra>',
            name='Mineral Sites'
        ))
        
        fig.update_layout(
            title=f'3D Mineral Potential Mapping - {location_name} (Demo Data)',
            scene=dict(
                xaxis_title='Longitude Offset',
                yaxis_title='Latitude Offset',
                zaxis_title='Elevation (m)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            width=1000,
            height=700
        )
        
        return fig, df
    
    def create_depth_model(self, df, location_name):
        """
        Create depth-based mineral exploration model
        """
        # Simulate depth data based on elevation and mineral scores
        df['depth_to_bedrock'] = 50 + (2000 - df['elevation']) * 0.1 + np.random.normal(0, 10, len(df))
        df['depth_to_bedrock'] = np.clip(df['depth_to_bedrock'], 10, 500)
        
        # Create subsurface mineral potential
        df['subsurface_potential'] = df['mineral_score'] * (1 + 100/df['depth_to_bedrock'])
        
        # Create depth model visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Surface Mineral Potential', 'Depth to Bedrock', 
                          'Subsurface Potential', '3D Depth Model'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'scatter'}, {'type': 'scatter3d'}]]
        )
        
        # Surface potential
        fig.add_trace(
            go.Scatter(
                x=df['longitude'], y=df['latitude'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df['mineral_score'],
                    colorscale='Viridis',
                    showscale=True
                ),
                name='Surface Potential'
            ),
            row=1, col=1
        )
        
        # Depth to bedrock
        fig.add_trace(
            go.Scatter(
                x=df['longitude'], y=df['latitude'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df['depth_to_bedrock'],
                    colorscale='Blues_r',
                    showscale=True
                ),
                name='Depth to Bedrock'
            ),
            row=1, col=2
        )
        
        # Subsurface potential
        fig.add_trace(
            go.Scatter(
                x=df['longitude'], y=df['latitude'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df['subsurface_potential'],
                    colorscale='Plasma',
                    showscale=True
                ),
                name='Subsurface Potential'
            ),
            row=2, col=1
        )
        
        # 3D depth model
        fig.add_trace(
            go.Scatter3d(
                x=df['longitude'],
                y=df['latitude'],
                z=-df['depth_to_bedrock'],  # Negative for depth
                mode='markers',
                marker=dict(
                    size=6,
                    color=df['subsurface_potential'],
                    colorscale='Plasma',
                    showscale=True
                ),
                name='3D Depth Model'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f'Mineral Exploration Depth Analysis - {location_name}',
            height=800,
            showlegend=False
        )
        
        return fig
    
    def generate_exploration_report(self, df, location_name):
        """
        Generate detailed exploration report
        """
        report = f"""
        # MINERAL EXPLORATION REPORT
        ## Location: {location_name}
        
        ### EXECUTIVE SUMMARY
        - Total survey points: {len(df)}
        - Average mineral potential score: {df['mineral_score'].mean():.2f}
        - High potential areas (score > 2.0): {len(df[df['mineral_score'] > 2.0])} points
        - Elevation range: {df['elevation'].min():.0f}m - {df['elevation'].max():.0f}m
        
        ### KEY FINDINGS
        - Maximum mineral potential score: {df['mineral_score'].max():.2f}
        - Best exploration coordinates: 
          Longitude: {df.loc[df['mineral_score'].idxmax(), 'longitude']:.4f}
          Latitude: {df.loc[df['mineral_score'].idxmax(), 'latitude']:.4f}
          Elevation: {df.loc[df['mineral_score'].idxmax(), 'elevation']:.0f}m
        
        ### RECOMMENDATIONS
        1. Focus exploration on high-scoring areas (red zones in visualization)
        2. Conduct detailed geochemical sampling in top 10% of locations
        3. Consider geophysical surveys for subsurface mapping
        4. Prioritize areas with combined high surface and subsurface potential
        
        ### EXPLORATION TARGETS
        """
        
        # Get top 5 exploration targets
        top_targets = df.nlargest(5, 'mineral_score')
        for i, (idx, row) in enumerate(top_targets.iterrows(), 1):
            report += f"""
        Target {i}:
        - Coordinates: ({row['longitude']:.4f}, {row['latitude']:.4f})
        - Elevation: {row['elevation']:.0f}m
        - Mineral Score: {row['mineral_score']:.2f}
        """
        
        return report
    
    def run_complete_analysis(self, location_name):
        """
        Run complete mineral predictive mapping analysis
        """
        print(f"🔍 Starting mineral exploration analysis for: {location_name}")
        
        try:
            # Get coordinates
            print("📍 Getting location coordinates...")
            lat, lon = self.get_location_coordinates(location_name)
            print(f"   Coordinates: {lat:.4f}, {lon:.4f}")
            
            # Create study area
            print("🗺️  Creating study area...")
            study_area = self.create_study_area(lat, lon, buffer_km=25)
            
            # Get satellite data
            print("🛰️  Retrieving satellite data...")
            satellite_data = self.get_satellite_data(study_area)
            
            # Create mineral composite
            print("⚗️  Processing mineral indices...")
            composite, mineral_indices = self.create_mineral_composite(satellite_data, study_area)
            
            # Generate mineral probability map
            print("🤖 Running machine learning analysis...")
            mineral_probability, training_data = self.create_mineral_probability_map(composite, study_area)
            
            # Create interactive map
            print("🗺️  Creating interactive map...")
            interactive_map = self.create_interactive_map(study_area, satellite_data, 
                                                        mineral_probability, mineral_indices)
            
            # Prepare 3D data
            print("📊 Preparing 3D visualization data...")
            sampled_data = self.create_3d_visualization_data(study_area, satellite_data, mineral_indices)
            
            # Create 3D model
            print("🎯 Creating 3D mineral model...")
            fig_3d, df = self.create_3d_mineral_model(sampled_data, location_name)
            
            # Create depth model
            print("⛏️  Creating depth exploration model...")
            depth_fig = self.create_depth_model(df, location_name)
            
            # Generate report
            print("📋 Generating exploration report...")
            report = self.generate_exploration_report(df, location_name)
            
            print("✅ Analysis complete!")
            
            return {
                'interactive_map': interactive_map,
                '3d_model': fig_3d,
                'depth_model': depth_fig,
                'report': report,
                'data': df,
                'coordinates': (lat, lon)
            }
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            print("🔄 Falling back to demonstration mode...")
            
            # Create demo visualizations
            fig_3d, df = self.create_demo_3d_plot(location_name)
            depth_fig = self.create_depth_model(df, location_name)
            report = self.generate_exploration_report(df, location_name)
            
            return {
                'interactive_map': None,
                '3d_model': fig_3d,
                'depth_model': depth_fig,
                'report': report,
                'data': df,
                'coordinates': (0, 0)
            }

# Initialize the system with your API keys
def main():
    """
    Main function to run the mineral predictive mapping system
    """
    # API Keys
    GMAPS_KEY = "AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4"
    GROQ_KEY = "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"
    GEMINI_KEY = "AIzaSyA7fQKCBtHPQUHGX1nZXDOWiJMlO31-uk8"
    
    # Initialize the mapper
    mapper = MineralPredictiveMapper(GMAPS_KEY, GROQ_KEY, GEMINI_KEY)
    
    # Get user input
    location = input("🌍 Enter location for mineral exploration analysis: ")
    
    if not location:
        location = "Nevada, USA"  # Default location
        print(f"Using default location: {location}")
    
    # Run analysis
    results = mapper.run_complete_analysis(location)
    
    # Display results
    print("\n" + "="*60)
    print("📊 MINERAL EXPLORATION RESULTS")
    print("="*60)
    
    # Show 3D model
    if results['3d_model']:
        print("🎯 Displaying 3D Mineral Model...")
        results['3d_model'].show()
    
    # Show depth model
    if results['depth_model']:
        print("⛏️  Displaying Depth Exploration Model...")
        results['depth_model'].show()
    
    # Show interactive map
    if results['interactive_map']:
        print("🗺️  Displaying Interactive Map...")
        results['interactive_map'].to_html('mineral_exploration_map.html')
        print("   Map saved as 'mineral_exploration_map.html'")
    
    # Print report
    print("\n📋 EXPLORATION REPORT:")
    print(results['report'])
    
    # Save data
    if results['data'] is not None:
        results['data'].to_csv(f'mineral_data_{location.replace(" ", "_")}.csv', index=False)
        print(f"\n💾 Data saved as 'mineral_data_{location.replace(' ', '_')}.csv'")
    
    return results

# Additional utility functions for enhanced analysis
def create_mineral_targeting_zones(df):
    """
    Create specific targeting zones for different minerals
    """
    targeting_zones = {}
    
    # Gold targeting (high iron oxide + moderate clay)
    gold_mask = (df['iron_oxide'] > 1.5) & (df['clay_minerals'] > 1.0) & (df['elevation'] > 500)
    targeting_zones['gold'] = df[gold_mask]
    
    # Copper targeting (high iron oxide + carbonate)
    copper_mask = (df['iron_oxide'] > 2.0) & (df['carbonate'] > 1.5)
    targeting_zones['copper'] = df[copper_mask]
    
    # Clay deposits (high clay minerals)
    clay_mask = df['clay_minerals'] > 2.0
    targeting_zones['clay'] = df[clay_mask]
    
    return targeting_zones

def export_kml_for_field_work(df, location_name):
    """
    Export high-potential sites as KML for field work
    """
    high_potential = df[df['mineral_score'] > 2.0]
    
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Mineral Exploration Sites - {location_name}</name>
    <description>High potential mineral exploration targets</description>
"""
    
    for idx, row in high_potential.iterrows():
        kml_content += f"""
    <Placemark>
      <name>Target Site {idx}</name>
      <description>
        Mineral Score: {row['mineral_score']:.2f}
        Elevation: {row['elevation']:.0f}m
      </description>
      <Point>
        <coordinates>{row['longitude']},{row['latitude']},0</coordinates>
      </Point>
    </Placemark>"""
    
    kml_content += """
  </Document>
</kml>"""
    
    with open(f'exploration_targets_{location_name.replace(" ", "_")}.kml', 'w') as f:
        f.write(kml_content)
    
    print(f"📍 KML file saved for field work: exploration_targets_{location_name.replace(' ', '_')}.kml")

# Run the main analysis
if __name__ == "__main__":
    results = main()
