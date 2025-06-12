import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import time
from components.challenge import ChallengeDetox
from components.pomodoro import PomodoroTimer
from components.tracker import SosmedTracking
from utils.history import update_history_sosmed

# UI STYLE
st.set_page_config(page_title="FocusGuard - Detox App", layout="centered")
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #003049;
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.25rem;
        border-radius: 10px;
        border: none;
        font-size: 16px;
        transition: all 0.3s ease-in-out;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #780000;
        transform: scale(1.03);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Machine Learning
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd

# Load data (pastikan Anda sudah membaca file CSV ke dalam df)
url = 'https://raw.githubusercontent.com/eeezra/TUBES_PASD/main/dataset%20mobile_usage_behavioral_analysis.csv'
df = pd.read_csv(url)

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


# SESSION STATE
if 'history' not in st.session_state:
    st.session_state.history = []
if 'pomodoro_timer' not in st.session_state:
    st.session_state.pomodoro_timer = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'fokus_berjalan' not in st.session_state:
    st.session_state.fokus_berjalan = False
if 'sosmed_timer_start' not in st.session_state:
    st.session_state.sosmed_timer_start = None
if 'selected_sosmed' not in st.session_state:
    st.session_state.selected_sosmed = None
if 'history_sosmed' not in st.session_state:
    st.session_state.history_sosmed = []
if 'fitur' not in st.session_state:
    st.session_state.fitur = "Beranda"
if 'running_challenge' not in st.session_state:
    st.session_state.running_challenge = None

# UI NAVIGATION
st.title("FocusGuard - Digital Detox Tracker")
st.markdown("Fokusin waktumu, jauhin distraksi digital. Pilih fitur yang mau kamu pakai hari ini!")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🧠 Challenge Detox"):
        st.session_state.fitur = "Challenge Detox"
with col2:
    if st.button("⏱️ Pomodoro Timer"):
        st.session_state.fitur = "Pomodoro Timer"
with col3:
    if st.button("📱 Social Media Tracking"):
        st.session_state.fitur = "Social Media Tracking"

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("📊 Riwayat Penggunaan"):
        st.session_state.fitur = "Riwayat Penggunaan"

fitur = st.session_state.fitur

