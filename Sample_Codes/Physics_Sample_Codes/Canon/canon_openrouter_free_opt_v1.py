import math

# Global arrays
x = [0.0] * 5003
y = [0.0] * 5003

def initialize():
    global dt, vinit, theta, Am, lsym, nsym, method
    
    print("Euler (1) or Runge-Kutta 2nd order (2), 4th (3)? -> ")
    method = int(input().strip())
    
    if method not in [1, 2, 3]:
        print("must select 1, 2, or 3 ..")
        exit()
    
    print("initial velocity -> ")
    vinit = float(input().strip())
    
    print("time step -> ")
    dt = float(input().strip())
    
    print("drag/m -> ")
    Am = float(input().strip())
    
    print("firing angle -> ")
    theta = float(input().strip())
    
    print("set line, symbol?")
    ans = input().strip()
    
    if ans == 'y':
        print("line and symbol numbers -> ")
        lsym_str = input().strip()
        nsym_str = input().strip()
        lsym = int(lsym_str)
        nsym = int(nsym_str)
    else:
        lsym = -1
        nsym = 1
    
    return dt, vinit, theta, Am, lsym, nsym, method

def deriv(x0, y0, vx0, vy0, t0, Am):
    dx = vx0
    dy = vy0
    f = Am * math.sqrt(vx0**2 + vy0**2)
    dvx = -f * vx0
    dvy = -f * vy0 - 9.8
    return dx, dy, dvx, dvy

def calculate(x, y, dt, vinit, theta, Am, method):
    x[0] = 0.0
    y[0] = 0.0
    vx = vinit * math.cos(3.141592 * theta / 180.0)
    vy = vinit * math.sin(3.141592 * theta / 180.0)
    nmax = 5000
    
    if method == 1:
        for i in range(1, nmax):
            dx, dy, dvx, dvy = deriv(x[i-1], y[i-1], vx, vy, 0.0, Am)
            x[i] = x[i-1] + dt * dx
            y[i] = y[i-1] + dt * dy
            vx += dt * dvx
            vy += dt * dvy
            if y[i] <= 0.0:
                n = i
                break
        else:
            n = nmax
    elif method == 2:
        for i in range(1, nmax):
            dx, dy, dvx, dvy = deriv(x[i-1], y[i-1], vx, vy, 0.0, Am)
            x1 = x[i-1] + 0.5 * dt * dx
            y1 = y[i-1] + 0.5 * dt * dy
            vx1 = vx + 0.5 * dt * dvx
            vy1 = vy + 0.5 * dt * dvy
            dx2, dy2, dvx2, dvy2 = deriv(x1, y1, vx1, vy1, 0.0, Am)
            x[i] = x[i-1] + dt * dx2
            y[i] = y[i-1] + dt * dy2
            vx += dt * dvx2
            vy += dt * dvy2
            if y[i] <= 0.0:
                n = i
                break
        else:
            n = nmax
    else:
        for i in range(1, nmax):
            dx, dy, dvx, dvy = deriv(x[i-1], y[i-1], vx, vy, 0.0, Am)
            x1 = x[i-1] + 0.5 * dt * dx
            y1 = y[i-1] + 0.5 * dt * dy
            vx1 = vx + 0.5 * dt * dvx
            vy1 = vy + 0.5 * dt * dvy
            dx2, dy2, dvx2, dvy2 = deriv(x1, y1, vx1, vy1, 0.0, Am)
            x2 = x[i-1] + 0.16666667 * dt * (dx + 2*dx2 + 2*dx3 + dx4)
            y2 = y[i-1] + 0.16666667 * dt * (dy + 2*dy2 + 2*dy3 + dy4)
            vx2 = vx + 0.16666667 * dt * (dvx + 2*dvx2 + 2*dvx3 + dvx4)
            vy2 = vy + 0.16666667 * dt * (dvy + 2*dvy2 + 2*dvy3 + dvy4)
            x3 = x[i-1] + dt * (dx + 2*dx2 + 2*dx3 + dx4)
            y3 = y[i-1] + dt * (dy + 2*dy2 + 2*dy3 + dy4)
            vx3 = vx + dt * (dvx + 2*dvx2 + 2*dvx3 + dvx4)
            vy3 = vy + dt * (dvy + 2*dvy2 + 2*dvy3 + dvy4)
            x[i] = x[i] - 0.16666667 * dt * (dx + 2*dx2 + 2*dx3 + dx4)
            y[i] = y[i] - 0.16666667 * dt * (dy + 2*dy2 + 2*dy3 + dy4)
            vx = vx + dt * dvx3
            vy = vy + dt * dvy3
            if y[i] <= 0.0:
                n = i
                break
        else:
            n = nmax
    
    a = -y[n] / y[n-1]
    x[n] = (x[n] + a * x[n-1]) / (1 + a)
    y[n] = 0.0
    
    return n

def display(x, y, nmax, theta, Am, dt, lsym, nsym, method):
    with open('graph.out', 'w') as f:
        f.write("Distance(m)       Height(m)\n")
        for i in range(nmax + 1):
            f.write(f"{x[i]} {y[i]}\n")
    
    print("Data successfully written to graph.out for comparison.")

def main():
    global dt, vinit, theta, Am, lsym, nsym, method
    
    dt, vinit, theta, Am, lsym, nsym, method = initialize()
    n = calculate(x, y, dt, vinit, theta, Am, method)
    display(x, y, n, theta, Am, dt, lsym, nsym, method)

if __name__ == "__main__":
    main()