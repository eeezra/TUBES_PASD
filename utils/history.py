def update_history_sosmed(history_sosmed, selected_sosmed, start_time, end_time, duration):
    history_sosmed.append({
        "Sosmed": selected_sosmed,
        "Start": start_time.strftime("%H:%M"),
        "End": end_time.strftime("%H:%M"),
        "Durasi (menit)": duration
    })
