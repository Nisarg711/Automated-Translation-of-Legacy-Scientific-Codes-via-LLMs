# Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)
# Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
# Fortran version written by H. Nakanishi
# Modified: Removed external plotting library dependency, prints array values instead

def decay():
    # Declare the arrays we will need
    uranium = [0.0] * 1003
    t = [0.0] * 1003
    
    # Use subroutines to do the work
    tau, dt, n, lsym, nsym, method = initialize(uranium, t)
    uranium, t = calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)

def initialize(unuclei, t):
    # Initialize variables
    method = int(input("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ").strip())
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        return
    
    unuclei[0] = float(input("initial number of nuclei -> ").strip())
    t[0] = 0.0
    tc = float(input("time constant -> ").strip())
    dt = float(input("time step -> ").strip())
    time = float(input("total time -> ").strip())
    n = min(int(time / dt), 1000)
    print("set line, symbol?")
    ans = input("line and symbol numbers -> ").strip()
    
    if ans == 'y':
        lsym = int(input("line number -> ").strip())
        nsym = int(input("symbol number -> ").strip())
    else:
        lsym, nsym = -1, 1
    
    return tau, dt, n, lsym, nsym, method

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
            x[i + 1] = x[i] + 0.16666667 * dt * (dx + 2 * dx2 + 2 * dx3 + dx4)
            t[i + 1] = t[i] + dt

    return x, t

def display(uranium, t, tau, dt, n, lsym, nsym, method):
    # Display results: Print time and uranium values to compare
    # No external plotting library dependency
    methodname = 'Euler' if method == 1 else 'Runge-Kutta2' if method == 2 else 'Runge-Kutta4'
    
    print('=')
    print(f'Radioactive Decay: {methodname}')
    print(f'tau = {tau}')
    print(f'dt = {dt}')
    print('=')
    print('Time (s) | Number of Nuclei')
    print('-')
    
    step = max(1, n // 20)
    for i in range(0, n, step):
        print(f'{t[i]:10.4f} | {uranium[i]:15.2f}')

if __name__ == "__main__":
    decay()