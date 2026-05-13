import numpy as np

def f(v, p, x, c, rho, a):
    return (p / v - c * rho * a * v**2) / x

def initialize():
    global dt, power, mass, nmax, c, area, density, lsym, nsym, method
    t = np.zeros(5003)
    velocity = np.zeros(5003)

    print('Euler (1) or Runge-Kutta (2)? -> ')
    method = int(input().strip())
    if method != 1 and method != 2:
        print('must select 1 or 2 ..')
        exit()

    print('initial velocity -> ')
    velocity[0] = float(input().strip())
    t[0] = 0

    print('time step -> ')
    dt = float(input().strip())
    
    print('max time -> ')
    tmax = float(input().strip())
    nmax = min(int(tmax / dt), 5000)

    print('constant power -> ')
    power = float(input().strip())
    
    mass = 70
    c = 0.5
    area = 0.33
    density = 1.29

    print('set line, symbol?')
    ans = input().strip()
    if ans == 'y':
        print('line and symbol numbers -> ')
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1

    return t, velocity

def calculate(t, velocity):
    if method == 1:
        for i in range(nmax - 1):
            velocity[i + 1] = velocity[i] + dt * f(velocity[i], power, mass, c, density, area)
            t[i + 1] = t[i] + dt
    else:
        for i in range(nmax - 1):
            v1 = velocity[i] + 0.5 * dt * f(velocity[i], power, mass, c, density, area)
            velocity[i + 1] = velocity[i] + dt * f(v1, power, mass, c, density, area)
            t[i + 1] = t[i] + dt

def display(t, velocity):
    with open('graph.out', 'w') as f:
        f.write('Time(s)           Velocity(m/s)\n')
        for i in range(nmax):
            f.write(f"{t[i]:<17} {velocity[i]:<15}\n")
    
    print('Data successfully written to graph.out for comparison.')

if __name__ == "__main__":
    t, velocity = initialize()
    calculate(t, velocity)
    display(t, velocity)