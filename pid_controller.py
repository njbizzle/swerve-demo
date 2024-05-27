

class PidController():
    def __init__(self, target: float = None):
        self.target: float = target

    def calculate(self, value_in: float) -> float:
        assert self.target is not None, "target not set"

        return self.target - value_in