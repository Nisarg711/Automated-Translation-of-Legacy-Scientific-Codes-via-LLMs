import math

def initialize(th, om, t):
    yes = 'y'
    print('Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> ')
    method = int(input().strip())
    if method != 1 and method != 2 and method != 3:
        print('must select 1, 2, or 3 ..')
        exit()
    
    print('initial angle, angular velocity, pendulum length?')
    th[0] = float(input().strip())
    om[0] = float(input().strip())
    ext = float(input().strip())
    t[0] = 0.0
    
    print('time step, damping const, force amp, frequency?')
    dt = float(input().strip())
    q = float(input().strip())
    fd = float(input().strip())
    dr = float(input().strip())
    
    print('set line, symbol?')
    ans = input().strip()
    if ans == yes:
        print('lsym, nsym ? -> ')
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1
    
    return ext, dt, q, fd, dr, method, lsym, nsym

def dv(om0, th0, t0, g, ext, q, fd, dr):
    dth = om0
    dom = -g/ext * math.sin(th0) - q * om0 + fd * math.sin(dr * t0)
    return dom, dth

def calculate(th, om, t, ext, dt, q, fd, dr, n, method):
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
            n[0] = i + 1
            return
    
    n[0] = nmax

def display(th, om, t, n):
    with open('graph.out', 'w') as f:
        f.write('Time(s)           Angle(rad)\n')
        for i in range(n[0]):
            f.write(f"{t[i]:<20} {th[i]:<20}\n")
    
    print('Data successfully written to graph.out for comparison.')

def main():
    th = [0.0] * 5003
    om = [0.0] * 5003
    t = [0.0] * 5003
    n = [0]
    
    ext, dt, q, fd, dr, method, lsym, nsym = initialize(th, om, t)
    calculate(th, om, t, ext, dt, q, fd, dr, n, method)
    display(th, om, t, n)

if __name__ == "__main__":
    main()