import matplotlib.axes
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons

import time
from typing import Dict, List, Tuple, Callable, Self

# from inputs import devices, get_gamepad
from swerve_chassis import SwerveChassis
from swerve_module import SwerveModule
from tools import vec

import pygame
pygame.init()

try:
    controller: pygame.joystick = pygame.joystick.Joystick(0)
except pygame.error:
    print("Could not connect controller.")
    controller = None


class Arrow():
    def __init__(self,
        arrow: plt.arrow = None,
        size: float = 0.2,
        color: str = "b",
        module: SwerveModule = None,
        update: Callable[[Self], None] = None
    ):
        x, y = module.pos_vec

        self.arrow: plt.arrow = arrow or plt.arrow(
            x, y, 0,  0, head_width=size, head_length=size,
            length_includes_head=True, color=color
        )

        self.module: SwerveModule = module
        self.update: Callable[[Self], None] = update


def main() -> None:
    global controller

    plt.ion()

    x_vel: float = 0
    y_vel: float = 0
    rot_vel: float = 0

    x_vel_on_press: float = 5 # units per second per second
    y_vel_on_press: float = 5 # units per second per second
    rot_vel_on_press: float = 0.5 # radians per second per second


    key_bindings: Dict[str, str] = {
        "forward": "up",
        "back": "down",
        "left": "left",
        "right": "right",
        "rotate_left": "z",
        "rotate_right": "x",
    }

    controller_bindings: Dict[str, str] = {
        "x_vel": "0",
        "y_vel": "1",
        "rot_vel": "2"
    }

    size: int = 5
    w = 10
    h = 10

    swerve: SwerveChassis = SwerveChassis(modules=[
        SwerveModule((-w / 2, -h / 2)),
        SwerveModule((w / 2, -h / 2)),
        SwerveModule((-w / 2, h / 2)),
        SwerveModule((w / 2, h / 2))
    ])

    fig, ax = plt.subplots()


    # --- INPUT STUFF ---

    def key_pressed(key, pressed) -> None:
        nonlocal x_vel, y_vel, rot_vel

        if key == key_bindings["rotate_left"]:
            rot_vel = -rot_vel_on_press if pressed else 0
        elif key == key_bindings["rotate_right"]:
            rot_vel = rot_vel_on_press if pressed else 0
        elif key == key_bindings["forward"]:
            y_vel = y_vel_on_press if pressed else 0
        elif key == key_bindings["back"]:
            y_vel = -y_vel_on_press if pressed else 0
        elif key == key_bindings["left"]:
            x_vel = -x_vel_on_press if pressed else 0
        elif key == key_bindings["right"]:
            x_vel = x_vel_on_press if pressed else 0

    def check_controller(controller: pygame.joystick) -> None:
        nonlocal x_vel, y_vel, rot_vel

        if controller is None:
            return

        for event in pygame.event.get():
            try:
                axis: str = str(event.dict["axis"])
            except KeyError:
                continue

            val = event.dict["value"]

            if axis == controller_bindings["x_vel"]:
                x_vel = val * x_vel_on_press
            elif axis == controller_bindings["y_vel"]:
                y_vel = -val * y_vel_on_press
            elif axis == controller_bindings["rot_vel"]:
                rot_vel = val * rot_vel_on_press

    fig.canvas.mpl_connect('key_press_event', lambda event : key_pressed(event.key, True))
    fig.canvas.mpl_connect('key_release_event', lambda event : key_pressed(event.key, False))

    # --- ARROWS ---

    module_arrows: Dict[SwerveModule, Dict[str, Arrow]] = {}

    for module in swerve.modules:
        x, y = module.pos_vec

        plt.plot(x, y, "bo")

        def update_commanded_vel_arrow(arrow: Arrow) -> None:
            xv, yv = arrow.module.commanded_vel_vec
            arrow.arrow.set_data(dx=xv, dy=yv)

        def update_commanded_trans_arrow(arrow: Arrow) -> None:
            xtv, ytv = arrow.module.commanded_trans_vel_vec
            arrow.arrow.set_data(dx=xtv, dy=ytv)

        def update_commanded_rot_arrow(arrow: Arrow) -> None:
            rv = arrow.module.commanded_rot_vel
            xp, yp = arrow.module.parallel_vec

            arrow.arrow.set_data(dx=rv * xp, dy=rv * yp)

        def update_commanded_rot_tip_arrow(arrow: Arrow) -> None:
            rv = arrow.module.commanded_rot_vel
            xp, yp = arrow.module.parallel_vec

            x_org, y_org = arrow.module.pos_vec
            xc, yc = arrow.module.commanded_trans_vel_vec

            x_org += xc
            y_org += yc

            arrow.arrow.set_data(x=x_org, y=y_org, dx=rv * xp, dy=rv * yp)

        module_arrows[module] = {
            "Translational Velocity": Arrow(module=module, update=update_commanded_trans_arrow, color="r"),
            # "commanded_rot_arrow": Arrow(module=module, update=update_commanded_rot_arrow, color="r"),
            "Rotational Velocity": Arrow(module=module, update=update_commanded_rot_tip_arrow, color="r"),
            "Total Commanded Velocity": Arrow(module=module, update=update_commanded_vel_arrow, color="g", size=0.5)
        }

    bound = size * 3
    plt.axis((-bound, bound, -bound, bound))
    plt.subplots_adjust(left=0.3, bottom=0.3, right=0.7, top=0.95)

    labels: List[str] = []
    if len(swerve.modules) > 0:
        labels = list(module_arrows[swerve.modules[0]].keys())

    def update_arrow_check(arrow_checks: CheckButtons, swerve: SwerveChassis, module_arrows: Dict[SwerveModule, Dict[str, Arrow]]):
        statuses: List[bool] = arrow_checks.get_status()

        if not len(swerve.modules) > 0:
            return

        # multiline list comprehension :)
        arrow_groups = [
            [module_arrows[module][arrow_name]
                for module in swerve.modules]
                    for arrow_name in module_arrows[swerve.modules[0]].keys()
        ]

        for status, arrows in zip(statuses, arrow_groups):
            if not status:
                [arrow.arrow.set_alpha(0) for arrow in arrows]
            else:
                [arrow.arrow.set_alpha(1) for arrow in arrows]

    arrow_checks = CheckButtons(plt.axes((0.05, 0.05, 0.4, 0.15)), labels)
    arrow_checks.on_clicked(lambda _: update_arrow_check(arrow_checks, swerve, module_arrows))

    # --- UPDATE ---

    current_time: float = time.time()
    prev_time: float = current_time

    while True:
        check_controller(controller)

        current_time: float = time.time()

        swerve.command(vec(x_vel, y_vel), rot_vel)
        for module in swerve.modules:
            [arrow.update(arrow) for arrow in module_arrows[module].values()]

        fig.canvas.draw()
        fig.canvas.flush_events()

        prev_time = current_time


if __name__ == '__main__':
    main()
