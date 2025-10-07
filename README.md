# LogiTrack : A Inventory Management System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2025--03--24-brightgreen)

A web-based inventory management and logistics optimization tool built with Python and Streamlit. This version focuses on core fulfillment logic to determine the most cost-effective way to allocate orders across a network of warehouses.

(Feel free to replace the image link with your own screenshot!)

🚀 Core Features
📊 Interactive Dashboard: A real-time overview of total inventory, pending orders, and products needing replenishment.

📦 Warehouse Management: Monitor individual warehouse utilization and view detailed stock levels.

📋 Smart Order Management: Prioritizes urgent orders using a hybrid logic that considers both manual flags (status) and upcoming deadlines (delivery_deadline).

🧠 Optimization Engine: Calculates the optimal fulfillment plan by balancing shipping distance and warehouse storage costs to minimize total operational expenses.

🔔 Reorder Alerts: Correctly identifies products with combined stock levels across all warehouses that have fallen below their defined reorder point.

🗺️ Geographic Visualization: Maps out the final allocation plan, showing the routes from warehouses to customer locations.

🛠️ Technology Stack
Backend: Python

Web Framework: Streamlit

Data Handling: Pandas, NumPy

Visualization: Plotly

💾 Data Model
The system runs on a set of simple CSV files located in the /data directory:

sample_warehouses.csv: Contains details for each warehouse (location, capacity, storage cost).

product_inventory.csv: A catalog of all products and their properties (cost, reorder point).

sample_sales.csv: A list of all customer orders, including their status and delivery destination.

inventory_levels.csv: (Key Table) A detailed breakdown of the stock level for each product within each specific warehouse.

⚙️ Getting Started
Follow these instructions to get the project running on your local machine.

Prerequisites
Python 3.9 or higher

pip package manager

Git

Installation
Clone your repository:

Bash

git clone https://github.com/adithprajwalk/logitrack.git
cd logitrack
Create and activate a virtual environment:

On macOS/Linux:

Bash

python3 -m venv venv
source venv/bin/activate
On Windows:

Bash

python -m venv venv
venv\Scripts\activate
Install dependencies:
(Note: You will need to create a requirements.txt file first if you haven't already. You can do this by running pip freeze > requirements.txt in your activated environment.)

Bash

pip install -r requirements.txt
Run the application:

Bash

streamlit run src/app.py
Your browser should open with the application running.

🕹️ How to Use
Once the application is running, enter a username to log in.

In the sidebar, ensure "Sample Data" is selected as the data source. The app will load the included CSV files.

Navigate to the "Optimization" page using the sidebar.

Click the "🚀 Run Optimization" button.

Review the generated allocation plan, cost analysis, and map visualization.










