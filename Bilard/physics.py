import math


GRAVITY = 900.0

SLIDING_FRICTION = 0.18
ROLLING_RESISTANCE = 0.015

AIR_SPIN_DAMPING = 0.4

CUSHION_RESTITUTION = 0.85
BALL_RESTITUTION = 0.95

BALL_FRICTION = 0.08

STOP_SPEED = 3.0
STOP_SPIN = 0.5


def calculate_speed(ball):
    return math.hypot(ball.vx, ball.vy)


def calculate_angular_speed(ball):
    return math.sqrt(
        ball.wx ** 2
        + ball.wy ** 2
        + ball.wz ** 2
    )


def calculate_kinetic_energy(ball, mass=None):
    if mass is None:
        mass = ball.mass

    translational_energy = (
        0.5
        * mass
        * calculate_speed(ball) ** 2
    )

    rotational_energy = (
        0.5
        * ball.moment_of_inertia
        * (
            ball.wx ** 2
            + ball.wy ** 2
            + ball.wz ** 2
        )
    )

    return (
        translational_energy
        + rotational_energy
    )


def strike(
    ball,
    target_x,
    target_y,
    power,
    side_spin=0.0,
    vertical_spin=0.0
):
    dx = target_x - ball.x
    dy = target_y - ball.y

    distance = math.hypot(dx, dy)

    if distance < 0.001:
        return

    speed = max(0.0, float(power)) * 60.0

    ball.vx = dx / distance * speed
    ball.vy = dy / distance * speed

    ball.wx = -ball.vy / ball.radius
    ball.wy = ball.vx / ball.radius

    ball.wz = float(side_spin)
    ball.wx += float(vertical_spin)


def _limit_vector(x, y, maximum):
    length = math.hypot(x, y)

    if length > maximum and length > 0:
        factor = maximum / length
        return x * factor, y * factor

    return x, y



def _apply_table_friction(ball, dt):
    radius = max(ball.radius, 0.001)

    friction_acceleration = SLIDING_FRICTION * GRAVITY
    rolling_deceleration = ROLLING_RESISTANCE * GRAVITY

    remaining_dt = dt

    slip_x = ball.vx - radius * ball.wy
    slip_y = ball.vy + radius * ball.wx
    slip_speed = math.hypot(slip_x, slip_y)

    if slip_speed > 0.01:
        slip_deceleration = 3.5 * friction_acceleration
        time_to_roll = slip_speed / slip_deceleration

        sliding_dt = min(remaining_dt, time_to_roll)

        acceleration_x = (
            -friction_acceleration * slip_x / slip_speed
        )
        acceleration_y = (
            -friction_acceleration * slip_y / slip_speed
        )

        ball.vx += acceleration_x * sliding_dt
        ball.vy += acceleration_y * sliding_dt

        ball.wx += (
            2.5 * acceleration_y / radius * sliding_dt
        )
        ball.wy -= (
            2.5 * acceleration_x / radius * sliding_dt
        )

        remaining_dt -= sliding_dt

        if time_to_roll <= sliding_dt + 1e-9:
            ball.wx = -ball.vy / radius
            ball.wy = ball.vx / radius

    else:
        ball.wx = -ball.vy / radius
        ball.wy = ball.vx / radius

    if remaining_dt > 0:
        speed = calculate_speed(ball)

        if speed > 0.001:
            new_speed = max(
                0.0,
                speed - rolling_deceleration * remaining_dt
            )

            factor = new_speed / speed

            ball.vx *= factor
            ball.vy *= factor

            ball.wx = -ball.vy / radius
            ball.wy = ball.vx / radius

        else:
            ball.vx = 0.0
            ball.vy = 0.0
            ball.wx = 0.0
            ball.wy = 0.0

    spin_decay = math.exp(-AIR_SPIN_DAMPING * dt)
    ball.wz *= spin_decay

    if calculate_speed(ball) < STOP_SPEED:
        ball.vx = 0.0
        ball.vy = 0.0
        ball.wx = 0.0
        ball.wy = 0.0

    if abs(ball.wz) < STOP_SPIN:
        ball.wz = 0.0



def _apply_cushions(ball, table):
    left = table.play_x + ball.radius
    right = (
        table.play_x
        + table.play_width
        - ball.radius
    )

    top = table.play_y + ball.radius
    bottom = (
        table.play_y
        + table.play_height
        - ball.radius
    )

    if ball.x < left:
        ball.x = left

        if ball.vx < 0:
            ball.vx = (
                -ball.vx
                * CUSHION_RESTITUTION
            )

            ball.wz *= 0.85

    elif ball.x > right:
        ball.x = right

        if ball.vx > 0:
            ball.vx = (
                -ball.vx
                * CUSHION_RESTITUTION
            )

            ball.wz *= 0.85

    if ball.y < top:
        ball.y = top

        if ball.vy < 0:
            ball.vy = (
                -ball.vy
                * CUSHION_RESTITUTION
            )

            ball.wz *= 0.85

    elif ball.y > bottom:
        ball.y = bottom

        if ball.vy > 0:
            ball.vy = (
                -ball.vy
                * CUSHION_RESTITUTION
            )

            ball.wz *= 0.85


