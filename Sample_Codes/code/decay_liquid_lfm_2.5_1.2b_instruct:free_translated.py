import sys

def initialize(uranium, t, tc, dt, n, lsym, nsym, method):
    dimension = len(uranium)
    t = t[:]
    t[0] = 0
    print(f'Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ')
    method = method.strip()
    if method not in ('1', '2', '3'):
        print('must select 1, 2 or 3 ..')
        sys.exit(1)
    print('initial number of nuclei -> ')
    n1 = int(input())
    t = t[:]
    t[0] = n1
    print(f'time constant -> {t[0]}')
    print(f'time step -> {dt}')
    print(f'total time -> {time}')
    n = min(int(time / dt), 1000)
    print('set line, symbol?')
    n2 = int(input())
    lsym = int(input())
    nsym = n2 if n2 > 1 else 1
    return t, lsym, nsym

def calculate(x, t, dt, tau, n, method):
    dimension = len(x)
    t = t[:]
    if method == '1':
        for i in range(1, n-1):
            x[i+1] = x[i] - x[i] / tau * dt
    elif method == '2':
        for i in range(1, n-1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x[i+1] = x[i] + dt * dx2
    else:  # method == '3'
        for i in range(1, n-1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x2 = x[i] + 0.5 * dt * dx2
            x3 = x[i] + 0.1666666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
            x[i+1] = x[i] + 0.1666666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
    return t, x

def display(uranium, t, tau, dt, n, lsym, nsym, method):
    dimension = len(uranium)
    methodname = 'Runge-Kutta2' if method == '2' else 'Runge-Kutta4' if method == '3' else 'Euler'
    print('=')
    print(f'Radioactive Decay: {methodname}')
    print(f'tau = {tau}')
    print(f'dt = {dt}')
    print('=')
    print(f'Time (s) | Number of Nuclei')
    for i in range(0, n, max(1, n // 20)):
        print(f'{100:,} t({i}) {uranium[i]}')

def main():
    print("Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)")
    print("Program to accompany 'Computational Physics' by N. Giordano and H. Nakanishi")
    print("Modified: Removed external plotting library dependency, prints array values instead")
    
    uranium = [0] * 1003
    t = [0] * 1003
    method = input().strip()
    n = int(input())
    t, lsym, nsym = initialize(uranium, t, 1, 0.01, n, lsym, nsym, method)
    t, _, nsym = calculate(uranium, t, 0.01, 0.01, n, method)
    display(uranium, t, 0.01, 0.01, n, lsym, nsym, method)
    sys.exit(0)

if __name__ == "__main__":
    main()