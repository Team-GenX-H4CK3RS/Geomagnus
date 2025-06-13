import requests
import geocoder
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

def get_weather_risk_assessment():
    """Complete weather risk assessment with agricultural impact analysis"""
    
    def get_current_location() -> Tuple[float, float]:
        """Get current location using IP geolocation"""
        try:
            g = geocoder.ip('me')
            if g.ok:
                return 12.9915, 80.2337
            else:
                return 28.6139, 77.2090
        except Exception as e:
            print(f"Error getting current location: {e}")
            return 28.6139, 77.2090

    def assess_weather_risks(current: Dict, forecast: List[Dict]) -> Dict:
        """Assess weather-related risks for agriculture"""
        risks = {
            'immediate_risks': [],
            'short_term_risks': [],
            'long_term_risks': [],
            'risk_level': 'low'
        }
        
        if not current:
            return risks
        
        temp = current.get('temperature', 0)
        humidity = current.get('humidity', 0)
        wind_speed = current.get('wind_speed', 0)
        
        # Immediate risks (next 24 hours)
        if temp < 2:
            risks['immediate_risks'].append("Frost damage risk - protect sensitive crops")
            risks['risk_level'] = 'high'
        elif temp > 40:
            risks['immediate_risks'].append("Heat stress risk - increase irrigation")
            risks['risk_level'] = 'high'
        
        if humidity > 90:
            risks['immediate_risks'].append("Disease pressure risk - improve ventilation")
            if risks['risk_level'] == 'low':
                risks['risk_level'] = 'medium'
        
        if wind_speed > 20:
            risks['immediate_risks'].append("Wind damage risk - secure structures")
            if risks['risk_level'] == 'low':
                risks['risk_level'] = 'medium'
        
        # Short-term risks (next 7 days)
        if forecast:
            total_precipitation = sum(item.get('precipitation', 0) for item in forecast[:24])
            avg_temp = sum(item.get('temperature', 0) for item in forecast[:24]) / len(forecast[:24])
            
            if total_precipitation > 50:
                risks['short_term_risks'].append("Waterlogging risk - ensure drainage")
                if risks['risk_level'] != 'high':
                    risks['risk_level'] = 'medium'
            elif total_precipitation < 5:
                risks['short_term_risks'].append("Drought stress risk - plan irrigation")
            
            if avg_temp > 35:
                risks['short_term_risks'].append("Extended heat stress - cooling measures needed")
        
        # Long-term risks (seasonal outlook)
        current_month = datetime.now().month
        if current_month in [6, 7, 8]:  # Summer months
            risks['long_term_risks'].extend([
                "Pest population buildup during warm season",
                "Water resource depletion risk",
                "Heat stress on perennial crops"
            ])
        elif current_month in [12, 1, 2]:  # Winter months
            risks['long_term_risks'].extend([
                "Frost damage to winter crops",
                "Reduced growth rates",
                "Equipment winterization needs"
            ])
        
        return risks

    def get_weather_adaptation_strategies(risks: Dict) -> Dict:
        """Get adaptation strategies for weather risks"""
        strategies = {
            'immediate_actions': [],
            'short_term_planning': [],
            'long_term_adaptation': [],
            'infrastructure_needs': []
        }
        
        # Immediate actions based on current risks
        for risk in risks.get('immediate_risks', []):
            if 'frost' in risk.lower():
                strategies['immediate_actions'].extend([
                    "Deploy frost protection covers",
                    "Use water sprinklers for frost protection",
                    "Harvest sensitive crops early"
                ])
            elif 'heat' in risk.lower():
                strategies['immediate_actions'].extend([
                    "Increase irrigation frequency",
                    "Apply shade cloth to sensitive crops",
                    "Schedule field work for cooler hours"
                ])
            elif 'disease' in risk.lower():
                strategies['immediate_actions'].extend([
                    "Improve field ventilation",
                    "Apply preventive fungicides",
                    "Remove infected plant material"
                ])
            elif 'wind' in risk.lower():
                strategies['immediate_actions'].extend([
                    "Secure greenhouse structures",
                    "Install windbreaks",
                    "Stake tall plants"
                ])
        
        # Short-term planning
        for risk in risks.get('short_term_risks', []):
            if 'waterlogging' in risk.lower():
                strategies['short_term_planning'].extend([
                    "Install drainage systems",
                    "Create raised beds",
                    "Plan crop rotation with water-tolerant varieties"
                ])
            elif 'drought' in risk.lower():
                strategies['short_term_planning'].extend([
                    "Install drip irrigation",
                    "Apply mulching",
                    "Select drought-resistant varieties"
                ])
        
        # Long-term adaptation
        strategies['long_term_adaptation'] = [
            "Climate-resilient crop variety selection",
            "Diversified cropping systems",
            "Water conservation infrastructure",
            "Integrated pest management systems",
            "Soil health improvement programs",
            "Weather monitoring technology adoption"
        ]
        
        # Infrastructure needs
        strategies['infrastructure_needs'] = [
            "Weather monitoring stations",
            "Irrigation and drainage systems",
            "Protected cultivation structures",
            "Storage and processing facilities",
            "Emergency response equipment",
            "Renewable energy systems"
        ]
        
        return strategies

    def get_crop_specific_weather_guidance(lat: float, lon: float) -> Dict:
        """Get crop-specific weather guidance"""
        crop_weather_guidance = {
            'wheat': {
                'temperature_requirements': '15-25°C optimal',
                'water_needs': '450-600mm total',
                'critical_periods': ['Flowering', 'Grain filling'],
                'weather_risks': ['Frost during flowering', 'Heat during grain filling', 'Excessive rain at harvest'],
                'adaptation_measures': ['Frost-resistant varieties', 'Timely planting', 'Proper drainage']
            },
            'rice': {
                'temperature_requirements': '20-35°C optimal',
                'water_needs': '1200-1500mm total',
                'critical_periods': ['Transplanting', 'Flowering', 'Grain filling'],
                'weather_risks': ['Drought during critical periods', 'Cyclones', 'Temperature extremes'],
                'adaptation_measures': ['Water management', 'Storm-resistant varieties', 'Alternate wetting and drying']
            },
            'corn': {
                'temperature_requirements': '18-30°C optimal',
                'water_needs': '500-700mm total',
                'critical_periods': ['Silking', 'Grain filling'],
                'weather_risks': ['Drought stress', 'Hail damage', 'Wind lodging'],
                'adaptation_measures': ['Drought-tolerant hybrids', 'Proper plant density', 'Windbreaks']
            },
            'tomato': {
                'temperature_requirements': '18-26°C optimal',
                'water_needs': '400-600mm total',
                'critical_periods': ['Flowering', 'Fruit development'],
                'weather_risks': ['Temperature extremes', 'Humidity-related diseases', 'Wind damage'],
                'adaptation_measures': ['Protected cultivation', 'Disease-resistant varieties', 'Proper spacing']
            },
            'potato': {
                'temperature_requirements': '15-20°C optimal',
                'water_needs': '400-500mm total',
                'critical_periods': ['Tuber initiation', 'Tuber bulking'],
                'weather_risks': ['Late blight in humid conditions', 'Heat stress', 'Frost damage'],
                'adaptation_measures': ['Disease management', 'Hilling practices', 'Variety selection']
            }
        }
        
        # Add location-specific adjustments
        abs_lat = abs(lat)
        if abs_lat < 23.5:  # Tropical
            for crop in crop_weather_guidance:
                crop_weather_guidance[crop]['location_notes'] = 'Tropical climate - manage heat and humidity'
        elif abs_lat < 40:  # Subtropical
            for crop in crop_weather_guidance:
                crop_weather_guidance[crop]['location_notes'] = 'Subtropical climate - seasonal variation management'
        else:  # Temperate
            for crop in crop_weather_guidance:
                crop_weather_guidance[crop]['location_notes'] = 'Temperate climate - frost and season length considerations'
        
        return crop_weather_guidance

    def get_weather_monitoring_recommendations() -> Dict:
        """Get weather monitoring and early warning recommendations"""
        return {
            'essential_parameters': {
                'temperature': {
                    'measurement': 'Daily min/max temperatures',
                    'importance': 'Critical for crop development timing',
                    'equipment': 'Digital thermometer with data logger',
                    'cost': '₹2,000-5,000'
                },
                'rainfall': {
                    'measurement': 'Daily precipitation amounts',
                    'importance': 'Water management and disease prediction',
                    'equipment': 'Rain gauge or automatic weather station',
                    'cost': '₹1,000-10,000'
                },
                'humidity': {
                    'measurement': 'Relative humidity levels',
                    'importance': 'Disease risk assessment',
                    'equipment': 'Hygrometer or weather station',
                    'cost': '₹1,500-3,000'
                },
                'wind': {
                    'measurement': 'Wind speed and direction',
                    'importance': 'Spraying conditions and structural damage risk',
                    'equipment': 'Anemometer',
                    'cost': '₹3,000-8,000'
                },
                'soil_temperature': {
                    'measurement': 'Soil temperature at various depths',
                    'importance': 'Planting timing and root development',
                    'equipment': 'Soil thermometer',
                    'cost': '₹1,000-2,500'
                }
            },
            'monitoring_frequency': {
                'critical_periods': 'Hourly during extreme weather',
                'growing_season': 'Daily readings',
                'off_season': 'Weekly monitoring sufficient'
            },
            'early_warning_systems': {
                'weather_apps': ['IMD Weather', 'AccuWeather', 'Weather Underground'],
                'government_services': ['IMD alerts', 'State agriculture department warnings'],
                'satellite_services': ['NASA POWER', 'ECMWF forecasts'],
                'local_networks': ['Farmer WhatsApp groups', 'Cooperative society alerts']
            },
            'decision_support_tools': {
                'disease_prediction_models': 'Use weather data to predict disease outbreaks',
                'irrigation_scheduling': 'Weather-based irrigation timing',
                'spray_timing': 'Wind and humidity considerations',
                'harvest_planning': 'Weather window identification'
            }
        }

    # Main execution
    lat, lon = get_current_location()
    
    # Get current weather data
    try:
        api_key = 'dff8a714e30a29e438b4bd2ebb11190f'
        current_url = f"https://api.openweathermap.org/data/2.5/weather"
        current_params = {'lat': lat, 'lon': lon, 'appid': api_key, 'units': 'metric'}
        current_response = requests.get(current_url, params=current_params)
        
        current_weather = {}
        forecast_data = []
        
        if current_response.status_code == 200:
            current_data = current_response.json()
            current_weather = {
                'temperature': current_data['main']['temp'],
                'humidity': current_data['main']['humidity'],
                'wind_speed': current_data['wind']['speed'],
                'description': current_data['weather'][0]['description']
            }
        
        # Get forecast data
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {'lat': lat, 'lon': lon, 'appid': api_key, 'units': 'metric'}
        forecast_response = requests.get(forecast_url, params=forecast_params)
        
        if forecast_response.status_code == 200:
            forecast_json = forecast_response.json()
            for item in forecast_json['list'][:24]:  # Next 3 days
                forecast_data.append({
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'precipitation': item.get('rain', {}).get('3h', 0)
                })
    
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        current_weather = {}
        forecast_data = []
    
    # Perform risk assessment
    weather_risks = assess_weather_risks(current_weather, forecast_data)
    adaptation_strategies = get_weather_adaptation_strategies(weather_risks)
    crop_guidance = get_crop_specific_weather_guidance(lat, lon)
    monitoring_recommendations = get_weather_monitoring_recommendations()
    
    print(f"\n🌦️ WEATHER RISK ASSESSMENT for location {lat:.4f}, {lon:.4f}:")
    print(f"   Overall Risk Level: {weather_risks['risk_level'].upper()}")
    
    if weather_risks['immediate_risks']:
        print("   Immediate Risks:")
        for risk in weather_risks['immediate_risks'][:3]:
            print(f"     ⚠️ {risk}")
    
    if adaptation_strategies['immediate_actions']:
        print("   Immediate Actions:")
        for action in adaptation_strategies['immediate_actions'][:3]:
            print(f"     🔧 {action}")
    
    print("\n📊 WEATHER MONITORING ESSENTIALS:")
    essentials = monitoring_recommendations['essential_parameters']
    for param, details in list(essentials.items())[:3]:
        print(f"   {param.title()}: {details['importance']} (₹{details['cost']})")
    
    return {
        'location': {'lat': lat, 'lon': lon},
        'current_weather': current_weather,
        'weather_risks': weather_risks,
        'adaptation_strategies': adaptation_strategies,
        'crop_guidance': crop_guidance,
        'monitoring_recommendations': monitoring_recommendations,
        'analysis_date': datetime.now().isoformat()
    }

# Run the function
if __name__ == "__main__":
    result = get_weather_risk_assessment()
    print("\n📋 Weather Risk Assessment Completed")