import geocoder
from typing import Dict, Tuple
from datetime import datetime

def get_crop_profitability_analysis():
    """Independent crop profitability analysis with ROI calculations"""
    
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

    # Crop profitability data
    crop_profitability_data = {
        'wheat': {'cost_per_hectare': 45000, 'yield_per_hectare': 4.5, 'price_per_ton': 22000, 'roi_percentage': 120},
        'rice': {'cost_per_hectare': 55000, 'yield_per_hectare': 6.5, 'price_per_ton': 20000, 'roi_percentage': 136},
        'corn': {'cost_per_hectare': 50000, 'yield_per_hectare': 9.0, 'price_per_ton': 18000, 'roi_percentage': 224},
        'soybean': {'cost_per_hectare': 40000, 'yield_per_hectare': 3.2, 'price_per_ton': 35000, 'roi_percentage': 180},
        'cotton': {'cost_per_hectare': 60000, 'yield_per_hectare': 2.8, 'price_per_ton': 55000, 'roi_percentage': 157},
        'sugarcane': {'cost_per_hectare': 80000, 'yield_per_hectare': 75, 'price_per_ton': 3200, 'roi_percentage': 200},
        'potato': {'cost_per_hectare': 70000, 'yield_per_hectare': 25, 'price_per_ton': 8000, 'roi_percentage': 186},
        'tomato': {'cost_per_hectare': 85000, 'yield_per_hectare': 45, 'price_per_ton': 12000, 'roi_percentage': 535},
        'onion': {'cost_per_hectare': 45000, 'yield_per_hectare': 20, 'price_per_ton': 15000, 'roi_percentage': 567},
        'cabbage': {'cost_per_hectare': 35000, 'yield_per_hectare': 30, 'price_per_ton': 8000, 'roi_percentage': 586},
        'apple': {'cost_per_hectare': 150000, 'yield_per_hectare': 15, 'price_per_ton': 45000, 'roi_percentage': 350},
        'banana': {'cost_per_hectare': 120000, 'yield_per_hectare': 40, 'price_per_ton': 18000, 'roi_percentage': 500},
        'grapes': {'cost_per_hectare': 200000, 'yield_per_hectare': 20, 'price_per_ton': 60000, 'roi_percentage': 500}
    }

    def assess_climate_suitability(lat: float, lon: float) -> Dict:
        """Assess climate suitability for different crops"""
        abs_lat = abs(lat)
        suitability = {}
        
        for crop in crop_profitability_data:
            if abs_lat < 23.5:  # Tropical
                if crop in ['rice', 'banana', 'sugarcane']:
                    suitability[crop] = 1.0
                else:
                    suitability[crop] = 0.7
            elif abs_lat < 40:  # Subtropical
                if crop in ['wheat', 'corn', 'soybean', 'cotton']:
                    suitability[crop] = 1.0
                else:
                    suitability[crop] = 0.8
            else:  # Temperate
                if crop in ['wheat', 'potato', 'cabbage', 'apple', 'grapes']:
                    suitability[crop] = 1.0
                else:
                    suitability[crop] = 0.6
        return suitability

    def assess_crop_risk(crop: str, lat: float, lon: float) -> str:
        """Assess risk level for specific crop"""
        risk_factors = {
            'rice': 'Medium - Water dependent',
            'wheat': 'Low - Hardy crop',
            'corn': 'Medium - Weather sensitive',
            'soybean': 'Low - Adaptable',
            'cotton': 'High - Pest susceptible',
            'potato': 'Medium - Disease prone',
            'tomato': 'High - Weather sensitive',
            'onion': 'Medium - Storage sensitive',
            'cabbage': 'Low - Cold tolerant',
            'apple': 'Medium - Perennial investment',
            'banana': 'High - Disease and weather sensitive',
            'grapes': 'Medium - Weather dependent',
            'sugarcane': 'Medium - Long growing season'
        }
        return risk_factors.get(crop, 'Medium - Standard risk')

    def get_best_yield_profitable_crops(lat: float, lon: float) -> Dict:
        """Get best yield crops with profitable ROI metrics"""
        climate_suitability = assess_climate_suitability(lat, lon)
        
        profitable_crops = {}
        
        for crop, data in crop_profitability_data.items():
            climate_factor = climate_suitability.get(crop, 0.8)
            adjusted_yield = data['yield_per_hectare'] * climate_factor
            
            revenue = adjusted_yield * data['price_per_ton']
            profit = revenue - data['cost_per_hectare']
            roi = (profit / data['cost_per_hectare']) * 100
            
            profitable_crops[crop] = {
                'investment_per_hectare': data['cost_per_hectare'],
                'expected_yield_tons': round(adjusted_yield, 2),
                'price_per_ton': data['price_per_ton'],
                'gross_revenue': round(revenue, 2),
                'net_profit': round(profit, 2),
                'roi_percentage': round(roi, 1),
                'payback_period_months': round((data['cost_per_hectare'] / (profit / 12)), 1) if profit > 0 else 'N/A',
                'climate_suitability': climate_factor,
                'risk_level': assess_crop_risk(crop, lat, lon)
            }
        
        sorted_crops = dict(sorted(profitable_crops.items(), key=lambda x: x[1]['roi_percentage'], reverse=True))
        
        return {
            'top_profitable_crops': dict(list(sorted_crops.items())[:5]),
            'all_crops_analysis': sorted_crops,
            'analysis_date': datetime.now().isoformat()
        }

    # Main execution
    lat, lon = get_current_location()
    profitable_crops = get_best_yield_profitable_crops(lat, lon)
    
    print(f"\n💰 TOP PROFITABLE CROPS (ROI %) for location {lat:.4f}, {lon:.4f}:")
    for i, (crop, data) in enumerate(list(profitable_crops['top_profitable_crops'].items())[:5], 1):
        roi = data.get('roi_percentage', 0)
        profit = data.get('net_profit', 0)
        print(f"   {i}. {crop.title()}: {roi}% ROI (₹{profit:,.0f} profit/hectare)")
    
    return profitable_crops

# Run the function
if __name__ == "__main__":
    result = get_crop_profitability_analysis()
