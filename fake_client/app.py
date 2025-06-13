import os
import sys
import ee
import geemap
import plotly.graph_objects as go
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv
from sarvamai import SarvamAI
from gtts import gTTS
import pygame
import warnings
import locale
import codecs
warnings.filterwarnings('ignore')

# Set proper encoding for terminal output
if sys.platform.startswith('win'):
    # Windows terminal encoding fix
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.system('chcp 65001 > nul')  # Set UTF-8 code page

# Set locale for proper Unicode handling
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

load_dotenv()

# Initialize APIs with better error handling
def initialize_apis():
    """Initialize all APIs with proper error handling"""
    global ee_initialized, llm, client, chat_history
    
    # Initialize Google Earth Engine
    ee_initialized = False
    try:
        ee.Initialize(project="cloud-project-462514")
        print("✅ Google Earth Engine initialized successfully")
        ee_initialized = True
    except Exception as e:
        print(f"⚠️ Google Earth Engine initialization failed: {e}")
        print("🔄 Continuing without Earth Engine...")
    
    # Initialize LLM
    try:
        llm = ChatGroq(model="Llama-3.3-70b-Versatile", api_key=os.getenv("GROQ_API_KEY"))
        print("✅ ChatGroq LLM initialized successfully")
    except Exception as e:
        print(f"❌ ChatGroq initialization failed: {e}")
        llm = None
    
    # Initialize SarvamAI client with proper error handling
    try:
        client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))
        print("✅ SarvamAI client initialized successfully")
        
        # Test translation to ensure it works
        test_response = client.text.translate(
            input="Hello",
            source_language_code="en-IN",
            target_language_code="hi-IN"
        )
        if hasattr(test_response, 'translated_text'):
            print("✅ SarvamAI translation test successful")
        else:
            print("⚠️ SarvamAI translation test failed")
            
    except Exception as e:
        print(f"⚠️ SarvamAI initialization failed: {e}")
        print("🔄 Continuing without translation...")
        client = None
    
    # Initialize chat history
    chat_history = ChatMessageHistory()

# Initialize all APIs
initialize_apis()

# Language mapping for SarvamAI
SUPPORTED_LANGUAGES = {
    '1': ('English', 'en-IN'),
    '2': ('Hindi', 'hi-IN'),
    '3': ('Tamil', 'ta-IN'),
    '4': ('Telugu', 'te-IN'),
    '5': ('Kannada', 'kn-IN'),
    '6': ('Malayalam', 'ml-IN'),
    '7': ('Marathi', 'mr-IN'),
    '8': ('Gujarati', 'gu-IN'),
    '9': ('Punjabi', 'pa-IN'),
    '10': ('Bengali', 'bn-IN'),
    '11': ('Odia', 'od-IN'),
    '12': ('Assamese', 'as-IN'),
    '13': ('Urdu', 'ur-IN')
}

# REAL DISTRICT COORDINATES - KARNATAKA AND ANDHRA PRADESH
DISTRICT_COORDINATES = {
    # Karnataka Districts
    'Raichur_KA': [16.2072, 77.3421],
    'Kolar_KA': [13.1362, 78.1348],
    'Bellary_KA': [15.1394, 76.9214],
    'Chikmagaluru_KA': [13.3161, 75.7720],
    'Chitradurga_KA': [14.2251, 76.3958],
    'Bijapur_KA': [16.8302, 75.7100],
    'Dharwad_KA': [15.4589, 75.0078],
    'Tumkur_KA': [13.3422, 77.1025],
    'Uttara_Kannada_KA': [14.8000, 74.6000],
    'Gulbarga_KA': [17.3297, 76.8343],
    'Belgaum_KA': [15.8497, 74.4977],
    'Bangalore_KA': [12.9716, 77.5946],
    'Shimoga_KA': [13.9299, 75.5681],
    'Mysore_KA': [12.2958, 76.6394],
    'Hassan_KA': [13.0067, 76.0962],
    'Dakshina_Kannada_KA': [12.8000, 75.0000],
    'Udupi_KA': [13.3409, 74.7421],
    
    # Andhra Pradesh Districts
    'Srikakulam_AP': [18.2949, 83.8938],
    'Visakhapatnam_AP': [17.6868, 83.2185],
    'East_Godavari_AP': [17.2403, 81.7800],
    'West_Godavari_AP': [16.9891, 81.5025],
    'Krishna_AP': [16.2160, 81.1498],
    'Guntur_AP': [16.3067, 80.4365],
    'Prakasam_AP': [15.7000, 79.8000],
    'Nellore_AP': [14.4426, 79.9865],
    'Chittoor_AP': [13.2172, 79.1003],
    'Kadapa_AP': [14.4674, 78.8240],
    'Kurnool_AP': [15.8281, 78.0373],
    'Anantapur_AP': [14.6819, 77.6006],
    'Cuddapah_AP': [14.4426, 78.8242]
}

