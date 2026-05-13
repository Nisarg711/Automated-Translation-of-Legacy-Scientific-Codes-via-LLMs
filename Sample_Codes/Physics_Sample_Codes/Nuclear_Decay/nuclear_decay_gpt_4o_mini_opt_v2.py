import numpy as np

def initialize(unuclei, t):
    method = int(input('Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ').strip())
    if method not in {1, 2, 3}:
        raise ValueError('must select 1, 2 or 3 ..')
    
    unuclei[0] = float(input('initial number of nuclei -> ').strip())
    t[0] = 0.0
    tc = float(input('time constant -> ').strip())
    dt = float(input('time step -> ').strip())
    time = float(input('total time -> ').strip())
    n = min(int(time / dt), 1000)
    
    ans = input('set line, symbol? (y/n) ').strip().lower()
    lsym, nsym = (int(input('line and symbol numbers -> ').strip()) for _ in range(2)) if ans == 'y' else (-1, 1)
    
    return tc, dt, n, lsym, nsym, method

def calculate(x, t, dt, tau, n, method):
    if method == 1:
        for i in range(n - 1):
            x[i + 1] = x[i] * (1 - dt / tau)
            t[i + 1] = t[i] + dt
    elif method == 2:
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            x[i + 1] = x[i] + dt * (-x1 / tau)
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
            x[i + 1] = x[i] + (dt / 6) * (dx + 2 * dx2 + 2 * dx3 + dx4)
            t[i + 1] = t[i] + dt

def display(uranium, t, tau, dt, n, lsym, nsym, method):
    methodname = ['Euler', 'Runge-Kutta2', 'Runge-Kutta4'][method - 1]
    print(f"=\nRadioactive Decay: {methodname}\ntau = {tau}\ndt = {dt}\n=\nTime (s) | Number of Nuclei\n-")
    
    step = max(1, n // 20)
    for i in range(0, n, step):
        print(f"{t[i]:10.4f} | {uranium[i]:15.2f}")

def main():
    uranium = np.zeros(1003)
    t = np.zeros(1003)
    
    tau, dt, n, lsym, nsym, method = initialize(uranium, t)
    calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)

if __name__ == "__main__":
    main()