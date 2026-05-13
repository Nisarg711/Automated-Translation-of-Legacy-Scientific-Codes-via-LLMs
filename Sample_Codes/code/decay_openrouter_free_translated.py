# Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)
# Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
# Fortran version written by H. Nakanishi
# Modified: Removed external plotting library dependency, prints array values instead

def initialize():
    # Initialize variables
    print("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ")
    method = int(input().strip())
    if method not in (1, 2, 3):
        print("must select 1, 2 or 3 ..")
        exit()

    print("initial number of nuclei -> ")
    initial_nuclei = float(input().strip())

    print("time constant -> ")
    tau = float(input().strip())

    print("time step -> ")
    dt = float(input().strip())

    print("total time -> ")
    total_time = float(input().strip())

    # Number of points (including the initial point)
    n = min(int(total_time / dt), 1000) + 1   # +1 to store the initial state, matching Fortran's n points

    print("set line, symbol?")
    ans = input().strip()
    if ans == 'y':
        print("line and symbol numbers -> ")
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1

    # Allocate arrays with exactly n elements (indices 0 .. n-1)
    uranium = [0.0] * n
    t = [0.0] * n
    uranium[0] = initial_nuclei
    t[0] = 0.0

    return uranium, t, tau, dt, n, lsym, nsym, method


def calculate(x, t, dt, tau, n, method):
    # Now use the Euler method or the Runge-Kutta (2nd or 4th order)
    # Fortran updates n-1 times, filling indices 1 .. n-1
    for i in range(n - 1):
        if method == 1:                     # Euler
            x[i + 1] = x[i] - x[i] / tau * dt
        elif method == 2:                   # Runge-Kutta 2nd order
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x[i + 1] = x[i] + dt * dx2
        else:                               # Runge-Kutta 4th order
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
    # Display results: Print time and uranium values to compare
    if method == 1:
        methodname = 'Euler'
    elif method == 2:
        methodname = 'Runge-Kutta2'
    else:
        methodname = 'Runge-Kutta4'

    print("=")
    print("Radioactive Decay: ", methodname)
    print("tau = ", tau)
    print("dt = ", dt)
    print("=")
    print("Time (s) | Number of Nuclei")
    print("-")

    # Print roughly 20 points, always including the first point
    step = max(1, n // 20)
    for i in range(0, n, step):
        print(f"{t[i]:10.4f} | {uranium[i]:15.2f}")


def main():
    uranium, t, tau, dt, n, lsym, nsym, method = initialize()
    calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)


if __name__ == "__main__":
    main()