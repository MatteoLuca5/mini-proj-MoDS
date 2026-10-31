import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch
from matplotlib.collections import LineCollection

from utils import S, Mode


def mode_segments(t, q, q_t):
    modes = [qq.mode for qq in q]
    segments = []
    for k in range(len(q_t) - 1):
        if q_t[k + 1] > q_t[k]:
            segments.append((q_t[k], q_t[k + 1], modes[k]))
    # Simulation stopped by max_events
    if t[-1] > q_t[-1]:
        segments.append((q_t[-1], t[-1], modes[-1]))
    return segments

# With the help of AI I can get a load of colors without having to define them
def mode_colors():
    cmap = plt.get_cmap("tab20")
    return {m: cmap((m - 1) % 20) for m in Mode}


def shade(ax, segs, colors, alpha=0.15):
    for t0, t1, m in segs:
        ax.axvspan(t0, t1, color=colors[m], alpha=alpha, lw=0)


def draw_area(ax, x, p, y_ref, n_ref):
    dx = getattr(p, "XD", p.dx)
    dy = getattr(p, "YD", p.dy)
    ax.add_patch(Rectangle((0, 0), dx, dy, fill=False, ls="--", color="k"))
    if y_ref is not None:
        prog = np.linspace(0, x[:, S.PROG].max(), n_ref)
        ref = np.array([np.asarray(y_ref(s)) for s in prog])
        ax.plot(ref[:, 0], ref[:, 1], "k:", lw=1)
    return dx, dy


def plot_path(t, x, p, y_ref=None, n_ref=500):
    t = np.asarray(t)
    x = np.asarray(x)
    fig, ax = plt.subplots(figsize=(6, 6))
    dx, dy = draw_area(ax, x, p, y_ref, n_ref)

    trajectory_points = np.column_stack((x[:, S.X], x[:, S.Y]))
    segments = np.stack((trajectory_points[:-1], trajectory_points[1:]), axis=1)
    lc = LineCollection(segments, cmap="viridis", lw=2)
    lc.set_array(0.5 * (t[:-1] + t[1:]))
    ax.add_collection(lc)
    fig.colorbar(lc, ax=ax, label="Time [s]", shrink=0.8)

    ax.plot(trajectory_points[0, 0], trajectory_points[0, 1], "ko", ms=6, label="Start") # lil circle
    ax.plot(trajectory_points[-1, 0], trajectory_points[-1, 1], "ks", ms=6, label="End") #lil square

    margin = 0.1 * max(dx, dy)
    ax.set_xlim(min(trajectory_points[:, 0].min(), 0) - margin, max(trajectory_points[:, 0].max(), dx) + margin) # plot area
    ax.set_ylim(min(trajectory_points[:, 1].min(), 0) - margin, max(trajectory_points[:, 1].max(), dy) + margin) # ""
    ax.set_aspect("equal")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Printing trajectory (color = time)")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_hybrid(t, x, q, q_t, p, y_ref=None, n_ref=500):
    t = np.asarray(t)
    x = np.asarray(x)
    segments = mode_segments(t, q, q_t)
    colors = mode_colors()
    present = list(dict.fromkeys(m for _, _, m in segments))  # modes visited, in order

    # Figure 1 is the PATH described by tool head
    fig_xy, ax = plt.subplots(figsize=(6, 6))
    dx, dy = draw_area(ax, x, p, y_ref, n_ref)

    for t0, t1, m in segments:
        mask = (t >= t0) & (t <= t1)
        ax.plot(x[mask, S.X], x[mask, S.Y], color=colors[m], lw=1.5)

    ax.plot(x[0, S.X], x[0, S.Y], "ko", ms=6)

    handles = [Line2D([], [], color=colors[m], lw=2, label=m.name) for m in present]
    handles += [
        Line2D([], [], color="k", ls="--", label="Printing area"),
        Line2D([], [], color="k", ls=":", label="Printed part"),
        Line2D([], [], color="k", marker="o", ls="", label="Start"),
    ]
    ax.legend(handles=handles, fontsize=8, loc="upper right")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Printing path")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    fig_xy.tight_layout()

    fig_t, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)

    # Discrete mode
    ax = axs[0]
    ax.step(q_t, [qq.mode for qq in q], where="post", color="k")
    ax.set_yticks([int(m) for m in present], [m.name for m in present], fontsize=8)
    ax.set_title("Active mode")
    ax.grid(True, alpha=0.3)

    # Position in time
    ax = axs[1]
    shade(ax, segments, colors)
    ax.plot(t, x[:, S.X], label="x")
    ax.plot(t, x[:, S.Y], label="y")
    ax.axhline(0, color="k", lw=0.8)
    ax.axhline(dx, color="k", lw=0.8, ls="--")
    ax.set_ylabel("Position [m]")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # motor angular velocities (theta_l and theta_r derivatives)
    ax = axs[2]
    shade(ax, segments, colors)
    th_l = (x[:, S.DX] + x[:, S.DY]) / p.r_m
    th_r = (x[:, S.DX] - x[:, S.DY]) / p.r_m
    ax.plot(t, th_l, label=r"theta_l'")
    ax.plot(t, th_r, label=r"theta_r'")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Motor speed [rad/s]")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Nozzle temperature
    ax = axs[3]
    shade(ax, segments, colors)
    ax.plot(t, x[:, S.TN], color="tab:red", label=r"T_n")
    if hasattr(p, "hot_temp"):
        ax.axhline(p.hot_temp, color="tab:red", ls="--", lw=1, label="hot limit")
    if hasattr(p, "cold_temp"):
        ax.axhline(p.cold_temp, color="tab:blue", ls="--", lw=1, label="cold limit")
    ax.set_ylabel("Temperature [Celsius]")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Filament remaining
    ax = axs[4]
    shade(ax, segments, colors)
    ax.plot(t, x[:, S.FIL], color="tab:green", label="Filament left")
    ax.set_ylabel("Filament")
    ax2 = ax.twinx()
    ax2.plot(t, x[:, S.PROG], color="tab:purple", ls="--", label="PROG (progress)")
    ax2.set_ylabel("PROG [s]")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], fontsize=8, loc="upper right")
    ax.set_xlabel("Time [s]")
    ax.grid(True, alpha=0.3)

    fig_t.legend(
        handles=[Patch(color=colors[m], alpha=0.4, label=m.name) for m in present],
        loc="lower center", ncol=min(len(present), 6), fontsize=8,
    )
    fig_t.tight_layout(rect=(0, 0.04, 1, 1))

    fig_path = plot_path(t, x, p, y_ref=y_ref, n_ref=n_ref)
    return fig_xy, fig_t, fig_path