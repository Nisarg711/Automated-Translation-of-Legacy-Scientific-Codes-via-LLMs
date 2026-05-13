import math

def initialize(th, om, t, ext, dt, q, fd, dr, lsym, nsym, method):
    print('Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> ')
    method = int(input())
    if method not in [1, 2, 3]:
        print('must select 1, 2, or 3 ..')
        exit()
    print('initial angle, angular velocity, pendulum length?')
    th0 = input()
    om0 = input()
    ext0 = input()
    th[0], om[0], ext = map(float, [th0, om0, ext0])
    t[0] = 0.0
    print('time step, damping const, force amp, frequency?')
    dt0 = input()
    q0 = input()
    fd0 = input()
    dr0 = input()
    dt, q, fd, dr = map(float, [dt0, q0, fd0, dr0])
    print('set line, symbol?')
    ans = input()
    if ans == 'y':
        print('lsym, nsym ? -> ')
        lsym0 = input()
        nsym0 = input()
        lsym, nsym = map(int, [lsym0, nsym0])
    else:
        lsym = -1
        nsym = 1
    return th, om, t, ext, dt, q, fd, dr, lsym, nsym, method

def calculate(th, om, t, ext, dt, q, fd, dr, n, lsym, nsym, method):
    g = 9.8
    period = 6.2831853 / math.sqrt(g / ext)
    nmax = 5000
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
            n = i
            return th, om, t, n
    n = nmax
    return th, om, t, n

def dv(om0, th0, t0, g, ext, q, fd, dr):
    dth = om0
    dom = -g / ext * math.sin(th0) - q * om0 + fd * math.sin(dr * t0)
    return dom, dth

def display(th, om, t, ext, dt, q, fd, dr, n, lsym, nsym, method):
    with open('graph.out', 'w') as f:
        f.write('Time(s)           Angle(rad)\n')
        for i in range(n+1):
            f.write(f'{t[i]} {th[i]}\n')
    print('Data successfully written to graph.out for comparison.')
    return

def main():
    th = [0.0] * 5003
    om = [0.0] * 5003
    t = [0.0] * 5003
    ext = 0.0
    dt = 0.0
    q = 0.0
    fd = 0.0
    dr = 0.0
    lsym = 0
    nsym = 0
    method = 0
    n = 0
    th, om, t, ext, dt, q, fd, dr, lsym, nsym, method = initialize(th, om, t, ext, dt, q, fd, dr, lsym, nsym, method)
    th, om, t, n = calculate(th, om, t, ext, dt, q, fd, dr, n, lsym, nsym, method)
    display(th, om, t, ext, dt, q, fd, dr, n, lsym, nsym, method)

if __name__ == '__main__':
    main()