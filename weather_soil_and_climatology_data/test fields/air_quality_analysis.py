import requests
import geocoder
from typing import Dict, List, Tuple

def get_air_quality_analysis():
    """Independent air quality analysis with agricultural insights"""
    
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

    def get_air_quality_index(lat: float, lon: float) -> Dict:
        """Get comprehensive air quality data and agricultural insights"""
        try:
            api_key = 'dff8a714e30a29e438b4bd2ebb11190f'
            pollution_url = "https://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key
            }
            
            response = requests.get(pollution_url, params=params)
            air_quality_data = {}
            
            if response.status_code == 200:
                data = response.json()
                if 'list' in data and data['list']:
                    aqi_data = data['list'][0]
                    
                    aqi = aqi_data['main']['aqi']
                    components = aqi_data['components']
                    
                    aqi_categories = {
                        1: {'level': 'Good', 'color': 'Green', 'description': 'Air quality is considered satisfactory'},
                        2: {'level': 'Fair', 'color': 'Yellow', 'description': 'Air quality is acceptable'},
                        3: {'level': 'Moderate', 'color': 'Orange', 'description': 'Members of sensitive groups may experience health effects'},
                        4: {'level': 'Poor', 'color': 'Red', 'description': 'Everyone may begin to experience health effects'},
                        5: {'level': 'Very Poor', 'color': 'Purple', 'description': 'Health warnings of emergency conditions'}
                    }
                    
                    air_quality_data = {
                        'aqi_index': aqi,
                        'aqi_category': aqi_categories.get(aqi, {'level': 'Unknown', 'color': 'Gray', 'description': 'Unknown'}),
                        'pollutants': {
                            'co': {'value': components.get('co', 0), 'unit': 'μg/m³', 'name': 'Carbon Monoxide'},
                            'no': {'value': components.get('no', 0), 'unit': 'μg/m³', 'name': 'Nitrogen Monoxide'},
                            'no2': {'value': components.get('no2', 0), 'unit': 'μg/m³', 'name': 'Nitrogen Dioxide'},
                            'o3': {'value': components.get('o3', 0), 'unit': 'μg/m³', 'name': 'Ozone'},
                            'so2': {'value': components.get('so2', 0), 'unit': 'μg/m³', 'name': 'Sulfur Dioxide'},
                            'pm2_5': {'value': components.get('pm2_5', 0), 'unit': 'μg/m³', 'name': 'Fine Particulate Matter'},
                            'pm10': {'value': components.get('pm10', 0), 'unit': 'μg/m³', 'name': 'Coarse Particulate Matter'},
                            'nh3': {'value': components.get('nh3', 0), 'unit': 'μg/m³', 'name': 'Ammonia'}
                        },
                        'agricultural_impact': analyze_air_quality_agricultural_impact(aqi, components),
                        'recommendations': get_air_quality_agricultural_recommendations(aqi, components)
                    }
            
            return air_quality_data
        except Exception as e:
            print(f"Error getting air quality data: {e}")
            return {}

    def analyze_air_quality_agricultural_impact(aqi: int, components: Dict) -> Dict:
        """Analyze how air quality affects agricultural activities"""
        impact_analysis = {
            'crop_health_impact': 'Low',
            'photosynthesis_efficiency': 'Normal',
            'pest_disease_pressure': 'Normal',
            'irrigation_needs': 'Standard',
            'harvest_timing': 'No adjustment needed'
        }
        
        if aqi >= 4:
            impact_analysis.update({
                'crop_health_impact': 'High',
                'photosynthesis_efficiency': 'Reduced',
                'pest_disease_pressure': 'Increased',
                'irrigation_needs': 'Increased (dust removal)',
                'harvest_timing': 'Consider early morning harvesting'
            })
        elif aqi == 3:
            impact_analysis.update({
                'crop_health_impact': 'Moderate',
                'photosynthesis_efficiency': 'Slightly reduced',
                'pest_disease_pressure': 'Slightly increased',
                'irrigation_needs': 'Slightly increased',
                'harvest_timing': 'Monitor air quality trends'
            })
        
        pollutant_impacts = []
        
        if components.get('o3', 0) > 120:
            pollutant_impacts.append("High ozone levels may cause leaf damage and reduce crop yields")
        
        if components.get('so2', 0) > 20:
            pollutant_impacts.append("Elevated SO2 levels can cause leaf chlorosis and stunted growth")
        
        if components.get('pm2_5', 0) > 35:
            pollutant_impacts.append("High particulate matter can block sunlight and reduce photosynthesis")
        
        if components.get('no2', 0) > 40:
            pollutant_impacts.append("Elevated NO2 can affect plant metabolism and growth")
        
        impact_analysis['specific_pollutant_impacts'] = pollutant_impacts
        
        return impact_analysis

    def get_air_quality_agricultural_recommendations(aqi: int, components: Dict) -> List[str]:
        """Get agricultural recommendations based on air quality"""
        recommendations = []
        
        if aqi >= 4:
            recommendations.extend([
                "Increase irrigation frequency to wash pollutants off plant surfaces",
                "Consider protective measures for sensitive crops",
                "Monitor crop health more frequently",
                "Avoid field operations during peak pollution hours",
                "Consider air-purifying plants around field boundaries"
            ])
        elif aqi == 3:
            recommendations.extend([
                "Monitor sensitive crops for stress symptoms",
                "Maintain adequate soil moisture",
                "Consider timing field operations for better air quality periods"
            ])
        else:
            recommendations.append("Air quality is suitable for normal agricultural operations")
        
        if components.get('o3', 0) > 120:
            recommendations.append("Apply antioxidant foliar sprays to protect against ozone damage")
        
        if components.get('pm2_5', 0) > 35 or components.get('pm10', 0) > 50:
            recommendations.append("Increase leaf washing through sprinkler irrigation")
        
        return recommendations

    # Main execution
    lat, lon = get_current_location()
    air_quality_data = get_air_quality_index(lat, lon)
    
    if air_quality_data:
        aqi_cat = air_quality_data.get('aqi_category', {})
        print(f"\n🌬️ AIR QUALITY: {aqi_cat.get('level', 'Unknown')} (AQI: {air_quality_data.get('aqi_index', 'N/A')})")
        
        ag_impact = air_quality_data.get('agricultural_impact', {})
        if ag_impact:
            print(f"   Crop Health Impact: {ag_impact.get('crop_health_impact', 'Unknown')}")
            print("   Recommendations:")
            for rec in air_quality_data.get('recommendations', [])[:3]:
                print(f"     • {rec}")
    
    return air_quality_data

# Run the function
if __name__ == "__main__":
    result = get_air_quality_analysis()
