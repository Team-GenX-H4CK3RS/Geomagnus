import geocoder
from datetime import datetime
from typing import Dict, Tuple

def get_dynamic_pricing_strategy():
    """Independent dynamic pricing strategy implementation"""
    
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

    # Base crop data
    crop_profitability_data = {
        'wheat': {'cost_per_hectare': 45000, 'yield_per_hectare': 4.5, 'price_per_ton': 22000},
        'rice': {'cost_per_hectare': 55000, 'yield_per_hectare': 6.5, 'price_per_ton': 20000},
        'corn': {'cost_per_hectare': 50000, 'yield_per_hectare': 9.0, 'price_per_ton': 18000},
        'tomato': {'cost_per_hectare': 85000, 'yield_per_hectare': 45, 'price_per_ton': 12000},
        'onion': {'cost_per_hectare': 45000, 'yield_per_hectare': 20, 'price_per_ton': 15000},
        'potato': {'cost_per_hectare': 70000, 'yield_per_hectare': 25, 'price_per_ton': 8000}
    }

    # Market volatility data
    market_volatility = {
        'wheat': {'volatility': 0.15, 'seasonal_factor': 1.2, 'demand_elasticity': 0.8},
        'rice': {'volatility': 0.12, 'seasonal_factor': 1.1, 'demand_elasticity': 0.7},
        'corn': {'volatility': 0.18, 'seasonal_factor': 1.3, 'demand_elasticity': 0.9},
        'tomato': {'volatility': 0.35, 'seasonal_factor': 2.0, 'demand_elasticity': 1.8},
        'onion': {'volatility': 0.40, 'seasonal_factor': 2.2, 'demand_elasticity': 2.0},
        'potato': {'volatility': 0.30, 'seasonal_factor': 1.8, 'demand_elasticity': 1.5}
    }

    def get_seasonal_pricing_factors(month: int, lat: float) -> Dict:
        """Get seasonal pricing factors for crops"""
        is_northern = lat >= 0
        
        if is_northern:
            if month in [3, 4, 5]:  # Spring
                factors = {'wheat': 1.1, 'corn': 0.9, 'tomato': 1.3, 'potato': 1.2, 'onion': 1.1, 'rice': 1.0}
            elif month in [6, 7, 8]:  # Summer
                factors = {'wheat': 0.9, 'corn': 1.1, 'tomato': 0.8, 'potato': 0.9, 'onion': 0.9, 'rice': 1.0}
            elif month in [9, 10, 11]:  # Autumn
                factors = {'wheat': 1.0, 'corn': 0.8, 'tomato': 1.2, 'potato': 1.1, 'onion': 1.3, 'rice': 1.1}
            else:  # Winter
                factors = {'wheat': 1.2, 'corn': 1.3, 'tomato': 1.5, 'potato': 1.3, 'onion': 1.4, 'rice': 1.0}
        else:
            # Reverse seasons for southern hemisphere
            if month in [9, 10, 11]:  # Spring (Southern)
                factors = {'wheat': 1.1, 'corn': 0.9, 'tomato': 1.3, 'potato': 1.2, 'onion': 1.1, 'rice': 1.0}
            elif month in [12, 1, 2]:  # Summer (Southern)
                factors = {'wheat': 0.9, 'corn': 1.1, 'tomato': 0.8, 'potato': 0.9, 'onion': 0.9, 'rice': 1.0}
            elif month in [3, 4, 5]:  # Autumn (Southern)
                factors = {'wheat': 1.0, 'corn': 0.8, 'tomato': 1.2, 'potato': 1.1, 'onion': 1.3, 'rice': 1.1}
            else:  # Winter (Southern)
                factors = {'wheat': 1.2, 'corn': 1.3, 'tomato': 1.5, 'potato': 1.3, 'onion': 1.4, 'rice': 1.0}
        
        return factors

    def calculate_demand_adjustment(crop: str, current_date: datetime) -> float:
        """Calculate demand adjustment factor"""
        base_demand = 1.0
        month = current_date.month
        
        if crop in ['tomato', 'onion', 'potato']:
            if month in [11, 12, 1, 2]:  # Winter demand higher
                base_demand *= 1.2
        
        # Market trend factors
        market_trends = {
            'wheat': 1.05, 'rice': 1.02, 'corn': 1.08,
            'tomato': 1.12, 'onion': 1.06, 'potato': 1.03
        }
        
        return base_demand * market_trends.get(crop, 1.0)

    def analyze_market_sentiment(crop: str) -> float:
        """Analyze market sentiment factor"""
        sentiment_factors = {
            'wheat': 1.05, 'rice': 1.02, 'corn': 1.08,
            'tomato': 1.12, 'onion': 1.06, 'potato': 1.03
        }
        return sentiment_factors.get(crop, 1.0)

    def generate_pricing_strategies(crop: str, dynamic_price: float, base_price: float) -> Dict:
        """Generate pricing strategies for the crop"""
        return {
            'immediate_sale': {
                'price': dynamic_price,
                'timing': 'At harvest',
                'pros': ['Immediate cash flow', 'No storage costs'],
                'cons': ['May miss price peaks', 'Market timing risk']
            },
            'storage_strategy': {
                'price': dynamic_price * 1.15,
                'timing': '3-6 months post harvest',
                'pros': ['Higher prices', 'Market timing flexibility'],
                'cons': ['Storage costs', 'Quality deterioration risk']
            },
            'contract_farming': {
                'price': base_price * 1.05,
                'timing': 'Pre-season contract',
                'pros': ['Price certainty', 'Reduced market risk'],
                'cons': ['May miss price upside', 'Contract obligations']
            },
            'premium_market': {
                'price': dynamic_price * 1.25,
                'timing': 'Direct to consumer',
                'pros': ['Highest margins', 'Brand building'],
                'cons': ['Marketing costs', 'Limited volume']
            }
        }

    def implement_dynamic_pricing_strategy(lat: float, lon: float) -> Dict:
        """Implement dynamic pricing strategy based on market conditions"""
        current_date = datetime.now()
        seasonal_factors = get_seasonal_pricing_factors(current_date.month, lat)
        
        dynamic_pricing = {}
        
        for crop, base_data in crop_profitability_data.items():
            base_price = base_data['price_per_ton']
            
            seasonal_adjustment = seasonal_factors.get(crop, 1.0)
            demand_adjustment = calculate_demand_adjustment(crop, current_date)
            sentiment_factor = analyze_market_sentiment(crop)
            
            # Weather impact (simplified)
            weather_impact = 1.05
            
            dynamic_price = base_price * seasonal_adjustment * demand_adjustment * sentiment_factor * weather_impact
            
            pricing_strategies = generate_pricing_strategies(crop, dynamic_price, base_price)
            
            dynamic_pricing[crop] = {
                'base_price': base_price,
                'dynamic_price': round(dynamic_price, 2),
                'price_change_percentage': round(((dynamic_price - base_price) / base_price) * 100, 1),
                'pricing_factors': {
                    'seasonal_adjustment': seasonal_adjustment,
                    'demand_adjustment': demand_adjustment,
                    'sentiment_factor': sentiment_factor,
                    'weather_impact': weather_impact
                },
                'pricing_strategies': pricing_strategies,
                'market_trend': 'Growing demand' if sentiment_factor > 1.05 else 'Stable demand'
            }
        
        return {
            'analysis_date': current_date.isoformat(),
            'location': {'lat': lat, 'lon': lon},
            'dynamic_pricing_analysis': dynamic_pricing
        }

    # Main execution
    lat, lon = get_current_location()
    pricing_analysis = implement_dynamic_pricing_strategy(lat, lon)
    
    print(f"\n📈 DYNAMIC PRICING OPPORTUNITIES for location {lat:.4f}, {lon:.4f}:")
    opportunities = []
    for crop, data in pricing_analysis['dynamic_pricing_analysis'].items():
        price_change = data.get('price_change_percentage', 0)
        if price_change > 10:
            opportunities.append((crop, price_change))
    
    opportunities.sort(key=lambda x: x[1], reverse=True)
    for crop, change in opportunities[:3]:
        print(f"   {crop.title()}: +{change}% price opportunity")
    
    print("\n💡 PRICING STRATEGIES:")
    for crop, data in list(pricing_analysis['dynamic_pricing_analysis'].items())[:3]:
        print(f"\n   {crop.title()}:")
        print(f"     Base Price: ₹{data['base_price']:,.0f}/ton")
        print(f"     Dynamic Price: ₹{data['dynamic_price']:,.0f}/ton")
        print(f"     Best Strategy: {list(data['pricing_strategies'].keys())[0]}")
    
    return pricing_analysis

# Run the function
if __name__ == "__main__":
    result = get_dynamic_pricing_strategy()
