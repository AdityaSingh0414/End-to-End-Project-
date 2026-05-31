import sqlite3
import pandas as pd
import numpy as np
import os

db_path = os.path.join('database', 'sqlite', 'sample.db')

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)

# 1. Customers Table
np.random.seed(42)
num_customers = 500
customers = pd.DataFrame({
    'customer_id': range(1, num_customers + 1),
    'name': [f"Customer_{i}" for i in range(1, num_customers + 1)],
    'segment': np.random.choice(['Corporate', 'Consumer', 'Home Office'], num_customers),
    'region': np.random.choice(['North', 'South', 'East', 'West'], num_customers),
    'signup_date': pd.date_range(start='2020-01-01', end='2023-12-31', periods=num_customers)
})
customers.to_sql('customers', conn, index=False, if_exists='replace')

# 2. Products Table
num_products = 50
products = pd.DataFrame({
    'product_id': range(1, num_products + 1),
    'product_name': [f"Product_{i}" for i in range(1, num_products + 1)],
    'category': np.random.choice(['Technology', 'Furniture', 'Office Supplies'], num_products),
    'price': np.random.uniform(10, 500, num_products).round(2),
    'cost': np.random.uniform(5, 200, num_products).round(2)
})
products.to_sql('products', conn, index=False, if_exists='replace')

# 3. Orders Table
num_orders = 2000
orders = pd.DataFrame({
    'order_id': range(1, num_orders + 1),
    'customer_id': np.random.choice(customers['customer_id'], num_orders),
    'order_date': pd.date_range(start='2022-01-01', end='2024-05-31', periods=num_orders),
    'status': np.random.choice(['Shipped', 'Processing', 'Cancelled'], num_orders, p=[0.8, 0.15, 0.05])
})
orders.to_sql('orders', conn, index=False, if_exists='replace')

# 4. Order Details (Items)
num_items = 5000
order_items = pd.DataFrame({
    'order_id': np.random.choice(orders['order_id'], num_items),
    'product_id': np.random.choice(products['product_id'], num_items),
    'quantity': np.random.randint(1, 10, num_items),
    'discount': np.random.choice([0, 0.05, 0.1, 0.2], num_items, p=[0.6, 0.2, 0.1, 0.1])
})

# Merge to get price and calculate revenue
merged = order_items.merge(products, on='product_id')
order_items['unit_price'] = merged['price']
order_items['revenue'] = (order_items['quantity'] * order_items['unit_price'] * (1 - order_items['discount'])).round(2)
order_items['profit'] = (order_items['revenue'] - (order_items['quantity'] * merged['cost'])).round(2)

order_items.drop(columns=['unit_price'], inplace=True) # just keep revenue and profit
order_items.to_sql('order_items', conn, index=False, if_exists='replace')

conn.close()
print(f"Sample database created successfully at {db_path}!")
