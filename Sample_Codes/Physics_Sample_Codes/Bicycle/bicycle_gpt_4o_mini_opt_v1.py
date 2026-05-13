import numpy as np

def f(v, p, x, c, rho, a):
    return (p / v - c * rho * a * v**2) / x

def initialize():
    global dt, power, mass, nmax, c, area, density, lsym, nsym, method
    t = np.zeros(5003)
    velocity = np.zeros(5003)

    method = int(input('Euler (1) or Runge-Kutta (2)? -> ').strip())
    if method not in (1, 2):
        print('must select 1 or 2 ..')
        exit()

    velocity[0] = float(input('initial velocity -> ').strip())
    t[0] = 0
    dt = float(input('time step -> ').strip())
    tmax = float(input('max time -> ').strip())
    nmax = min(int(tmax / dt), 5000)
    power = float(input('constant power -> ').strip())
    
    mass, c, area, density = 70, 0.5, 0.33, 1.29
    ans = input('set line, symbol? (y/n) ').strip()
    lsym, nsym = (int(input('line and symbol numbers -> ').strip()), int(input().strip())) if ans == 'y' else (-1, 1)

    return t, velocity

def calculate(t, velocity):
    f_vals = np.zeros(nmax)
    for i in range(nmax - 1):
        f_vals[i] = f(velocity[i], power, mass, c, density, area)
        if method == 1:
            velocity[i + 1] = velocity[i] + dt * f_vals[i]
        else:
            v1 = velocity[i] + 0.5 * dt * f_vals[i]
            f_vals[i + 1] = f(v1, power, mass, c, density, area)
            velocity[i + 1] = velocity[i] + dt * f_vals[i + 1]
        t[i + 1] = t[i] + dt

def display(t, velocity):
    np.savetxt('graph.out', np.column_stack((t, velocity)), header='Time(s)           Velocity(m/s)', fmt='%17.6f %15.6f', comments='')

if __name__ == "__main__":
    t, velocity = initialize()
    calculate(t, velocity)
    display(t, velocity)