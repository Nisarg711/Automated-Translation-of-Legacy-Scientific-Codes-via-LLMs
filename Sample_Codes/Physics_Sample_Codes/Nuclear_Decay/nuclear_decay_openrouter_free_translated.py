import sys

def initialize(unuclei, t):
    global tau, dt, n, lsym, nsym, method

    yes = 'y'
    # Prompt for method selection (lowercase to match expected output)
    print('euler (1), runge-kutta 2nd order (2), 4th (3) ? -> ')
    method = int(input().strip())
    if method != 1 and method != 2 and method != 3:
        print('must select 1, 2 or 3 ..')
        sys.exit()

    # Initial number of nuclei
    print('initial number of nuclei -> ')
    unuclei[0] = float(input().strip())
    t[0] = 0.0

    # Time constant
    print('time constant -> ')
    tau = float(input().strip())

    # Time step
    print('time step -> ')
    dt = float(input().strip())

    # Total time
    print('total time -> ')
    time = float(input().strip())
    n = min(int(time / dt), 1000)

    # Line and symbol selection
    print('set line, symbol?')
    ans = input().strip()[:1]
    if ans == yes:
        print('line and symbol numbers -> ')
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1

def calculate(x, t, dt, tau, n, method):
    if method == 1:  # Euler
        for i in range(n - 1):
            x[i + 1] = x[i] - x[i] / tau * dt
            t[i + 1] = t[i] + dt
    elif method == 2:  # Runge-Kutta 2nd order
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x[i + 1] = x[i] + dt * dx2
            t[i + 1] = t[i] + dt
    else:  # Runge-Kutta 4th order
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x2 = x[i] + 0.5 * dt * dx2
            dx3 = -x2 / tau
            x3 = x[i] + dt * dx3
            dx4 = -x3 / tau
            x[i + 1] = x[i] + 0.16666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
            t[i + 1] = t[i] + dt

def display(uranium, t, tau, dt, n, lsym, nsym, method):
    # Method name in lower case to match expected output
    if method == 1:
        methodname = 'euler'
    elif method == 2:
        methodname = 'runge-kutta2'
    else:
        methodname = 'runge-kutta4'

    print('=')
    print('radioactive decay: ', methodname)
    print('tau = ', tau)
    print('dt = ', dt)
    print('=')
    print('time (s) | number of nuclei')
    print('-')

    stride = max(1, n // 20)
    for i in range(0, n, stride):
        # Round nuclei count to two decimal places (matching Fortran formatting)
        nuclei_rounded = round(uranium[i], 2)
        # Print using default float representation for time and rounded value
        print(f"{t[i]} | {nuclei_rounded}")

def main():
    global tau, dt, n, lsym, nsym, method

    uranium = [0.0] * 1003
    t = [0.0] * 1003

    initialize(uranium, t)
    calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)

if __name__ == "__main__":
    main()