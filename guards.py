from utils import S, Q, Mode
from resets import *
from automaton import M, O, Automaton

def make_events(x, q, p, p_func):
    C_m = p.r_m / (p.r_m * p.r_m * p.m + 2 * p.J_m)
    match q.mode:
        case Mode.PRINTING:
            def g_print_color(t, x):
                return (t - p.t_c) # color change
            g_print_color.terminal = True
            g_print_color.direction = 1
            g_print_color.target = Mode.SAVING
            g_print_color.reset = reset_saving
            def g_print_fil(t, x):
                return x[S.FIL] # filament replacement needed
            g_print_fil.terminal = True
            g_print_fil.direction = -1
            g_print_fil.target = Mode.SAVING
            g_print_fil.reset = reset_saving
            return [g_print_color, g_print_fil]
        case Mode.SAVING:
            def g_saving(t, x):
                return x[S.ELAPSED_TIME] - p.t_saving
            g_saving.terminal = True
            g_saving.direction = 1
            g_saving.target = Mode.MOVING
            g_saving.reset = reset_none
            return [g_saving]
        case Mode.MOVING:
            cmd = q.automaton.command
            next_state = q.automaton.step(cmd, O.ZERO)
            if cmd == M.V:
                def g_wall(t, x):
                    return x[S.Y]
                g_wall.reset = reset_hit_y0
            else:
                def g_wall(t, x):
                    return x[S.X]
                g_wall.reset = reset_hit_x0
            g_wall.terminal = True
            g_wall.direction = -1
            g_wall.target = Q(Mode.WIPING, next_state) if next_state.accepting else Q(Mode.MOVING, next_state)
            return [g_wall]
        case Mode.WIPING:
            def g_wiping(t, x):
                return x[S.ELAPSED_TIME] - p.t_wipe
            g_wiping.terminal = True
            g_wiping.direction = 1
            g_wiping.target = Q(Mode.HEAT_OFF)
            g_wiping.reset = reset_heat_off
            return [g_wiping]
        case Mode.HEAT_OFF:
            def g_heat_off(t, x):
                return x[S.TN] - p.cold_temp
            g_heat_off.terminal = True
            g_heat_off.direction = -1
            g_heat_off.target = Mode.LOADING
            g_heat_off.reset = reset_loading
            return [g_heat_off]
        case Mode.LOADING:
            def g_loading(t, x):
                return x[S.ELAPSED_TIME] - p.t_loading
            g_loading.terminal = True
            g_loading.direction = 1
            g_loading.target = Mode.HEAT_ON
            g_loading.reset = reset_heat_on
            return [g_loading]
        case Mode.HEAT_ON:
            def g_heat_on(t, x):
                return x[S.TN] - p.hot_temp
            g_heat_on.terminal = True
            g_heat_on.direction = 1
            g_heat_on.target = Mode.MOVING_BACK
            g_heat_on.reset = reset_moving_back
            return [g_heat_on]
        case Mode.MOVING_BACK:
            def g_moving_back(t, x):
                return x[S.ELAPSED_TIME] - p.t_return
            g_moving_back.terminal = True
            g_moving_back.direction = 1
            g_moving_back.target = Mode.PRINTING
            g_moving_back.reset = reset_printing
            return [g_moving_back]
