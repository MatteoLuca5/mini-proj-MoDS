import jax, jax.numpy as jnp

def open_loop_control(y, A, B, C, CAAB, CAAA, p):

    f1 = p.mu_r * p.r_m**2 / (p.r_b**2)
    f2 = p.r_m**2 / 2 * (p.mu_l_x + p.mu_l_y)
    f3 = p.r_m**2 / 2 * (p.mu_l_x - p.mu_l_y)
    
    C_m = p.r_m / (p.r_m * p.r_m * p.m + 2 * p.J_m)

    dydt = jax.jacfwd(y)
    
    dydt_2 = jax.jacfwd(dydt)
    
    dydt_3 = jax.jacfwd(dydt_2)
    
    def x(t, *args):
        r = y(t, *args)
        drdt = dydt(t, *args)
        drdt_2 = dydt_2(t, *args)
        return jnp.array([
        r[0],
        drdt[0],
        (1/(p.K_M*C_m)) * drdt_2[0] + (2 / (p.K_M*p.r_m)) * (4*f1 + f2 + f3) * drdt[0], #current calculated in terms of trajectory
        r[1],
        drdt[1],
        (1/(p.K_M*C_m)) * drdt_2[1] + (2 / (p.K_M*p.r_m)) * (2*f1 + f2 - f3) * drdt[1], #current calculated in terms of trajectory
    ])
    CAAB_inv = jnp.linalg.pinv(CAAB)
    
    def u(t, *args):
        return CAAB_inv @ (dydt_3(t, *args) - CAAA @ x(t, *args))

    return u, x