def update_ball(ball, table, dt):
    if dt <= 0:
        return

    dt = min(dt, 0.05)

    substeps = max(
        1,
        math.ceil(dt / 0.005)
    )

    step_dt = dt / substeps

    for _ in range(substeps):
        _apply_table_friction(
            ball,
            step_dt
        )

        ball.update_orientation(step_dt)


        ball.x += ball.vx * step_dt
        ball.y += ball.vy * step_dt

        ball.rotation_angle += (
            calculate_speed(ball)
            / max(ball.radius, 0.001)
            * step_dt
        )

        ball.rotation_angle %= (
            2.0 * math.pi
        )

        _apply_cushions(
            ball,
            table
        )


def resolve_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y

    distance = math.hypot(dx, dy)

    min_distance = (
        ball1.radius
        + ball2.radius
    )

    if distance >= min_distance:
        return

    if distance < 0.001:
        dx = 0.001
        dy = 0.0
        distance = 0.001

    nx = dx / distance
    ny = dy / distance

    tx = -ny
    ty = nx

    inverse_mass1 = 1.0 / ball1.mass
    inverse_mass2 = 1.0 / ball2.mass

    inverse_mass_sum = (
        inverse_mass1
        + inverse_mass2
    )

    overlap = min_distance - distance

    correction_percent = 0.8

    correction = (
        max(0.0, overlap - 0.01)
        * correction_percent
        / inverse_mass_sum
    )

    ball1.x -= (
        correction
        * inverse_mass1
        * nx
    )

    ball1.y -= (
        correction
        * inverse_mass1
        * ny
    )

    ball2.x += (
        correction
        * inverse_mass2
        * nx
    )

    ball2.y += (
        correction
        * inverse_mass2
        * ny
    )

    relative_vx = ball2.vx - ball1.vx
    relative_vy = ball2.vy - ball1.vy

    velocity_normal = (
        relative_vx * nx
        + relative_vy * ny
    )

    if velocity_normal >= 0:
        return

    impulse_normal = (
        -(1.0 + BALL_RESTITUTION)
        * velocity_normal
        / inverse_mass_sum
    )

    ball1.vx -= (
        impulse_normal
        * inverse_mass1
        * nx
    )

    ball1.vy -= (
        impulse_normal
        * inverse_mass1
        * ny
    )

    ball2.vx += (
        impulse_normal
        * inverse_mass2
        * nx
    )

    ball2.vy += (
        impulse_normal
        * inverse_mass2
        * ny
    )

    relative_vx = ball2.vx - ball1.vx
    relative_vy = ball2.vy - ball1.vy

    tangent_velocity = (
        relative_vx * tx
        + relative_vy * ty
        - ball1.wz * ball1.radius
        - ball2.wz * ball2.radius
    )

    inverse_inertia1 = (
        1.0 / ball1.moment_of_inertia
    )

    inverse_inertia2 = (
        1.0 / ball2.moment_of_inertia
    )

    tangent_denominator = (
        inverse_mass_sum
        + ball1.radius ** 2 * inverse_inertia1
        + ball2.radius ** 2 * inverse_inertia2
    )

    if tangent_denominator > 0:
        impulse_tangent = (
            -tangent_velocity
            / tangent_denominator
        )

        maximum_tangent_impulse = (
            BALL_FRICTION
            * impulse_normal
        )

        impulse_tangent = max(
            -maximum_tangent_impulse,
            min(
                impulse_tangent,
                maximum_tangent_impulse
            )
        )

        ball1.vx -= (
            impulse_tangent
            * inverse_mass1
            * tx
        )

        ball1.vy -= (
            impulse_tangent
            * inverse_mass1
            * ty
        )

        ball2.vx += (
            impulse_tangent
            * inverse_mass2
            * tx
        )

        ball2.vy += (
            impulse_tangent
            * inverse_mass2
            * ty
        )

        ball1.wz -= (
            ball1.radius
            * impulse_tangent
            * inverse_inertia1
        )

        ball2.wz -= (
            ball2.radius
            * impulse_tangent
            * inverse_inertia2
        )


def calculate_momentum(ball):
    return (
        ball.mass * ball.vx,
        ball.mass * ball.vy
    )


def calculate_total_kinetic_energy(balls):
    return sum(
        calculate_kinetic_energy(ball)
        for ball in balls
    )