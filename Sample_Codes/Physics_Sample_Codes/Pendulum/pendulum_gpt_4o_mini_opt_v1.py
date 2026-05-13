import math

def initialize(th, om, t):
    print('Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> ')
    method = int(input().strip())
    if method not in {1, 2, 3}:
        print('must select 1, 2, or 3 ..')
        exit()
    
    print('initial angle, angular velocity, pendulum length?')
    th[0], om[0], ext = map(float, (input().strip(), input().strip(), input().strip()))
    t[0] = 0.0
    
    print('time step, damping const, force amp, frequency?')
    dt, q, fd, dr = map(float, (input().strip(), input().strip(), input().strip(), input().strip()))
    
    print('set line, symbol?')
    ans = input().strip()
    lsym, nsym = (map(int, (input().strip(), input().strip())) if ans == 'y' else (-1, 1))
    
    return ext, dt, q, fd, dr, method, lsym, nsym

def dv(om0, th0, t0, g, ext, q, fd, dr):
    dth = om0
    dom = -g/ext * math.sin(th0) - q * om0 + fd * math.sin(dr * t0)
    return dom, dth

def calculate(th, om, t, ext, dt, q, fd, dr, n, method):
    g = 9.8
    period = 2 * math.pi / math.sqrt(g / ext)
    nmax = 5000
    
    for i in range(1, nmax):
        t[i] = t[i-1] + dt
        dom, dth = dv(om[i-1], th[i-1], t[i-1], g, ext, q, fd, dr)
        
        if method == 1:
            om[i] = om[i-1] + dt * dom
            th[i] = th[i-1] + dt * dth
        elif method == 2:
            om[i] = om[i-1] + dt * dom
            th[i] = th[i-1] + dt * om[i]
        else:
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
        f.writelines(f"{t[i]:<20} {th[i]:<20}\n" for i in range(n[0]))
    
    print('Data successfully written to graph.out for comparison.')

def main():
    th, om, t = [0.0] * 5003, [0.0] * 5003, [0.0] * 5003
    n = [0]
    
    ext, dt, q, fd, dr, method, lsym, nsym = initialize(th, om, t)
    calculate(th, om, t, ext, dt, q, fd, dr, n, method)
    display(th, om, t, n)

if __name__ == "__main__":
    main()