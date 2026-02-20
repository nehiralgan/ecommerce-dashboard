# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa config
st.set_page_config(page_title="E-Ticaret Analytics", page_icon="🛒", layout="wide")

# CSS ile özelleştirme
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Veri yükleme
@st.cache_data
def load_data():
    df = pd.read_excel('data/online_retail.xlsx')
    
    # Veri tiplerini kontrol et ve dönüştür
    print("Kolon tipleri:", df.dtypes)
    print("UnitPrice örnekleri:", df['UnitPrice'].head(10))
    
    # UnitPrice'ı sayıya çevir
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    
    # Quantity'yi sayıya çevir
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    
    # InvoiceDate'i datetime'a çevir
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    
    # NaN değerleri temizle
    df = df.dropna(subset=['CustomerID', 'Quantity', 'UnitPrice'])
    
    # Negatif değerleri sil
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    
    # Toplam tutar
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # Yardımcı kolonlar
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.to_period('M')
    df['MonthName'] = df['InvoiceDate'].dt.month_name()
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df['InvoiceDate'].dt.hour
    
    print("Dönüştürülmüş tipler:", df.dtypes)
    
    return df

df = load_data()

# Sidebar
st.sidebar.title("🛒 E-Commerce Analytics")
st.sidebar.markdown("---")

# Filtreler
min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()

st.sidebar.info(f"📅 Veri Aralığı: {min_date} - {max_date}")

selected_countries = st.sidebar.multiselect(
    "🌍 Ülkeler",
    options=df['Country'].unique(),
    default=['United Kingdom', 'Germany', 'France', 'Norway', 'EIRE']
)

# Filtreleme
if selected_countries:
    filtered_df = df[df['Country'].isin(selected_countries)]
else:
    filtered_df = df

# Ana Başlık
st.markdown('<p class="title">📊 Online Retail Analytics</p>', unsafe_allow_html=True)
st.markdown("---")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df['TotalPrice'].sum()
total_orders = filtered_df['InvoiceNo'].nunique()
total_customers = filtered_df['CustomerID'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

with col1:
    st.metric("💰 Toplam Gelir", f"${total_revenue:,.0f}")
with col2:
    st.metric("📦 Toplam Sipariş", f"{total_orders:,}")
with col3:
    st.metric("👥 Müşteri Sayısı", f"{total_customers:,}")
with col4:
    st.metric("🛍️ Ortalama Sipariş", f"${avg_order_value:,.2f}")

st.markdown("---")

# Grafikler
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📈 Aylık Gelir Trendi")
    monthly = filtered_df.groupby(filtered_df['InvoiceDate'].dt.to_period('M'))['TotalPrice'].sum().reset_index()
    monthly['InvoiceDate'] = monthly['InvoiceDate'].astype(str)
    
    fig_trend = px.bar(
        monthly, 
        x='InvoiceDate', 
        y='TotalPrice',
        labels={'InvoiceDate': 'Ay', 'TotalPrice': 'Gelir ($)'},
        color_discrete_sequence=['#1f77b4']
    )
    fig_trend.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_trend, use_container_width=True)

with row1_col2:
    st.subheader("🥧 Ülke Dağılımı (Top 10)")
    country_sales = filtered_df.groupby('Country')['TotalPrice'].sum().reset_index()
    country_sales = country_sales.nlargest(10, 'TotalPrice')
    
    fig_pie = px.pie(
        country_sales, 
        values='TotalPrice', 
        names='Country',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_pie, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("🏆 En Çok Satılan Ürünler (Top 15)")
    top_products = filtered_df.groupby('Description')['Quantity'].sum().reset_index()
    top_products = top_products.nlargest(15, 'Quantity')
    
    fig_products = px.bar(
        top_products, 
        x='Quantity', 
        y='Description',
        orientation='h',
        labels={'Description': 'Ürün', 'Quantity': 'Satılan Adet'},
        color_discrete_sequence=['#ff7f0e']
    )
    fig_products.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_products, use_container_width=True)

with row2_col2:
    st.subheader("🕐 Saatlere Göre Siparişler")
    hourly = filtered_df.groupby('Hour').size().reset_index(name='Orders')
    
    fig_hourly = px.bar(
        hourly, 
        x='Hour', 
        y='Orders',
        labels={'Hour': 'Saat', 'Orders': 'Sipariş Sayısı'},
        color_discrete_sequence=['#2ca02c']
    )
    fig_hourly.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig_hourly, use_container_width=True)

# Alt Grafikler
st.markdown("---")
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("📅 Günlere Göre Siparişler")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_names_tr = {'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba', 
                   'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'}
    
    daily = filtered_df.groupby('DayOfWeek').size().reset_index(name='Orders')
    daily['DayOfWeek_tr'] = daily['DayOfWeek'].map(day_names_tr)
    
    fig_daily = px.bar(
        daily, 
        x='DayOfWeek_tr', 
        y='Orders',
        category_orders={'DayOfWeek_tr': ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']},
        labels={'DayOfWeek_tr': 'Gün', 'Orders': 'Sipariş Sayısı'},
        color_discrete_sequence=['#d62728']
    )
    st.plotly_chart(fig_daily, use_container_width=True)

with row3_col2:
    st.subheader("💵 Birim Fiyat Dağılımı")
    # Outlier'ları çıkaralım
    price_data = filtered_df[filtered_df['UnitPrice'] < 50]
    
    fig_price = px.histogram(
        price_data, 
        x='UnitPrice',
        nbins=30,
        labels={'UnitPrice': 'Birim Fiyat ($)', 'count': 'Adet'},
        color_discrete_sequence=['#9467bd']
    )
    st.plotly_chart(fig_price, use_container_width=True)

# Data Table
st.markdown("---")
st.subheader("📋 Son Siparişler")
st.dataframe(
    filtered_df.sort_values('InvoiceDate', ascending=False).head(20)[['InvoiceNo', 'Description', 'Quantity', 'UnitPrice', 'TotalPrice', 'Country', 'InvoiceDate']],
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("---")
st.markdown("🚀 **Online Retail Analytics**")