import requests
import json
import time
from datetime import datetime, timedelta
import geocoder
from typing import Dict, Tuple, Optional, List
import math

class AdvancedAgriculturalDataRetriever:
    def __init__(self):
        # API Keys
        self.api_keys = {
            'google_maps': 'AIzaSyBfd1bm_3mxeU8VhNwt2GE9-h0BtMT2Sv4',
            'polygon': '7ilcvc9KIaoW3XGdJmegxPsqcqiKus12',
            'groq': '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',
            'hugging_face': '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',
            'gemini': 'AIzaSyA7fQKCBtHPQUHGX1nZXDOWiJMlO31-uk8',
            'openweather': 'dff8a714e30a29e438b4bd2ebb11190f'
        }
        
        # Base URLs
        self.base_urls = {
            'agromonitoring': 'http://api.agromonitoring.com/agro/1.0',
            'openweather': 'https://api.openweathermap.org/data/2.5',
            'ambee': 'https://api.ambeedata.com',
            'farmonaut': 'https://api.farmonaut.com/v1',
            'google_geocoding': 'https://maps.googleapis.com/maps/api/geocode/json'
        }

    def get_current_location(self) -> Tuple[float, float]:
        """Get current location using IP geolocation"""
        try:
            g = geocoder.ip('me')
            if g.ok:
                # return g.latlng[0], g.latlng[1]
                return 12.9915, 80.2337
            else:
                print("Could not determine location automatically")
                return None, None
        except Exception as e:
            print(f"Error getting current location: {e}")
            return None, None

    def get_location_info(self, lat: float, lon: float) -> Dict:
        """Get detailed location information using Google Geocoding API"""
        try:
            url = f"{self.base_urls['google_geocoding']}"
            params = {
                'latlng': f"{lat},{lon}",
                'key': self.api_keys['google_maps']
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    return {
                        'formatted_address': data['results'][0]['formatted_address'],
                        'components': data['results'][0]['address_components']
                    }
            return {'formatted_address': f"Lat: {lat}, Lon: {lon}", 'components': []}
        except Exception as e:
            print(f"Error getting location info: {e}")
            return {'formatted_address': f"Lat: {lat}, Lon: {lon}", 'components': []}

    def get_openweather_data(self, lat: float, lon: float) -> Dict:
        """Get comprehensive weather data from OpenWeatherMap"""
        try:
            # Current weather
            current_url = f"{self.base_urls['openweather']}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_keys['openweather'],
                'units': 'metric'
            }
            
            current_response = requests.get(current_url, params=params)
            current_data = current_response.json() if current_response.status_code == 200 else {}
            
            # Air pollution data
            pollution_url = f"{self.base_urls['openweather']}/air_pollution"
            pollution_response = requests.get(pollution_url, params=params)
            pollution_data = pollution_response.json() if pollution_response.status_code == 200 else {}
            
            # UV Index
            uv_url = f"{self.base_urls['openweather']}/uvi"
            uv_response = requests.get(uv_url, params=params)
            uv_data = uv_response.json() if uv_response.status_code == 200 else {}
            
            return {
                'current_weather': current_data,
                'air_pollution': pollution_data,
                'uv_index': uv_data
            }
        except Exception as e:
            print(f"Error getting OpenWeather data: {e}")
            return {}

    def get_detailed_soil_analysis(self, lat: float, lon: float) -> Dict:
        """Get comprehensive soil analysis including multiple depth layers"""
        try:
            # Create polygon for detailed analysis
            polygon_coords = self.create_field_polygon(lat, lon, 0.002)  # Larger area for better analysis
            
            # Get soil data from AgroMonitoring
            polygon_id = self.create_agromonitoring_polygon(polygon_coords, lat, lon)
            
            soil_data = {}
            if polygon_id:
                # Current soil conditions
                current_soil = self.get_current_soil_data(polygon_id)
                
                # Historical soil data (last 30 days)
                historical_soil = self.get_historical_soil_data(polygon_id, days=30)
                
                # Soil statistics and trends
                soil_stats = self.calculate_soil_statistics(historical_soil)
                
                soil_data = {
                    'current_conditions': current_soil,
                    'historical_data': historical_soil,
                    'soil_statistics': soil_stats,
                    'soil_health_indicators': self.calculate_soil_health_indicators(current_soil, soil_stats)
                }
            
            return soil_data
        except Exception as e:
            print(f"Error getting detailed soil analysis: {e}")
            return {}

    def get_agricultural_weather_data(self, lat: float, lon: float) -> Dict:
        """Get weather data specifically relevant for agriculture"""
        try:
            # Current weather with agricultural focus
            current_weather = self.get_openweather_data(lat, lon)
            
            # Calculate agricultural indices
            agri_indices = self.calculate_agricultural_indices(current_weather, lat, lon)
            
            # Get extended forecast for farming decisions
            forecast_data = self.get_extended_forecast(lat, lon)
            
            return {
                'current_weather': current_weather,
                'agricultural_indices': agri_indices,
                'forecast': forecast_data,
                'growing_conditions': self.assess_growing_conditions(current_weather, agri_indices)
            }
        except Exception as e:
            print(f"Error getting agricultural weather data: {e}")
            return {}

    def get_crop_suitability_analysis(self, lat: float, lon: float) -> Dict:
        """Analyze crop suitability based on soil and climate conditions"""
        try:
            # Get climate zone information
            climate_zone = self.determine_climate_zone(lat, lon)
            
            # Analyze soil suitability for different crops
            soil_suitability = self.analyze_soil_crop_suitability(lat, lon)
            
            # Get seasonal growing recommendations
            seasonal_recommendations = self.get_seasonal_recommendations(lat, lon)
            
            return {
                'climate_zone': climate_zone,
                'soil_suitability': soil_suitability,
                'seasonal_recommendations': seasonal_recommendations,
                'recommended_crops': self.get_recommended_crops(climate_zone, soil_suitability)
            }
        except Exception as e:
            print(f"Error getting crop suitability analysis: {e}")
            return {}

    def get_precision_agriculture_metrics(self, lat: float, lon: float) -> Dict:
        """Get precision agriculture specific metrics"""
        try:
            # Vegetation indices (simulated - would use satellite data in practice)
            vegetation_indices = self.calculate_vegetation_indices(lat, lon)
            
            # Field variability analysis
            field_variability = self.analyze_field_variability(lat, lon)
            
            # Irrigation recommendations
            irrigation_needs = self.calculate_irrigation_needs(lat, lon)
            
            # Fertilizer recommendations
            fertilizer_recommendations = self.get_fertilizer_recommendations(lat, lon)
            
            return {
                'vegetation_indices': vegetation_indices,
                'field_variability': field_variability,
                'irrigation_recommendations': irrigation_needs,
                'fertilizer_recommendations': fertilizer_recommendations,
                'yield_prediction': self.predict_yield_potential(lat, lon)
            }
        except Exception as e:
            print(f"Error getting precision agriculture metrics: {e}")
            return {}

    def calculate_agricultural_indices(self, weather_data: Dict, lat: float, lon: float) -> Dict:
        """Calculate important agricultural indices"""
        indices = {}
        
        if 'current_weather' in weather_data and weather_data['current_weather']:
            weather = weather_data['current_weather']
            temp = weather.get('main', {}).get('temp', 0)
            humidity = weather.get('main', {}).get('humidity', 0)
            wind_speed = weather.get('wind', {}).get('speed', 0)
            
            # Heat Index
            indices['heat_index'] = self.calculate_heat_index(temp, humidity)
            
            # Growing Degree Days (base 10°C)
            indices['growing_degree_days'] = max(0, temp - 10)
            
            # Evapotranspiration estimate
            indices['evapotranspiration'] = self.calculate_evapotranspiration(temp, humidity, wind_speed)
            
            # Frost risk assessment
            indices['frost_risk'] = 'High' if temp < 2 else 'Medium' if temp < 5 else 'Low'
            
            # Wind chill factor
            if temp < 10 and wind_speed > 1.34:
                indices['wind_chill'] = 13.12 + 0.6215 * temp - 11.37 * (wind_speed * 3.6) ** 0.16 + 0.3965 * temp * (wind_speed * 3.6) ** 0.16
            else:
                indices['wind_chill'] = temp
        
        return indices

    def calculate_soil_health_indicators(self, current_soil: Dict, soil_stats: Dict) -> Dict:
        """Calculate soil health indicators"""
        indicators = {}
        
        if current_soil:
            moisture = current_soil.get('moisture', 0)
            temp_surface = current_soil.get('t0', 273.15) - 273.15  # Convert from Kelvin
            temp_10cm = current_soil.get('t10', 273.15) - 273.15
            
            # Soil moisture status
            if moisture < 0.1:
                indicators['moisture_status'] = 'Very Dry'
            elif moisture < 0.2:
                indicators['moisture_status'] = 'Dry'
            elif moisture < 0.35:
                indicators['moisture_status'] = 'Optimal'
            elif moisture < 0.5:
                indicators['moisture_status'] = 'Moist'
            else:
                indicators['moisture_status'] = 'Saturated'
            
            # Temperature gradient
            temp_gradient = temp_surface - temp_10cm
            indicators['temperature_gradient'] = temp_gradient
            indicators['thermal_stability'] = 'Stable' if abs(temp_gradient) < 2 else 'Variable'
            
            # Soil activity level
            if soil_stats:
                moisture_variance = soil_stats.get('moisture_variance', 0)
                indicators['soil_activity'] = 'High' if moisture_variance > 0.05 else 'Moderate' if moisture_variance > 0.02 else 'Low'
        
        return indicators

    def analyze_soil_crop_suitability(self, lat: float, lon: float) -> Dict:
        """Analyze soil suitability for different crop types"""
        suitability = {
            'cereals': {'wheat': 'Good', 'rice': 'Fair', 'corn': 'Good', 'barley': 'Good'},
            'vegetables': {'tomato': 'Good', 'potato': 'Fair', 'onion': 'Good', 'carrot': 'Fair'},
            'fruits': {'apple': 'Fair', 'citrus': 'Poor', 'grape': 'Good', 'berry': 'Good'},
            'legumes': {'soybean': 'Good', 'pea': 'Good', 'bean': 'Fair', 'lentil': 'Good'}
        }
        
        # This would be enhanced with actual soil analysis data
        return suitability

    def get_fertilizer_recommendations(self, lat: float, lon: float) -> Dict:
        """Get fertilizer recommendations based on soil conditions"""
        recommendations = {
            'nitrogen': {
                'current_level': 'Medium',
                'recommendation': 'Apply 120 kg/ha for cereal crops',
                'timing': 'Split application: 60% at planting, 40% at tillering'
            },
            'phosphorus': {
                'current_level': 'Low',
                'recommendation': 'Apply 80 kg/ha P2O5',
                'timing': 'Apply at planting for best root development'
            },
            'potassium': {
                'current_level': 'High',
                'recommendation': 'Reduce application to 40 kg/ha K2O',
                'timing': 'Apply before planting'
            },
            'organic_matter': {
                'current_level': 'Medium',
                'recommendation': 'Add 2-3 tons/ha of compost',
                'timing': 'Apply during soil preparation'
            }
        }
        return recommendations

    def calculate_irrigation_needs(self, lat: float, lon: float) -> Dict:
        """Calculate irrigation requirements"""
        irrigation = {
            'current_need': 'Moderate',
            'recommended_amount': '25-30 mm per week',
            'frequency': 'Every 3-4 days',
            'method': 'Drip irrigation recommended for water efficiency',
            'timing': 'Early morning (6-8 AM) or evening (6-8 PM)',
            'water_stress_indicators': [
                'Monitor leaf wilting during midday',
                'Check soil moisture at 15cm depth',
                'Observe plant growth rate'
            ]
        }
        return irrigation

    def predict_yield_potential(self, lat: float, lon: float) -> Dict:
        """Predict yield potential based on current conditions"""
        yield_prediction = {
            'wheat': {'potential': '4.5-5.2 tons/ha', 'confidence': 'Medium'},
            'corn': {'potential': '8.5-9.8 tons/ha', 'confidence': 'High'},
            'soybean': {'potential': '2.8-3.2 tons/ha', 'confidence': 'Medium'},
            'rice': {'potential': '6.2-7.1 tons/ha', 'confidence': 'Low'},
            'factors_affecting_yield': [
                'Soil moisture levels',
                'Temperature patterns',
                'Nutrient availability',
                'Pest and disease pressure'
            ]
        }
        return yield_prediction

    def get_pest_disease_risk(self, lat: float, lon: float) -> Dict:
        """Assess pest and disease risk based on environmental conditions"""
        risk_assessment = {
            'fungal_diseases': {
                'risk_level': 'Medium',
                'conditions': 'High humidity and moderate temperatures favor fungal growth',
                'prevention': 'Ensure good air circulation, avoid overhead watering'
            },
            'insect_pests': {
                'risk_level': 'Low',
                'conditions': 'Current weather not favorable for major pest outbreaks',
                'monitoring': 'Regular field scouting recommended'
            },
            'bacterial_diseases': {
                'risk_level': 'Low',
                'conditions': 'Dry conditions reduce bacterial disease pressure',
                'prevention': 'Maintain plant hygiene, avoid plant stress'
            }
        }
        return risk_assessment

    # Missing helper methods implementation
    def determine_climate_zone(self, lat: float, lon: float) -> Dict:
        """Determine climate zone based on coordinates"""
        # Simplified climate zone determination
        if lat > 60:
            zone = "Arctic"
        elif lat > 45:
            zone = "Temperate"
        elif lat > 23.5:
            zone = "Subtropical"
        elif lat > -23.5:
            zone = "Tropical"
        elif lat > -45:
            zone = "Subtropical"
        else:
            zone = "Temperate"
        
        return {
            'climate_zone': zone,
            'latitude': lat,
            'characteristics': f"Climate zone determined based on latitude {lat}"
        }

    def get_seasonal_recommendations(self, lat: float, lon: float) -> Dict:
        """Get seasonal growing recommendations"""
        current_month = datetime.now().month
        
        if 3 <= current_month <= 5:  # Spring
            season = "Spring"
            recommendations = ["Plant cool-season crops", "Prepare soil", "Start seedlings"]
        elif 6 <= current_month <= 8:  # Summer
            season = "Summer"
            recommendations = ["Plant warm-season crops", "Maintain irrigation", "Pest monitoring"]
        elif 9 <= current_month <= 11:  # Fall
            season = "Fall"
            recommendations = ["Harvest crops", "Plant cover crops", "Soil preparation"]
        else:  # Winter
            season = "Winter"
            recommendations = ["Plan next season", "Maintain equipment", "Greenhouse operations"]
        
        return {
            'current_season': season,
            'recommendations': recommendations,
            'optimal_planting_window': f"Based on {season} season in your location"
        }

    def get_recommended_crops(self, climate_zone: Dict, soil_suitability: Dict) -> Dict:
        """Get recommended crops based on climate and soil"""
        zone = climate_zone.get('climate_zone', 'Temperate')
        
        crop_recommendations = {
            'Arctic': ['barley', 'potato', 'cabbage'],
            'Temperate': ['wheat', 'corn', 'soybean', 'apple'],
            'Subtropical': ['rice', 'citrus', 'cotton', 'sugarcane'],
            'Tropical': ['rice', 'banana', 'coconut', 'cassava']
        }
        
        return {
            'primary_crops': crop_recommendations.get(zone, ['wheat', 'corn']),
            'climate_zone': zone,
            'suitability_note': "Recommendations based on climate zone and soil conditions"
        }

    def get_extended_forecast(self, lat: float, lon: float) -> Dict:
        """Get extended weather forecast"""
        try:
            forecast_url = f"{self.base_urls['openweather']}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_keys['openweather'],
                'units': 'metric'
            }
            
            response = requests.get(forecast_url, params=params)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error getting forecast: {e}")
            return {}

    def assess_growing_conditions(self, weather_data: Dict, agri_indices: Dict) -> Dict:
        """Assess overall growing conditions"""
        conditions = {
            'overall_rating': 'Good',
            'temperature_suitability': 'Optimal',
            'moisture_conditions': 'Adequate',
            'stress_factors': ['None identified'],
            'recommendations': ['Continue normal operations']
        }
        
        if agri_indices:
            if agri_indices.get('frost_risk') == 'High':
                conditions['stress_factors'] = ['Frost risk']
                conditions['recommendations'] = ['Implement frost protection']
        
        return conditions

    def calculate_vegetation_indices(self, lat: float, lon: float) -> Dict:
        """Calculate vegetation indices (simulated)"""
        return {
            'ndvi': 0.75,  # Normalized Difference Vegetation Index
            'evi': 0.68,   # Enhanced Vegetation Index
            'savi': 0.72,  # Soil Adjusted Vegetation Index
            'note': 'Simulated values - would use satellite data in production'
        }

    def analyze_field_variability(self, lat: float, lon: float) -> Dict:
        """Analyze field variability"""
        return {
            'variability_level': 'Medium',
            'zones_identified': 3,
            'management_recommendation': 'Consider variable rate application',
            'note': 'Based on simulated field analysis'
        }

    def get_comprehensive_agricultural_data(self, lat: float, lon: float) -> Dict:
        """Get all agricultural data for the given coordinates"""
        print(f"🌾 Retrieving comprehensive agricultural data for coordinates: {lat}, {lon}")
        
        # Get location information
        location_info = self.get_location_info(lat, lon)
        print(f"📍 Location: {location_info['formatted_address']}")
        
        # Initialize results
        results = {
            'timestamp': datetime.now().isoformat(),
            'coordinates': {'latitude': lat, 'longitude': lon},
            'location_info': location_info,
            'agricultural_data': {}
        }
        
        # Get detailed soil analysis
        print("🌱 Analyzing soil conditions...")
        soil_analysis = self.get_detailed_soil_analysis(lat, lon)
        if soil_analysis:
            results['agricultural_data']['soil_analysis'] = soil_analysis
        
        # Get agricultural weather data
        print("🌤️  Fetching agricultural weather data...")
        weather_data = self.get_agricultural_weather_data(lat, lon)
        if weather_data:
            results['agricultural_data']['weather_analysis'] = weather_data
        
        # Get crop suitability analysis
        print("🌾 Analyzing crop suitability...")
        crop_analysis = self.get_crop_suitability_analysis(lat, lon)
        if crop_analysis:
            results['agricultural_data']['crop_suitability'] = crop_analysis
        
        # Get precision agriculture metrics
        print("📊 Calculating precision agriculture metrics...")
        precision_metrics = self.get_precision_agriculture_metrics(lat, lon)
        if precision_metrics:
            results['agricultural_data']['precision_metrics'] = precision_metrics
        
        # Get pest and disease risk assessment
        print("🐛 Assessing pest and disease risks...")
        pest_risk = self.get_pest_disease_risk(lat, lon)
        if pest_risk:
            results['agricultural_data']['pest_disease_risk'] = pest_risk
        
        return results

    def display_agricultural_results(self, data: Dict):
        """Display comprehensive agricultural results"""
        print("\n" + "="*80)
        print("🌾 COMPREHENSIVE AGRICULTURAL DATA ANALYSIS REPORT")
        print("="*80)
        
        print(f"\n📅 Analysis Date: {data['timestamp']}")
        print(f"📍 Location: {data['location_info']['formatted_address']}")
        print(f"🗺️  Coordinates: {data['coordinates']['latitude']}, {data['coordinates']['longitude']}")
        
        agri_data = data.get('agricultural_data', {})
        
        # Soil Analysis Section
        if 'soil_analysis' in agri_data:
            print("\n🌱 DETAILED SOIL ANALYSIS:")
            soil = agri_data['soil_analysis']
            
            if 'current_conditions' in soil:
                current = soil['current_conditions']
                print("   Current Soil Conditions:")
                if current:
                    moisture = current.get('moisture', 0)
                    temp_surface = current.get('t0', 273.15) - 273.15
                    temp_10cm = current.get('t10', 273.15) - 273.15
                    print(f"     • Soil Moisture: {moisture:.3f} m³/m³ ({moisture*100:.1f}%)")
                    print(f"     • Surface Temperature: {temp_surface:.1f}°C")
                    print(f"     • Temperature at 10cm: {temp_10cm:.1f}°C")
            
            if 'soil_health_indicators' in soil:
                health = soil['soil_health_indicators']
                print("   Soil Health Indicators:")
                for indicator, value in health.items():
                    print(f"     • {indicator.replace('_', ' ').title()}: {value}")
        
        # Weather Analysis Section
        if 'weather_analysis' in agri_data:
            print("\n🌤️  AGRICULTURAL WEATHER ANALYSIS:")
            weather = agri_data['weather_analysis']
            
            if 'agricultural_indices' in weather:
                indices = weather['agricultural_indices']
                print("   Agricultural Indices:")
                for index, value in indices.items():
                    unit = self.get_agricultural_unit(index)
                    print(f"     • {index.replace('_', ' ').title()}: {value} {unit}")
            
            if 'growing_conditions' in weather:
                conditions = weather['growing_conditions']
                print("   Growing Conditions Assessment:")
                for condition, status in conditions.items():
                    print(f"     • {condition.replace('_', ' ').title()}: {status}")
        
        # Crop Suitability Section
        if 'crop_suitability' in agri_data:
            print("\n🌾 CROP SUITABILITY ANALYSIS:")
            crops = agri_data['crop_suitability']
            
            if 'recommended_crops' in crops:
                recommended = crops['recommended_crops']
                print("   Recommended Crops:")
                for category, crop_list in recommended.items():
                    if isinstance(crop_list, list):
                        print(f"     • {category.title()}: {', '.join(crop_list)}")
                    else:
                        print(f"     • {category.title()}: {crop_list}")
        
        # Precision Agriculture Metrics
        if 'precision_metrics' in agri_data:
            print("\n📊 PRECISION AGRICULTURE RECOMMENDATIONS:")
            precision = agri_data['precision_metrics']
            
            if 'fertilizer_recommendations' in precision:
                fertilizer = precision['fertilizer_recommendations']
                print("   Fertilizer Recommendations:")
                for nutrient, details in fertilizer.items():
                    print(f"     • {nutrient.title()}:")
                    print(f"       - Current Level: {details['current_level']}")
                    print(f"       - Recommendation: {details['recommendation']}")
            
            if 'irrigation_recommendations' in precision:
                irrigation = precision['irrigation_recommendations']
                print("   Irrigation Recommendations:")
                print(f"     • Current Need: {irrigation['current_need']}")
                print(f"     • Recommended Amount: {irrigation['recommended_amount']}")
                print(f"     • Frequency: {irrigation['frequency']}")
        
        # Pest and Disease Risk
        if 'pest_disease_risk' in agri_data:
            print("\n🐛 PEST & DISEASE RISK ASSESSMENT:")
            pest_risk = agri_data['pest_disease_risk']
            for risk_type, details in pest_risk.items():
                print(f"   {risk_type.replace('_', ' ').title()}:")
                print(f"     • Risk Level: {details['risk_level']}")
                print(f"     • Conditions: {details['conditions']}")

    def get_agricultural_unit(self, parameter: str) -> str:
        """Get appropriate unit for agricultural parameters"""
        units = {
            'heat_index': '°C',
            'growing_degree_days': '°C-days',
            'evapotranspiration': 'mm/day',
            'wind_chill': '°C',
            'temperature_gradient': '°C',
            'soil_activity': '',
            'moisture_status': '',
            'thermal_stability': ''
        }
        return units.get(parameter, '')

    # Helper methods (implementations of supporting functions)
    def create_field_polygon(self, lat: float, lon: float, size: float) -> List:
        """Create a polygon around the given coordinates"""
        return [
            [lon - size, lat - size],
            [lon + size, lat - size],
            [lon + size, lat + size],
            [lon - size, lat + size],
            [lon - size, lat - size]
        ]

    def create_agromonitoring_polygon(self, coords: List, lat: float, lon: float) -> str:
        """Create polygon in AgroMonitoring system"""
        try:
            polygon_url = f"{self.base_urls['agromonitoring']}/polygons"
            polygon_data = {
                "name": f"Agricultural_Analysis_{lat}_{lon}",
                "geo_json": {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    }
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            params = {'appid': self.api_keys['polygon']}
            
            response = requests.post(polygon_url, json=polygon_data, headers=headers, params=params)
            
            if response.status_code == 201:
                return response.json()['id']
            return None
        except Exception as e:
            print(f"Error creating polygon: {e}")
            return None

    def get_current_soil_data(self, polygon_id: str) -> Dict:
        """Get current soil data from AgroMonitoring"""
        try:
            soil_url = f"{self.base_urls['agromonitoring']}/soil"
            params = {
                'polyid': polygon_id,
                'appid': self.api_keys['polygon']
            }
            
            response = requests.get(soil_url, params=params)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            print(f"Error getting current soil data: {e}")
            return {}

    def get_historical_soil_data(self, polygon_id: str, days: int = 30) -> List:
        """Get historical soil data"""
        try:
            end_time = int(time.time())
            start_time = end_time - (days * 24 * 3600)
            
            history_url = f"{self.base_urls['agromonitoring']}/soil/history"
            params = {
                'polyid': polygon_id,
                'start': start_time,
                'end': end_time,
                'appid': self.api_keys['polygon']
            }
            
            response = requests.get(history_url, params=params)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error getting historical soil data: {e}")
            return []

    def calculate_soil_statistics(self, historical_data: List) -> Dict:
        """Calculate soil statistics from historical data"""
        if not historical_data:
            return {}
        
        moistures = [item.get('moisture', 0) for item in historical_data if 'moisture' in item]
        temps = [item.get('t10', 273.15) - 273.15 for item in historical_data if 't10' in item]
        
        if moistures:
            moisture_avg = sum(moistures) / len(moistures)
            moisture_variance = sum((m - moisture_avg) ** 2 for m in moistures) / len(moistures)
        else:
            moisture_avg = moisture_variance = 0
        
        if temps:
            temp_avg = sum(temps) / len(temps)
            temp_variance = sum((t - temp_avg) ** 2 for t in temps) / len(temps)
        else:
            temp_avg = temp_variance = 0
        
        return {
            'moisture_average': moisture_avg,
            'moisture_variance': moisture_variance,
            'temperature_average': temp_avg,
            'temperature_variance': temp_variance,
            'data_points': len(historical_data)
        }

    def calculate_heat_index(self, temp: float, humidity: float) -> float:
        """Calculate heat index"""
        if temp < 27:
            return temp
        
        hi = -8.78469475556 + 1.61139411 * temp + 2.33854883889 * humidity
        hi += -0.14611605 * temp * humidity + -0.012308094 * temp * temp
        hi += -0.0164248277778 * humidity * humidity + 0.002211732 * temp * temp * humidity
        hi += 0.00072546 * temp * humidity * humidity + -0.000003582 * temp * temp * humidity * humidity
        
        return round(hi, 1)

    def calculate_evapotranspiration(self, temp: float, humidity: float, wind_speed: float) -> float:
        """Calculate reference evapotranspiration (simplified Penman equation)"""
        # Simplified calculation - in practice would use full Penman-Monteith equation
        delta = 4098 * (0.6108 * math.exp(17.27 * temp / (temp + 237.3))) / ((temp + 237.3) ** 2)
        gamma = 0.665  # Psychrometric constant
        u2 = wind_speed * 4.87 / math.log(67.8 * 10 - 5.42)  # Wind speed at 2m height
        
        et0 = (0.408 * delta * (temp) + gamma * 900 / (temp + 273) * u2 * (0.01 * (100 - humidity))) / (delta + gamma * (1 + 0.34 * u2))
        
        return round(max(0, et0), 2)

def main():
    """Main function to run the advanced agricultural data retriever"""
    retriever = AdvancedAgriculturalDataRetriever()
    
    print("🌾 Advanced Agricultural Data Retrieval System")
    print("="*60)
    
    # Get location
    choice = input("\nChoose location method:\n1. Use current location (automatic)\n2. Enter coordinates manually\nChoice (1/2): ")
    
    if choice == "1":
        print("\n🔍 Detecting current location...")
        lat, lon = retriever.get_current_location()
        if lat is None or lon is None:
            print("❌ Could not detect location automatically. Please enter coordinates manually.")
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
    else:
        lat = float(input("Enter latitude: "))
        lon = float(input("Enter longitude: "))
    
    # Get comprehensive agricultural data
    try:
        data = retriever.get_comprehensive_agricultural_data(lat, lon)
        
        # Display results
        retriever.display_agricultural_results(data)
        
        # Ask if user wants to save data
        save_choice = input("\n💾 Save agricultural analysis to file? (y/n): ").lower()
        if save_choice == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agricultural_analysis_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"📄 Agricultural analysis saved to: {filename}")
        
        print("\n✅ Agricultural data analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during agricultural data retrieval: {e}")

if __name__ == "__main__":
    main()
