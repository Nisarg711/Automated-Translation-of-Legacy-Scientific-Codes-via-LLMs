# Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)
# Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
# Fortran version written by H. Nakanishi
# Modified: Removed external plotting library dependency, prints array values instead
#
def decay():
    # Declare the arrays we will need
    uranium = [0.0] * 1003
    t = [0.0] * 1003

    # Use subroutines to do the work
    tau, dt = initialize(uranium, t, 1.0, 0.01, 1000, 1, 1)
    calculate(uranium, t, dt, tau, 1000, 1)
    display(uranium, t, tau, dt, 1000, 1, 1, 1)

if __name__ == "__main__":
    decay()

def initialize(unuclei, t, tc, dt, n, lsym, nsym, method):
    # Initialize variables
    unuclei_list = [0] * len(unuclei)
    yes = 'y'
    print("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ")
    method_input = input()
    method = int(method_input.strip())
    if method != 1 and method != 2 and method != 3:
        print("must select 1, 2 or 3 ..")
        exit()
    print("initial number of nuclei -> ")
    try:
        unuclei[0] = float(input())
    except ValueError:
        print("Invalid input for initial number of nuclei. Please enter a number.")
        exit()
    t[0] = 0.0
    print("time constant -> ")
    try:
        tc = float(input())
    except ValueError:
        print("Invalid input for time constant. Please enter a number.")
        exit()
    print("time step -> ")
    try:
        dt = float(input())
    except ValueError:
        print("Invalid input for time step. Please enter a number.")
        exit()
    print("total time -> ")
    try:
        time = float(input())
    except ValueError:
        print("Invalid input for total time. Please enter a number.")
        exit()
    n = min(int(time / dt), 1000)
    print("set line, symbol?")
    ans = input()
    if ans.lower() == yes:
        print("line and symbol numbers -> ")
        lsym = int(input().strip())
        nsym = int(input().strip())
    else:
        lsym = -1
        nsym = 1
    return tau, dt

def calculate(x, t, dt, tau, n, method):
    # Now use the Euler method or the Runge-Kutta (2nd or 4th order)
    if method == 1:
        for i in range(0, n - 1):
            x[i + 1] = x[i] - x[i] / tau * dt
            t[i + 1] = t[i] + dt
    elif method == 2:
        for i in range(0, n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            dx2 = -x1 / tau
            x[i + 1] = x[i] + dt * dx2
            t[i + 1] = t[i] + dt
    else:
        for i in range(0, n - 1):
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
    # No external plotting library dependency
    methodname = ""
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

    for i in range(0, n, max(1, n // 20)):
        print("{:10.4f} | {:15.2f}".format(t[i], uranium[i]))