# FITUR CHALLENGE DETOX
if fitur == "Challenge Detox":
    st.subheader("💪 Mulai Challenge Baru")
    challenge_name = st.text_input("Nama Challenge", "", key="challenge_name")
    durasi_menit = st.slider("Durasi (menit)", 5, 180, 30)

    if st.button("🚀 Mulai Challenge"):
        if not challenge_name.strip():
            st.error("Nama challenge wajib diisi.")
        else:
            challenge = ChallengeDetox(challenge_name, durasi_menit)
            challenge.start_challenge()
            st.session_state.running_challenge = challenge
            st.session_state.history.append({
                "Tanggal": datetime.now().date(),
                "Challenge": challenge_name,
                "Status": challenge.status,
                "Start Time": challenge.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "End Time": "-",
                "Durasi (menit)": durasi_menit
            })
            st.success(f"Challenge '{challenge_name}' dimulai. Target: {durasi_menit} menit.")
            st.toast("Challenge dimulai. Tetap semangat!")

            countdown_placeholder = st.empty()
            progress_reminder_sent = False
            while datetime.now() < challenge.end_time:
                remaining = challenge.end_time - datetime.now()
                minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                elapsed_minutes = durasi_menit - int(remaining.total_seconds() // 60)

                if not progress_reminder_sent and elapsed_minutes >= durasi_menit / 2:
                    st.toast("💡 Tetap semangat! Challenge Detox kamu masih berlangsung.")
                    progress_reminder_sent = True

                countdown_placeholder.info(f"⏳ Waktu tersisa: {minutes:02d} menit {seconds:02d} detik")
                time.sleep(1)

            countdown_placeholder.success("🎉 Waktu challenge selesai!")
            st.toast("Selamat! Kamu telah menyelesaikan Challenge Detox 🎉")

            last = st.session_state.history[-1]
            last["Status"] = "success"
            last["End Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last["Durasi (menit)"] = durasi_menit
            st.session_state.running_challenge = None

    if st.button("❌ Batalkan Challenge Berjalan"):
        if st.session_state.running_challenge and st.session_state.running_challenge.status == "started":
            st.session_state.running_challenge.cancel_challenge()
            if st.session_state.history:
                last = st.session_state.history[-1]
                last["Status"] = "cancelled"
                last["End Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last["Durasi (menit)"] = int((datetime.now() - st.session_state.running_challenge.start_time).total_seconds() / 60)
            st.success("Challenge berhasil dibatalkan.")
            st.toast("Challenge telah dibatalkan ⛔")
            st.session_state.running_challenge = None
        else:
            st.warning("Tidak ada challenge yang sedang berjalan.")

    if st.button("✅ Tandai Challenge Terakhir Selesai"):
        if st.session_state.history:
            last = st.session_state.history[-1]
            if last["Status"] == "started":
                challenge = ChallengeDetox(last["Challenge"], last["Durasi (menit)"])
                challenge.start_time = datetime.strptime(last["Start Time"], "%Y-%m-%d %H:%M:%S")
                durasi = challenge.end_challenge()
                last["Status"] = challenge.status
                last["End Time"] = challenge.end_time.strftime("%Y-%m-%d %H:%M:%S")
                last["Durasi (menit)"] = durasi
                st.success(f"Challenge selesai dalam {durasi} menit. Good job!")
                st.toast("Challenge berhasil diselesaikan ✅")
            else:
                st.warning("Challenge terakhir sudah diselesaikan atau dibatalkan.")
        else:
            st.warning("Belum ada challenge yang dimulai.")

# FITUR POMODORO TIMER
elif fitur == "Pomodoro Timer":
    st.subheader("⏱️ Focus Mode - Pomodoro Timer")
    pomodoro_durasi = st.number_input("Durasi Fokus (menit)", min_value=5, max_value=60, value=25)
    break_durasi = st.number_input("Durasi Istirahat (menit)", min_value=1, max_value=15, value=5)

    if st.button("🎯 Mulai Sesi Pomodoro"):
        pomodoro = PomodoroTimer(pomodoro_durasi, break_durasi)
        pomodoro.start()
        st.session_state.pomodoro_timer = pomodoro
        st.session_state.fokus_berjalan = True
        st.session_state.pause = False
        st.success(f"Pomodoro dimulai. Fokus selama {pomodoro_durasi} menit!")
        st.toast("Pomodoro fokus dimulai 🚀")

    if st.session_state.pomodoro_timer:
        timer = st.session_state.pomodoro_timer
        col1, col2, col3 = st.columns(3)

        if col1.button("⏸️ Pause") and timer.is_running:
            timer.pause()
            st.session_state.fokus_berjalan = False
            st.session_state.pause = True
            st.toast("Timer dijeda ⏸️")

        if col2.button("▶️ Resume") and timer.is_paused:
            timer.resume()
            st.session_state.fokus_berjalan = True
            st.session_state.pause = False
            st.toast("Timer dilanjutkan ⏯️")

        if col3.button("🔁 Reset"):
            timer.reset()
            st.session_state.fokus_berjalan = False
            st.session_state.pause = False
            st.success("Timer direset ke waktu awal")

        if st.session_state.fokus_berjalan:
            countdown_placeholder = st.empty()
            remaining = timer.get_remaining_time()
            while remaining.total_seconds() > 0 and st.session_state.fokus_berjalan:
                remaining = timer.get_remaining_time()
                m, s = divmod(int(remaining.total_seconds()), 60)
                countdown_placeholder.info(f"⏳ Waktu tersisa: {m:02d} menit {s:02d} detik")
                time.sleep(1)
                if not st.session_state.fokus_berjalan:
                    break

            if remaining.total_seconds() <= 0:
                timer.stop()
                st.session_state.fokus_berjalan = False
                st.success(f"🍅 Sesi fokus selesai! Saatnya istirahat selama {break_durasi} menit.")
                st.toast("Sesi fokus selesai, masuk waktu istirahat 💤")

        elif st.session_state.pause:
            st.info("⏸️ Timer dijeda.")

# FITUR SOCIAL MEDIA TRACKING
elif fitur == "Social Media Tracking":
    st.subheader("📱 Social Media Tracking")
    tab1, tab2 = st.tabs(["🔴 Real-time Tracking", "✍️ Input Manual"])

    sosmed_list = {
        "Instagram": "📸 Instagram",
        "TikTok": "🎵 TikTok",
        "Twitter": "🐦 Twitter",
        "YouTube": "📺 YouTube",
        "Facebook": "📘 Facebook"
    }

    with tab1:
        selected = st.selectbox("Sosial media yang sedang kamu gunakan:", list(sosmed_list.values()))

        if st.button("▶️ Mulai Tracking Sosmed"):
            tracking = SosmedTracking(selected)
            tracking.start_tracking()
            st.session_state.sosmed_timer_start = tracking
            st.session_state.selected_sosmed = selected
            st.success(f"Tracking {selected} dimulai pada {tracking.start_time.strftime('%H:%M:%S')}")
            st.toast(f"Tracking {selected} dimulai 🕒")

        if st.session_state.sosmed_timer_start and st.session_state.selected_sosmed:
            elapsed = datetime.now() - st.session_state.sosmed_timer_start.start_time
            menit, detik = divmod(int(elapsed.total_seconds()), 60)
            st.info(f"⏳ Durasi sekarang: {menit:02d} menit {detik:02d} detik")

            if elapsed.total_seconds() >= 1500:
                st.warning(f"⛔ Sudah 25 menit di {st.session_state.selected_sosmed}. Saatnya rehat.")
                st.toast("Waktu penggunaan sosmed melebihi batas ⏰")
                update_history_sosmed(
                    st.session_state.history_sosmed,
                    st.session_state.selected_sosmed,
                    st.session_state.sosmed_timer_start.start_time,
                    datetime.now(), 25
                )
                st.session_state.sosmed_timer_start = None
                st.session_state.selected_sosmed = None
            else:
                if st.button("⏹️ Stop Manual"):
                    total_durasi = st.session_state.sosmed_timer_start.stop_tracking()
                    update_history_sosmed(
                        st.session_state.history_sosmed,
                        st.session_state.selected_sosmed,
                        st.session_state.sosmed_timer_start.start_time,
                        datetime.now(), total_durasi
                    )
                    st.success(f"Tracking {st.session_state.selected_sosmed} dihentikan.")
                    st.toast(f"Tracking {st.session_state.selected_sosmed} dihentikan 🛑")
                    st.session_state.sosmed_timer_start = None
                    st.session_state.selected_sosmed = None

    with tab2:
        manual_sosmed = st.selectbox("Pilih Sosial Media:", list(sosmed_list.values()), key="manual_sosmed")
        start_manual = st.time_input("Jam Mulai", key="manual_start")
        end_manual = st.time_input("Jam Selesai", key="manual_end")
        if st.button("➕ Tambahkan ke Riwayat"):
            start_dt = datetime.combine(datetime.today(), start_manual)
            end_dt = datetime.combine(datetime.today(), end_manual)
            if end_dt > start_dt:
                durasi_manual = int((end_dt - start_dt).total_seconds() / 60)
                update_history_sosmed(st.session_state.history_sosmed, manual_sosmed, start_dt, end_dt, durasi_manual)
                st.success(f"Riwayat {manual_sosmed} berhasil ditambahkan.")
                st.toast("Data manual ditambahkan ke riwayat 🗂️")
            else:
                st.error("Jam selesai harus lebih besar dari jam mulai.")

# FITUR RIWAYAT PENGGUNAAN
elif fitur == "Riwayat Penggunaan":
    st.subheader("📊 Riwayat Challenge")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Riwayat (CSV)", csv, "riwayat_challenge.csv", "text/csv")
        st.toast("Tabel riwayat challenge berhasil dimuat ✅")
    else:
        st.info("Belum ada data challenge.")

    st.subheader("📊 Riwayat Screen Time Sosmed Hari Ini")
    if st.session_state.history_sosmed:
        df_sosmed = pd.DataFrame(st.session_state.history_sosmed)
        st.dataframe(df_sosmed, use_container_width=True)

        total_duration_hours = df_sosmed["Durasi (menit)"].sum() / 60

        if total_duration_hours > overuse_threshold:
            st.warning("Penggunaan sudah melebihi batas rata-rata")

        fig = px.pie(df_sosmed, names="Sosmed", values="Durasi (menit)", title="Proporsi Penggunaan Sosmed")
        st.plotly_chart(fig, use_container_width=True)

        max_entry = df_sosmed.loc[df_sosmed["Durasi (menit)"].idxmax()]
        st.success(f"📌 Sosial media dengan durasi terbanyak hari ini: {max_entry['Sosmed']} ({max_entry['Durasi (menit)']} menit)")

        csv_sosmed = df_sosmed.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Screen Time (CSV)", csv_sosmed, "riwayat_sosmed.csv", "text/csv")
    else:
        st.info("Belum ada data penggunaan sosmed hari ini.")