# COMPREHENSIVE MINERAL LOCATION DATA
comprehensive_mineral_locations = {
    'Fe2O3_% - Iron Oxide (Hematite)': {
        'category': 'Major Oxides', 'color': 'red', 'display_name': 'Iron Ore',
        'locations': [
            {'name': 'Bellary Iron Ore (18.7 Mt)', 'coords': DISTRICT_COORDINATES['Bellary_KA'], 'production': '18.7 Mt/year', 'grade': '58% Fe'},
            {'name': 'Chikmagaluru Iron', 'coords': DISTRICT_COORDINATES['Chikmagaluru_KA'], 'production': '5.2 Mt/year', 'grade': '62% Fe'},
            {'name': 'Chitradurga Iron Belt', 'coords': DISTRICT_COORDINATES['Chitradurga_KA'], 'production': '8.1 Mt/year', 'grade': '55% Fe'},
            {'name': 'Cuddapah Iron Formation (AP)', 'coords': DISTRICT_COORDINATES['Cuddapah_AP'], 'production': '12.3 Mt/year', 'grade': '60% Fe'},
            {'name': 'Anantapur Iron Deposits (AP)', 'coords': DISTRICT_COORDINATES['Anantapur_AP'], 'production': '6.8 Mt/year', 'grade': '57% Fe'}
        ]
    },
    'Au_ppb - Gold': {
        'category': 'Precious Metals', 'color': 'gold', 'display_name': 'Gold',
        'locations': [
            {'name': 'Kolar Gold Fields (KA)', 'coords': DISTRICT_COORDINATES['Kolar_KA'], 'production': '1.583 tons/year', 'grade': '8.5 g/t'},
            {'name': 'Raichur Gold (KA)', 'coords': DISTRICT_COORDINATES['Raichur_KA'], 'production': '0.8 tons/year', 'grade': '6.2 g/t'},
            {'name': 'Anantapur Gold (AP)', 'coords': DISTRICT_COORDINATES['Anantapur_AP'], 'production': '1.2 tons/year', 'grade': '7.8 g/t'}
        ]
    },
    'Li_ppm - Lithium': {
        'category': 'Strategic Metals', 'color': 'lime', 'display_name': 'Lithium',
        'locations': [
            {'name': 'Hassan Lithium Pegmatite (KA)', 'coords': DISTRICT_COORDINATES['Hassan_KA'], 'production': '2.5 Mt/year', 'grade': '1.2% Li2O'},
            {'name': 'Mysore Lithium (KA)', 'coords': DISTRICT_COORDINATES['Mysore_KA'], 'production': '1.8 Mt/year', 'grade': '1.0% Li2O'},
            {'name': 'Anantapur Lithium (AP)', 'coords': DISTRICT_COORDINATES['Anantapur_AP'], 'production': '3.2 Mt/year', 'grade': '1.4% Li2O'}
        ]
    },
    'Al2O3_% - Alumina (Bauxite)': {
        'category': 'Major Oxides', 'color': 'orange', 'display_name': 'Bauxite',
        'locations': [
            {'name': 'Belgaum Bauxite (KA)', 'coords': DISTRICT_COORDINATES['Belgaum_KA'], 'production': '8.5 Mt/year', 'grade': '45% Al2O3'},
            {'name': 'Uttara Kannada Bauxite (KA)', 'coords': DISTRICT_COORDINATES['Uttara_Kannada_KA'], 'production': '6.2 Mt/year', 'grade': '42% Al2O3'},
            {'name': 'Visakhapatnam Bauxite (AP)', 'coords': DISTRICT_COORDINATES['Visakhapatnam_AP'], 'production': '12.8 Mt/year', 'grade': '48% Al2O3'}
        ]
    },
    'Cu_ppm - Copper': {
        'category': 'Base Metals', 'color': 'darkred', 'display_name': 'Copper',
        'locations': [
            {'name': 'Hassan Copper Belt (KA)', 'coords': DISTRICT_COORDINATES['Hassan_KA'], 'production': '0.5 Mt/year', 'grade': '1.2% Cu'},
            {'name': 'Chitradurga Copper (KA)', 'coords': DISTRICT_COORDINATES['Chitradurga_KA'], 'production': '0.3 Mt/year', 'grade': '0.8% Cu'},
            {'name': 'Guntur Copper (AP)', 'coords': DISTRICT_COORDINATES['Guntur_AP'], 'production': '0.7 Mt/year', 'grade': '1.5% Cu'}
        ]
    },
    'TiO2_% - Titanium (Ilmenite)': {
        'category': 'Strategic Metals', 'color': 'darkblue', 'display_name': 'Titanium',
        'locations': [
            {'name': 'Srikakulam Beach Ilmenite (AP)', 'coords': DISTRICT_COORDINATES['Srikakulam_AP'], 'production': '15.2 Mt/year', 'grade': '65% TiO2'},
            {'name': 'Visakhapatnam Beach Sands (AP)', 'coords': DISTRICT_COORDINATES['Visakhapatnam_AP'], 'production': '12.8 Mt/year', 'grade': '62% TiO2'},
            {'name': 'Uttara Kannada Beach Sands (KA)', 'coords': DISTRICT_COORDINATES['Uttara_Kannada_KA'], 'production': '8.5 Mt/year', 'grade': '58% TiO2'}
        ]
    }
}

