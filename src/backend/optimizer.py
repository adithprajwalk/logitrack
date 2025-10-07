import logging
import time
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class InventoryOptimizer:
    def __init__(self):
        """Initialize the optimizer with default parameters"""
        self.logger = logging.getLogger(__name__)
        self.solver_time = 20  # Default solver time limit in seconds
        self.current_datetime = "2025-03-24 21:07:26"
        self.current_user = "tanishpoddar"

    def calculate_distance(self, warehouse_row: pd.Series, order_row: pd.Series) -> float:
        """Calculate distance between warehouse and delivery location using Haversine formula"""
        try:
            lat1, lon1 = warehouse_row['latitude'], warehouse_row['longitude']
            lat2, lon2 = order_row['delivery_latitude'], order_row['delivery_longitude']
            
            lat1, lon1 = map(radians, [float(lat1), float(lon1)])
            lat2, lon2 = map(radians, [float(lat2), float(lon2)])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            r = 6371  # Earth's radius in kilometers
            
            return c * r
        except Exception as e:
            self.logger.error(f"Error calculating distance: {str(e)}")
            return float('inf')

    def optimize(self, warehouses: pd.DataFrame, orders: pd.DataFrame, inventory: pd.DataFrame) -> Dict[str, Any]:
        """Optimize inventory distribution using detailed, per-product stock levels."""
        try:
            optimization_start_time = time.time()
            
            results = {
                'allocation_plan': {},
                'warehouse_utilization': {},
                'unfulfilled_orders': [],
                'total_cost': 0,
                'solving_time': 0,
                'status': 'In Progress'
            }

            # Create a copy of the detailed inventory to track changes
            inventory_levels = inventory.copy()
            
            orders = orders.sort_values(by=['status', 'quantity'], ascending=[True, False])

            for _, order in orders.iterrows():
                best_allocation = {'warehouse_id': None, 'cost': float('inf'), 'distance': float('inf')}
                order_product_id = order['product_id']
                order_quantity = order['quantity']

                # Find warehouses that stock this specific product
                possible_inventory = inventory_levels[inventory_levels['product_id'] == order_product_id]

                for _, stock_info in possible_inventory.iterrows():
                    # Check if this warehouse has enough stock OF THIS PRODUCT
                    if stock_info['current_stock'] >= order_quantity:
                        warehouse_id = stock_info['warehouse_id']
                        warehouse = warehouses[warehouses['warehouse_id'] == warehouse_id].iloc[0]
                        
                        # --- REVISED COST CALCULATION ---
                        transport_cost = self.calculate_distance(warehouse, order) * 10
                        storage_cost_penalty = warehouse['storage_cost'] * 0.1
                        cost = transport_cost + storage_cost_penalty
                        
                        if cost < best_allocation['cost']:
                            best_allocation.update({
                                'warehouse_id': warehouse_id,
                                'cost': cost,
                                'distance': self.calculate_distance(warehouse, order)
                            })

                # Allocate order if a suitable warehouse was found
                if best_allocation['warehouse_id'] is not None:
                    warehouse_id = best_allocation['warehouse_id']
                    
                    if warehouse_id not in results['allocation_plan']:
                        results['allocation_plan'][warehouse_id] = []
                    
                    results['allocation_plan'][warehouse_id].append({
                        'order_id': order['order_id'],
                        'quantity': order_quantity,
                        'cost': best_allocation['cost'],
                        'distance': best_allocation['distance']
                    })
                    
                    # Update the specific product's stock in the correct warehouse
                    inventory_mask = (inventory_levels['warehouse_id'] == warehouse_id) & \
                                     (inventory_levels['product_id'] == order_product_id)
                    inventory_levels.loc[inventory_mask, 'current_stock'] -= order_quantity
                    
                    results['total_cost'] += best_allocation['cost']
                else:
                    results['unfulfilled_orders'].append({
                        'order_id': order['order_id'],
                        'quantity': order_quantity,
                        'reason': f'Insufficient stock for product {order_product_id}'
                    })

            results['solving_time'] = time.time() - optimization_start_time
            results['status'] = 'Completed'
            
            # (Optional: Re-add performance_metrics dictionary calculation here if needed)

            return results

        except Exception as e:
            self.logger.error(f"Optimization error: {str(e)}")
            raise ValueError(f"Optimization error: {str(e)}")

    def get_optimization_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of optimization results"""
        try:
            # Note: This part might need adjustment if performance_metrics isn't recalculated
            summary = {
                'total_cost': round(results.get('total_cost', 0), 2),
                'solving_time': round(results.get('solving_time', 0), 2),
                'status': results.get('status', 'Unknown'),
                'timestamp': results.get('optimization_timestamp')
            }
            return summary
        except Exception as e:
            self.logger.error(f"Error generating optimization summary: {str(e)}")
            return {}