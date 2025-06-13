# ml_model.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Load data
df = pd.read_csv('https://raw.githubusercontent.com/eeezra/TUBES_PASD/main/dataset/mobile_usage_behavioral_analysis.csv')

# Fitur yang digunakan untuk clustering
usage_features = ['Daily_Screen_Time_Hours', 'Total_App_Usage_Hours',
                  'Social_Media_Usage_Hours', 'Productivity_App_Usage_Hours',
                  'Gaming_App_Usage_Hours']

# Standardisasi
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df[usage_features])

# KMeans clustering
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(scaled_data)

# Temukan cluster dengan penggunaan tertinggi
cluster_summary = df.groupby('Cluster')['Daily_Screen_Time_Hours'].mean().sort_values(ascending=False)
overuse_cluster = cluster_summary.idxmax()

# Hitung ambang batas penggunaan berlebihan
overuse_threshold = df[df['Cluster'] == overuse_cluster]['Daily_Screen_Time_Hours'].mean()

# Ekspor variabel yang dibutuhkan
__all__ = ['overuse_threshold', 'df']
