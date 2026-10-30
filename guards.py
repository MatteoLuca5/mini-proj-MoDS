from utils import S, Q, Mode
from resets import *

def make_events(x, q, p, p_func):
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
            def g_x0_wall(t, x):
                return x[S.X]
            g_x0_wall.terminal = True
            g_x0_wall.direction = -1
            g_x0_wall.target = Mode.MOVING_X0
            g_x0_wall.reset = reset_hit_x0
            def g_y0_wall(t, x):
                return x[S.Y]
            g_y0_wall.terminal = True
            g_y0_wall.direction = -1
            g_y0_wall.target = Mode.MOVING_Y0
            g_y0_wall.reset = reset_hit_y0
            def g_xd_wall(t, x):
                return x[S.X] - p.dx
            g_xd_wall.terminal = True
            g_xd_wall.direction = 1
            g_xd_wall.target = Mode.MOVING_XD
            g_xd_wall.reset = reset_hit_xd
            def g_yd_wall(t, x):
                return x[S.Y] - p.dy
            g_yd_wall.terminal = True
            g_yd_wall.direction = 1
            g_yd_wall.target = Mode.MOVING_YD
            g_yd_wall.reset = reset_hit_yd
            return [g_x0_wall, g_xd_wall, g_y0_wall, g_yd_wall]
        case Mode.MOVING_X0:
            def g_yd_wall(t, x):
                return x[S.Y] - p.dy
            g_yd_wall.terminal = True
            g_yd_wall.direction = 1
            g_yd_wall.target = Mode.MOVING_YD
            g_yd_wall.reset = reset_hit_yd
            def g_hit_origin(t, x):
                return x[S.Y]
            g_hit_origin.terminal = True
            g_hit_origin.direction = -1
            g_hit_origin.target = Mode.WIPING
            g_hit_origin.reset = reset_wiping
            return [g_hit_origin, g_yd_wall]
        case Mode.MOVING_XD:
            def g_yd_wall(t, x):
                return x[S.Y] - p.dy
            g_yd_wall.terminal = True
            g_yd_wall.direction = 1
            g_yd_wall.target = Mode.MOVING_YD
            g_yd_wall.reset = reset_hit_yd
            def g_y0_wall(t, x):
                return x[S.Y]
            g_y0_wall.terminal = True
            g_y0_wall.direction = -1
            g_y0_wall.target = Mode.MOVING_Y0
            g_y0_wall.reset = reset_hit_y0
            return [g_y0_wall, g_yd_wall]
        case Mode.MOVING_Y0:
            def g_hit_origin(t, x):
                return x[S.X] + x[S.Y]
            g_hit_origin.terminal = True
            g_hit_origin.direction = -1
            g_hit_origin.target = Mode.WIPING
            g_hit_origin.reset = reset_wiping
            def g_xd_wall(t, x):
                return x[S.X] - p.dx
            g_xd_wall.terminal = True
            g_xd_wall.direction = 1
            g_xd_wall.target = Mode.MOVING_XD
            g_xd_wall.reset = reset_hit_xd
            return [g_hit_origin, g_xd_wall]
        case Mode.MOVING_YD:
            def g_x0_wall(t, x):
                return x[S.X]
            g_x0_wall.terminal = True
            g_x0_wall.direction = -1
            g_x0_wall.target = Mode.MOVING_X0
            g_x0_wall.reset = reset_hit_x0
            def g_xd_wall(t, x):
                return x[S.X] - p.dx
            g_xd_wall.terminal = True
            g_xd_wall.direction = 1
            g_xd_wall.target = Mode.MOVING_XD
            g_xd_wall.reset = reset_hit_xd
            return [g_x0_wall, g_xd_wall]
        case Mode.WIPING:
            def g_wiping(t, x):
                return x[S.ELAPSED_TIME] - p.t_wipe
            g_wiping.terminal = True
            g_wiping.direction = 1
            g_wiping.target = Mode.HEAT_OFF
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
