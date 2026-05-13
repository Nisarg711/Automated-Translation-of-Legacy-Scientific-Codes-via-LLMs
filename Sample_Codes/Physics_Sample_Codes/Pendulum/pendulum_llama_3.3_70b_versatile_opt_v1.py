import math
import numpy as np

def initialize():
    """Get user input for simulation parameters."""
    print('Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> ')
    method = int(input())
    if method not in [1, 2, 3]:
        print('must select 1, 2, or 3 ..')
        exit()
    print('initial angle, angular velocity, pendulum length?')
    th0, om0, ext = map(float, input().split())
    print('time step, damping const, force amp, frequency?')
    dt, q, fd, dr = map(float, input().split())
    print('set line, symbol?')
    ans = input()
    if ans == 'y':
        print('lsym, nsym ? -> ')
        lsym, nsym = map(int, input().split())
    else:
        lsym = -1
        nsym = 1
    return th0, om0, ext, dt, q, fd, dr, lsym, nsym, method

def calculate(th0, om0, ext, dt, q, fd, dr, method):
    """Calculate pendulum motion using the specified method."""
    g = 9.8
    period = 6.2831853 / math.sqrt(g / ext)
    nmax = 5000
    th = np.zeros(nmax)
    om = np.zeros(nmax)
    t = np.zeros(nmax)
    th[0] = th0
    om[0] = om0
    t[0] = 0.0
    for i in range(1, nmax):
        t[i] = t[i-1] + dt
        if method == 1:
            dom, dth = dv(om[i-1], th[i-1], t[i-1], g, ext, q, fd, dr)
            om[i] = om[i-1] + dt * dom
            th[i] = th[i-1] + dt * dth
        elif method == 2:
            dom, dth = dv(om[i-1], th[i-1], t[i-1], g, ext, q, fd, dr)
            om[i] = om[i-1] + dt * dom
            th[i] = th[i-1] + dt * om[i]
        else:
            dom, dth = dv(om[i-1], th[i-1], t[i-1], g, ext, q, fd, dr)
            om1 = om[i-1] + 0.5 * dt * dom
            th1 = th[i-1] + 0.5 * dt * dth
            t1 = t[i-1] + 0.5 * dt
            dom2, dth2 = dv(om1, th1, t1, g, ext, q, fd, dr)
            om[i] = om[i-1] + dt * dom2
            th[i] = th[i-1] + dt * dth2
        if t[i] >= 10.0 * period:
            return th[:i+1], om[:i+1], t[:i+1]
    return th, om, t

def dv(om0, th0, t0, g, ext, q, fd, dr):
    """Calculate derivatives of pendulum motion."""
    dth = om0
    dom = -g / ext * math.sin(th0) - q * om0 + fd * math.sin(dr * t0)
    return dom, dth

def display(th, om, t, ext, dt, q, fd, dr, method):
    """Write pendulum motion data to file."""
    with open('graph.out', 'w') as f:
        f.write('Time(s)           Angle(rad)\n')
        for i in range(len(t)):
            f.write(f'{t[i]} {th[i]}\n')
    print('Data successfully written to graph.out for comparison.')
    return

def main():
    th0, om0, ext, dt, q, fd, dr, lsym, nsym, method = initialize()
    th, om, t = calculate(th0, om0, ext, dt, q, fd, dr, method)
    display(th, om, t, ext, dt, q, fd, dr, method)

if __name__ == '__main__':
    main()