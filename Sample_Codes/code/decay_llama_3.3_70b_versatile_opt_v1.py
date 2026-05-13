import numpy as np

def initialize():
    # Initialize variables
    uranium = np.zeros(1003)
    t = np.zeros(1003)
    method = int(input("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> "))
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        exit()
    uranium[0] = float(input("initial number of nuclei -> "))
    t[0] = 0
    tau = float(input("time constant -> "))
    dt = float(input("time step -> "))
    time = float(input("total time -> "))
    n = min(int(time / dt), 1000)
    ans = input("set line, symbol? -> ")
    if ans == 'y':
        lsym = int(input("line and symbol numbers -> "))
        nsym = int(input())
    else:
        lsym = -1
        nsym = 1
    return uranium, t, tau, dt, n, lsym, nsym, method


def calculate(x, t, dt, tau, n, method):
    # Now use the Euler method or the Runge-Kutta (2nd or 4th order)
    if method == 1:
        for i in range(n - 1):
            x[i + 1] = x[i] - x[i] / tau * dt
            t[i + 1] = t[i] + dt
    elif method == 2:
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x[i + 1] = x[i] + dt * dx2
            t[i + 1] = t[i] + dt
    else:
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x2 = x[i] + 0.5 * dt * dx2
            dx3 = -x2 / tau
            x3 = x[i] + dt * dx3
            dx4 = -x3 / tau
            x[i + 1] = x[i] + 1/6 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
            t[i + 1] = t[i] + dt
    return x, t


def display(uranium, t, tau, dt, n, lsym, nsym, method):
    # Display results: Print time and uranium values to compare
    methodname = ''
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
    uranium, t, tau, dt, n, lsym, nsym, method = initialize()
    uranium, t = calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)


if __name__ == "__main__":
    main()