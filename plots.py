from IPython.display import HTML
import ipywidgets as widgets
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# With help of AI I managed to create an animated plot
def plot_q14(u_arr, y_arr, y_calculated, t):
    fig, axs = plt.subplots(2, 2, figsize=(12, 8), dpi = 60)

    # 2D ellipse
    desired_trajectory = axs[0, 0].plot(y_arr[0], y_arr[1], 'r--', label='Target shape', linewidth=0.2)
    calculated_trajectory, = axs[0, 0].plot([], [], 'b-', label='Actual trajectory', alpha=0.8)
    axs[0, 0].set_title('2D Tracking')
    axs[0, 0].set_xlabel('X Position')
    axs[0, 0].set_ylabel('Y Position')
    axs[0, 0].legend()
    axs[0, 0].grid(True)
    axs[0, 0].set_aspect('equal') # Keeps the ellipse from distorting

    # x over time
    axs[0, 1].plot(t, y_arr[0, :], 'r--', label='desired X', linewidth=2)
    calculated_x, = axs[0, 1].plot([], [], 'b-', label='calculated X')
    axs[0, 1].set_title('X-Axis position in time')
    axs[0, 1].set_xlabel('Time')
    axs[0, 1].set_ylabel('Position')
    axs[0, 1].legend()
    axs[0, 1].grid(True)

    # y over time
    axs[1, 0].plot(t, y_arr[1, :], 'r--', label='desired Y', linewidth=2)
    calculated_y, = axs[1, 0].plot([], [], 'b-', label='calculated Y')
    axs[1, 0].set_title('Y-Axis Position in Time')
    axs[1, 0].set_xlabel('Time')
    axs[1, 0].set_ylabel('Position')
    axs[1, 0].legend()
    axs[1, 0].grid(True)

    # inputs over time
    input_1, = axs[1, 1].plot([], [], label='Voltage U1', color='purple')
    input_2, = axs[1, 1].plot([], [], label='Voltage U2', color='orange')
    axs[1, 1].set_title('Required Control Inputs (Voltages)')
    axs[1, 1].set_xlabel('Time (s)')
    axs[1, 1].set_ylabel('Voltage')
    axs[1, 1].legend()
    axs[1, 1].grid(True)
    axs[1, 1].set_xlim(t[0], t[-1])
    axs[1, 1].set_ylim(u_arr.min() * 1.1, u_arr.max() * 1.1)

    def init_graphs_q14():
        calculated_trajectory.set_data([], [])
        calculated_x.set_data([], [])
        calculated_y.set_data([], [])
        input_1.set_data([], [])
        input_2.set_data([], [])
        return calculated_trajectory, calculated_x, calculated_y, input_1, input_2

    def update_graphs_q14(timestep):
        calculated_trajectory.set_data(y_calculated[0, :timestep], y_calculated[1, :timestep])
        calculated_x.set_data(t[:timestep], y_calculated[0, :timestep])
        calculated_y.set_data(t[:timestep], y_calculated[1, :timestep])
        input_1.set_data(t[:timestep], u_arr[0, :timestep])
        input_2.set_data(t[:timestep], u_arr[1, :timestep])
        return calculated_trajectory, calculated_x, calculated_y, input_1, input_2
    
    plt.tight_layout()
    
    
    ani = animation.FuncAnimation(fig, update_graphs_q14, frames=range(0, len(t), 5), init_func=init_graphs_q14, 
                                  interval=10, blit=False, repeat=False)

    plt.show()

    return ani

def plots_q16(T, num_blocks, dt, dx):
    time = np.arange(T.shape[1]) * dt
    pos = np.arange(num_blocks) * dx
    
    fig, axs = plt.subplots(2, 1, figsize=(8,8))
    m = axs[0].pcolormesh(time, pos, np.ma.masked_invalid(T), cmap="inferno", shading="auto")
    fig.colorbar(m, label="Temperature (Celsius)")
    axs[0].set_xlabel("time (s)")
    axs[0].set_ylabel("position along filament (m)")
    
    for i in (0, 5, num_blocks // 4, num_blocks // 2, num_blocks - 1):
        axs[1].plot(time, T[i], label=f"cell {i}")
    axs[1].set_xlabel("time (s)")
    axs[1].set_ylabel("Temperature (Celsius)")
    axs[1].legend()
    
    plt.show()

def plot_q16_over_time(T, num_blocks, num_timesteps, r, dt, p, step=20):
    fig, ax = plt.subplots()

    theta = 2*np.pi * np.arange(num_blocks) / num_blocks
    x_pts, y_pts = r*np.cos(theta), r*np.sin(theta)

    sc = ax.scatter(x_pts, y_pts, c=np.full(num_blocks, p.T_env),
                    cmap="inferno", vmin=p.T_env, vmax=p.T_fill, s=8)
    sc.cmap.set_bad(alpha=0)
    fig.colorbar(sc, label="Temperature (Celsius)")
    ax.set_aspect("equal")
    title = ax.set_title("t = 0s")
    plt.tight_layout()

    def update(k):
        sc.set_array(np.ma.masked_invalid(T[:, k]))
        title.set_text(f"t = {k*dt:.2f} s")
        return sc, title

    an = animation.FuncAnimation(fig, update, frames=range(0, num_timesteps, step),
                                  interval=30, blit=False, repeat=True)

    plt.show()
    
    return an