from typing import List
import math
from typing import Tuple


from swerve_module import SwerveModule
from tools import vec


class SwerveChassis:

    def __init__(
        self,
        module_count: int = 0,
        size: float = 0,
        modules: List[SwerveModule] = []
    ):
        self.modules: List[SwerveModule] = modules

        if len(modules) != 0:
            return

        for i in range(module_count):
            self.modules.append(SwerveModule(vec(
                size * math.sin(math.pi * (2 * i + 1.25 * module_count) / module_count),
                size * math.cos(math.pi * (2 * i + 1.25 * module_count) / module_count)
            )))

    def command(self, translational_vel: Tuple[float, float], angular_vel: float):
        for module in self.modules:
            module.command(translational_vel, angular_vel)