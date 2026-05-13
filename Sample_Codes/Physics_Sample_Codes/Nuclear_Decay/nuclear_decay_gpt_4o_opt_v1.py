import math

def initialize():
    print("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ")
    method = int(input().strip())
    if method not in [1, 2, 3]:
        print("must select 1, 2 or 3 ..")
        exit()

    print("initial number of nuclei -> ")
    unuclei = float(input().strip())

    print("time constant -> ")
    tau = float(input().strip())

    print("time step -> ")
    dt = float(input().strip())

    print("total time -> ")
    total_time = float(input().strip())
    n = min(int(total_time / dt), 1000)

    return unuclei, tau, dt, n, method


def calculate(x, dt, tau, n, method):
    t = [i * dt for i in range(n)]
    results = [x]

    if method == 1:
        for _ in range(n - 1):
            x -= x / tau * dt
            results.append(x)
    elif method == 2:
        for _ in range(n - 1):
            dx = -x / tau
            x1 = x + 0.5 * dt * dx
            dx2 = -x1 / tau
            x += dt * dx2
            results.append(x)
    else:
        for _ in range(n - 1):
            dx = -x / tau
            x1 = x + 0.5 * dt * dx
            dx2 = -x1 / tau
            x2 = x + 0.5 * dt * dx2
            dx3 = -x2 / tau
            x3 = x + dt * dx3
            dx4 = -x3 / tau
            x += dt * (dx + 2 * dx2 + 2 * dx3 + dx4) / 6
            results.append(x)

    return t, results


def display(t, uranium, tau, dt, n, method):
    methodname = ["Euler", "Runge-Kutta2", "Runge-Kutta4"][method - 1]

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
    unuclei, tau, dt, n, method = initialize()
    t, uranium = calculate(unuclei, dt, tau, n, method)
    display(t, uranium, tau, dt, n, method)


if __name__ == "__main__":
    main()