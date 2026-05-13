import numpy as np

def decay():
    # Declare the arrays we will need
    uranium = np.zeros(1003)
    t = np.zeros(1003)

    # Use subroutines to do the work
    tau, dt, n, lsym, nsym, method = initialize(uranium, t)
    uranium, t = calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)

def initialize(unuclei, t):
    # Initialize variables
    method = int(input("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ").strip())
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        exit()
    unuclei[0] = float(input("initial number of nuclei -> ").strip())
    t[0] = 0
    tau = float(input("time constant -> ").strip())
    dt = float(input("time step -> ").strip())
    time = float(input("total time -> ").strip())
    n = min(int(time / dt), 1000)
    ans = input("set line, symbol? ").strip()
    lsym, nsym = (-1, 1) if ans != 'y' else (int(input("line and symbol numbers -> ").strip()), int(input("line and symbol numbers -> ").strip()))
    return tau, dt, n, lsym, nsym, method

def calculate(x, t, dt, tau, n, method):
    # Now use the Euler method or the Runge-Kutta (2nd or 4th order)
    if method == 1:
        x[1:] = x[:-1] - x[:-1] / tau * dt
    elif method == 2:
        dx = -x[:-1] / tau
        x1 = x[:-1] + 0.5 * dt * dx
        dx2 = -x1 / tau
        x[1:] = x[:-1] + dt * dx2
    else:
        dx = -x[:-1] / tau
        x1 = x[:-1] + 0.5 * dt * dx
        dx2 = -x1 / tau
        x2 = x[:-1] + 0.5 * dt * dx2
        dx3 = -x2 / tau
        x3 = x[:-1] + dt * dx3
        dx4 = -x3 / tau
        x[1:] = x[:-1] + 0.16666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
    t[1:] = t[:-1] + dt
    return x, t

def display(uranium, t, tau, dt, n, lsym, nsym, method):
    # Display results: Print time and uranium values to compare
    # No external plotting library dependency
    methodname = ['Euler', 'Runge-Kutta2', 'Runge-Kutta4'][method-1]
    
    print('=')
    print('Radioactive Decay: ', methodname)
    print('tau = ', tau)
    print('dt = ', dt)
    print('=')
    print('Time (s) | Number of Nuclei')
    print('-')
    
    for i in range(0, n, max(1, n // 20)):
        print(f"{t[i]:10.4f} | {uranium[i]:15.2f}")
    
    return

if __name__ == "__main__":
    decay()