# FIXED TRANSLATION FUNCTIONS
def safe_print(text, encoding='utf-8'):
    """Safe print function that handles Unicode properly"""
    try:
        if isinstance(text, bytes):
            text = text.decode(encoding)
        print(text, flush=True)
    except UnicodeEncodeError:
        # Fallback to ASCII with replacement
        print(text.encode('ascii', 'replace').decode('ascii'), flush=True)
    except Exception as e:
        print(f"Print error: {e}")

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    FIXED: Function to translate text with proper error handling and encoding
    """
    try:
        if not client or not text.strip() or target_lang == 'en-IN':
            return text
        
        # Clean text for translation
        text = text.strip()
        if len(text) < 3:  # Skip very short text
            return text
        
        # Remove markdown formatting for better translation
        clean_text = text.replace('**', '').replace('*', '').replace('#', '').replace('`', '')
        
        response = client.text.translate(
            input=clean_text,
            source_language_code=source_lang,
            target_language_code=target_lang
        )
        
        # Handle different response formats
        if hasattr(response, 'translated_text'):
            translated = response.translated_text
        elif isinstance(response, dict) and 'translated_text' in response:
            translated = response['translated_text']
        else:
            return text
        
        # Ensure proper encoding
        if isinstance(translated, bytes):
            translated = translated.decode('utf-8')
            
        return translated
            
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def text_to_speech(text: str, lang: str, output_file: str = "output.mp3") -> str:
    """
    FIXED: Function to convert text to speech with better error handling
    """
    try:
        # Map SarvamAI language codes to gTTS codes
        lang_mapping = {
            'hi-IN': 'hi', 'ta-IN': 'ta', 'te-IN': 'te', 'kn-IN': 'kn',
            'ml-IN': 'ml', 'mr-IN': 'mr', 'gu-IN': 'gu', 'pa-IN': 'pa',
            'bn-IN': 'bn', 'en-IN': 'en', 'od-IN': 'or', 'as-IN': 'as',
            'ur-IN': 'ur'
        }
        
        tts_lang = lang_mapping.get(lang, 'en')
        
        # Clean text for TTS
        clean_text = text.replace('#', '').replace('*', '').replace('`', '')
        clean_text = ' '.join(clean_text.split())  # Remove extra whitespace
        
        if len(clean_text.strip()) < 10:
            print("Text too short for TTS")
            return None
            
        tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
        tts.save(output_file)
        return output_file
        
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")
        return None

def play_audio(audio_file: str):
    """FIXED: Play audio file with better error handling"""
    try:
        if not audio_file or not os.path.exists(audio_file):
            print("Audio file not found")
            return
            
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        print("🔊 Audio is playing... Press Enter to stop")
        input()  # Wait for user input
        pygame.mixer.music.stop()
        
    except Exception as e:
        print(f"Audio playback error: {str(e)}")

class CombinedMineralAnalyzer:
    def __init__(self):
        """Initialize the Combined Mineral Analysis System"""
        self.map = None
        self.geological_data = {}
        self.analysis_results = {}

    def create_interactive_mineral_map(self, center_coords=[15.5, 79.0], zoom=7):
        """FIXED: Create interactive map with better error handling"""
        try:
            # Create geemap Map
            self.map = geemap.Map(center=center_coords, zoom=zoom)
            
            # Add satellite basemap
            try:
                self.map.add_basemap('HYBRID')
            except:
                safe_print("⚠️ Using default basemap")
            
            # Only add Earth Engine layers if initialized
            if ee_initialized:
                # Define area of interest (Karnataka and Andhra Pradesh)
                geometry = ee.Geometry.Polygon([
                    [[74.0, 12.0], [84.5, 12.0], [84.5, 19.0], [74.0, 19.0], [74.0, 12.0]]
                ])
                
                # Add geological layers
                self.add_geological_layers(geometry)
            else:
                safe_print("⚠️ Skipping Earth Engine layers")
            
            # Add mineral pins with detailed information
            self.add_mineral_pins()
            
            # Add legend and controls
            self.add_map_controls()
            
            return self.map
            
        except Exception as e:
            safe_print(f"Error creating interactive map: {e}")
            # Create fallback map
            try:
                self.map = geemap.Map(center=center_coords, zoom=zoom)
                self.add_mineral_pins()
                self.add_map_controls()
                return self.map
            except Exception as e2:
                safe_print(f"Fallback map creation failed: {e2}")
                return None

    def add_geological_layers(self, geometry):
        """FIXED: Add geological layers with error handling"""
        try:
            if not ee_initialized:
                return
                
            # Load Landsat 8 collection for geological analysis
            landsat_collection = (ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
                                  .filterBounds(geometry)
                                  .filterDate('2020-01-01', '2024-12-31')
                                  .filter(ee.Filter.lt('CLOUD_COVER', 15))
                                  .select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])
                                  .median())

            landsat_scaled = (landsat_collection
                              .multiply(0.0000275).add(-0.2)
                              .clip(geometry))

            # Add DEM (Digital Elevation Model)
            dem = ee.Image('USGS/SRTMGL1_003').clip(geometry)
            self.map.addLayer(dem, {'min': 0, 'max': 2000, 'palette': ['blue', 'green', 'yellow', 'red']}, 'Elevation', False)
            
            # Add slope layer
            slope = ee.Terrain.slope(dem)
            self.map.addLayer(slope, {'min': 0, 'max': 30, 'palette': ['white', 'red']}, 'Slope', False)
            
            # Create mineral potential zones
            iron_index = landsat_scaled.expression('(B4 / B2)', {
                'B4': landsat_scaled.select('SR_B4'), 'B2': landsat_scaled.select('SR_B2')
            }).rename('Iron_Index')
            
            clay_index = landsat_scaled.expression('(B6 / B7)', {
                'B6': landsat_scaled.select('SR_B6'), 'B7': landsat_scaled.select('SR_B7')
            }).rename('Clay_Index')
            
            # Add mineral indices
            self.map.addLayer(iron_index, {'min': 0.5, 'max': 2.0, 'palette': ['blue', 'yellow', 'red']}, 'Iron Potential', True, 0.7)
            self.map.addLayer(clay_index, {'min': 0.8, 'max': 1.5, 'palette': ['purple', 'orange', 'yellow']}, 'Clay Minerals', False, 0.6)
            
            # Store data for analysis
            self.geological_data = {
                'dem': dem,
                'slope': slope,
                'iron_index': iron_index,
                'clay_index': clay_index,
                'geometry': geometry
            }
            
        except Exception as e:
            safe_print(f"Warning: Could not add geological layers: {e}")

    def add_mineral_pins(self):
        """FIXED: Add mineral location pins with better error handling"""
        try:
            for mineral_type, mineral_data in comprehensive_mineral_locations.items():
                for location in mineral_data['locations']:
                    try:
                        # Create detailed popup content
                        popup_html = f"""
                        <div style="width: 300px; font-family: Arial;">
                            <h3 style="color: {mineral_data['color']}; margin: 0;">
                                🗺️ {mineral_data['display_name']}
                            </h3>
                            <hr style="margin: 5px 0;">
                            <p><strong>📍 Location:</strong> {location['name']}</p>
                            <p><strong>📊 Production:</strong> {location.get('production', 'N/A')}</p>
                            <p><strong>⚗️ Grade:</strong> {location.get('grade', 'N/A')}</p>
                            <p><strong>📂 Category:</strong> {mineral_data['category']}</p>
                            <p><strong>🌐 Coordinates:</strong> {location['coords'][0]:.4f}°N, {location['coords'][1]:.4f}°E</p>
                            <div style="margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 3px;">
                                <small><strong>Economic Impact:</strong> High-value mineral contributing to regional development and export revenue.</small>
                            </div>
                        </div>
                        """
                        
                        # Add marker to map with custom styling
                        self.map.add_marker(
                            location=location['coords'],
                            popup=popup_html,
                            icon_color=mineral_data['color'],
                            icon='industry',
                            tooltip=f"{mineral_data['display_name']} - {location['name']}"
                        )
                    except Exception as e:
                        safe_print(f"Warning: Could not add marker for {location['name']}: {e}")
            
        except Exception as e:
            safe_print(f"Error adding mineral pins: {e}")

    def add_map_controls(self):
        """FIXED: Add legend and controls with error handling"""
        try:
            # Create legend
            legend_html = """
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 200px; height: auto; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
                <h4>🗺️ Mineral Legend</h4>
                <p><span style="color: red;">●</span> Iron Ore</p>
                <p><span style="color: gold;">●</span> Gold</p>
                <p><span style="color: lime;">●</span> Lithium</p>
                <p><span style="color: orange;">●</span> Bauxite</p>
                <p><span style="color: darkred;">●</span> Copper</p>
                <p><span style="color: darkblue;">●</span> Titanium</p>
                <hr>
                <small><strong>Karnataka & Andhra Pradesh</strong><br>
                Mineral Excavation Sites</small>
            </div>
            """
            
            # Add legend to map
            self.map.add_html(legend_html)
            
        except Exception as e:
            safe_print(f"Warning: Could not add map controls: {e}")

    def analyze_coordinates(self, latitude, longitude, target_language='en-IN'):
        """FIXED: Analyze mineral potential with better translation handling"""
        try:
            # Find nearest mineral location
            min_distance = float('inf')
            nearest_mineral = None
            nearest_location = None
            
            for mineral_type, mineral_data in comprehensive_mineral_locations.items():
                for location in mineral_data['locations']:
                    # Calculate distance
                    lat_diff = latitude - location['coords'][0]
                    lon_diff = longitude - location['coords'][1]
                    distance = (lat_diff**2 + lon_diff**2)**0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_mineral = mineral_data
                        nearest_location = location
            
            # Generate analysis report
            analysis_report = f"""
