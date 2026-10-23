import pygame

from physics import strike
from game import stop_ball_motion


def _update_power_from_mouse(state, mouse_x):
    slider_width = state["slider_width"]
    if slider_width <= 0:
        return

    relative_x = max(
        0,
        min(mouse_x - state["slider_x"], slider_width)
    )

    state["power"] = round(
        state["min_power"]
        + relative_x / slider_width
        * (state["max_power"] - state["min_power"])
    )


def handle_event(event, state):
    if event.type == pygame.QUIT:
        state["running"] = False

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            state["running"] = False

    elif event.type == pygame.VIDEORESIZE:
        return ("resize", event.size)

    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos

        if event.button == 1:
            if state["button_rect"].collidepoint(event.pos):
                state["reset_game"]()
                state["cue_ball_active"] = True

            elif (
                state["slider_x"] - 10
                <= mouse_x
                <= state["slider_x"] + state["slider_width"] + 15
                and state["slider_y"] - 10
                <= mouse_y
                <= state["slider_y"] + 30
            ):
                state["dragging_slider"] = True

                _update_power_from_mouse(state, mouse_x)

            elif (
                state["cue_ball_active"]
                and not state["cue_ball"].is_moving()
                and state["table"].x
                <= mouse_x
                <= state["table"].x + state["table"].width
                and state["table"].y
                <= mouse_y
                <= state["table"].y + state["table"].height
            ):
                strike(
                    state["cue_ball"],
                    mouse_x,
                    mouse_y,
                    state["power"]
                )

        elif event.button == 3:
            # After the cue ball is pocketed it is inactive and may still have
            # a stale velocity in older Ball implementations. Allow placement
            # whenever it is inactive, then clear its motion.
            cue_ball = state["cue_ball"]
            cue_is_inactive = not state["cue_ball_active"]

            if cue_is_inactive or not cue_ball.is_moving():
                if state["cue_position_is_valid"](mouse_x, mouse_y):
                    cue_ball.x = mouse_x
                    cue_ball.y = mouse_y
                    stop_ball_motion(cue_ball)
                    if hasattr(cue_ball, "active"):
                        cue_ball.active = True
                    state["cue_ball_active"] = True

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            state["dragging_slider"] = False

    elif event.type == pygame.MOUSEMOTION:
        if state["dragging_slider"]:
            mouse_x = event.pos[0]

            _update_power_from_mouse(state, mouse_x)

    return None
