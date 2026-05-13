def initialize(uranium, t, tau, dt, n, lsym, nsym, method):
    print("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ")
    method = int(input())
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        exit()
    print("initial number of nuclei -> ")
    uranium[0] = float(input())
    t[0] = 0
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
    return uranium, t, tau, dt, n, lsym, nsym, method


def calculate(x, t, dt, tau, n, method):
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
    uranium = [0] * 1003
    t = [0] * 1003
    tau = 0
    dt = 0
    n = 0
    lsym = 0
    nsym = 0
    method = 0
    uranium, t, tau, dt, n, lsym, nsym, method = initialize(uranium, t, tau, dt, n, lsym, nsym, method)
    uranium, t = calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, lsym, nsym, method)


if __name__ == "__main__":
    main()