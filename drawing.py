import jax, jax.numpy as jnp
from utils import smoothstep

def lissajous(a, b, omega, delta, t_start, t_fin):
    def y(t):
        return jnp.array([
            a * jnp.sin(omega * t + delta),
            b * jnp.sin(t)
        ])

    return y

def straight(x_s, y_s, x0, y0, t_return):
    def y(t, x_s, y_s, x0, y0, t_return):
        return jnp.array([
            x0 + smoothstep(t / t_return) * (x_s - x0),
            y0 + smoothstep(t / t_return) * (y_s - y0)
        ])

    return y

def lissajous_centered(a, b, omega, delta, t_start, t_fin, dx, dy):
    def y(t):
        return jnp.array([
            a * jnp.sin(omega * t + delta) + dx/2,
            b * jnp.sin(t) + dy/2
        ])

    return y