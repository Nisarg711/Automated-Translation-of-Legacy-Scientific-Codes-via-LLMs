import math

def initialize():
    method = int(input('Euler (1) or Runge-Kutta (2)? -> ').strip())
    if method not in (1, 2):
        raise ValueError('Must select 1 or 2.')

    velocity = [float(input('Initial velocity -> ').strip())]
    t = [0.0]
    dt = float(input('Time step -> ').strip())
    tmax = float(input('Max time -> ').strip())
    nmax = min(int(tmax / dt), 5000)
    power = float(input('Constant power -> ').strip())

    mass = 70.0
    c = 0.5
    area = 0.33
    density = 1.29

    ans = input('Set line, symbol? (y/n) -> ').strip().lower()
    if ans == 'y':
        lsym = int(input('Line number -> ').strip())
        nsym = int(input('Symbol number -> ').strip())
    else:
        lsym, nsym = -1, 1

    return t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method

def f(v, p, x, c, rho, a):
    return (p / v - c * rho * a * v**2) / x if v != 0 else (float('inf') if p > 0 else float('-inf'))

def calculate(t, v, dt, power, mass, nmax, c, area, density, method):
    for i in range(nmax - 1):
        t_next = t[i] + dt
        if method == 1:  # Euler
            v_next = v[i] + dt * f(v[i], power, mass, c, density, area)
        else:  # Runge-Kutta 2nd order
            v1 = v[i] + 0.5 * dt * f(v[i], power, mass, c, density, area)
            v_next = v[i] + dt * f(v1, power, mass, c, density, area)
        t.append(t_next)
        v.append(v_next)

def display(t, velocity):
    with open('graph.out', 'w') as file:
        file.write('Time(s)           Velocity(m/s)\n')
        file.writelines(f"{t[i]:.6f}           {velocity[i]:.6f}\n" for i in range(len(t)))
    print('Data successfully written to graph.out for comparison.')

def main():
    t, velocity, dt, power, mass, nmax, c, area, density, lsym, nsym, method = initialize()
    calculate(t, velocity, dt, power, mass, nmax, c, area, density, method)
    display(t, velocity)

if __name__ == "__main__":
    main()