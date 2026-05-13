# Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)
# Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
# Fortran version written by H. Nakanishi
# Modified: Removed external plotting library dependency, prints array values instead

import math

def initialize():
    # Initialize variables
    print("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ")
    method = int(input().strip())
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        exit()

    print("initial number of nuclei -> ")
    unuclei = [float(input().strip())]
    t = [0.0]

    print("time constant -> ")
    tau = float(input().strip())

    print("time step -> ")
    dt = float(input().strip())

    print("total time -> ")
    total_time = float(input().strip())
    n = min(int(total_time / dt), 1000)

    print("set line, symbol?")
    ans = input().strip()
    yes = 'y'
    if ans == yes:
        print("line and symbol numbers -> ")
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1

    return unuclei, t, tau, dt, n, lsym, nsym, method


def calculate(x, t, dt, tau, n, method):
    # Now use the Euler method or the Runge-Kutta (2nd or 4th order)
    if method == 1:
        for i in range(n - 1):
            x.append(x[i] - x[i] / tau * dt)
            t.append(t[i] + dt)
    elif method == 2:
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x.append(x[i] + dt * dx2)
            t.append(t[i] + dt)
    else:
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x2 = x[i] + 0.5 * dt * dx2
            dx3 = -x2 / tau
            x3 = x[i] + dt * dx3
            dx4 = -x3 / tau
            x.append(x[i] + 0.16666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4))
            t.append(t[i] + dt)


def display(uranium, t, tau, dt, n, lsym, nsym, method):
    # Display results: Print time and uranium values to compare
    # No external plotting library dependency
    if method == 1:
        methodname = "Euler"
    elif method == 2:
        methodname = "Runge-Kutta2"
    else:
        methodname = "Runge-Kutta4"

    print("=")
    print(f"Radioactive Decay: {methodname}")
    print(f"tau = {tau}")
    print(f"dt = {dt}")
    print("=")
    print("Time (s) | Number of Nuclei")
    print("-")

    stride = max(1, n // 20)
    for i in range(0, n, stride):
        print(f"{t[i]:10.4f} | {uranium[i]:15.2f}")


def main():
    uranium, t, tau, dt, n, lsym, nsym, method = initialize()
    calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)


if __name__ == "__main__":
    main()