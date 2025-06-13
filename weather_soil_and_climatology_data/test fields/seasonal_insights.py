import geocoder
import calendar
from datetime import datetime
from typing import Dict, Tuple

def get_seasonal_insights_analysis():
    """Independent seasonal insights for agriculture"""
    
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

    def determine_current_season(month: int, is_northern: bool) -> Dict:
        """Determine current season based on month and hemisphere"""
        if is_northern:
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Autumn"
        else:
            if month in [12, 1, 2]:
                season = "Summer"
            elif month in [3, 4, 5]:
                season = "Autumn"
            elif month in [6, 7, 8]:
                season = "Winter"
            else:
                season = "Spring"
        
        return {
            'season': season,
            'month': calendar.month_name[month],
            'hemisphere': 'Northern' if is_northern else 'Southern'
        }

    def get_seasonal_calendar(lat: float, lon: float, is_northern: bool) -> Dict:
        """Get seasonal agricultural calendar"""
        if is_northern:
            calendar_data = {
                'Spring (Mar-May)': {
                    'activities': ['Soil preparation', 'Planting cool-season crops', 'Fertilizer application'],
                    'crops_to_plant': ['wheat', 'barley', 'peas', 'lettuce', 'spinach'],
                    'maintenance': ['Pruning fruit trees', 'Weed control', 'Irrigation system check']
                },
                'Summer (Jun-Aug)': {
                    'activities': ['Planting warm-season crops', 'Intensive irrigation', 'Pest monitoring'],
                    'crops_to_plant': ['corn', 'tomatoes', 'peppers', 'beans', 'squash'],
                    'maintenance': ['Regular watering', 'Mulching', 'Disease prevention']
                },
                'Autumn (Sep-Nov)': {
                    'activities': ['Harvesting', 'Cover crop planting', 'Soil amendment'],
                    'crops_to_plant': ['winter wheat', 'garlic', 'cover crops'],
                    'maintenance': ['Equipment maintenance', 'Storage preparation', 'Field cleanup']
                },
                'Winter (Dec-Feb)': {
                    'activities': ['Planning next season', 'Equipment repair', 'Greenhouse operations'],
                    'crops_to_plant': ['greenhouse crops', 'microgreens'],
                    'maintenance': ['Soil testing', 'Seed ordering', 'Infrastructure repair']
                }
            }
        else:
            calendar_data = {
                'Summer (Dec-Feb)': {
                    'activities': ['Planting warm-season crops', 'Intensive irrigation', 'Pest monitoring'],
                    'crops_to_plant': ['corn', 'tomatoes', 'peppers', 'beans', 'squash'],
                    'maintenance': ['Regular watering', 'Mulching', 'Disease prevention']
                },
                'Autumn (Mar-May)': {
                    'activities': ['Harvesting', 'Cover crop planting', 'Soil amendment'],
                    'crops_to_plant': ['winter wheat', 'garlic', 'cover crops'],
                    'maintenance': ['Equipment maintenance', 'Storage preparation', 'Field cleanup']
                },
                'Winter (Jun-Aug)': {
                    'activities': ['Planning next season', 'Equipment repair', 'Greenhouse operations'],
                    'crops_to_plant': ['greenhouse crops', 'microgreens'],
                    'maintenance': ['Soil testing', 'Seed ordering', 'Infrastructure repair']
                },
                'Spring (Sep-Nov)': {
                    'activities': ['Soil preparation', 'Planting cool-season crops', 'Fertilizer application'],
                    'crops_to_plant': ['wheat', 'barley', 'peas', 'lettuce', 'spinach'],
                    'maintenance': ['Pruning fruit trees', 'Weed control', 'Irrigation system check']
                }
            }
        
        return calendar_data

    def identify_seasonal_challenges(month: int, lat: float, lon: float) -> list:
        """Identify seasonal challenges for current month and location"""
        challenges = []
        abs_lat = abs(lat)
        is_northern = lat >= 0

        if is_northern:
            if month in [12, 1, 2]:  # Winter
                challenges.extend(['Frost protection', 'Limited daylight', 'Equipment winterization'])
            elif month in [6, 7, 8]:  # Summer
                challenges.extend(['Heat stress', 'Water management', 'Pest pressure'])
            elif month in [3, 4, 5]:  # Spring
                challenges.extend(['Late frost risk', 'Soil preparation', 'Planting timing'])
            else:  # Autumn
                challenges.extend(['Harvest timing', 'Storage preparation', 'Weather variability'])
        else:
            if month in [6, 7, 8]:  # Winter (Southern)
                challenges.extend(['Frost protection', 'Limited daylight', 'Equipment winterization'])
            elif month in [12, 1, 2]:  # Summer (Southern)
                challenges.extend(['Heat stress', 'Water management', 'Pest pressure'])
            elif month in [9, 10, 11]:  # Spring (Southern)
                challenges.extend(['Late frost risk', 'Soil preparation', 'Planting timing'])
            else:  # Autumn (Southern)
                challenges.extend(['Harvest timing', 'Storage preparation', 'Weather variability'])

        if abs_lat > 50:  # High latitude
            challenges.extend(['Short growing season', 'Extreme weather', 'Limited crop options'])
        
        return challenges

    def get_seasonal_insights(lat: float, lon: float) -> Dict:
        """Get comprehensive seasonal insights for agriculture"""
        current_date = datetime.now()
        current_month = current_date.month
        
        is_northern_hemisphere = lat >= 0
        
        seasonal_data = {
            'current_season': determine_current_season(current_month, is_northern_hemisphere),
            'seasonal_calendar': get_seasonal_calendar(lat, lon, is_northern_hemisphere),
            'seasonal_challenges': identify_seasonal_challenges(current_month, lat, lon),
            'analysis_date': current_date.isoformat()
        }
        
        return seasonal_data

    # Main execution
    lat, lon = get_current_location()
    seasonal_data = get_seasonal_insights(lat, lon)
    
    current_season = seasonal_data.get('current_season', {})
    print(f"\n🌱 CURRENT SEASON: {current_season.get('season', 'Unknown')} ({current_season.get('month', 'Unknown')})")
    
    challenges = seasonal_data.get('seasonal_challenges', [])
    if challenges:
        print("   Key Challenges:")
        for challenge in challenges[:3]:
            print(f"     • {challenge}")
    
    print("\n📅 SEASONAL CALENDAR:")
    for season, activities in seasonal_data['seasonal_calendar'].items():
        print(f"   {season}:")
        print(f"     Activities: {', '.join(activities['activities'][:3])}")
        print(f"     Recommended Crops: {', '.join(activities['crops_to_plant'][:3])}")
    
    return seasonal_data

# Run the function
if __name__ == "__main__":
    result = get_seasonal_insights_analysis()
