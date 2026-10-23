import math
import pygame

from table import BilliardTable
from ball import Ball
from controls import handle_event
from game import rack_balls, update_all_balls, reset_game as reset_game_logic
from renderer import BilliardsRenderer


pygame.init()

WINDOW_SIZE = (1280, 720)

screen = pygame.display.set_mode(
    WINDOW_SIZE,
    pygame.RESIZABLE
)

pygame.display.set_caption("Billiards | Physics Simulation")

clock = pygame.time.Clock()
renderer = BilliardsRenderer()

min_power = 5
max_power = 15
power = 5

dragging_slider = False
cue_ball_active = True
object_balls = []

ball_colors = [
    (240, 195, 35),
    (40, 90, 215),
    (215, 45, 45),
    (120, 45, 165),
    (240, 125, 25),
    (30, 145, 75),
    (135, 40, 35),
    (25, 25, 25),
    (240, 195, 35),
    (40, 90, 215),
    (215, 45, 45),
    (120, 45, 165),
    (240, 125, 25),
    (30, 145, 75),
    (135, 40, 35)
]


def create_layout():
    global WIDTH, HEIGHT
    global table, cue_ball, button_rect
    global slider_x, slider_y, slider_width
    global panel_x, panel_y, panel_width, panel_height
    global ball_radius

    old_table = globals().get("table")
    old_cue_ball = globals().get("cue_ball")
    old_balls = list(object_balls)
    balls_to_preserve = []

    old_positions = {}
    if old_table is not None and old_cue_ball is not None:
        balls_to_preserve = [old_cue_ball] + old_balls
        for ball in balls_to_preserve:
            old_positions[id(ball)] = (
                ball.x,
                ball.y,
                getattr(ball, "vx", 0.0),
                getattr(ball, "vy", 0.0),
            )

    WIDTH, HEIGHT = screen.get_size()
    table = BilliardTable(WIDTH, HEIGHT)

    ball_radius = max(
        9,
        round(table.width * 12 / 1060)
    )

    if old_table is None or old_cue_ball is None:
        cue_ball = Ball(
            table.play_x + table.play_width // 4,
            table.play_y + table.play_height // 2,
            radius=ball_radius
        )
        rack_balls(table, ball_radius, ball_colors, object_balls)
    else:
        cue_ball = old_cue_ball

        scale_x = table.play_width / max(1, old_table.play_width)
        scale_y = table.play_height / max(1, old_table.play_height)

        for ball in balls_to_preserve:
            old_x, old_y, old_vx, old_vy = old_positions[id(ball)]
            normalized_x = (old_x - old_table.play_x) / max(1, old_table.play_width)
            normalized_y = (old_y - old_table.play_y) / max(1, old_table.play_height)

            ball.x = table.play_x + normalized_x * table.play_width
            ball.y = table.play_y + normalized_y * table.play_height
            ball.vx = old_vx * scale_x
            ball.vy = old_vy * scale_y
            ball.radius = ball_radius

    button_rect = pygame.Rect(
        int(WIDTH * 0.32),
        20,
        max(145, int(WIDTH * 0.12)),
        42
    )

    slider_x = int(WIDTH * 0.48)
    slider_y = 39
    slider_width = int(WIDTH * 0.12)

    panel_x = int(WIDTH * 0.74)
    panel_y = table.y
    panel_width = WIDTH - panel_x - int(WIDTH * 0.025)
    panel_height = table.height


def cue_position_is_valid(x, y):
    margin = cue_ball.radius

    if not (
        table.play_x + margin
        <= x
        <= table.play_x + table.play_width - margin
    ):
        return False

    if not (
        table.play_y + margin
        <= y
        <= table.play_y + table.play_height - margin
    ):
        return False

    for ball in object_balls:
        if math.hypot(
            x - ball.x,
            y - ball.y
        ) < cue_ball.radius + ball.radius:
            return False

    return True


def reset_game():
    global cue_ball_active

    cue_ball_active = reset_game_logic(
        table,
        cue_ball,
        object_balls,
        ball_radius,
        ball_colors
    )


create_layout()

running = True

while running:
    dt = min(
        clock.tick(60) / 1000.0,
        0.05
    )

    for event in pygame.event.get():
        state = {
            "running": running,
            "power": power,
            "dragging_slider": dragging_slider,
            "min_power": min_power,
            "max_power": max_power,
            "slider_x": slider_x,
            "slider_y": slider_y,
            "slider_width": slider_width,
            "button_rect": button_rect,
            "table": table,
            "cue_ball": cue_ball,
            "cue_ball_active": cue_ball_active,
            "reset_game": reset_game,
            "cue_position_is_valid": cue_position_is_valid
        }

        action = handle_event(event, state)

        running = state["running"]
        power = state["power"]
        dragging_slider = state["dragging_slider"]
        cue_ball_active = state["cue_ball_active"]

        if action is not None and action[0] == "resize":
            screen = pygame.display.set_mode(
                action[1],
                pygame.RESIZABLE
            )
            create_layout()

    cue_ball_active = update_all_balls(
        dt,
        cue_ball,
        cue_ball_active,
        object_balls,
        table
    )

    renderer.render(
        screen=screen,
        width=WIDTH,
        table=table,
        cue_ball=cue_ball,
        cue_ball_active=cue_ball_active,
        object_balls=object_balls,
        ball_radius=ball_radius,
        power=power,
        min_power=min_power,
        max_power=max_power,
        button_rect=button_rect,
        slider_x=slider_x,
        slider_y=slider_y,
        slider_width=slider_width,
        panel_x=panel_x,
        panel_y=panel_y,
        panel_width=panel_width,
        panel_height=panel_height
    )

pygame.quit()
