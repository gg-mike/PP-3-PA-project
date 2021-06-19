from numpy import sin, pi, sign

u_curr = 0.0


def calculate(start_velocity=0, end_velocity=10, angle=0, mass=1500, engine_torque=400,
              wheels_radius=0.41, wind=0, aerodynamic_drag=0.25, duration=120):
    global u_curr
    M = mass
    Tor = engine_torque
    r = wheels_radius
    Ca = aerodynamic_drag
    Fd = [-Tor / r, Tor / r]
    v = [start_velocity, end_velocity]
    v_w = wind
    angle = angle * pi / 180

    T = {'i': 0.1, 'p': 0.1}

    e = [0.0, 0.0]
    de = [0.0, 0.0]
    u = (-2, 2)
    u_curr = 0
    k_p = 1

    N = int(duration / T['p'])
    v_all = [v[0]]
    t_all = [0]
    a_all = [0]

    def clamp(val, mn, mx):
        if val < mn:
            return mn
        elif val > mx:
            return mx
        return val

    def e_calc(v_curr):
        e[0] = e[1]
        e[1] = v[1] - v_curr

        de[0] = de[1]
        de[1] = e[1] - e[0]

    def du_calc():
        return k_p * (de[1] + T['p'] / T['i'] * e[1])

    def fg_calc():
        return M * 9.81 * sin(angle)

    def fa_calc(v_curr):
        return sign(v_curr - v_w) * Ca * (v_curr - v_w) ** 2.0

    def fd_calc():
        global u_curr
        u_curr = clamp(u_curr, u[0], u[1])
        return (u_curr * (Fd[1] - Fd[0])) / (u[1] - u[0])

    def v_all_calc(v_num):
        global u_curr
        v_curr = v_all[v_num - 1]
        e_calc(v_curr)
        u_curr += du_calc()
        return ((fd_calc() - (fg_calc() + fa_calc(v_curr))) / M) * T['p'] + v_curr

    for n in range(1, N + 1):
        v_all.append(v_all_calc(n))
        t_all.append(float(n * T['p']))
        a_all.append((v_all[n] - v_all[n-1]) / T['p'])

    for i in range(0, N + 1):
        v_all[i] *= 3.6

    return [t_all, v_all, a_all]
