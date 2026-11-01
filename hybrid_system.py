import jax, jax.numpy as jnp
from utils import *
from system_control import open_loop_control
from guards import make_events
from automaton import M, O, Automaton
import scipy.integrate as spintg

def simulate_hybrid_system(p: Params, A, B, C, CAAB, CAAA, sys, t_start, t_fin, y, max_events = 100):
    t = [t_start]

    const_temp = p.T_fill
    const_temp_input = np.sqrt(p.R_n / p.R_t_n * (200 - p.T_env)) # Steady state input needed to maintain 200

    q_t = [t_start]
    q = [Q(Mode.PRINTING, Automaton(0))]

    initial_nozzle = [
        (1/p.R_n) * const_temp_input,
        const_temp_input,
        const_temp
    ]

    u_print, p_func = open_loop_control(y, A, B, C, CAAB, CAAA, p)
    p0 = p_func(0.0)
    u_print = jax.jit(u_print)
    def y_straight(t, x0, y0, t_prog, t_return):

        def smooth_path(t, func, t_prog): # smoothstep, except the final values for velocity and acceleration are NOT zero. I had to calculate by hand
            # ax**5 + bx**4 + cx**3 + dx**2 + ex + f = p(x)
            # I want p(0) = 0,                 p'(0) = 0,                  p''(0) = 0
            #        p(x_fin) = p_func(x_fin), p'(x_fin) = p_func'(x_fin), p''(x_fin) = p_func''(x_fin)
            # Note: derivatives with respect to t/t_return, so parameters scaled accordingly
            vel_func = jax.jacfwd(func)
            accel_func = jax.jacfwd(vel_func)
            vel = t_return * vel_func(t_prog)
            accel = t_return**2 * accel_func(t_prog)
            pos = func(t_prog)

            a = accel/2 -3*vel + 6*pos
            b = -accel + 7*vel - 15*pos
            c = accel/2 - 4*vel + 10*pos

            return a*t**5 + b*t**4 + c*t**3

        return jnp.array([x0, y0]) + smooth_path(t / t_return, y, t_prog)

    u_straight, _ = open_loop_control(y_straight, A, B, C, CAAB, CAAA, p)
    u_straight = jax.jit(u_straight)


    x0 = np.concatenate((p0, initial_nozzle, [p.new_fil_amount, 0, 0, 0]))
    x = [x0]
    print(x)

    def controller(t, x, q, p):
        match q.mode:
            case Mode.PRINTING:
                return np.append(np.asarray([u_print(x[S.PROG])]), const_temp_input)
            case Mode.MOVING:
                if q.automaton.command == M.V:
                    return [0, -10, const_temp_input]
                else:
                    return [-10, 0, const_temp_input]
            case Mode.MOVING_BACK:
                return np.append(np.asarray([u_straight(x[S.ELAPSED_TIME], 0, 0, x[S.PROG], p.t_return)]), const_temp_input)
            case Mode.HEAT_OFF | Mode.LOADING:
                return [0, 0, 0]
            case _ :
                return [0, 0, const_temp_input]

    while t[-1] < t_fin:
        current_q = q[-1]
        current_x = x[-1]

        events = make_events(current_x, current_q, p, p_func)

        sol = spintg.solve_ivp(lambda t, x: 
                        sys(x, current_q, controller(t, x, current_q, p), p),
                        [t[-1], t_fin],
                        current_x,
                        events=events,
                        dense_output=True,
                        method='LSODA'
                        )

        hit = [i for i, te in enumerate(sol.t_events) if te.size > 0]

        if hit:

            t_event = sol.t_events[hit[0]][0]
            x_event = sol.y_events[hit[0]][0]
            new_x = events[hit[0]].reset(x_event.copy(), current_q, p)
            target = events[hit[0]].target
            new_q = target if isinstance(target, Q) else Q(target) # automatically put whatever is returned in a Q if isnt a Q already (see guards.py)

            t.extend(sol.t[sol.t < t_event])
            x.extend(sol.y.T[sol.t < t_event])
            t.append(t_event)
            x.append(new_x)
            q.append(new_q)
            q_t.append(t_event)

            if len(q) >= max_events:
                print("Maximum number of events reached (possible Zeno behavior).")
                break
        else:
            t.extend(sol.t[1:])
            x.extend(sol.y.T[1:])
            q_t.append(t_fin)
            q.append(current_q)
            break

    return np.array(t), np.array(x), np.array(q), np.array(q_t)