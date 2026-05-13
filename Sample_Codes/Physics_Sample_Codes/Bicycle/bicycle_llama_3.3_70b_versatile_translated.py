import math

def initialize(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method):
    print('Euler (1) or Runge-Kutta (2)? -> ')
    method = int(input())
    if method != 1 and method != 2:
        print('must select 1 or 2 ..')
        exit()
    print('initial velocity -> ')
    velocity[0] = float(input())
    t[0] = 0
    print('time step -> ')
    dt[0] = float(input())
    print('max time -> ')
    tmax = float(input())
    nmax[0] = min(int(tmax / dt[0]), 5000)
    print('constant power -> ')
    power[0] = float(input())
    mass[0] = 70
    c[0] = 0.5
    area[0] = 0.33
    density[0] = 1.29
    print('set line, symbol?')
    ans = input()
    if ans == 'y':
        print('line and symbol numbers -> ')
        lsym_input = input().strip()
        nsym_input = input().strip()
        try:
            lsym[0], nsym[0] = int(lsym_input), int(nsym_input)
        except ValueError:
            print("Invalid input for line and symbol numbers. Using default values.")
            lsym[0] = -1
            nsym[0] = 1
    else:
        lsym[0] = -1
        nsym[0] = 1

def calculate(t, v, dt, power, mass, nmax, c, area, density, lsym, nsym, method):
    if method == 1:
        for i in range(nmax[0] - 1):
            v[i + 1] = v[i] + dt[0] * f(v[i], power[0], mass[0], c[0], density[0], area[0])
            t[i + 1] = t[i] + dt[0]
    else:
        for i in range(nmax[0] - 1):
            v1 = v[i] + 0.5 * dt[0] * f(v[i], power[0], mass[0], c[0], density[0], area[0])
            v[i + 1] = v[i] + dt[0] * f(v1, power[0], mass[0], c[0], density[0], area[0])
            t[i + 1] = t[i] + dt[0]

def f(v, p, x, c, rho, a):
    if v == 0:
        return float('inf')
    return (p / v - c * rho * a * v ** 2) / x

def display(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method):
    with open('graph.out', 'w') as f:
        f.write('Time(s)           Velocity(m/s)\n')
        for i in range(nmax[0]):
            f.write(f'{t[i]:.10f} {velocity[i]:.10f}\n')
    print('Data successfully written to graph.out for comparison.')

def main():
    t = [0] * 5003
    velocity = [0] * 5003
    dt = [0]
    power = [0]
    mass = [0]
    nmax = [0]
    c = [0]
    area = [0]
    density = [0]
    lsym = [0]
    nsym = [0]
    method = 0
    initialize(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method)
    calculate(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method)
    display(t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method)

if __name__ == "__main__":
    main()