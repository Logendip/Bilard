
import pygame


class BilliardTable:
    def __init__(self, screen_width=1500, screen_height=760):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.x = int(screen_width * 0.035)
        self.width = int(screen_width * 0.68)
        self.height = min(
            int(self.width / 1.89),
            int(screen_height * 0.70)
        )
        self.y = max(
            95,
            int((screen_height - self.height + 80) / 2)
        )

        self.rail = max(24, int(self.width * 0.030))
        self.pocket_radius = max(18, int(self.width * 0.023))

        self.wood_color = (104, 57, 29)
        self.cloth_color = (29, 105, 59)
        self.pocket_color = (5, 6, 6)
        self.line_color = (220, 218, 195)

        self.play_x = self.x + self.rail
        self.play_y = self.y + self.rail
        self.play_width = self.width - 2 * self.rail
        self.play_height = self.height - 2 * self.rail

        self.pockets = [
            (self.play_x, self.play_y),
            (self.play_x + self.play_width // 2, self.play_y),
            (self.play_x + self.play_width, self.play_y),
            (self.play_x, self.play_y + self.play_height),
            (
                self.play_x + self.play_width // 2,
                self.play_y + self.play_height
            ),
            (
                self.play_x + self.play_width,
                self.play_y + self.play_height
            )
        ]

    def draw(self, screen):
        x = self.x
        y = self.y
        w = self.width
        h = self.height
        r = self.rail

        # Shadow
        pygame.draw.rect(
            screen,
            (5, 8, 6),
            (x + 8, y + 10, w, h),
            border_radius=15
        )

        # Dark outer edge
        pygame.draw.rect(
            screen,
            (43, 25, 16),
            (x - 4, y - 4, w + 8, h + 8),
            border_radius=16
        )

        # Wooden frame
        pygame.draw.rect(
            screen,
            (104, 57, 29),
            (x, y, w, h),
            border_radius=13
        )

        # Subtle wood grain
        for i in range(7):
            line_y = y + 9 + i * max(2, r // 5)

            pygame.draw.line(
                screen,
                (119, 70, 38),
                (x + 12, line_y),
                (x + w - 12, line_y),
                1
            )

        # Inner edge
        pygame.draw.rect(
            screen,
            (47, 32, 22),
            (
                self.play_x - 4,
                self.play_y - 4,
                self.play_width + 8,
                self.play_height + 8
            ),
            border_radius=4
        )

        # Cushion
        pygame.draw.rect(
            screen,
            (20, 68, 41),
            (
                self.play_x,
                self.play_y,
                self.play_width,
                self.play_height
            )
        )

        # Clean felt surface
        pygame.draw.rect(
            screen,
            self.cloth_color,
            (
                self.play_x + 3,
                self.play_y + 3,
                self.play_width - 6,
                self.play_height - 6
            )
        )

        # Soft light across the upper cushion
        pygame.draw.line(
            screen,
            (53, 124, 75),
            (self.play_x + 8, self.play_y + 5),
            (
                self.play_x + self.play_width - 8,
                self.play_y + 5
            ),
            2
        )

        # Head string
        head_x = self.play_x + self.play_width // 4

        pygame.draw.line(
            screen,
            self.line_color,
            (head_x, self.play_y + 8),
            (
                head_x,
                self.play_y + self.play_height - 8
            ),
            1
        )

        pygame.draw.circle(
            screen,
            self.line_color,
            (
                head_x,
                self.play_y + self.play_height // 2
            ),
            max(3, self.width // 350)
        )

        # Pocket openings
        for px, py in self.pockets:
            pygame.draw.circle(
                screen,
                (37, 25, 18),
                (px, py),
                self.pocket_radius + 5
            )

            pygame.draw.circle(
                screen,
                (8, 9, 8),
                (px, py),
                self.pocket_radius
            )

            pygame.draw.circle(
                screen,
                (2, 3, 2),
                (px, py),
                max(5, self.pocket_radius - 5)
            )

        # Rail diamonds
        for i in range(1, 8):
            px = self.play_x + self.play_width * i // 8

            for py in (y + r // 2, y + h - r // 2):
                pygame.draw.circle(
                    screen,
                    (218, 186, 126),
                    (px, py),
                    max(2, self.width // 500)
                )

        for i in range(1, 4):
            py = self.play_y + self.play_height * i // 4

            for px in (x + r // 2, x + w - r // 2):
                pygame.draw.circle(
                    screen,
                    (218, 186, 126),
                    (px, py),
                    max(2, self.width // 500)
                )

        # Frame highlight
        pygame.draw.rect(
            screen,
            (145, 91, 52),
            (x + 2, y + 2, w - 4, h - 4),
            2,
            border_radius=12
        )
