import math

from tools import vec
from typing import Tuple
from pid_controller import PidController


class SwerveModule:

    def __init__(self, pos_vec: Tuple[float, float]):
        self.pos_vec: Tuple[float, float] = pos_vec
        x, y = pos_vec
        self.parallel_vec: Tuple[float, float] = (-y, x)

        self.commanded_vel_vec: Tuple[float, float] = 0, 0
        self.commanded_rot_vel: float = 0

        self.commanded_trans_vel_vec: Tuple[float, float] = 0, 0
        self.commanded_rot_vel_vec: Tuple[float, float] = 0, 0

        # simulated values
        self.driving_motor_out: float = 0
        self.turning_motor_out: float = 0

        self.turning_motor_controller: PidController = PidController()
        self.turning_motor_target: float = 0

    def command(self, trans: Tuple[float, float], rot: float) -> None:
        self.commanded_trans_vel_vec = trans

        self.commanded_rot_vel = rot
        parallel_x, parallel_y = self.parallel_vec
        self.commanded_rot_vel_vec = parallel_x * rot, parallel_y * rot

        xtv, ytv = self.commanded_trans_vel_vec
        xr, yr = self.commanded_rot_vel_vec

        self.commanded_vel_vec = (xtv + xr, ytv + yr) # THE swerve math

    def update_motor_outs(self) -> None:
        xv, yv = self.commanded_vel_vec

        # driving
        self.driving_motor_out = math.sqrt(xv ** 2 + yv ** 2)

        # turning
        self.turning_motor_target = math.atan2(yv, xv)
        self.turning_motor_out = self.turning_motor_controller.calculate(self.turning_motor_target)

    def update_sim(self, delta_time: float) -> None:
        pass



