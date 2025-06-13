import geocoder
from datetime import datetime
from typing import Dict, Tuple

def get_advanced_investment_analysis():
    """Independent advanced investment analysis with risk assessment"""
    
    def get_current_location() -> Tuple[float, float]:
        """Get current location using IP geolocation"""
        try:
            g = geocoder.ip('me')
            if g.ok:
                return 12.9915, 80.2337
                # return g.latlng[0], g.latlng[1]
            else:
                return 28.6139, 77.2090
        except Exception as e:
            print(f"Error getting current location: {e}")
            return 28.6139, 77.2090

    # Crop data
    crop_profitability_data = {
        'wheat': {'cost_per_hectare': 45000, 'yield_per_hectare': 4.5, 'price_per_ton': 22000},
        'rice': {'cost_per_hectare': 55000, 'yield_per_hectare': 6.5, 'price_per_ton': 20000},
        'corn': {'cost_per_hectare': 50000, 'yield_per_hectare': 9.0, 'price_per_ton': 18000},
        'soybean': {'cost_per_hectare': 40000, 'yield_per_hectare': 3.2, 'price_per_ton': 35000},
        'tomato': {'cost_per_hectare': 85000, 'yield_per_hectare': 45, 'price_per_ton': 12000},
        'onion': {'cost_per_hectare': 45000, 'yield_per_hectare': 20, 'price_per_ton': 15000},
        'potato': {'cost_per_hectare': 70000, 'yield_per_hectare': 25, 'price_per_ton': 8000}
    }

    def assess_climate_suitability(lat: float, lon: float) -> Dict:
        """Assess climate suitability for different crops"""
        abs_lat = abs(lat)
        suitability = {}
        
        for crop in crop_profitability_data:
            if abs_lat < 23.5:  # Tropical
                if crop in ['rice', 'tomato']:
                    suitability[crop] = 1.0
                else:
                    suitability[crop] = 0.7
            elif abs_lat < 40:  # Subtropical
                if crop in ['wheat', 'corn', 'soybean']:
                    suitability[crop] = 1.0
                else:
                    suitability[crop] = 0.8
            else:  # Temperate
                if crop in ['wheat', 'potato']:
                    suitability[crop] = 1.0
                else:
                    suitability[crop] = 0.6
        return suitability

    def get_risk_factor(crop: str, lat: float, lon: float) -> float:
        """Calculate overall risk factor for a crop"""
        base_risk = {
            'wheat': 0.15, 'rice': 0.20, 'corn': 0.18, 'soybean': 0.12,
            'potato': 0.22, 'tomato': 0.28, 'onion': 0.24
        }
        
        climate_suitability = assess_climate_suitability(lat, lon)
        climate_risk = 1 - climate_suitability.get(crop, 0.8)
        market_risk = 0.2  # Simplified market risk
        
        overall_risk = (base_risk.get(crop, 0.2) + climate_risk + market_risk) / 3
        return min(0.5, max(0.05, overall_risk))

    def categorize_risk(risk_factor: float) -> str:
        """Categorize risk level"""
        if risk_factor < 0.15:
            return "Low Risk"
        elif risk_factor < 0.25:
            return "Medium Risk"
        else:
            return "High Risk"

    def get_investment_recommendation(roi: float, risk_factor: float, crop: str) -> str:
        """Get investment recommendation"""
        if roi > 50 and risk_factor < 0.2:
            return "Highly Recommended - High ROI with manageable risk"
        elif roi > 30 and risk_factor < 0.3:
            return "Recommended - Good balance of return and risk"
        elif roi > 15:
            return "Consider - Moderate returns, assess risk tolerance"
        else:
            return "Not Recommended - Low returns for risk level"

    def calculate_monthly_cash_flow(crop: str, annual_profit: float, hectares: float) -> Dict:
        """Calculate monthly cash flow projection"""
        growing_periods = {
            'wheat': {'planting': 3, 'harvest': 7},
            'rice': {'planting': 4, 'harvest': 9},
            'corn': {'planting': 4, 'harvest': 8},
            'soybean': {'planting': 5, 'harvest': 9},
            'potato': {'planting': 3, 'harvest': 6},
            'tomato': {'planting': 2, 'harvest': 6},
            'onion': {'planting': 2, 'harvest': 7}
        }
        
        period = growing_periods.get(crop, {'planting': 3, 'harvest': 8})
        monthly_flow = {}
        
        for month in range(1, 13):
            if month == period['planting']:
                monthly_flow[f"Month_{month}"] = -crop_profitability_data[crop]['cost_per_hectare'] * hectares
            elif month == period['harvest']:
                monthly_flow[f"Month_{month}"] = annual_profit + crop_profitability_data[crop]['cost_per_hectare'] * hectares
            else:
                monthly_flow[f"Month_{month}"] = 0
        
        return monthly_flow

    def get_better_profitable_yield_analysis(lat: float, lon: float, investment_amount: float = 100000) -> Dict:
        """Advanced profitable yield analysis with detailed ROI calculations"""
        climate_suitability = assess_climate_suitability(lat, lon)
        
        advanced_analysis = {}
        
        for crop, data in crop_profitability_data.items():
            climate_factor = climate_suitability.get(crop, 0.8)
            market_factor = 1.0  # Simplified market factor
            
            adjusted_yield = data['yield_per_hectare'] * climate_factor
            adjusted_price = data['price_per_ton'] * market_factor
            
            hectares_possible = investment_amount / data['cost_per_hectare']
            
            total_revenue = adjusted_yield * adjusted_price * hectares_possible
            total_cost = data['cost_per_hectare'] * hectares_possible
            net_profit = total_revenue - total_cost
            roi_percentage = (net_profit / investment_amount) * 100
            
            risk_factor = get_risk_factor(crop, lat, lon)
            risk_adjusted_roi = roi_percentage * (1 - risk_factor)
            
            break_even_yield = data['cost_per_hectare'] / adjusted_price
            break_even_price = data['cost_per_hectare'] / adjusted_yield
            
            monthly_cash_flow = calculate_monthly_cash_flow(crop, net_profit, hectares_possible)
            
            advanced_analysis[crop] = {
                'investment_analysis': {
                    'total_investment': investment_amount,
                    'hectares_cultivated': round(hectares_possible, 2),
                    'cost_per_hectare': data['cost_per_hectare'],
                    'adjusted_yield_per_hectare': round(adjusted_yield, 2),
                    'adjusted_price_per_ton': round(adjusted_price, 2)
                },
                'financial_metrics': {
                    'total_revenue': round(total_revenue, 2),
                    'total_cost': round(total_cost, 2),
                    'net_profit': round(net_profit, 2),
                    'roi_percentage': round(roi_percentage, 1),
                    'risk_adjusted_roi': round(risk_adjusted_roi, 1),
                    'profit_margin': round((net_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0
                },
                'break_even_analysis': {
                    'break_even_yield_tons': round(break_even_yield, 2),
                    'break_even_price_per_ton': round(break_even_price, 2),
                    'safety_margin_yield': round(((adjusted_yield - break_even_yield) / adjusted_yield) * 100, 1),
                    'safety_margin_price': round(((adjusted_price - break_even_price) / adjusted_price) * 100, 1)
                },
                'risk_assessment': {
                    'overall_risk_factor': risk_factor,
                    'climate_risk': 1 - climate_factor,
                    'risk_category': categorize_risk(risk_factor)
                },
                'cash_flow_projection': monthly_cash_flow,
                'investment_recommendation': get_investment_recommendation(roi_percentage, risk_factor, crop)
            }
        
        sorted_analysis = dict(sorted(advanced_analysis.items(), 
                                    key=lambda x: x[1]['financial_metrics']['risk_adjusted_roi'], 
                                    reverse=True))
        
        return {
            'investment_amount': investment_amount,
            'analysis_date': datetime.now().isoformat(),
            'location': {'lat': lat, 'lon': lon},
            'top_recommendations': dict(list(sorted_analysis.items())[:3]),
            'detailed_analysis': sorted_analysis
        }

    # Main execution
    lat, lon = get_current_location()
    investment_amount = 100000  # Default investment amount
    
    advanced_analysis = get_better_profitable_yield_analysis(lat, lon, investment_amount)
    
    print(f"\n📊 INVESTMENT ANALYSIS (₹{investment_amount:,.0f}) for location {lat:.4f}, {lon:.4f}:")
    for crop, data in list(advanced_analysis['top_recommendations'].items())[:3]:
        risk_adj_roi = data['financial_metrics']['risk_adjusted_roi']
        hectares = data['investment_analysis']['hectares_cultivated']
        risk_category = data['risk_assessment']['risk_category']
        print(f"   {crop.title()}: {risk_adj_roi}% Risk-Adj ROI ({hectares:.1f} hectares) - {risk_category}")
    
    print("\n💡 DETAILED BREAKDOWN (Top Crop):")
    top_crop = list(advanced_analysis['top_recommendations'].keys())[0]
    top_data = advanced_analysis['top_recommendations'][top_crop]
    
    print(f"   Crop: {top_crop.title()}")
    print(f"   Investment: ₹{top_data['investment_analysis']['total_investment']:,.0f}")
    print(f"   Expected Revenue: ₹{top_data['financial_metrics']['total_revenue']:,.0f}")
    print(f"   Net Profit: ₹{top_data['financial_metrics']['net_profit']:,.0f}")
    print(f"   ROI: {top_data['financial_metrics']['roi_percentage']}%")
    print(f"   Recommendation: {top_data['investment_recommendation']}")
    
    return advanced_analysis

# Run the function
if __name__ == "__main__":
    result = get_advanced_investment_analysis()
