
import pygame
import math


class Ball:
    def __init__(
        self,
        x,
        y,
        radius=12,
        color=(245, 245, 245),
        number=0,
        mass=1.0
    ):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.color = color
        self.number = number
        self.mass = float(mass)

        self.moment_of_inertia = (
            2.0 / 5.0
            * self.mass
            * self.radius ** 2
        )

        self.vx = 0.0
        self.vy = 0.0

        self.wx = 0.0
        self.wy = 0.0
        self.wz = 0.0

        self.spin = 0.0
        self.side_spin = 0.0

        self.rotation_angle = 0.0

        self.orientation = [1.0, 0.0, 0.0, 0.0]

    def update_orientation(self, dt):
        wx = self.wx
        wy = self.wy
        wz = self.wz

        angular_speed = math.sqrt(
            wx * wx + wy * wy + wz * wz
        )

        if angular_speed < 1e-8 or dt <= 0:
            return

        half_angle = angular_speed * dt * 0.5

        sin_half = math.sin(half_angle) / angular_speed
        dw = math.cos(half_angle)
        dx = wx * sin_half
        dy = wy * sin_half
        dz = wz * sin_half

        qw, qx, qy, qz = self.orientation

        self.orientation = [
            dw * qw - dx * qx - dy * qy - dz * qz,
            dw * qx + dx * qw + dy * qz - dz * qy,
            dw * qy - dx * qz + dy * qw + dz * qx,
            dw * qz + dx * qy - dy * qx + dz * qw
        ]

        length = math.sqrt(
            sum(component * component for component in self.orientation)
        )

        if length > 1e-8:
            self.orientation = [
                component / length
                for component in self.orientation
            ]

    def rotate_vector(self, vector):
        qw, qx, qy, qz = self.orientation
        vx, vy, vz = vector

        tx = 2.0 * (qy * vz - qz * vy)
        ty = 2.0 * (qz * vx - qx * vz)
        tz = 2.0 * (qx * vy - qy * vx)

        return (
            vx + qw * tx + qy * tz - qz * ty,
            vy + qw * ty + qz * tx - qx * tz,
            vz + qw * tz + qx * ty - qy * tx
        )

    def _draw_number_patch(self, screen, x, y, r):
        if self.number <= 0:
            return

        normal = self.rotate_vector((0.0, 0.0, 1.0))

        if normal[2] <= 0.015:
            return

        axis_u = self.rotate_vector((1.0, 0.0, 0.0))
        axis_v = self.rotate_vector((0.0, 1.0, 0.0))

        patch_angle = math.asin(0.48)
        cos_angle = math.cos(patch_angle)
        sin_angle = math.sin(patch_angle)

        points_3d = []
        segments = 48

        for i in range(segments):
            angle = 2.0 * math.pi * i / segments

            tangent_u = math.cos(angle)
            tangent_v = math.sin(angle)

            px = (
                normal[0] * cos_angle
                + (
                    axis_u[0] * tangent_u
                    + axis_v[0] * tangent_v
                ) * sin_angle
            )

            py = (
                normal[1] * cos_angle
                + (
                    axis_u[1] * tangent_u
                    + axis_v[1] * tangent_v
                ) * sin_angle
            )

            pz = (
                normal[2] * cos_angle
                + (
                    axis_u[2] * tangent_u
                    + axis_v[2] * tangent_v
                ) * sin_angle
            )

            points_3d.append((px, py, pz))

        clipped = []
        previous = points_3d[-1]

        for current in points_3d:
            previous_visible = previous[2] > 0.0
            current_visible = current[2] > 0.0

            if previous_visible != current_visible:
                denominator = current[2] - previous[2]

                if abs(denominator) > 1e-8:
                    t = -previous[2] / denominator

                    intersection = (
                        previous[0] + t * (current[0] - previous[0]),
                        previous[1] + t * (current[1] - previous[1]),
                        0.0
                    )

                    clipped.append(intersection)

            if current_visible:
                clipped.append(current)

            previous = current

        if len(clipped) < 3:
            return

        patch_points = [
            (
                round(x + point[0] * r),
                round(y + point[1] * r)
            )
            for point in clipped
        ]

        pygame.draw.polygon(
            screen,
            (246, 243, 227),
            patch_points
        )

        pygame.draw.polygon(
            screen,
            (185, 181, 164),
            patch_points,
            max(1, round(r * 0.035))
        )

        scale_u = math.hypot(axis_u[0], axis_u[1])
        scale_v = math.hypot(axis_v[0], axis_v[1])

        if min(scale_u, scale_v) < 0.06:
            return

        font_size = max(8, round(r * 0.88))
        font = pygame.font.Font(None, font_size)

        number_surface = font.render(
            str(self.number),
            True,
            (20, 20, 20)
        )

        scaled_width = max(
            1,
            round(number_surface.get_width() * scale_u)
        )

        scaled_height = max(
            1,
            round(number_surface.get_height() * scale_v)
        )

        number_surface = pygame.transform.smoothscale(
            number_surface,
            (scaled_width, scaled_height)
        )

        angle = -math.degrees(
            math.atan2(axis_u[1], axis_u[0])
        )

        number_surface = pygame.transform.rotate(
            number_surface,
            angle
        )

        center = (
            round(x + normal[0] * r),
            round(y + normal[1] * r)
        )

        screen.blit(
            number_surface,
            number_surface.get_rect(center=center)
        )

    def draw(self, screen):
        x = round(self.x)
        y = round(self.y)
        r = max(1, round(self.radius))

        pygame.draw.circle(
            screen,
            (12, 27, 18),
            (
                x + max(2, r // 5),
                y + max(3, r // 4)
            ),
            r
        )

        pygame.draw.circle(
            screen,
            self.color,
            (x, y),
            r
        )

        dark_color = tuple(
            max(0, int(channel * 0.55))
            for channel in self.color
        )

        pygame.draw.arc(
            screen,
            dark_color,
            (x - r, y - r, r * 2, r * 2),
            0.2,
            3.0,
            max(2, r // 5)
        )

        highlight_color = tuple(
            min(255, int(channel * 1.3 + 35))
            for channel in self.color
        )

        pygame.draw.circle(
            screen,
            highlight_color,
            (x - r // 3, y - r // 3),
            max(2, r // 2)
        )

        pygame.draw.circle(
            screen,
            (255, 255, 250),
            (x - r // 3, y - r // 3),
            max(1, r // 5)
        )

        self._draw_number_patch(
            screen,
            x,
            y,
            r
        )

        pygame.draw.circle(
            screen,
            (38, 38, 34),
            (x, y),
            r,
            1
        )

    def is_moving(self):
        linear_speed = math.hypot(
            self.vx,
            self.vy
        )

        angular_speed = math.sqrt(
            self.wx ** 2
            + self.wy ** 2
            + self.wz ** 2
        )

        return (
            linear_speed > 3
            or angular_speed > 0.1
        )

    def reset_motion(self):
        self.vx = 0.0
        self.vy = 0.0

        self.wx = 0.0
        self.wy = 0.0
        self.wz = 0.0

        self.spin = 0.0
        self.side_spin = 0.0

    def contains_point(self, position):
        mouse_x, mouse_y = position

        return (
            math.hypot(
                mouse_x - self.x,
                mouse_y - self.y
            )
            <= self.radius
        )
