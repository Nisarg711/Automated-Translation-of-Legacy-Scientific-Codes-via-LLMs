# Simulation of velocity vs. time for a bicyclist
# - Euler or 2nd order Runge-Kutta
# Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi

import math

def initialize():
    # Initialize variables
    print('Euler (1) or Runge-Kutta (2)? -> ')
    method = int(input().strip())
    if method != 1 and method != 2:
        print('must select 1 or 2 ..')
        exit()

    print('initial velocity -> ')
    velocity = [float(input().strip())]
    t = [0.0]

    print('time step -> ')
    dt = float(input().strip())

    print('max time -> ')
    tmax = float(input().strip())
    nmax = min(int(tmax / dt), 5000)

    print('constant power -> ')
    power = float(input().strip())

    mass = 70.0
    c = 0.5
    area = 0.33
    density = 1.29

    print('set line, symbol?')
    ans = input().strip()
    yes = 'y'
    if ans == yes:
        print('line and symbol numbers -> ')
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1

    return t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method

def f(v, p, x, c, rho, a):
    if v == 0:
        return float('inf') if p > 0 else float('-inf')
    return (p / v - c * rho * a * v**2) / x

def calculate(t, v, dt, power, mass, nmax, c, area, density, lsym, nsym, method):
    # Now use the Euler method or the Runge-Kutta (2nd order)
    if method == 1:
        for i in range(nmax - 1):
            v.append(v[i] + dt * f(v[i], power, mass, c, density, area))
            t.append(t[i] + dt)
    else:
        for i in range(nmax - 1):
            v1 = v[i] + 0.5 * dt * f(v[i], power, mass, c, density, area)
            v.append(v[i] + dt * f(v1, power, mass, c, density, area))
            t.append(t[i] + dt)

def display(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method):
    # Modified to write simple text output to "graph.out" for comparison.
    with open('graph.out', 'w') as file:
        file.write('Time(s)           Velocity(m/s)\n')
        for i in range(nmax):
            file.write(f"{t[i]:.6f}           {velocity[i]:.6f}\n")

    print('Data successfully written to graph.out for comparison.')

def main():
    t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method = initialize()
    calculate(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method)
    display(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method)

if __name__ == "__main__":
    main()