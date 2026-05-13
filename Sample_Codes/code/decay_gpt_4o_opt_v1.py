def initialize():
    # Initialize variables
    method = int(input("Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> ").strip())
    if method not in [1, 2, 3]:
        raise ValueError("Must select 1, 2, or 3.")

    unuclei_0 = float(input("Initial number of nuclei -> ").strip())
    tau = float(input("Time constant -> ").strip())
    dt = float(input("Time step -> ").strip())
    total_time = float(input("Total time -> ").strip())
    n = min(int(total_time / dt), 1000)

    ans = input("Set line, symbol? (y/n) -> ").strip().lower()
    if ans == 'y':
        lsym, nsym = map(int, input("Line and symbol numbers -> ").strip().split())
    else:
        lsym, nsym = -1, 1

    return unuclei_0, tau, dt, n, lsym, nsym, method


def calculate(x, t, dt, tau, n, method):
    # Optimized calculation using precomputed constants
    if method == 1:  # Euler
        for i in range(n - 1):
            x[i + 1] = x[i] * (1 - dt / tau)
            t[i + 1] = t[i] + dt
    elif method == 2:  # Runge-Kutta 2nd order
        for i in range(n - 1):
            dx = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx
            x[i + 1] = x[i] + dt * (-x1 / tau)
            t[i + 1] = t[i] + dt
    else:  # Runge-Kutta 4th order
        for i in range(n - 1):
            dx1 = -x[i] / tau
            x1 = x[i] + 0.5 * dt * dx1
            dx2 = -x1 / tau
            x2 = x[i] + 0.5 * dt * dx2
            dx3 = -x2 / tau
            x3 = x[i] + dt * dx3
            dx4 = -x3 / tau
            x[i + 1] = x[i] + dt * (dx1 + 2 * dx2 + 2 * dx3 + dx4) / 6
            t[i + 1] = t[i] + dt


def display(uranium, t, tau, dt, n, method):
    # Display results
    methodname = ["Euler", "Runge-Kutta2", "Runge-Kutta4"][method - 1]
    print(f"Radioactive Decay: {methodname}\nTau = {tau}, dt = {dt}\n")
    print("Time (s) | Number of Nuclei")
    print("-" * 30)
    step = max(1, n // 20)
    for i in range(0, n, step):
        print(f"{t[i]:10.4f} | {uranium[i]:15.2f}")


def main():
    # Declare arrays
    uranium = [0.0] * 1003
    t = [0.0] * 1003

    # Initialize and calculate
    unuclei_0, tau, dt, n, lsym, nsym, method = initialize()
    uranium[0] = unuclei_0

    calculate(uranium, t, dt, tau, n, method)
    display(uranium, t, tau, dt, n, method)


if __name__ == "__main__":
    main()