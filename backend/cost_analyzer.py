#!/usr/bin/env python3
"""
Cost Analysis Service for Cloud Health Dashboard Phase 2
Provides detailed cost tracking, analysis, and optimization recommendations
"""

from datetime import datetime, timedelta
from app import db, Service, Metric
import json

class CostAnalyzer:
    """Service for analyzing service costs and providing optimization insights"""
    
    def __init__(self):
        self.cost_thresholds = {
            'high': 0.001,  # $0.001 per request
            'medium': 0.0005,  # $0.0005 per request
            'low': 0.0001   # $0.0001 per request
        }
    
    def get_service_cost_summary(self, service_id, days=30):
        """Get comprehensive cost summary for a service"""
        service = Service.query.get(service_id)
        if not service:
            return None
        
        # Get metrics from specified time period
        start_date = datetime.utcnow() - timedelta(days=days)
        metrics = Metric.query.filter(
            Metric.service_id == service_id,
            Metric.timestamp >= start_date
        ).all()
        
        if not metrics:
            return {
                'service_name': service.name,
                'period_days': days,
                'total_cost': 0.0,
                'total_requests': 0,
                'avg_cost_per_request': 0.0,
                'cost_trend': 'stable',
                'recommendations': []
            }
        
        # Calculate costs
        total_cost = sum(m.cost for m in metrics)
        total_requests = len(metrics)
        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
        
        # Calculate daily costs for trend analysis
        daily_costs = {}
        for metric in metrics:
            date = metric.timestamp.date().isoformat()
            daily_costs[date] = daily_costs.get(date, 0) + metric.cost
        
        # Determine cost trend
        cost_trend = self._analyze_cost_trend(daily_costs)
        
        # Generate recommendations
        recommendations = self._generate_cost_recommendations(
            service, total_cost, avg_cost_per_request, total_requests, days
        )
        
        return {
            'service_name': service.name,
            'period_days': days,
            'total_cost': round(total_cost, 6),
            'total_requests': total_requests,
            'avg_cost_per_request': round(avg_cost_per_request, 6),
            'daily_costs': daily_costs,
            'cost_trend': cost_trend,
            'cost_per_request': service.cost_per_request,
            'cost_per_gb_hour': service.cost_per_gb_hour,
            'recommendations': recommendations,
            'cost_efficiency_score': self._calculate_cost_efficiency_score(service, avg_cost_per_request)
        }
    
    def get_all_services_cost_summary(self, days=30):
        """Get cost summary for all services"""
        services = Service.query.all()
        summaries = []
        
        for service in services:
            summary = self.get_service_cost_summary(service.id, days)
            if summary:
                summaries.append(summary)
        
        # Sort by total cost (highest first)
        summaries.sort(key=lambda x: x['total_cost'], reverse=True)
        
        return {
            'period_days': days,
            'total_cost_across_services': round(sum(s['total_cost'] for s in summaries), 6),
            'services': summaries,
            'cost_breakdown': self._get_cost_breakdown_by_type(summaries)
        }
    
    def get_cost_optimization_recommendations(self, service_id):
        """Get specific cost optimization recommendations for a service"""
        service = Service.query.get(service_id)
        if not service:
            return []
        
        # Get recent metrics for analysis
        recent_metrics = Metric.query.filter(
            Metric.service_id == service_id,
            Metric.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not recent_metrics:
            return ["No recent data available for analysis"]
        
        recommendations = []
        
        # Analyze request sizes
        avg_request_size = sum(m.request_size for m in recent_metrics) / len(recent_metrics)
        avg_response_size = sum(m.response_size for m in recent_metrics) / len(recent_metrics)
        
        # Check for optimization opportunities
        if avg_request_size > 1000:  # > 1KB
            recommendations.append({
                'type': 'request_optimization',
                'priority': 'medium',
                'title': 'Optimize Request Payloads',
                'description': f'Average request size is {avg_request_size:.0f} bytes. Consider compressing or reducing payload size.',
                'potential_savings': '10-20% reduction in data transfer costs',
                'effort': 'medium'
            })
        
        if avg_response_size > 5000:  # > 5KB
            recommendations.append({
                'type': 'response_optimization',
                'priority': 'high',
                'title': 'Optimize Response Payloads',
                'description': f'Average response size is {avg_response_size:.0f} bytes. Implement response compression and pagination.',
                'potential_savings': '15-30% reduction in data transfer costs',
                'effort': 'medium'
            })
        
        # Check cost per request
        if service.cost_per_request > self.cost_thresholds['high']:
            recommendations.append({
                'type': 'pricing_optimization',
                'priority': 'high',
                'title': 'Review Service Pricing',
                'description': f'Cost per request (${service.cost_per_request:.6f}) is above recommended threshold.',
                'potential_savings': '20-40% reduction in per-request costs',
                'effort': 'low'
            })
        
        # Check for high error rates that increase costs
        error_rate = sum(1 for m in recent_metrics if m.error) / len(recent_metrics) * 100
        if error_rate > 5:
            recommendations.append({
                'type': 'reliability_improvement',
                'priority': 'high',
                'title': 'Reduce Error Rates',
                'description': f'Error rate is {error_rate:.1f}%. Failed requests still incur costs.',
                'potential_savings': f'{error_rate:.1f}% reduction in wasted costs',
                'effort': 'high'
            })
        
        # Check for maintenance window optimization
        if service.maintenance_window:
            recommendations.append({
                'type': 'maintenance_optimization',
                'priority': 'medium',
                'title': 'Optimize Maintenance Windows',
                'description': f'Current maintenance window: {service.maintenance_window}. Consider off-peak hours for better cost efficiency.',
                'potential_savings': '5-15% reduction in maintenance costs',
                'effort': 'low'
            })
        
        return recommendations
    
    def get_cost_forecast(self, service_id, days_ahead=30):
        """Forecast costs for the next specified period"""
        service = Service.query.get(service_id)
        if not service:
            return None
        
        # Get historical data for trend analysis
        historical_metrics = Metric.query.filter(
            Metric.service_id == service_id,
            Metric.timestamp >= datetime.utcnow() - timedelta(days=90)  # 3 months of data
        ).order_by(Metric.timestamp.asc()).all()
        
        if len(historical_metrics) < 7:  # Need at least a week of data
            return None
        
        # Calculate daily averages
        daily_costs = {}
        for metric in historical_metrics:
            date = metric.timestamp.date().isoformat()
            if date not in daily_costs:
                daily_costs[date] = {'total_cost': 0, 'count': 0}
            daily_costs[date]['total_cost'] += metric.cost
            daily_costs[date]['count'] += 1
        
        # Calculate average daily cost
        avg_daily_cost = sum(d['total_cost'] for d in daily_costs.values()) / len(daily_costs)
        
        # Simple linear forecast
        forecasted_cost = avg_daily_cost * days_ahead
        
        # Calculate confidence interval (simple approach)
        daily_costs_list = [d['total_cost'] for d in daily_costs.values()]
        variance = sum((cost - avg_daily_cost) ** 2 for cost in daily_costs_list) / len(daily_costs_list)
        std_dev = variance ** 0.5
        
        confidence_interval = {
            'low': max(0, forecasted_cost - (std_dev * days_ahead * 0.5)),
            'high': forecasted_cost + (std_dev * days_ahead * 0.5)
        }
        
        return {
            'service_name': service.name,
            'forecast_period_days': days_ahead,
            'forecasted_cost': round(forecasted_cost, 6),
            'confidence_interval': {
                'low': round(confidence_interval['low'], 6),
                'high': round(confidence_interval['high'], 6)
            },
            'avg_daily_cost': round(avg_daily_cost, 6),
            'trend': 'increasing' if avg_daily_cost > 0 else 'stable',
            'assumptions': [
                'Based on historical 90-day trend',
                'Assumes consistent usage patterns',
                'Does not account for seasonal variations'
            ]
        }
    
    def _analyze_cost_trend(self, daily_costs):
        """Analyze cost trend from daily cost data"""
        if len(daily_costs) < 2:
            return 'stable'
        
        # Convert to sorted list of (date, cost) tuples
        sorted_costs = sorted(daily_costs.items())
        costs = [cost for _, cost in sorted_costs]
        
        # Simple trend analysis
        if len(costs) >= 7:  # At least a week of data
            first_week_avg = sum(costs[:7]) / 7
            last_week_avg = sum(costs[-7:]) / 7
            
            if last_week_avg > first_week_avg * 1.1:
                return 'increasing'
            elif last_week_avg < first_week_avg * 0.9:
                return 'decreasing'
        
        return 'stable'
    
    def _generate_cost_recommendations(self, service, total_cost, avg_cost_per_request, total_requests, days):
        """Generate cost optimization recommendations"""
        recommendations = []
        
        # High cost recommendations
        if total_cost > 0.01:  # More than $0.01 in the period
            recommendations.append({
                'type': 'cost_monitoring',
                'priority': 'high',
                'title': 'Monitor High-Cost Service',
                'description': f'Service has generated ${total_cost:.6f} in costs over {days} days.',
                'action': 'Review usage patterns and consider optimization'
            })
        
        # Cost per request recommendations
        if avg_cost_per_request > self.cost_thresholds['high']:
            recommendations.append({
                'type': 'pricing_optimization',
                'priority': 'high',
                'title': 'High Cost Per Request',
                'description': f'Average cost per request (${avg_cost_per_request:.6f}) is above recommended threshold.',
                'action': 'Review service pricing and consider alternatives'
            })
        
        # Volume-based recommendations
        if total_requests > 1000:
            recommendations.append({
                'type': 'volume_optimization',
                'priority': 'medium',
                'title': 'High Request Volume',
                'description': f'Service handled {total_requests} requests in {days} days.',
                'action': 'Consider implementing caching and rate limiting'
            })
        
        return recommendations
    
    def _calculate_cost_efficiency_score(self, service, avg_cost_per_request):
        """Calculate a cost efficiency score (0-100)"""
        if avg_cost_per_request <= self.cost_thresholds['low']:
            return 100
        elif avg_cost_per_request <= self.cost_thresholds['medium']:
            return 75
        elif avg_cost_per_request <= self.cost_thresholds['high']:
            return 50
        else:
            return 25
    
    def _get_cost_breakdown_by_type(self, summaries):
        """Get cost breakdown by service type"""
        breakdown = {}
        
        for summary in summaries:
            service = Service.query.filter_by(name=summary['service_name']).first()
            if service and service.service_type:
                service_type = service.service_type
                if service_type not in breakdown:
                    breakdown[service_type] = {'total_cost': 0, 'services': []}
                
                breakdown[service_type]['total_cost'] += summary['total_cost']
                breakdown[service_type]['services'].append({
                    'name': summary['service_name'],
                    'cost': summary['total_cost']
                })
        
        # Round costs
        for service_type in breakdown:
            breakdown[service_type]['total_cost'] = round(breakdown[service_type]['total_cost'], 6)
        
        return breakdown
