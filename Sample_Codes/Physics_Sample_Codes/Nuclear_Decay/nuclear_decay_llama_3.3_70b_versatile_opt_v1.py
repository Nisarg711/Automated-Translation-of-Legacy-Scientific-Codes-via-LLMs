import numpy as np

def initialize():
    """Get user input for simulation parameters."""
    print("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ")
    method = int(input())
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        exit()
    print("initial number of nuclei -> ")
    uranium0 = float(input())
    print("time constant -> ")
    tau = float(input())
    print("time step -> ")
    dt = float(input())
    print("total time -> ")
    time = float(input())
    n = min(int(time / dt), 1000)
    print("set line, symbol?")
    ans = input()
    if ans == 'y':
        print("line and symbol numbers -> ")
        line = input()
        values = line.split()
        if len(values) == 2:
            lsym, nsym = map(int, values)
        else:
            lsym = int(values[0])
            nsym = 1
    else:
        lsym = -1
        nsym = 1
    return uranium0, tau, dt, n, lsym, nsym, method


def calculate(uranium0, tau, dt, n, method):
    """Calculate uranium decay using the specified method."""
    uranium = np.zeros(n)
    t = np.zeros(n)
    uranium[0] = uranium0
    t[0] = 0
    if method == 1:
        for i in range(n - 1):
            uranium[i + 1] = uranium[i] - uranium[i] / tau * dt
            t[i + 1] = t[i] + dt
    elif method == 2:
        for i in range(n - 1):
            dx = -uranium[i] / tau
            x1 = uranium[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            uranium[i + 1] = uranium[i] + dt * dx2
            t[i + 1] = t[i] + dt
    else:
        for i in range(n - 1):
            dx = -uranium[i] / tau
            x1 = uranium[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x2 = uranium[i] + 0.5 * dt * dx2
            dx3 = -x2 / tau
            x3 = uranium[i] + dt * dx3
            dx4 = -x3 / tau
            uranium[i + 1] = uranium[i] + 0.16666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
            t[i + 1] = t[i] + dt
    return uranium, t


def display(uranium, t, tau, dt, n, lsym, nsym, method):
    """Display the results of the simulation."""
    if method == 1:
        methodname = 'Euler'
    elif method == 2:
        methodname = 'Runge-Kutta2'
    else:
        methodname = 'Runge-Kutta4'
    print('=')
    print('Radioactive Decay: ', methodname)
    print('tau = ', tau)
    print('dt = ', dt)
    print('=')
    print('Time (s) | Number of Nuclei')
    print('-')
    for i in range(0, n, max(1, n // 20)):
        print(f"{t[i]:10.4f} | {uranium[i]:15.2f}")


def main():
    uranium0, tau, dt, n, lsym, nsym, method = initialize()
    uranium, t = calculate(uranium0, tau, dt, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)


if __name__ == "__main__":
    main()