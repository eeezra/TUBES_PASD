# Dokumentasi OOP

1. OOP untuk fitur challenge detox 

class ChallengeDetox:
    def __init__(self, challenge_name: str, duration: int):
        self.challenge_name = challenge_name
        self.duration = duration
        self.start_time = None
        self.end_time = None
        self.status = "not started"

    def start_challenge(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.duration)
        self.status = "started"

    def end_challenge(self):
        self.end_time = datetime.now()
        self.status = "success"
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def cancel_challenge(self):
        self.status = "cancelled"
        self.end_time = datetime.now()