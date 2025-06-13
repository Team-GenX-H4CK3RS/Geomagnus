import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import requests
import json
import folium
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from sarvamai import SarvamAI
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyA7fQKCBtHPQUHGX1nZXDOWiJMlO31-uk8"
GOOGLE_MAPS_API_KEY = "AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4"
SARVAM_API_KEY = "56a811e6-81a8-4c71-b0c9-6ea7855c8490"

# Initialize APIs
groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')
sarvam_client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

class MineralPredictionSystem:
    def __init__(self):
        """Initialize the Mineral Prediction System with KNN"""
        self.scaler = StandardScaler()
        self.knn_model = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
        self.mineral_data = self.load_mineral_database()
        self.setup_model()
        
    def load_mineral_database(self):
        """Load comprehensive mineral database for Karnataka & Andhra Pradesh"""
        mineral_data = {
            # Karnataka Minerals
            'Kolar_Gold_KA': {
                'coords': [13.1362, 78.1348], 'mineral': 'Gold', 'grade': 8.5, 
                'production': 1583, 'depth': 3200, 'reserves': 45.2,
                'geological_score': 9.2, 'accessibility': 8.5, 'infrastructure': 9.0
            },
            'Bellary_Iron_KA': {
                'coords': [15.1394, 76.9214], 'mineral': 'Iron Ore', 'grade': 58.0,
                'production': 18700000, 'depth': 150, 'reserves': 2800.5,
                'geological_score': 9.8, 'accessibility': 9.2, 'infrastructure': 9.5
            },
            'Raichur_Gold_KA': {
                'coords': [16.2072, 77.3421], 'mineral': 'Gold', 'grade': 6.2,
                'production': 800, 'depth': 280, 'reserves': 12.8,
                'geological_score': 8.5, 'accessibility': 8.0, 'infrastructure': 7.5
            },
            'Chitradurga_Manganese_KA': {
                'coords': [14.2251, 76.3958], 'mineral': 'Manganese', 'grade': 42.0,
                'production': 850000, 'depth': 120, 'reserves': 156.2,
                'geological_score': 8.8, 'accessibility': 8.2, 'infrastructure': 8.0
            },
            'Hassan_Copper_KA': {
                'coords': [13.0067, 76.0962], 'mineral': 'Copper', 'grade': 1.2,
                'production': 500000, 'depth': 200, 'reserves': 85.6,
                'geological_score': 7.8, 'accessibility': 7.5, 'infrastructure': 7.8
            },
            'Gulbarga_Limestone_KA': {
                'coords': [17.3297, 76.8343], 'mineral': 'Limestone', 'grade': 95.0,
                'production': 14000000, 'depth': 80, 'reserves': 51000.0,
                'geological_score': 9.5, 'accessibility': 9.0, 'infrastructure': 8.8
            },
            'Mysore_Granite_KA': {
                'coords': [12.2958, 76.6394], 'mineral': 'Granite', 'grade': 98.5,
                'production': 2500000, 'depth': 50, 'reserves': 1200.0,
                'geological_score': 8.2, 'accessibility': 8.8, 'infrastructure': 9.2
            },
            'Chikmagaluru_Chromite_KA': {
                'coords': [13.3161, 75.7720], 'mineral': 'Chromite', 'grade': 45.8,
                'production': 125000, 'depth': 180, 'reserves': 28.5,
                'geological_score': 7.5, 'accessibility': 7.2, 'infrastructure': 7.0
            },
            
            # Andhra Pradesh Minerals
            'Tummalapalle_Uranium_AP': {
                'coords': [14.2074, 78.9742], 'mineral': 'Uranium', 'grade': 0.15,
                'production': 1500, 'depth': 300, 'reserves': 49000.0,
                'geological_score': 9.8, 'accessibility': 8.5, 'infrastructure': 8.8
            },
            'Cuddapah_Iron_AP': {
                'coords': [14.4426, 78.8242], 'mineral': 'Iron Ore', 'grade': 60.0,
                'production': 12300000, 'depth': 200, 'reserves': 1850.0,
                'geological_score': 9.2, 'accessibility': 8.8, 'infrastructure': 8.5
            },
            'Srikakulam_Ilmenite_AP': {
                'coords': [18.2949, 83.8938], 'mineral': 'Titanium', 'grade': 65.0,
                'production': 15200000, 'depth': 25, 'reserves': 320.5,
                'geological_score': 9.0, 'accessibility': 8.2, 'infrastructure': 8.0
            },
            'Visakhapatnam_Bauxite_AP': {
                'coords': [17.6868, 83.2185], 'mineral': 'Bauxite', 'grade': 48.0,
                'production': 12800000, 'depth': 100, 'reserves': 285.6,
                'geological_score': 8.5, 'accessibility': 9.0, 'infrastructure': 9.2
            },
            'Anantapur_Gold_AP': {
                'coords': [14.6819, 77.6006], 'mineral': 'Gold', 'grade': 7.8,
                'production': 1200, 'depth': 250, 'reserves': 18.5,
                'geological_score': 8.2, 'accessibility': 7.8, 'infrastructure': 7.5
            },
            'Kadapa_Limestone_AP': {
                'coords': [14.4674, 78.8240], 'mineral': 'Limestone', 'grade': 92.0,
                'production': 8500000, 'depth': 120, 'reserves': 2800.0,
                'geological_score': 8.8, 'accessibility': 8.5, 'infrastructure': 8.2
            },
            'Nellore_REE_AP': {
                'coords': [14.4426, 79.9865], 'mineral': 'Rare Earth', 'grade': 12.5,
                'production': 45000, 'depth': 15, 'reserves': 136.0,
                'geological_score': 8.0, 'accessibility': 8.0, 'infrastructure': 7.8
            },
            'Guntur_Copper_AP': {
                'coords': [16.3067, 80.4365], 'mineral': 'Copper', 'grade': 1.5,
                'production': 700000, 'depth': 180, 'reserves': 95.2,
                'geological_score': 7.8, 'accessibility': 8.2, 'infrastructure': 8.0
            }
        }
        return mineral_data
    
    def setup_model(self):
        """Setup KNN model with mineral features"""
        # Prepare feature matrix
        features = []
        self.locations = []
        self.mineral_names = []
        
        for name, data in self.mineral_data.items():
            feature_vector = [
                data['coords'][0],  # Latitude
                data['coords'][1],  # Longitude
                data['grade'],      # Grade
                data['depth'],      # Depth
                data['geological_score'],  # Geological favorability
                data['accessibility'],     # Accessibility score
                data['infrastructure']     # Infrastructure score
            ]
            features.append(feature_vector)
            self.locations.append(data['coords'])
            self.mineral_names.append(name)
        
        # Scale features and fit KNN model
        self.features_scaled = self.scaler.fit_transform(features)
        self.knn_model.fit(self.features_scaled)
        
        # Store original features for analysis
        self.features_df = pd.DataFrame(features, columns=[
            'latitude', 'longitude', 'grade', 'depth', 
            'geological_score', 'accessibility', 'infrastructure'
        ])
        self.features_df['location'] = self.mineral_names
        
    def predict_nearby_sites(self, lat, lon, n_neighbors=5):
        """Predict nearby high-potential mineral sites using KNN"""
        try:
            # Create query point with estimated features
            query_features = self.estimate_location_features(lat, lon)
            query_scaled = self.scaler.transform([query_features])
            
            # Find nearest neighbors
            distances, indices = self.knn_model.kneighbors(query_scaled, n_neighbors=n_neighbors)
            
            # Prepare results
            predictions = []
            for i, idx in enumerate(indices[0]):
                location_name = self.mineral_names[idx]
                location_data = self.mineral_data[location_name]
                
                prediction = {
                    'rank': i + 1,
                    'location': location_name,
                    'mineral': location_data['mineral'],
                    'coordinates': location_data['coords'],
                    'distance_km': self.calculate_distance(lat, lon, location_data['coords']),
                    'similarity_score': 1 / (1 + distances[0][i]),  # Convert distance to similarity
                    'grade': location_data['grade'],
                    'production': location_data['production'],
                    'reserves': location_data['reserves'],
                    'geological_score': location_data['geological_score'],
                    'prediction_confidence': self.calculate_confidence(query_features, idx)
                }
                predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return []
    
    def estimate_location_features(self, lat, lon):
        """Estimate geological features for a given location using AI"""
        try:
            # Use Gemini to estimate geological characteristics
            prompt = f"""
            Analyze the geological potential at coordinates {lat}°N, {lon}°E in Karnataka/Andhra Pradesh region.
            Provide estimates (0-10 scale) for:
            1. Geological favorability score
            2. Accessibility score  
            3. Infrastructure score
            4. Estimated mineral grade (%)
            5. Estimated depth to mineralization (meters)
            
            Format: geological_score,accessibility,infrastructure,grade,depth
            """
            
            response = gemini_model.generate_content(prompt)
            
            # Parse response and create feature vector
            try:
                scores = [float(x.strip()) for x in response.text.split(',')]
                return [lat, lon, scores[3], scores[4], scores[0], scores[1], scores[2]]
            except:
                # Fallback to average values
                return [lat, lon, 5.0, 150.0, 7.5, 7.5, 7.5]
                
        except Exception as e:
            print(f"Error estimating features: {e}")
            # Return default values
            return [lat, lon, 5.0, 150.0, 7.5, 7.5, 7.5]
    
    def calculate_distance(self, lat1, lon1, coords2):
        """Calculate distance between two points in kilometers"""
        lat2, lon2 = coords2
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = (np.sin(dlat/2)**2 + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c
    
    def calculate_confidence(self, query_features, neighbor_idx):
        """Calculate prediction confidence based on feature similarity"""
        neighbor_features = self.features_df.iloc[neighbor_idx][
            ['latitude', 'longitude', 'grade', 'depth', 'geological_score', 'accessibility', 'infrastructure']
        ].values
        
        # Calculate feature-wise similarity
        similarities = []
        for i, (q_feat, n_feat) in enumerate(zip(query_features, neighbor_features)):
            if i < 2:  # Lat/Lon - use distance-based similarity
                continue
            else:  # Other features - use normalized difference
                max_val = self.features_df.iloc[:, i].max()
                min_val = self.features_df.iloc[:, i].min()
                if max_val != min_val:
                    similarity = 1 - abs(q_feat - n_feat) / (max_val - min_val)
                else:
                    similarity = 1.0
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.5
    
    def get_location_info(self, lat, lon):
        """Get location information using Google Maps API"""
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lon}",
                'key': GOOGLE_MAPS_API_KEY
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                return data['results'][0]['formatted_address']
            return f"Location: {lat:.4f}°N, {lon:.4f}°E"
            
        except Exception as e:
            print(f"Error getting location info: {e}")
            return f"Location: {lat:.4f}°N, {lon:.4f}°E"
    
    def generate_ai_analysis(self, predictions, lat, lon):
        """Generate AI-powered analysis using Groq"""
        try:
            # Prepare context for AI analysis
            context = f"""
            Location: {lat}°N, {lon}°E
            Nearby mineral sites found:
            """
            
            for pred in predictions[:3]:  # Top 3 predictions
                context += f"""
                - {pred['location']}: {pred['mineral']} ({pred['distance_km']:.1f}km away)
                  Grade: {pred['grade']}%, Production: {pred['production']}, Confidence: {pred['prediction_confidence']:.2f}
                """
            
            prompt = f"""
            {context}
            
            Provide a comprehensive geological analysis and mineral exploration recommendations for this location.
            Include:
            1. Geological assessment
            2. Mineral potential evaluation
            3. Economic viability analysis
            4. Exploration recommendations
            5. Risk assessment
            
            Keep response concise but informative.
            """
            
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating AI analysis: {e}")
            return "AI analysis unavailable at this time."
    
    def translate_analysis(self, text, target_language='ta-IN'):
        """Translate analysis using SarvamAI"""
        try:
            if target_language == 'en-IN':
                return text
                
            response = sarvam_client.text.translate(
                input=text,
                source_language_code='en-IN',
                target_language_code=target_language
            )
            return response.translated_text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def create_prediction_map(self, lat, lon, predictions, filename="mineral_predictions.html"):
        """Create interactive map with predictions"""
        try:
            # Create base map
            m = folium.Map(location=[lat, lon], zoom_start=8)
            
            # Add query location
            folium.Marker(
                [lat, lon],
                popup=f"Query Location: {lat:.4f}°N, {lon:.4f}°E",
                icon=folium.Icon(color='red', icon='search'),
                tooltip="Query Location"
            ).add_to(m)
            
            # Add predicted locations
            colors = ['green', 'blue', 'orange', 'purple', 'pink']
            for i, pred in enumerate(predictions):
                color = colors[i % len(colors)]
                
                popup_html = f"""
                <div style="width: 250px;">
                    <h4>{pred['location']}</h4>
                    <p><strong>Mineral:</strong> {pred['mineral']}</p>
                    <p><strong>Distance:</strong> {pred['distance_km']:.1f} km</p>
                    <p><strong>Grade:</strong> {pred['grade']}%</p>
                    <p><strong>Confidence:</strong> {pred['prediction_confidence']:.2f}</p>
                    <p><strong>Geological Score:</strong> {pred['geological_score']}/10</p>
                </div>
                """
                
                folium.Marker(
                    pred['coordinates'],
                    popup=popup_html,
                    icon=folium.Icon(color=color, icon='industry'),
                    tooltip=f"Rank {pred['rank']}: {pred['mineral']}"
                ).add_to(m)
                
                # Add connection line
                folium.PolyLine(
                    [[lat, lon], pred['coordinates']],
                    color=color,
                    weight=2,
                    opacity=0.6
                ).add_to(m)
            
            # Save map
            m.save(filename)
            return filename
            
        except Exception as e:
            print(f"Error creating map: {e}")
            return None
    
    def create_3d_visualization(self, predictions):
        """Create 3D visualization of mineral predictions"""
        try:
            fig = go.Figure()
            
            # Add predicted locations
            for pred in predictions:
                fig.add_trace(go.Scatter3d(
                    x=[pred['coordinates'][1]],  # Longitude
                    y=[pred['coordinates'][0]],  # Latitude
                    z=[pred['geological_score']],  # Geological score as height
                    mode='markers+text',
                    marker=dict(
                        size=pred['prediction_confidence'] * 20,
                        color=pred['geological_score'],
                        colorscale='Viridis',
                        opacity=0.8
                    ),
                    text=pred['mineral'],
                    textposition="top center",
                    name=f"Rank {pred['rank']}: {pred['mineral']}",
                    hovertemplate=f"""
                    <b>{pred['location']}</b><br>
                    Mineral: {pred['mineral']}<br>
                    Distance: {pred['distance_km']:.1f} km<br>
                    Confidence: {pred['prediction_confidence']:.2f}<br>
                    Grade: {pred['grade']}%<br>
                    <extra></extra>
                    """
                ))
            
            fig.update_layout(
                title='3D Mineral Prediction Visualization',
                scene=dict(
                    xaxis_title='Longitude',
                    yaxis_title='Latitude',
                    zaxis_title='Geological Score',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
                ),
                height=600
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating 3D visualization: {e}")
            return None

def main_prediction_system():
    """Main function to run the mineral prediction system"""
    print("🗺️ MINERAL PREDICTION SYSTEM - Karnataka & Andhra Pradesh")
    print("=" * 70)
    print("🤖 Powered by KNN Machine Learning + Multi-AI Integration")
    print("🔍 APIs: Groq + Gemini + Google Maps + SarvamAI")
    print("=" * 70)
    
    # Initialize prediction system
    predictor = MineralPredictionSystem()
    
    while True:
        try:
            print("\n📋 MAIN MENU")
            print("1. Predict Mineral Sites (KNN Analysis)")
            print("2. View Active Mineral Database")
            print("3. Create Prediction Map")
            print("4. Generate 3D Visualization")
            print("5. Multilingual Analysis")
            print("6. Exit")
            
            choice = input("\n➤ Select option (1-6): ").strip()
            
            if choice == '1':
                print("\n🔍 MINERAL SITE PREDICTION")
                print("-" * 40)
                
                # Get coordinates
                try:
                    lat = float(input("➤ Enter Latitude: "))
                    lon = float(input("➤ Enter Longitude: "))
                    n_neighbors = int(input("➤ Number of predictions (default 5): ") or "5")
                except ValueError:
                    print("❌ Invalid input. Please enter numeric values.")
                    continue
                
                # Get location info
                location_info = predictor.get_location_info(lat, lon)
                print(f"\n📍 Location: {location_info}")
                
                # Make predictions
                print("\n🤖 Running KNN analysis...")
                predictions = predictor.predict_nearby_sites(lat, lon, n_neighbors)
                
                if predictions:
                    print(f"\n🎯 TOP {len(predictions)} MINERAL PREDICTIONS:")
                    print("=" * 60)
                    
                    for pred in predictions:
                        print(f"""
📊 RANK {pred['rank']}: {pred['location']}
   🗺️ Mineral: {pred['mineral']}
   📍 Coordinates: {pred['coordinates'][0]:.4f}°N, {pred['coordinates'][1]:.4f}°E
   📏 Distance: {pred['distance_km']:.1f} km
   ⭐ Confidence: {pred['prediction_confidence']:.2f}
   📈 Grade: {pred['grade']}%
   💰 Production: {pred['production']:,}
   🏔️ Geological Score: {pred['geological_score']}/10
                        """)
                    
                    # Generate AI analysis
                    print("\n🧠 Generating AI Analysis...")
                    ai_analysis = predictor.generate_ai_analysis(predictions, lat, lon)
                    print("\n📝 AI GEOLOGICAL ANALYSIS:")
                    print("-" * 40)
                    print(ai_analysis)
                    
                else:
                    print("❌ No predictions could be generated.")
            
            elif choice == '2':
                print("\n📊 ACTIVE MINERAL DATABASE")
                print("=" * 50)
                
                for name, data in predictor.mineral_data.items():
                    print(f"""
🏭 {name}:
   🗺️ Mineral: {data['mineral']}
   📍 Location: {data['coords'][0]:.4f}°N, {data['coords'][1]:.4f}°E
   📈 Grade: {data['grade']}%
   💰 Production: {data['production']:,}
   💎 Reserves: {data['reserves']} Mt
   🏔️ Geological Score: {data['geological_score']}/10
                    """)
            
            elif choice == '3':
                print("\n🗺️ CREATING PREDICTION MAP")
                print("-" * 30)
                
                try:
                    lat = float(input("➤ Enter Latitude: "))
                    lon = float(input("➤ Enter Longitude: "))
                except ValueError:
                    print("❌ Invalid coordinates.")
                    continue
                
                predictions = predictor.predict_nearby_sites(lat, lon, 5)
                if predictions:
                    filename = predictor.create_prediction_map(lat, lon, predictions)
                    if filename:
                        print(f"✅ Map saved as: {filename}")
                        print("🌐 Open the HTML file in your browser to view the interactive map")
                    else:
                        print("❌ Failed to create map")
                else:
                    print("❌ No predictions available for mapping")
            
            elif choice == '4':
                print("\n📊 CREATING 3D VISUALIZATION")
                print("-" * 35)
                
                try:
                    lat = float(input("➤ Enter Latitude: "))
                    lon = float(input("➤ Enter Longitude: "))
                except ValueError:
                    print("❌ Invalid coordinates.")
                    continue
                
                predictions = predictor.predict_nearby_sites(lat, lon, 5)
                if predictions:
                    fig = predictor.create_3d_visualization(predictions)
                    if fig:
                        fig.write_html("3d_mineral_predictions.html")
                        print("✅ 3D visualization saved as: 3d_mineral_predictions.html")
                        try:
                            fig.show()
                        except:
                            print("📱 3D plot saved to file (browser display not available)")
                    else:
                        print("❌ Failed to create 3D visualization")
                else:
                    print("❌ No predictions available for visualization")
            
            elif choice == '5':
                print("\n🌐 MULTILINGUAL ANALYSIS")
                print("-" * 25)
                
                languages = {
                    '1': ('English', 'en-IN'),
                    '2': ('Hindi', 'hi-IN'),
                    '3': ('Tamil', 'ta-IN'),
                    '4': ('Telugu', 'te-IN'),
                    '5': ('Kannada', 'kn-IN')
                }
                
                print("Select Language:")
                for key, (name, code) in languages.items():
                    print(f"{key}. {name}")
                
                lang_choice = input("\n➤ Select language (1-5): ").strip()
                if lang_choice in languages:
                    lang_name, lang_code = languages[lang_choice]
                else:
                    lang_name, lang_code = 'English', 'en-IN'
                
                try:
                    lat = float(input("➤ Enter Latitude: "))
                    lon = float(input("➤ Enter Longitude: "))
                except ValueError:
                    print("❌ Invalid coordinates.")
                    continue
                
                predictions = predictor.predict_nearby_sites(lat, lon, 3)
                if predictions:
                    ai_analysis = predictor.generate_ai_analysis(predictions, lat, lon)
                    
                    if lang_code != 'en-IN':
                        print(f"\n🔄 Translating to {lang_name}...")
                        translated_analysis = predictor.translate_analysis(ai_analysis, lang_code)
                        print(f"\n📝 ANALYSIS IN {lang_name.upper()}:")
                        print("-" * 40)
                        print(translated_analysis)
                    else:
                        print("\n📝 ANALYSIS:")
                        print("-" * 15)
                        print(ai_analysis)
                else:
                    print("❌ No predictions available for analysis")
            
            elif choice == '6':
                print("\n👋 Thank you for using the Mineral Prediction System!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-6.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main_prediction_system()
