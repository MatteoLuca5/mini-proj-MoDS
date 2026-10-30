from utils import S

def reset_saving(x, q, p):
    new_state = x.copy()
    new_state[S.ELAPSED_TIME] = 0
    new_state[S.DX] = 0
    new_state[S.DY] = 0

    return new_state

def reset_none(x, q, p):
    return x

def reset_hit_x0(x, q, p):
    new_state = x.copy()
    new_state[S.X] = 0 # To not phase through walls due to numerical calculations
    new_state[S.DX] = 0

    return new_state

def reset_hit_y0(x, q, p):
    new_state = x.copy()
    new_state[S.Y] = 0
    new_state[S.DY] = 0

    return new_state

def reset_hit_xd(x, q, p):
    new_state = x.copy()
    new_state[S.X] = p.dx
    new_state[S.DX] = 0

    return new_state

def reset_hit_yd(x, q, p):
    new_state = x.copy()
    new_state[S.Y] = p.dy
    new_state[S.DY] = 0

    return new_state

def reset_wiping(x, q, p):
    new_state = x.copy()
    new_state[S.DX] = 0
    new_state[S.DY] = 0
    new_state[S.ELAPSED_TIME] = 0

    return new_state

def reset_heat_off(x, q, p):
    return x

def reset_loading(x, q, p):
    new_state = x.copy()
    new_state[S.ELAPSED_TIME] = 0

    return new_state

def reset_heat_on(x, q, p):
    new_state = x
    new_state[S.FIL] = p.new_fil_amount

    return new_state

def reset_moving_back(x, q, p):
    new_state = x.copy()
    new_state[S.ELAPSED_TIME] = 0

    return new_state

def reset_printing(x, q, p):
    return x