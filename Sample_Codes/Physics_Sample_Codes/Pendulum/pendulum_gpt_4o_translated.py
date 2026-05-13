import math

def pendulum():
    # Declare the arrays we will need
    th = [0.0] * 5003
    om = [0.0] * 5003
    t = [0.0] * 5003

    # Use functions to do the work
    ext, dt, q, fd, dr, lsym, nsym, method = initialize(th, om, t)
    n = calculate(th, om, t, ext, dt, q, fd, dr, lsym, nsym, method)
    display(th, om, t, ext, dt, q, fd, dr, n, lsym, nsym, method)

def initialize(th, om, t):
    # Initialize variables
    print("Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> ")
    method = int(input().strip())
    if method not in [1, 2, 3]:
        print("must select 1, 2, or 3 ..")
        exit()

    print("initial angle, angular velocity, pendulum length?")
    th[0] = float(input().strip())
    om[0] = float(input().strip())
    ext = float(input().strip())
    t[0] = 0.0

    print("time step, damping const, force amp, frequency?")
    dt = float(input().strip())
    q = float(input().strip())
    fd = float(input().strip())
    dr = float(input().strip())

    print("set line, symbol?")
    ans = input().strip()
    yes = 'y'
    if ans == yes:
        print("lsym, nsym ? -> ")
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1

    return ext, dt, q, fd, dr, lsym, nsym, method

def calculate(th, om, t, ext, dt, q, fd, dr, lsym, nsym, method):
    # Now use the Euler method or the Runge-Kutta (2nd order)
    g = 9.8
    period = 6.2831853 / math.sqrt(g / ext)
    nmax = 5000

    for i in range(1, nmax):
        t[i] = t[i - 1] + dt
        if method == 1:
            dom, dth = dv(om[i - 1], th[i - 1], t[i - 1], g, ext, q, fd, dr)
            om[i] = om[i - 1] + dt * dom
            th[i] = th[i - 1] + dt * dth
        elif method == 2:
            dom, dth = dv(om[i - 1], th[i - 1], t[i - 1], g, ext, q, fd, dr)
            om[i] = om[i - 1] + dt * dom
            th[i] = th[i - 1] + dt * om[i]
        else:
            dom, dth = dv(om[i - 1], th[i - 1], t[i - 1], g, ext, q, fd, dr)
            om1 = om[i - 1] + 0.5 * dt * dom
            th1 = th[i - 1] + 0.5 * dt * dth
            t1 = t[i - 1] + 0.5 * dt
            dom2, dth2 = dv(om1, th1, t1, g, ext, q, fd, dr)
            om[i] = om[i - 1] + dt * dom2
            th[i] = th[i - 1] + dt * dth2

        if t[i] >= 10.0 * period:
            return i

    return nmax

def dv(om0, th0, t0, g, ext, q, fd, dr):
    dth = om0
    dom = -g / ext * math.sin(th0) - q * om0 + fd * math.sin(dr * t0)
    return dom, dth

def display(th, om, t, ext, dt, q, fd, dr, n, lsym, nsym, method):
    # Modified to write simple text output to "graph.out" for comparison.
    with open('graph.out', 'w') as f:
        f.write("Time(s)           Angle(rad)\n")
        for i in range(n):
            f.write(f"{t[i]:.6f} {th[i]:.6f}\n")

    print("Data successfully written to graph.out for comparison.")

if __name__ == "__main__":
    pendulum()