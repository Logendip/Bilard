from ball import Ball
from physics import update_ball, resolve_collision


def stop_ball_motion(ball):
    for attribute in ("vx", "vy", "wx", "wy", "wz"):
        if hasattr(ball, attribute):
            setattr(ball, attribute, 0.0)


def rack_balls(table, ball_radius, ball_colors, object_balls):
    object_balls.clear()

    start_x = table.play_x + table.play_width * 0.72
    center_y = table.play_y + table.play_height / 2

    spacing_x = ball_radius * 1.85
    spacing_y = ball_radius * 2.08

    number = 1

    for row in range(5):
        for column in range(row + 1):
            x = start_x + row * spacing_x
            y = center_y + (column - row / 2) * spacing_y

            object_balls.append(
                Ball(
                    x,
                    y,
                    radius=ball_radius,
                    color=ball_colors[number - 1],
                    number=number
                )
            )

            number += 1


def is_in_pocket(ball, table):
    for px, py in table.pockets:
        dx = ball.x - px
        dy = ball.y - py
        if (dx * dx + dy * dy) ** 0.5 < table.pocket_radius:
            return True

    return False


def update_all_balls(dt, cue_ball, cue_ball_active, object_balls, table):
    if cue_ball_active:
        update_ball(cue_ball, table, dt)

    for ball in object_balls:
        update_ball(ball, table, dt)

    all_balls = object_balls.copy()

    if cue_ball_active:
        all_balls.append(cue_ball)

    for _ in range(3):
        for i in range(len(all_balls)):
            for j in range(i + 1, len(all_balls)):
                resolve_collision(all_balls[i], all_balls[j])

    object_balls[:] = [
        ball
        for ball in object_balls
        if not is_in_pocket(ball, table)
    ]

    if cue_ball_active and is_in_pocket(cue_ball, table):
        cue_ball_active = False
        stop_ball_motion(cue_ball)

    return cue_ball_active


def reset_game(table, cue_ball, object_balls, ball_radius, ball_colors):
    rack_balls(table, ball_radius, ball_colors, object_balls)

    cue_ball.x = table.play_x + table.play_width // 4
    cue_ball.y = table.play_y + table.play_height // 2

    stop_ball_motion(cue_ball)

    # Some Ball implementations have an independent active flag or history.
    if hasattr(cue_ball, "active"):
        cue_ball.active = True
    if hasattr(cue_ball, "path"):
        cue_ball.path = [(cue_ball.x, cue_ball.y)]

    return True
