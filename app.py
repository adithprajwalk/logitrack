import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from src.backend.data_loader import DataLoader
from src.backend.optimizer import InventoryOptimizer
from src.utils.helpers import format_currency, calculate_distance
import plotly.graph_objects as go

class LogiTrackApp:
    def __init__(self):
        """Initialize the LogiTrack application"""
        st.set_page_config(
            page_title="LogiTrack: Inventory Management System",
            page_icon="🏭",
            layout="wide"
        )
        
        # Initialize session state for login
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ''
        
        # Initialize data loader and optimizer
        self.data_loader = None
        self.optimizer = InventoryOptimizer()

    def get_file_download_link(self, filename):
        """Generate a download link for a file"""
        filepath = os.path.join('data', filename)
        try:
            with open(filepath, 'rb') as f:
                bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
            return href
        except FileNotFoundError:
            return f"File not found: {filename}"

    def login_page(self):
        """Display login page"""
        st.title("LogiTrack : Inventory Management")
        st.write("Welcome! Please enter your name to get started.")
        
        username = st.text_input("What should we call you?")
        
        if st.button("Enter"):
            if username.strip():
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.warning("Please enter a name")

    def show_user_context(self):
        """Display user context information"""
        with st.sidebar:
            st.write("---")
            st.subheader("👤 User Context")
            st.info(f"User: {st.session_state.username}")
            # Get real-time current datetime
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.info(f"UTC Time: {current_datetime}")

    def select_data_source(self):
        """Allow user to select data source and load appropriate data"""
        st.sidebar.title("📊 Data Source")
        data_source = st.sidebar.radio(
            "Select Data Source:",
            ["Sample Data", "Upload Data", "Database Connection"]
        )

        if data_source == "Sample Data":
            self.data_loader = DataLoader()
            st.sidebar.success("✅ Sample data loaded successfully!")
            return True
            
        elif data_source == "Upload Data":
            st.sidebar.info("📤 Upload your data files:")
            
            # File uploaders for each data type (Suppliers removed)
            uploaded_files = {}
            required_files = {
                'warehouses': 'sample_warehouses.csv',
                'sales': 'sample_sales.csv',
                'products': 'product_inventory.csv',
                'inventory': 'inventory_levels.csv',
                'transport': 'transportation_costs.csv'
            }

            # Show template downloads
            st.sidebar.markdown("📑 **Templates:**")
            for file_type, filename in required_files.items():
                download_link = self.get_file_download_link(filename)
                st.sidebar.markdown(download_link, unsafe_allow_html=True)

            # File uploaders (Suppliers removed)
            uploaded_files['warehouses'] = st.sidebar.file_uploader("Upload Warehouses Data", type=['csv'])
            uploaded_files['sales'] = st.sidebar.file_uploader("Upload Sales Data", type=['csv'])
            uploaded_files['products'] = st.sidebar.file_uploader("Upload Product Inventory", type=['csv'])
            uploaded_files['inventory'] = st.sidebar.file_uploader("Upload Inventory Levels", type=['csv'])
            uploaded_files['transport'] = st.sidebar.file_uploader("Upload Transport Costs", type=['csv'])

            if all(uploaded_files.values()):
                try:
                    self.data_loader = DataLoader(uploaded_files=uploaded_files)
                    st.sidebar.success("✅ Custom data loaded successfully!")
                    return True
                except Exception as e:
                    st.sidebar.error(f"Error loading data: {str(e)}")
                    st.sidebar.error("Please ensure your files match the template format")
                    return False
            else:
                st.sidebar.warning("⚠️ Please upload all required files")
                return False

        elif data_source == "Database Connection":
            st.sidebar.info("🔌 Database Connection")
            
            db_type = st.sidebar.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQLite"])
            if db_type in ["PostgreSQL", "MySQL"]:
                host = st.sidebar.text_input("Host")
                port = st.sidebar.text_input("Port")
                database = st.sidebar.text_input("Database Name")
                username = st.sidebar.text_input("Username")
                password = st.sidebar.text_input("Password", type="password")
                
                if st.sidebar.button("Connect"):
                    try:
                        self.data_loader = DataLoader(
                            db_config={
                                'type': db_type,
                                'host': host,
                                'port': port,
                                'database': database,
                                'username': username,
                                'password': password
                            }
                        )
                        st.sidebar.success("✅ Connected to database successfully!")
                        return True
                    except Exception as e:
                        st.sidebar.error(f"Database connection failed: {str(e)}")
                        return False
            else:  # SQLite
                db_file = st.sidebar.file_uploader("Upload SQLite Database", type=['db', 'sqlite'])
                if db_file:
                    try:
                        self.data_loader = DataLoader(sqlite_file=db_file)
                        st.sidebar.success("✅ Connected to SQLite database successfully!")
                        return True
                    except Exception as e:
                        st.sidebar.error(f"Database connection failed: {str(e)}")
                        return False

        return False

    def show_guide(self):
        """Display the user guide/documentation"""
        st.title("📚 LogiTrack User Guide")
        
        st.markdown("Welcome to LogiTrack - Your Comprehensive Inventory Management System!")
        
        tab_main, tab_features, tab_data, tab_optimize = st.tabs([
            "Getting Started", "Features", "Data Management", "Optimization Guide"
        ])
        
        with tab_main:
            st.subheader("🚀 Getting Started")
            st.markdown("""
            ### Quick Start
            1. **Login**: Enter your username to access the system.
            2. **Select Data Source**: Choose Sample Data, Upload Your Data, or connect to a Database.
            3. **Navigate**: Use the sidebar to access different features.
            """)
            st.info("💡 Tip: Start with the Overview page to get a snapshot of your inventory system!")

        with tab_features:
            st.subheader("🎯 Features Guide")
            st.markdown("### 📊 Overview")
            st.markdown("The Overview dashboard provides a snapshot of total inventory, pending and urgent orders, products needing reorder, and warehouse utilization.")
            
            st.markdown("### 📦 Inventory Management")
            st.markdown("Track and manage your inventory by viewing current stock levels, warehouse capacity, and storage costs.")
            
            st.markdown("### 📋 Order Management")
            st.markdown("Handle all order-related tasks by tracking pending, urgent, and historical orders.")
            
            st.markdown("### 🔄 Optimization")
            st.markdown("Run distribution optimization to get a cost-effective fulfillment plan, view cost analysis, and monitor warehouse utilization post-allocation.")

        with tab_data:
            st.subheader("💾 Data Management Guide")
            st.markdown("### Data Format")
            with st.expander("Warehouse Data Format"):
                st.code("warehouse_id,name,capacity,current_stock,location,storage_cost,latitude,longitude\nW001,Mumbai Central,10000,7500,Mumbai,1200,19.0760,72.8777")
            with st.expander("Sales/Orders Data Format"):
                st.code("order_id,date,product_id,quantity,delivery_deadline,status,delivery_latitude,delivery_longitude\nORD001,2025-03-24,P001,500,2025-03-26,Pending,19.0760,72.8777")
            with st.expander("Inventory Levels Data Format"):
                st.code("warehouse_id,product_id,current_stock\nW001,PROD001,450")
            
        with tab_optimize:
            st.subheader("⚙️ Optimization Guide")
            st.markdown("""
            1. **Prepare**: Ensure your data is up-to-date.
            2. **Configure**: Set parameters like solver time in the sidebar.
            3. **Execute**: Click "Run Optimization" and review the generated allocation plan.
            4. **Analyze**: Check the fulfillment rate, cost analysis, and address any unfulfilled orders.
            """)

    def show_overview_metrics(self):
        """Display key metrics in the overview section"""
        col1, col2, col3, col4 = st.columns(4)
        
        total_inventory = self.data_loader.warehouses_df['current_stock'].sum()
        total_capacity = self.data_loader.warehouses_df['capacity'].sum()
        
        with col1:
            st.metric("Total Inventory", f"{total_inventory:,} units", f"{(total_inventory/total_capacity)*100:.1f}% of capacity")
        
        pending_orders = len(self.data_loader.get_pending_orders(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        with col2:
            st.metric("Pending Orders", pending_orders)
        
        urgent_orders = len(self.data_loader.get_urgent_orders())
        with col3:
            st.metric("Urgent Orders", urgent_orders)
        
        reorder_needs = len(self.data_loader.calculate_reorder_needs())
        with col4:
            st.metric("Products to Reorder", reorder_needs)

    def show_inventory_status(self):
        """Display current inventory status"""
        st.subheader("📦 Inventory Status")
        warehouse_util = pd.DataFrame(self.data_loader.get_warehouse_utilization()).T
        st.bar_chart(warehouse_util['utilization'])
        st.dataframe(self.data_loader.get_current_inventory_status())

    def show_order_management(self):
        """Display order management section"""
        st.subheader("📋 Order Management")
        tabs = st.tabs(["Pending Orders", "Urgent Orders", "Order History"])
        
        with tabs[0]:
            pending_orders = self.data_loader.get_pending_orders(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.dataframe(pending_orders)
        with tabs[1]:
            urgent_orders = self.data_loader.get_urgent_orders()
            st.dataframe(urgent_orders)
        with tabs[2]:
            history = self.data_loader.get_order_history(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.dataframe(history)

    def show_distribution_map(self, warehouses, orders, allocation_results):
        """Display the distribution map visualization"""
        fig = go.Figure()

        fig.add_trace(go.Scattergeo(
            lon=warehouses['longitude'], lat=warehouses['latitude'],
            text=warehouses['name'], mode='markers', name='Warehouses',
            marker=dict(size=10, color='blue', symbol='square')
        ))

        fig.add_trace(go.Scattergeo(
            lon=orders['delivery_longitude'], lat=orders['delivery_latitude'],
            text=orders['order_id'], mode='markers', name='Delivery Locations',
            marker=dict(size=8, color='red', symbol='circle')
        ))

        for warehouse_id, allocations in allocation_results['allocation_plan'].items():
            warehouse = warehouses[warehouses['warehouse_id'] == warehouse_id].iloc[0]
            for allocation in allocations:
                order = orders[orders['order_id'] == allocation['order_id']].iloc[0]
                fig.add_trace(go.Scattergeo(
                    lon=[warehouse['longitude'], order['delivery_longitude']],
                    lat=[warehouse['latitude'], order['delivery_latitude']],
                    mode='lines', line=dict(width=1, color='green'),
                    name=f'Route: {warehouse_id} to {allocation["order_id"]}'
                ))

        fig.update_layout(title='Global Distribution Map', showlegend=True, geo=dict(projection_type='natural earth'))
        st.plotly_chart(fig, use_container_width=True)

    def run(self):
        """Run the Streamlit application"""
        if not st.session_state.logged_in:
            self.login_page()
            return

        st.title("🏭 LogiTrack: Inventory Management System")
        st.caption(f"Welcome back, {st.session_state.username}!")
        
        self.show_user_context()
        
        if not self.select_data_source():
            st.warning("Please select and configure a data source to continue")
            return

        st.sidebar.title("⚙️ Controls")
        action = st.sidebar.selectbox(
            "Select Action",
            ["Overview", "Inventory Management", "Order Management", "Optimization", "📚 User Guide"]
        )
        
        if action == "📚 User Guide":
            self.show_guide()
        elif action == "Overview":
            self.show_overview_metrics()
            self.show_inventory_status()
        elif action == "Inventory Management":
            self.show_inventory_status()
        elif action == "Order Management":
            self.show_order_management()
        elif action == "Optimization":
            st.subheader("🔄 Inventory Optimization")
            st.sidebar.subheader("Optimization Parameters")
            
            solver_time = st.sidebar.slider("Solver Time Limit (seconds)", 5, 60, 20)
            priority_weight = st.sidebar.select_slider("Order Priority Weight", options=["Low", "Medium", "High"], value="Medium")
            
            self.optimizer.solver_time = solver_time
            
            if st.button("🚀 Run Optimization"):
                try:
                    with st.spinner("Optimizing inventory distribution..."):
                        warehouses = self.data_loader.warehouses_df
                        orders = self.data_loader.get_pending_orders(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        
                        st.info("📊 Optimization Overview")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Warehouses in scope:", len(warehouses))
                            st.write("Current total stock:", f"{warehouses['current_stock'].sum():,} units")
                        with col2:
                            st.write("Pending orders:", len(orders))
                            st.write("Total order quantity:", f"{orders['quantity'].sum():,} units")
                        
                        results = self.optimizer.optimize(warehouses, orders, self.data_loader.inventory_df)
                        
                        st.success("✅ Optimization complete!")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Cost", f"${results['total_cost']:,.2f}")
                        with col2:
                            st.metric("Solving Time", f"{results['solving_time']:.2f}s")
                        with col3:
                            st.metric("Status", results['status'])
                        with col4:
                            if len(orders) > 0:
                                fulfilled_percent = (1 - (len(results['unfulfilled_orders']) / len(orders))) * 100
                                st.metric("Order Fulfillment", f"{fulfilled_percent:.1f}%")
                            else:
                                st.metric("Order Fulfillment", "N/A")

                        tabs = st.tabs(["Allocation Plan", "Warehouse Utilization", "Unfulfilled Orders", "Visualization"])
                        
                        with tabs[0]:
                            st.subheader("📦 Allocation Plan")
                            allocation_df = pd.DataFrame([
                                {'Warehouse': w, 'Order ID': item['order_id'], 'Quantity': item['quantity']}
                                for w, order_list in results['allocation_plan'].items() for item in order_list
                            ])
                            st.dataframe(allocation_df)
                        
                        with tabs[1]:
                            st.subheader("🏭 Warehouse Utilization")
                            st.write("Note: This is a conceptual view in the simplified model.")
                            st.dataframe(pd.DataFrame(results.get('warehouse_utilization', {}).items(), columns=['Warehouse', 'Utilization Info']))
                        
                        with tabs[2]:
                            if results['unfulfilled_orders']:
                                st.warning("⚠️ Some orders could not be fulfilled")
                                st.dataframe(pd.DataFrame(results['unfulfilled_orders']))
                            else:
                                st.success("✅ All orders can be fulfilled!")
                        
                        with tabs[3]:
                            st.subheader("🗺️ Distribution Map")
                            self.show_distribution_map(warehouses, orders, results)

                except Exception as e:
                    st.error(f"Optimization error: {str(e)}")
                    st.error("Please check your data and try again")

        st.markdown("---")
        st.markdown(
            "<p style='text-align: center;'>© 2025 | Made with  ♥  by Adith Prajwal</p>", 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    app = LogiTrackApp()
    app.run()