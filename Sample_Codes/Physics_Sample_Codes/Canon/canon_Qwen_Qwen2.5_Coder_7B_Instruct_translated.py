import math

def cannon2():
    # Declare the arrays we will need
    x = [0.0] * 5003
    y = [0.0] * 5003
    
    # Use subroutines to do the work
    dt, vinit, theta, Am, lsym, nsym, method = initialize()
    x, y, n = calculate(x, y, dt, vinit, theta, Am, method)
    display_rows = int(input("Number of data rows to display? -> ").strip())
    display(x, y, n, theta, Am, dt, lsym, nsym, method, display_rows)

def initialize():
    # Initialize variables
    method = int(input("Euler (1) or Runge-Kutta 2nd order (2), 4th (3)? -> ").strip())
    if method not in [1, 2, 3]:
        print('must select 1, 2, or 3 ..')
        exit()
    
    vinit = float(input("initial velocity -> ").strip())
    dt = float(input("time step -> ").strip())
    Am = float(input("drag/m -> ").strip())
    theta = float(input("firing angle -> ").strip())
    
    ans = input("set line, symbol?").strip().lower()
    if ans == 'y':
        lsym = int(input("line and symbol numbers -> ").strip())
        nsym = int(input("symbol?").strip())
    else:
        lsym = -1
        nsym = 1
    
    return dt, vinit, theta, Am, lsym, nsym, method

def calculate(x, y, dt, vinit, theta, Am, method):
    # Now use the Euler method or the Runge-Kutta (2nd order)
    x[0], y[0] = 0.0, 0.0
    vx = vinit * math.cos(math.radians(theta))
    vy = vinit * math.sin(math.radians(theta))
    nmax = 5000
    n = 0
    
    if method == 1:
        for i in range(1, nmax + 1):
            dx, dy, dvx, dvy = deriv(x[i - 1], y[i - 1], vx, vy, 0.0, Am)
            x[i] = x[i - 1] + dt * dx
            y[i] = y[i - 1] + dt * dy
            vx += dt * dvx
            vy += dt * dvy
            if y[i] <= 0.0:
                n = i
                break
    elif method == 2:
        for i in range(1, nmax + 1):
            dx, dy, dvx, dvy = deriv(x[i - 1], y[i - 1], vx, vy, 0.0, Am)
            x1 = x[i - 1] + 0.5 * dt * dx
            y1 = y[i - 1] + 0.5 * dt * dy
            vx1 = vx + 0.5 * dt * dvx
            vy1 = vy + 0.5 * dt * dvy
            dx2, dy2, dvx2, dvy2 = deriv(x1, y1, vx1, vy1, 0.0, Am)
            x[i] = x[i - 1] + dt * dx2
            y[i] = y[i - 1] + dt * dy2
            vx += dt * dvx2
            vy += dt * dvy2
            if y[i] <= 0.0:
                n = i
                break
    else:
        for i in range(1, nmax + 1):
            dx, dy, dvx, dvy = deriv(x[i - 1], y[i - 1], vx, vy, 0.0, Am)
            x1 = x[i - 1] + 0.5 * dt * dx
            y1 = y[i - 1] + 0.5 * dt * dy
            vx1 = vx + 0.5 * dt * dvx
            vy1 = vy + 0.5 * dt * dvy
            dx2, dy2, dvx2, dvy2 = deriv(x1, y1, vx1, vy1, 0.0, Am)
            x2 = x[i - 1] + 0.5 * dt * dx2
            y2 = y[i - 1] + 0.5 * dt * dy2
            vx2 = vx + 0.5 * dt * dvx2
            vy2 = vy + 0.5 * dt * dvy2
            dx3, dy3, dvx3, dvy3 = deriv(x2, y2, vx2, vy2, 0.0, Am)
            x3 = x[i - 1] + dt * dx3
            y3 = y[i - 1] + dt * dy3
            vx3 = vx + dt * dvx3
            vy3 = vy + dt * dvy3
            dx4, dy4, dvx4, dvy4 = deriv(x3, y3, vx3, vy3, 0.0, Am)
            x[i] = x[i - 1] + (1/6) * dt * (dx + 2*dx2 + 2*dx3 + dx4)
            y[i] = y[i - 1] + (1/6) * dt * (dy + 2*dy2 + 2*dy3 + dy4)
            vx += (1/6) * dt * (dvx + 2*dvx2 + 2*dvx3 + dvx4)
            vy += (1/6) * dt * (dvy + 2*dvy2 + 2*dvy3 + dvy4)
            if y[i] <= 0.0:
                n = i
                break
    
    n = nmax if n == 0 else n
    a = -y[n] / y[n - 1]
    x[n] = (x[n] + a * x[n - 1]) / (1 + a)
    y[n] = 0.0
    
    return x, y, n

def deriv(x0, y0, vx0, vy0, t0, Am):
    dx = vx0
    dy = vy0
    f = Am * math.sqrt(vx0**2 + vy0**2)
    dvx = -f * vx0
    dvy = -f * vy0 - 9.8
    return dx, dy, dvx, dvy

def display(x, y, n, theta, Am, dt, lsym, nsym, method, display_rows):
    # Modified to write simple text output to "graph.out" for comparison.
    with open('graph.out', 'w') as f:
        f.write('Distance(m)       Height(m)\n')
        step = max(1, n // display_rows)
        for i in range(0, n + 1, step):
            f.write(f"{x[i]:10.4f} {y[i]:10.4f}\n")
    
    print('Data successfully written to graph.out for comparison.')

if __name__ == "__main__":
    cannon2()