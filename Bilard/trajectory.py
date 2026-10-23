
import math
import pygame


def draw_dashed_line(
    screen,
    start,
    end,
    color,
    dash_length=9,
    gap_length=7
):
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    position = 0

    while position < distance:
        segment_end = min(
            position + dash_length,
            distance
        )

        pygame.draw.line(
            screen,
            color,
            (
                int(start[0] + dx * position),
                int(start[1] + dy * position)
            ),
            (
                int(start[0] + dx * segment_end),
                int(start[1] + dy * segment_end)
            ),
            2
        )

        position += dash_length + gap_length


def draw_cue_and_trajectory(
    screen,
    table,
    cue_ball,
    object_balls,
    ball_radius,
    power
):
    if not cue_ball.is_moving() is False:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    dx = mouse_x - cue_ball.x
    dy = mouse_y - cue_ball.y

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    start_x = cue_ball.x
    start_y = cue_ball.y

    left = table.play_x + cue_ball.radius
    right = table.play_x + table.play_width - cue_ball.radius
    top = table.play_y + cue_ball.radius
    bottom = table.play_y + table.play_height - cue_ball.radius

    wall_distance = float("inf")

    if dx > 0:
        wall_distance = min(
            wall_distance,
            (right - start_x) / dx
        )
    elif dx < 0:
        wall_distance = min(
            wall_distance,
            (left - start_x) / dx
        )

    if dy > 0:
        wall_distance = min(
            wall_distance,
            (bottom - start_y) / dy
        )
    elif dy < 0:
        wall_distance = min(
            wall_distance,
            (top - start_y) / dy
        )

    collision_distance = wall_distance
    hit_ball = None

    for ball in object_balls:
        ox = ball.x - start_x
        oy = ball.y - start_y

        projection = ox * dx + oy * dy

        if projection <= 0:
            continue

        perpendicular_sq = (
            ox * ox + oy * oy - projection * projection
        )

        radius_sum = cue_ball.radius + ball.radius

        if perpendicular_sq > radius_sum * radius_sum:
            continue

        offset = math.sqrt(
            max(
                0,
                radius_sum * radius_sum - perpendicular_sq
            )
        )

        hit_distance = projection - offset

        if 0 < hit_distance < collision_distance:
            collision_distance = hit_distance
            hit_ball = ball

    impact_x = start_x + dx * collision_distance
    impact_y = start_y + dy * collision_distance

    draw_dashed_line(
        screen,
        (start_x, start_y),
        (impact_x, impact_y),
        (240, 239, 205)
    )

    pygame.draw.circle(
        screen,
        (239, 105, 85),
        (int(impact_x), int(impact_y)),
        max(4, ball_radius // 3)
    )

    if hit_ball is not None:
        nx = (
            (impact_x - hit_ball.x)
            / (cue_ball.radius + hit_ball.radius)
        )

        ny = (
            (impact_y - hit_ball.y)
            / (cue_ball.radius + hit_ball.radius)
        )

        dot = dx * nx + dy * ny

        rx = dx - 2 * dot * nx
        ry = dy - 2 * dot * ny

        r_length = math.hypot(rx, ry)

        if r_length > 0:
            rx /= r_length
            ry /= r_length

            pygame.draw.circle(
                screen,
                (255, 230, 160),
                (int(hit_ball.x), int(hit_ball.y)),
                hit_ball.radius + 5,
                2
            )

            draw_dashed_line(
                screen,
                (impact_x, impact_y),
                (
                    impact_x + rx * table.width * 0.35,
                    impact_y + ry * table.width * 0.35
                ),
                (100, 220, 255)
            )

    else:
        rx = dx
        ry = dy

        if (
            abs(impact_x - left) < 2
            or abs(impact_x - right) < 2
        ):
            rx = -rx

        if (
            abs(impact_y - top) < 2
            or abs(impact_y - bottom) < 2
        ):
            ry = -ry

        remaining = table.width * 0.35

        end_x = impact_x + rx * remaining
        end_y = impact_y + ry * remaining

        pygame.draw.circle(
            screen,
            (255, 230, 160),
            (int(impact_x), int(impact_y)),
            max(4, ball_radius // 2),
            2
        )

        draw_dashed_line(
            screen,
            (impact_x, impact_y),
            (end_x, end_y),
            (100, 220, 255)
        )

    cue_length = ball_radius * 8 + power * 2

    cue_start = (
        cue_ball.x - dx * cue_length,
        cue_ball.y - dy * cue_length
    )

    cue_end = (
        cue_ball.x - dx * (cue_ball.radius + 3),
        cue_ball.y - dy * (cue_ball.radius + 3)
    )

    pygame.draw.line(
        screen,
        (48, 29, 19),
        cue_start,
        cue_end,
        max(5, ball_radius // 2)
    )

    pygame.draw.line(
        screen,
        (145, 87, 43),
        cue_start,
        cue_end,
        max(3, ball_radius // 3)
    )

    pygame.draw.line(
        screen,
        (220, 190, 135),
        (
            cue_start[0] + dx * 8,
            cue_start[1] + dy * 8
        ),
        (
            cue_end[0] - dx * 5,
            cue_end[1] - dy * 5
        ),
        2
    )