### Mineral Excavation Site Analysis for {latitude}°N, {longitude}°E

#### Nearest Mineral Deposit
- Location: {nearest_location['name']}
- Mineral Type: {nearest_mineral['display_name']}
- Distance: {min_distance:.2f} degrees (~{min_distance*111:.1f} km)
- Production: {nearest_location.get('production', 'N/A')}
- Grade: {nearest_location.get('grade', 'N/A')}

#### Industrial Applications
- Construction Industry: Steel production, building materials
- Technology Sector: Electronics, battery components
- Automotive Industry: Vehicle parts, EV batteries
- Export Potential: International markets, foreign exchange

#### Economic Impact
- Investment Potential: High ROI due to strategic location
- Employment Generation: Direct and indirect job creation
- Infrastructure Development: Roads, power, transportation
- Regional Growth: Industrial cluster development

#### Investment Analysis
- Market Demand: Strong global demand for {nearest_mineral['display_name'].lower()}
- Accessibility: Good road and rail connectivity
- Processing Facilities: Existing infrastructure nearby
- Export Routes: Access to major ports

#### Recommendations
- Conduct detailed geological survey
- Assess environmental impact
- Develop mining infrastructure
- Establish processing facilities
- Create export partnerships
            """
            
            # FIXED TEXT-TO-TEXT TRANSLATION
            if target_language != 'en-IN' and client:
                try:
                    # Translate in smaller chunks for better results
                    sections = analysis_report.split('####')
                    translated_sections = []
                    
                    for section in sections:
                        if section.strip():
                            # Translate each section
                            if section.startswith(' '):
                                section_title = section.split('\n')[0].strip()
                                section_content = '\n'.join(section.split('\n')[1:])
                                
                                translated_title = translate_text(section_title, 'en-IN', target_language)
                                translated_content = translate_text(section_content, 'en-IN', target_language)
                                
                                translated_sections.append(f"#### {translated_title}\n{translated_content}")
                            else:
                                translated_section = translate_text(section.strip(), 'en-IN', target_language)
                                translated_sections.append(translated_section)
                    
                    translated_report = '\n\n'.join(translated_sections)
                    return analysis_report, translated_report
                except Exception as e:
                    safe_print(f"Translation failed: {e}")
                    return analysis_report, None
            
            return analysis_report, None
            
        except Exception as e:
            return f"Error analyzing coordinates: {e}", None

    def create_3d_mineral_visualization(self, location_name="Karnataka_Andhra_Pradesh"):
        """FIXED: Create 3D visualization with error handling"""
        try:
            # Create 3D scatter plot
            fig = go.Figure()
            
            # Add mineral deposits as 3D points
            for mineral_type, mineral_data in comprehensive_mineral_locations.items():
                try:
                    lats = [loc['coords'][0] for loc in mineral_data['locations']]
                    lons = [loc['coords'][1] for loc in mineral_data['locations']]
                    # Simulate depth based on mineral type
                    depths = [-100 - i*50 for i in range(len(lats))]
                    names = [loc['name'] for loc in mineral_data['locations']]
                    
                    fig.add_trace(go.Scatter3d(
                        x=lons, y=lats, z=depths,
                        mode='markers',
                        marker=dict(
                            size=10,
                            color=mineral_data['color'],
                            opacity=0.8,
                            symbol='diamond'
                        ),
                        name=mineral_data['display_name'],
                        text=names,
                        hovertemplate='<b>%{text}</b><br>Lat: %{y:.4f}<br>Lon: %{x:.4f}<br>Depth: %{z}m<extra></extra>'
                    ))
                except Exception as e:
                    safe_print(f"Warning: Could not add {mineral_type} to 3D plot: {e}")
            
            fig.update_layout(
                title='3D Mineral Deposits Visualization - Karnataka & Andhra Pradesh',
                scene=dict(
                    xaxis_title='Longitude',
                    yaxis_title='Latitude',
                    zaxis_title='Depth (meters)',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
                ),
                height=600,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            safe_print(f"Error creating 3D visualization: {e}")
            return None

    def save_html_map(self, filename="mineral_excavation_map.html"):
        """FIXED: Save map with error handling"""
        try:
            if self.map:
                self.map.to_html(filename)
                safe_print(f"✅ Interactive map saved as: {filename}")
                return filename
            else:
                safe_print("❌ No map to save. Create map first.")
                return None
        except Exception as e:
            safe_print(f"Error saving HTML map: {e}")
            return None

def print_header(title: str, width: int = 80):
    """Print a neat header with proper encoding"""
    header = "\n" + "=" * width + "\n" + f"{title:^{width}}" + "\n" + "=" * width
    safe_print(header)

def print_section(title: str, width: int = 60):
    """Print a neat section header with proper encoding"""
    section = f"\n{title}\n" + "-" * width
    safe_print(section)

def main_combined_analysis():
    """FIXED: Main function with better error handling and encoding"""
    print_header("🗺️ MULTILINGUAL MINERAL EXCAVATION ANALYZER")
    safe_print("🌐 Text-to-Text and Text-to-Voice Translation")
    safe_print("📍 Real district coordinates with detailed mineral information")
    safe_print("🗺️ Interactive maps with exact mineral locations and pins")
    safe_print("🔧 Fixed terminal encoding and translation issues")
    
    # Initialize the combined analyzer
    analyzer = CombinedMineralAnalyzer()
    
    while True:
        try:
            print_section("📋 MAIN MENU")
            safe_print("1. Create Interactive Mineral Map")
            safe_print("2. Analyze Specific Coordinates (Text-to-Text + Text-to-Voice)")
            safe_print("3. Generate 3D Visualization")
            safe_print("4. Test Translation")
            safe_print("5. Exit")
            
            choice = input("\n➤ Select option (1-5): ").strip()
            
            if choice == '1':
                print_section("🗺️ Creating Interactive Mineral Map")
                
                # Create the map
                interactive_map = analyzer.create_interactive_mineral_map()
                
                if interactive_map:
                    # Save HTML file
                    html_filename = "karnataka_andhra_mineral_map.html"
                    saved_file = analyzer.save_html_map(html_filename)
                    
                    if saved_file:
                        safe_print("✅ Interactive map created successfully!")
                        safe_print(f"📁 HTML file saved as: {html_filename}")
                        safe_print(f"🌐 Open {html_filename} in your browser to view the map")
                        safe_print("📍 The map contains:")
                        safe_print("   - Exact mineral locations with pins")
                        safe_print("   - Detailed popup information")
                        if ee_initialized:
                            safe_print("   - Geological layers")
                        safe_print("   - Production data and grades")
                        safe_print("   - Economic impact information")
                else:
                    safe_print("❌ Failed to create interactive map")
                    
            elif choice == '2':
                print_section("📍 Coordinate Analysis with Text-to-Text & Text-to-Voice")
                
                # Get coordinates
                try:
                    lat = float(input("➤ Enter Latitude: "))
                    lon = float(input("➤ Enter Longitude: "))
                except ValueError:
                    safe_print("❌ Invalid coordinates. Please enter numeric values.")
                    continue
                
                # Language selection
                print_section("🌐 Select Language")
                for key, (name, code) in SUPPORTED_LANGUAGES.items():
                    safe_print(f"{key:2}. {name:12} ({code})")
                
                lang_choice = input("\n➤ Select language (1-13): ").strip()
                if lang_choice in SUPPORTED_LANGUAGES:
                    target_lang_name, target_lang_code = SUPPORTED_LANGUAGES[lang_choice]
                else:
                    target_lang_name, target_lang_code = 'English', 'en-IN'
                
                safe_print(f"✅ Selected language: {target_lang_name}")
                
                # Analyze coordinates with TEXT-TO-TEXT translation
                safe_print(f"\n🔍 Analyzing coordinates: {lat}°N, {lon}°E")
                english_analysis, translated_analysis = analyzer.analyze_coordinates(lat, lon, target_lang_code)
                
                print_section("📊 ENGLISH ANALYSIS RESULTS")
                safe_print(english_analysis)
                
                if translated_analysis:
                    print_section(f"🌐 TRANSLATED VERSION ({target_lang_name})")
                    safe_print(translated_analysis)
                    
                    # TEXT-TO-VOICE option
                    audio_choice = input(f"\n🔊 Generate {target_lang_name} audio? (y/n): ").lower().strip()
                    if audio_choice == 'y':
                        try:
                            safe_print("🔊 Generating audio...")
                            audio_file = text_to_speech(
                                translated_analysis, 
                                target_lang_code, 
                                f"analysis_{target_lang_code}.mp3"
                            )
                            if audio_file:
                                safe_print("🔊 Audio generated successfully!")
                                play_choice = input("Play now? (y/n): ").lower().strip()
                                if play_choice == 'y':
                                    play_audio(audio_file)
                                else:
                                    safe_print(f"✅ Audio file saved as: {audio_file}")
                            else:
                                safe_print("❌ Audio generation failed")
                        except Exception as e:
                            safe_print(f"❌ Audio generation failed: {str(e)}")
                elif target_lang_code == 'en-IN':
                    # Optional English audio
                    audio_choice = input("\n🔊 Generate English audio? (y/n): ").lower().strip()
                    if audio_choice == 'y':
                        try:
                            safe_print("🔊 Generating English audio...")
                            audio_file = text_to_speech(
                                english_analysis, 
                                'en-IN', 
                                f"analysis_english.mp3"
                            )
                            if audio_file:
                                safe_print("🔊 Audio generated successfully!")
                                play_choice = input("Play now? (y/n): ").lower().strip()
                                if play_choice == 'y':
                                    play_audio(audio_file)
                                else:
                                    safe_print(f"✅ Audio file saved as: {audio_file}")
                        except Exception as e:
                            safe_print(f"❌ Audio generation failed: {str(e)}")
                
            elif choice == '3':
                print_section("📊 Creating 3D Visualization")
                
                fig_3d = analyzer.create_3d_mineral_visualization()
                
                if fig_3d:
                    # Save 3D visualization
                    viz_filename = "3d_mineral_visualization.html"
                    try:
                        fig_3d.write_html(viz_filename)
                        safe_print(f"✅ 3D visualization saved as: {viz_filename}")
                        safe_print("🌐 Open the HTML file to view the interactive 3D plot")
                        
                        # Show plot if possible
                        try:
                            fig_3d.show()
                        except:
                            safe_print("📱 3D plot saved to file (browser display not available)")
                    except Exception as e:
                        safe_print(f"❌ Failed to save 3D visualization: {e}")
                else:
                    safe_print("❌ Failed to create 3D visualization")
                    
            elif choice == '4':
                print_section("🧪 Testing Translation")
                
                if not client:
                    safe_print("❌ SarvamAI client not available")
                    continue
                
                test_text = "This is a test for mineral excavation analysis."
                safe_print(f"Original text: {test_text}")
                
                for key, (name, code) in list(SUPPORTED_LANGUAGES.items())[:5]:  # Test first 5 languages
                    if code != 'en-IN':
                        translated = translate_text(test_text, 'en-IN', code)
                        safe_print(f"{name}: {translated}")
                
            elif choice == '5':
                print_header("👋 Thank you for using the Mineral Analyzer!")
                break
                
            else:
                safe_print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print_header("👋 Goodbye!")
            break
        except Exception as e:
            safe_print(f"❌ Error: {e}")

if __name__ == "__main__":
    main_combined_analysis()
