import math

def cannon2():
    x = [0.0] * 5003
    y = [0.0] * 5003

    dt, vinit, theta, Am, lsym, nsym, method = initialize()
    n = calculate(x, y, dt, vinit, theta, Am, method)
    display(x, y, n)

def initialize():
    method = int(input('Euler (1) or Runge-Kutta 2nd order (2), 4th (3)? -> ').strip())
    if method not in [1, 2, 3]:
        raise ValueError('Must select 1, 2, or 3.')

    vinit = float(input('Initial velocity -> ').strip())
    dt = float(input('Time step -> ').strip())
    Am = float(input('Drag/m -> ').strip())
    theta = float(input('Firing angle -> ').strip())

    ans = input('Set line, symbol? (y/n) -> ').strip().lower()
    if ans == 'y':
        try:
            lsym, nsym = map(int, input('Line and symbol numbers -> ').strip().split())
        except ValueError:
            lsym, nsym = -1, 1
    else:
        lsym, nsym = -1, 1

    return dt, vinit, theta, Am, lsym, nsym, method

def calculate(x, y, dt, vinit, theta, Am, method):
    x[0], y[0] = 0.0, 0.0
    vx, vy = vinit * math.cos(math.radians(theta)), vinit * math.sin(math.radians(theta))
    nmax = 5000

    for i in range(1, nmax):
        dx, dy, dvx, dvy = deriv(vx, vy, Am)
        if method == 1:  # Euler
            x[i], y[i] = x[i-1] + dt * dx, y[i-1] + dt * dy
            vx, vy = vx + dt * dvx, vy + dt * dvy
        elif method == 2:  # Runge-Kutta 2nd order
            x1, y1, vx1, vy1 = x[i-1] + 0.5 * dt * dx, y[i-1] + 0.5 * dt * dy, vx + 0.5 * dt * dvx, vy + 0.5 * dt * dvy
            dx2, dy2, dvx2, dvy2 = deriv(vx1, vy1, Am)
            x[i], y[i] = x[i-1] + dt * dx2, y[i-1] + dt * dy2
            vx, vy = vx + dt * dvx2, vy + dt * dvy2
        else:  # Runge-Kutta 4th order
            x1, y1, vx1, vy1 = x[i-1] + 0.5 * dt * dx, y[i-1] + 0.5 * dt * dy, vx + 0.5 * dt * dvx, vy + 0.5 * dt * dvy
            dx2, dy2, dvx2, dvy2 = deriv(vx1, vy1, Am)
            x2, y2, vx2, vy2 = x[i-1] + 0.5 * dt * dx2, y[i-1] + 0.5 * dt * dy2, vx + 0.5 * dt * dvx2, vy + 0.5 * dt * dvy2
            dx3, dy3, dvx3, dvy3 = deriv(vx2, vy2, Am)
            x3, y3, vx3, vy3 = x[i-1] + dt * dx3, y[i-1] + dt * dy3, vx + dt * dvx3, vy + dt * dvy3
            dx4, dy4, dvx4, dvy4 = deriv(vx3, vy3, Am)
            x[i] = x[i-1] + dt * (dx + 2 * dx2 + 2 * dx3 + dx4) / 6
            y[i] = y[i-1] + dt * (dy + 2 * dy2 + 2 * dy3 + dy4) / 6
            vx += dt * (dvx + 2 * dvx2 + 2 * dvx3 + dvx4) / 6
            vy += dt * (dvy + 2 * dvy2 + 2 * dvy3 + dvy4) / 6

        if y[i] <= 0.0:
            a = -y[i] / y[i-1]
            x[i] = (x[i] + a * x[i-1]) / (1 + a)
            y[i] = 0.0
            return i + 1

    return nmax

def deriv(vx, vy, Am):
    f = Am * math.hypot(vx, vy)
    return vx, vy, -f * vx, -f * vy - 9.8

def display(x, y, nmax):
    with open('graph.out', 'w') as f:
        f.write('Distance(m)       Height(m)\n')
        f.writelines(f'{x[i]:.6f} {y[i]:.6f}\n' for i in range(nmax))
    print('Data successfully written to graph.out for comparison.')

if __name__ == "__main__":
    cannon2()