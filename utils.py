from enum import IntEnum
from dataclasses import dataclass
import numpy as np

@dataclass
class Params:
    dx = 0.4
    dy = 0.4
    r_m = 0.01
    K_M = 0.1
    m = 0.1
    J_m = 1e-7
    L_m = 2e-6
    R_m = 150.0
    r_b = 0.003
    mu_r = 2e-9
    mu_l_x = 1e-5
    mu_l_y = 1e-5
    t_fin = 50
    L_n = 1e-3
    C_n = 1e-6
    R_n = 10.0
    C_t_n = 0.3
    R_t_n = 5.0
    rho_f = 1e3
    c_f = 1.5e3
    kappa_f = 0.2
    G_env = 0.016
    G_plate = 0.48
    a = 0.0004
    T_env = 23.0
    T_plate = 80.0
    T_fill = 200.0
    new_fil_amount = 5
    alpha = 0.4
    t_c = 2
    t_saving = 0.5
    t_wipe = 0.2
    t_loading = 0.5
    t_return = 3
    cold_temp = 40
    hot_temp = 180


class Mode(IntEnum):
    PRINTING = 1
    SAVING = 2
    MOVING = 3
    MOVING_X0 = 4
    MOVING_XD = 5
    MOVING_Y0 = 6
    MOVING_YD = 7
    WIPING = 8
    HEAT_OFF = 9
    LOADING = 10
    HEAT_ON = 11
    MOVING_BACK = 12
    STOPPING = 13

@dataclass
class Q:
    mode: Mode

class S(IntEnum):
    X = 0; DX = 1; I_X = 2;
    Y = 3; DY = 4; I_Y = 5;
    IN = 6; VC = 7; TN = 8;
    FIL = 9;
    PROG = 10;
    X_S = 11; Y_S = 12;
    TIME = 13; ELAPSED_TIME = 14;

class U(IntEnum):
    X = 0; Y = 1;
    N = 2;

state_size = len(S)
PRINTER = slice(S.X, S.I_Y + 1)
U_PRINTER = slice (U.X, U.Y+1)
NOZZLE  = slice(S.IN, S.TN + 1)
U_NOZZLE = U.N

# This is used to smoothly transition between two positions using open loop control
# Otherwise my input would have to be infinite to reach instantaneous acceleration!
def smoothstep(t):
    return 6*t**5 -15*t**4 + 10*t**3

def get_sys_matrices(p: Params):
    f1 = p.mu_r * p.r_m**2 / (p.r_b**2)
    f2 = p.r_m**2 / 2 * (p.mu_l_x + p.mu_l_y)
    f3 = p.r_m**2 / 2 * (p.mu_l_x - p.mu_l_y)
    
    C_m = p.r_m / (p.r_m * p.r_m * p.m + 2 * p.J_m)
    
    A = np.array([
        [0, 1, 0, 0, 0, 0],                             #position x
        [0, -2*(C_m / p.r_m)* (4*f1 + f2 + f3), C_m * p.K_M, 0, 0, 0],                           #velocity x
        [0, -2 * p.K_M / (p.r_m * p.L_m), -p.R_m / p.L_m, 0, 0, 0], #current x
        [0, 0, 0, 0, 1, 0],                             # position y
        [0, 0, 0, 0, -2*(C_m / p.r_m)* (2*f1 + f2 - f3), p.K_M*C_m],                           # velocity y
        [0, 0, 0, 0, -2 * p.K_M / (p.r_m * p.L_m), -p.R_m / p.L_m]  #current y
    ])
    
    B = np.array([
        [0, 0],
        [0, 0],
        [1/p.L_m, 0],
        [0, 0],
        [0, 0],
        [0, 1/p.L_m]
    ])
    
    
    C = np.array([
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0]
    ])
    
    CAAB = C @ A @ A @ B
    CAAA = C @ A @ A @ A

    return A, B, C, CAAB, CAAA