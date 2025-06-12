# OOP Class untuk fitur pomodoro timer
from datetime import datetime, timedelta

class PomodoroTimer:
    def __init__(self, duration: int, break_duration: int):
        self.duration = duration
        self.break_duration = break_duration
        self.start_time = None
        self.end_time = None
        self.break_time = None
        self.is_running = False
        self.is_paused = False
        self.remaining_time = timedelta(minutes=self.duration)

    def start(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.remaining_time
        self.is_running = True
        self.is_paused = False

    def pause(self):
        if self.is_running:
            self.remaining_time = self.end_time - datetime.now()
            self.is_paused = True
            self.is_running = False

    def resume(self):
        if self.is_paused:
            self.start()

    def reset(self):
        self.remaining_time = timedelta(minutes=self.duration)
        self.is_running = False
        self.is_paused = False

    def get_remaining_time(self):
        if self.is_running:
            return max(self.end_time - datetime.now(), timedelta(0))
        return self.remaining_time

    def stop(self):
        self.is_running = False
        self.is_paused = False
