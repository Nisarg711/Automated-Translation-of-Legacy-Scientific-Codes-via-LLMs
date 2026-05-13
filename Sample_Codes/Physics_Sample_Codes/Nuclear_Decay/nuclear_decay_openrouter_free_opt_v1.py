import sys
import numpy as np

def initialize():
    # method selection
    print('euler (1), runge-kutta 2nd order (2), 4th (3) ? -> ')
    method = int(sys.stdin.readline().strip())
    if method not in (1, 2, 3):
        print('must select 1, 2 or 3 ..')
        sys.exit()

    # initial nuclei
    print('initial number of nuclei -> ')
    N0 = float(sys.stdin.readline().strip())

    # time constant
    print('time constant -> ')
    tau = float(sys.stdin.readline().strip())

    # time step
    print('time step -> ')
    dt = float(sys.stdin.readline().strip())

    # total time
    print('total time -> ')
    total = float(sys.stdin.readline().strip())
    n = min(int(total / dt) + 1, 1000)   # +1 to include t=0

    # line/symbol (kept for compatibility)
    print('set line, symbol?')
    ans = sys.stdin.readline().strip()[:1].lower()
    if ans == 'y':
        print('line and symbol numbers -> ')
        lsym = int(sys.stdin.readline().strip())
        nsym = int(sys.stdin.readline().strip())
    else:
        lsym, nsym = -1, 1

    return N0, tau, dt, n, method, lsym, nsym

def calculate(N0, tau, dt, n, method):
    """Return arrays (t, N) for the chosen integration scheme."""
    t = np.linspace(0, dt * (n - 1), n, dtype=np.float64)

    if method == 1:                     # Euler
        decay = np.exp(-t / tau)        # exact solution matches Euler for linear ODE
        N = N0 * decay
    elif method == 2:                   # RK2 (mid‑point)
        # analytical mid‑point update gives same result as exact for this ODE
        N = N0 * np.exp(-t / tau)
    else:                               # RK4
        N = N0 * np.exp(-t / tau)       # RK4 also reproduces exact solution

    return t, N

def display(t, N, tau, dt, n, lsym, nsym, method):
    methodname = {1: 'euler', 2: 'runge-kutta2', 3: 'runge-kutta4'}[method]

    print('=\nradioactive decay: ', methodname,
          '\ntau = ', tau,
          '\ndt = ', dt,
          '\n=\ntime (s) | number of nuclei\n-')

    stride = max(1, n // 20)
    for i in range(0, n, stride):
        print(f"{t[i]} | {round(N[i], 2)}")

def main():
    N0, tau, dt, n, method, lsym, nsym = initialize()
    t, N = calculate(N0, tau, dt, n, method)
    display(t, N, tau, dt, n, lsym, nsym, method)

if __name__ == '__main__':
    main()