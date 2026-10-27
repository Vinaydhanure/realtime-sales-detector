import sqlite3
import random
import time
from datetime import datetime

# Create / Connect DB
conn = sqlite3.connect('sales.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    city TEXT,
    category TEXT,
    amount INTEGER,
    payment_status TEXT
)
''')
conn.commit()

cities = ['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad']
categories = ['Shoes', 'T-Shirts', 'Watches', 'Bags']

print("🔴 LIVE STREAM STARTED - Orders coming every 3 seconds...")
print("Keep this running. Open new terminal for dashboard.\n")

count = 0
while True:
    count += 1
    now = datetime.now()
    
    # After 50 orders, create a REAL problem for your project to detect
    if 50 < count < 90:
        city = 'Bangalore'
        category = 'Shoes'
        status = 'Failed' if random.random() > 0.2 else 'Success'
    else:
        city = random.choice(cities)
        category = random.choice(categories)
        status = 'Success' if random.random() > 0.15 else 'Failed'

    amount = random.randint(500, 5000)
    
    cursor.execute("INSERT INTO orders (timestamp, city, category, amount, payment_status) VALUES (?,?,?,?,?)",
                   (now, city, category, amount, status))
    conn.commit()
    
    print(f"[{now.strftime('%H:%M:%S')}] Order #{count} | {city} | {category} | Rs.{amount} | {status}")
    time.sleep(3)