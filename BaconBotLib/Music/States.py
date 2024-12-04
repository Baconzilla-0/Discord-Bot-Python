
class State:
    def __init__(self, Value):
        self.Value = Value


IDLE = State(0)
PLAYING = State(1)
PAUSED = State(2)
QUEUED = State(99)