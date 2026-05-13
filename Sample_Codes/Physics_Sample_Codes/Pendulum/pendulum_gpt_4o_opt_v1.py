import math

def pendulum():
    th = [0.0] * 5003
    om = [0.0] * 5003
    t = [0.0] * 5003

    ext, dt, q, fd, dr, lsym, nsym, method = initialize(th, om, t)
    n = calculate(th, om, t, ext, dt, q, fd, dr, lsym, nsym, method)
    display(th, t, n)

def initialize(th, om, t):
    method = int(input("Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> ").strip())
    if method not in [1, 2, 3]:
        raise ValueError("Must select 1, 2, or 3.")

    th[0], om[0], ext = map(float, input("Initial angle, angular velocity, pendulum length? ").split())
    t[0] = 0.0

    dt, q, fd, dr = map(float, input("Time step, damping const, force amp, frequency? ").split())

    ans = input("Set line, symbol? (y/n) -> ").strip().lower()
    if ans == 'y':
        lsym, nsym = map(int, input("lsym, nsym? -> ").split())
    else:
        lsym, nsym = -1, 1

    return ext, dt, q, fd, dr, lsym, nsym, method

def calculate(th, om, t, ext, dt, q, fd, dr, lsym, nsym, method):
    g = 9.8
    period = 6.2831853 / math.sqrt(g / ext)
    nmax = 5000
    sin, cos = math.sin, math.cos

    for i in range(1, nmax):
        t_prev, th_prev, om_prev = t[i - 1], th[i - 1], om[i - 1]
        t[i] = t_prev + dt

        if method == 1:  # Euler
            dom, dth = dv(om_prev, th_prev, t_prev, g, ext, q, fd, dr, sin)
            om[i] = om_prev + dt * dom
            th[i] = th_prev + dt * dth
        elif method == 2:  # Euler-Cromer
            dom, _ = dv(om_prev, th_prev, t_prev, g, ext, q, fd, dr, sin)
            om[i] = om_prev + dt * dom
            th[i] = th_prev + dt * om[i]
        else:  # Runge-Kutta
            dom, dth = dv(om_prev, th_prev, t_prev, g, ext, q, fd, dr, sin)
            om1 = om_prev + 0.5 * dt * dom
            th1 = th_prev + 0.5 * dt * dth
            dom2, dth2 = dv(om1, th1, t_prev + 0.5 * dt, g, ext, q, fd, dr, sin)
            om[i] = om_prev + dt * dom2
            th[i] = th_prev + dt * dth2

        if t[i] >= 10.0 * period:
            return i

    return nmax

def dv(om0, th0, t0, g, ext, q, fd, dr, sin):
    dth = om0
    dom = -g / ext * sin(th0) - q * om0 + fd * sin(dr * t0)
    return dom, dth

def display(th, t, n):
    with open('graph.out', 'w') as f:
        f.write("Time(s)           Angle(rad)\n")
        f.writelines(f"{t[i]:.6f} {th[i]:.6f}\n" for i in range(n))

    print("Data successfully written to graph.out for comparison.")

if __name__ == "__main__":
    pendulum()