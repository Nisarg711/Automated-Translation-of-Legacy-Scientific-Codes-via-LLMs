def decay():
    # Declare the arrays we will need
    uranium = [0] * 1003
    t = [0] * 1003
    tau, dt, n, lsym, nsym, method = initialize(uranium, t, tau, dt, n, lsym, nsym, method)
    calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)

def initialize(unuclei, t, tc, dt, n, lsym, nsym, method):
    # Initialize variables
    method = int(input("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> "))
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        return
    unuclei[0] = int(input("initial number of nuclei -> "))
    t[0] = 0
    tc = float(input("time constant -> "))
    dt = float(input("time step -> "))
    time = float(input("total time -> "))
    n = min(int(time / dt), 1000)
    ans = input("set line, symbol? (y/n) -> ")
    if ans.lower() == 'y':
        lsym = int(input("line number -> "))
        nsym = int(input("symbol number -> "))
    else:
        lsym, nsym = -1, 1
    return tc, dt, n, lsym, nsym, method

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
    print(f'Radioactive Decay: {methodname} tau = {tau} dt = {dt}')
    print('=')
    print('Time (s) | Number of Nuclei')
    print('-')
    for i in range(0, n, max(1, n // 20)):
        print(f'{t[i]:10.4f} | {uranium[i]:15.2f}')
    return

# Call the main function
decay()