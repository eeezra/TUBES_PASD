#OOP Class untuk fitur sosmed tracking
class SosmedTracking:
    def __init__(self, selected_sosmed: str):
        self.selected_sosmed = selected_sosmed
        self.start_time = None

    def start_tracking(self):
        self.start_time = datetime.now()

    def stop_tracking(self):
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            return int(elapsed.total_seconds() / 60)
        return 0
