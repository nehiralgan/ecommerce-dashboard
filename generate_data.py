# generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Türkiye şehirleri ve nüfus ağırlıkları
cities = {
    'İstanbul': 0.35, 'Ankara': 0.15, 'İzmir': 0.10,
    'Bursa': 0.05, 'Antalya': 0.05, 'Adana': 0.04,
    'Konya': 0.04, 'Gaziantep': 0.04, 'Kayseri': 0.03,
    'Eskişehir': 0.03, 'Diğer': 0.12
}

categories = ['Elektronik', 'Giyim', 'Ev & Yaşam', 'Kitap', 'Spor', 'Kozmetik']
products = {
    'Elektronik': ['Laptop', 'Telefon', 'Kulaklık', 'Tablet', 'Smartwatch'],
    'Giyim': ['Tişört', 'Kot Pantolon', 'Elbise', 'Ayakkabı', 'Mont'],
    'Ev & Yaşam': ['Halı', 'Perde', 'Vazo', 'Ayna', 'Lambader'],
    'Kitap': ['Roman', 'Bilim Kurgu', 'Biyografi', 'Ders Kitabı', 'Şiir'],
    'Spor': ['Koşu Bandı', 'Halter Seti', 'Yoga Matı', 'Bisiklet', 'Futbol Topu'],
    'Kozmetik': ['Ruj', 'Nemlendirici', 'Parfüm', 'Maskara', 'Güneş Kremi']
}

# 2000 sipariş oluştur
n_orders = 2000
start_date = datetime(2024, 1, 1)

data = {
    'order_id': [f'ORD-{i:06d}' for i in range(1, n_orders + 1)],
    'order_date': [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_orders)],
    'customer_id': [f'CUST-{np.random.randint(1000, 5000)}' for _ in range(n_orders)],
    'customer_age': np.random.randint(18, 65, n_orders),
    'customer_city': np.random.choice(list(cities.keys()), n_orders, p=list(cities.values())),
    'category': np.random.choice(categories, n_orders),
    'product': [np.random.choice(products[cat]) for cat in np.random.choice(categories, n_orders)],
    'quantity': np.random.randint(1, 5, n_orders),
    'unit_price': np.random.uniform(50, 5000, n_orders).round(2)
}

df = pd.DataFrame(data)
df['total_price'] = (df['quantity'] * df['unit_price']).round(2)
df['order_month'] = df['order_date'].dt.to_period('M')
df['day_of_week'] = df['order_date'].dt.day_name()

# data klasörüne kaydet
import os
os.makedirs('data', exist_ok=True)
df.to_csv('data/sales_data.csv', index=False)

print("✅ Veri seti oluşturuldu!")
print(f"Toplam {len(df)} sipariş")
print(df.head())