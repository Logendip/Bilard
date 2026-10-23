import pygame

from physics import calculate_speed, calculate_kinetic_energy
from trajectory import draw_cue_and_trajectory


BACKGROUND = (16, 22, 19)
PANEL_COLOR = (28, 36, 32)
PANEL_BORDER = (66, 86, 72)
TEXT_COLOR = (235, 239, 230)
MUTED_COLOR = (157, 174, 161)
ACCENT_COLOR = (215, 176, 91)
GREEN_COLOR = (85, 177, 111)


class BilliardsRenderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 31)
        self.value_font = pygame.font.Font(None, 32)

    def draw_text(
        self,
        screen,
        text,
        x,
        y,
        color=TEXT_COLOR,
        text_font=None
    ):
        if text_font is None:
            text_font = self.font

        image = text_font.render(str(text), True, color)
        screen.blit(image, (int(x), int(y)))

    def draw_panel(self, screen, rect, color=PANEL_COLOR):
        pygame.draw.rect(
            screen,
            (8, 12, 10),
            (rect.x + 3, rect.y + 4, rect.width, rect.height),
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            PANEL_BORDER,
            rect,
            1,
            border_radius=12
        )

    def draw_button(self, screen, rect, text):
        hovered = rect.collidepoint(pygame.mouse.get_pos())

        color = (
            (65, 91, 68)
            if hovered
            else (43, 62, 48)
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (107, 151, 104),
            rect,
            1,
            border_radius=8
        )

        label = self.font.render(text, True, TEXT_COLOR)

        screen.blit(
            label,
            label.get_rect(center=rect.center)
        )

    def draw_power_slider(
        self,
        screen,
        slider_x,
        slider_y,
        slider_width,
        power,
        min_power,
        max_power
    ):
        self.draw_text(
            screen,
            "POWER",
            slider_x,
            5,
            MUTED_COLOR,
            self.small_font
        )

        self.draw_text(
            screen,
            str(power),
            slider_x + slider_width + 10,
            27,
            ACCENT_COLOR
        )

        track_y = slider_y + 8

        pygame.draw.line(
            screen,
            (65, 78, 68),
            (slider_x, track_y),
            (slider_x + slider_width, track_y),
            6
        )

        ratio = (
            (power - min_power)
            / (max_power - min_power)
        )

        knob_x = int(
            slider_x + ratio * slider_width
        )

        pygame.draw.line(
            screen,
            GREEN_COLOR,
            (slider_x, track_y),
            (knob_x, track_y),
            6
        )

        pygame.draw.circle(
            screen,
            ACCENT_COLOR,
            (knob_x, track_y),
            9
        )

        pygame.draw.circle(
            screen,
            (255, 239, 193),
            (knob_x - 2, track_y - 2),
            3
        )

    def draw_physics_panel(
        self,
        screen,
        panel_x,
        panel_y,
        panel_width,
        panel_height,
        cue_ball,
        cue_ball_active,
        object_balls,
        power,
        max_power
    ):
        rect = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        self.draw_panel(screen, rect)

        margin = max(
            12,
            int(panel_width * 0.07)
        )

        content_width = panel_width - margin * 2

        self.draw_text(
            screen,
            "PHYSICS",
            panel_x + margin,
            panel_y + 16,
            ACCENT_COLOR,
            self.title_font
        )

        self.draw_text(
            screen,
            "LIVE MEASUREMENTS",
            panel_x + margin,
            panel_y + 47,
            MUTED_COLOR,
            self.small_font
        )

        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (panel_x + margin, panel_y + 76),
            (panel_x + panel_width - margin, panel_y + 76),
            1
        )

        if cue_ball_active:
            speed = calculate_speed(cue_ball)
            energy = calculate_kinetic_energy(cue_ball)
        else:
            speed = 0.0
            energy = 0.0

        card_height = max(
            68,
            int(panel_height * 0.15)
        )

        card_gap = max(
            10,
            int(panel_height * 0.018)
        )

        card_y = panel_y + 88

        cards = [
            (
                "VELOCITY",
                f"{speed:.1f}",
                "pixels / second",
                (34, 47, 39),
                GREEN_COLOR
            ),
            (
                "KINETIC ENERGY",
                f"{energy:.1f}",
                "relative units",
                (47, 42, 32),
                ACCENT_COLOR
            ),
            (
                "SHOT POWER",
                f"{power} / {max_power}",
                "",
                (39, 42, 52),
                (135, 175, 240)
            )
        ]

        for title, value, unit, color, value_color in cards:
            card = pygame.Rect(
                panel_x + margin // 2,
                card_y,
                content_width + margin,
                card_height
            )

            self.draw_panel(screen, card, color)

            self.draw_text(
                screen,
                title,
                card.x + 12,
                card.y + 9,
                MUTED_COLOR,
                self.small_font
            )

            self.draw_text(
                screen,
                value,
                card.x + 12,
                card.y + 31,
                value_color,
                self.value_font
            )

            if unit and panel_width > 350:
                self.draw_text(
                    screen,
                    unit,
                    card.x + int(card.width * 0.48),
                    card.y + 40,
                    MUTED_COLOR,
                    self.small_font
                )

            if title == "SHOT POWER":
                bar_y = card.y + card.height - 12
                bar_width = card.width - 24

                pygame.draw.rect(
                    screen,
                    (62, 69, 75),
                    (
                        card.x + 12,
                        bar_y,
                        bar_width,
                        5
                    ),
                    border_radius=3
                )

                pygame.draw.rect(
                    screen,
                    value_color,
                    (
                        card.x + 12,
                        bar_y,
                        int(bar_width * power / max_power),
                        5
                    ),
                    border_radius=3
                )

            card_y += card_height + card_gap

        formula_y = min(
            card_y + 4,
            panel_y + panel_height - 100
        )

        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (panel_x + margin, formula_y),
            (panel_x + panel_width - margin, formula_y),
            1
        )

        self.draw_text(
            screen,
            "MATHEMATICAL MODEL",
            panel_x + margin,
            formula_y + 10,
            MUTED_COLOR,
            self.small_font
        )

        self.draw_text(
            screen,
            "v = sqrt(vx^2 + vy^2)",
            panel_x + margin,
            formula_y + 35,
            TEXT_COLOR,
            self.small_font
        )

        self.draw_text(
            screen,
            "E = m * v^2 / 2",
            panel_x + margin,
            formula_y + 57,
            TEXT_COLOR,
            self.small_font
        )

        self.draw_text(
            screen,
            f"Balls remaining: {len(object_balls)}",
            panel_x + margin,
            panel_y + panel_height - 25,
            MUTED_COLOR,
            self.small_font
        )

    def render(
        self,
        screen,
        width,
        table,
        cue_ball,
        cue_ball_active,
        object_balls,
        ball_radius,
        power,
        min_power,
        max_power,
        button_rect,
        slider_x,
        slider_y,
        slider_width,
        panel_x,
        panel_y,
        panel_width,
        panel_height
    ):
        screen.fill(BACKGROUND)

        self.draw_text(
            screen,
            "BILLIARDS",
            int(width * 0.035),
            17,
            TEXT_COLOR,
            self.title_font
        )

        self.draw_text(
            screen,
            "PHYSICS SIMULATION",
            int(width * 0.035),
            46,
            MUTED_COLOR,
            self.small_font
        )

        self.draw_button(screen, button_rect, "New rack")
        self.draw_power_slider(
            screen,
            slider_x,
            slider_y,
            slider_width,
            power,
            min_power,
            max_power
        )

        table.draw(screen)

        for ball in object_balls:
            ball.draw(screen)

        if cue_ball_active:
            cue_ball.draw(screen)
            draw_cue_and_trajectory(
                screen,
                table,
                cue_ball,
                object_balls,
                ball_radius,
                power
            )

        self.draw_physics_panel(
            screen,
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            cue_ball,
            cue_ball_active,
            object_balls,
            power,
            max_power
        )

        if not cue_ball_active:
            self.draw_text(
                screen,
                "Right-click on the table to place the cue ball",
                table.x,
                table.y + table.height + 15,
                ACCENT_COLOR,
                self.small_font
            )

        pygame.display.flip()
