import jax, jax.numpy as jnp
from functools import partial
import numpy as np
from utils import smoothstep
import geopandas

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

def italy(N, x0, y0):
    PATH = "ne_110m_admin_0_countries.zip"
    world = geopandas.read_file(PATH)
    italy = world[world["ADMIN"] == "Italy"].geometry.iloc[0]
    mainland = max(italy.geoms, key=lambda g: g.area)          # removing the islands
    P = np.array(mainland.exterior.coords)                      # closed: first == last
    P[:, 0] *= np.cos(np.radians(P[:, 1].mean()))
    P = P / 40 # Scaling it down

    M = 1024 # samples
    seg = np.hypot(*np.diff(P, axis=0).T) # straight line lengths connecting P's elements
    s = np.concatenate([[0], np.cumsum(seg)]) # coordinates in increasing order
    u = np.linspace(0, s[-1], M, endpoint=False)
    z = np.interp(u, s, P[:, 0]) + 1j * np.interp(u, s, P[:, 1])
     
    # fourier coefficients
    c = np.fft.fft(z) / M # These need to be mapped to real values, right now they are imaginary numbers
    ks = np.arange(N + 1) # (discrete) frequencies
    cp, cm = c[ks], c[-ks]               # c_k and c_{-k}
    ax = (cp + cm).real;  bx = (cm - cp).imag
    ay = (cp + cm).imag;  by = (cp - cm).real
    ax[0], ay[0] = x0, y0 #c[0].real, c[0].imag  # constant term (center of italy)
    bx[0] = by[0] = 0.0

    ax, bx, ay, by = map(jnp.asarray, (ax, bx, ay, by))
    k = jnp.asarray(ks, dtype=float)

    def path(t):
        """Real point [x(t), y(t)] on the curve, t in [0, 2*pi)."""
        cos_kt = jnp.cos(k * t)
        sin_kt = jnp.sin(k * t)
        return jnp.array([ax @ cos_kt + bx @ sin_kt,
                          ay @ cos_kt + by @ sin_kt])

    return path