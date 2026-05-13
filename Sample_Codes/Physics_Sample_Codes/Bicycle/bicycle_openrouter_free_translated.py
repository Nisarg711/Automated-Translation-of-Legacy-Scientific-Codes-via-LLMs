import sys

# Global arrays (size 5003 to match Fortran's 5003 elements with 1-based indexing)
t = [0.0] * 5003
velocity = [0.0] * 5003

# Global variables
dt = 0.0
power = 0.0
mass = 0.0
nmax = 0
c = 0.0
area = 0.0
density = 0.0
lsym = 0
nsym = 0
method = 0


def initialize():
    global dt, power, mass, nmax, c, area, density, lsym, nsym, method
    
    yes = 'y'
    
    print('Euler (1) or Runge-Kutta (2)? -> ')
    method = int(input().strip())
    
    if method != 1 and method != 2:
        print('must select 1 or 2 ..')
        sys.exit()
    
    print('initial velocity -> ')
    velocity[1] = float(input().strip())
    t[1] = 0
    
    print('time step -> ')
    dt = float(input().strip())
    
    print('max time -> ')
    tmax = float(input().strip())
    
    nmax = min(int(tmax / dt), 5000)
    
    print('constant power -> ')
    power = float(input().strip())
    
    mass = 70.0
    c = 0.5
    area = 0.33
    density = 1.29
    
    print('set line, symbol?')
    ans = input().strip()
    
    if ans == yes:
        print('line and symbol numbers -> ')
        lsym_line = input().strip()
        nsym_line = input().strip()
        lsym = int(lsym_line)
        nsym = int(nsym_line)
    else:
        lsym = -1
        nsym = 1


def f(v, p, x, c_val, rho, a):
    # Fortran: f=(p/v-c*rho*a*v**2)/x
    # Handle division by zero - return inf like Fortran
    if v == 0.0:
        return float('inf')
    return (p / v - c_val * rho * a * v ** 2) / x


def calculate():
    global t, velocity
    
    if method == 1:
        # Euler method
        for i in range(1, nmax):
            # v(i+1) = v(i) + dt * f(v(i), power, mass, c, density, area)
            velocity[i + 1] = velocity[i] + dt * f(velocity[i], power, mass, c, density, area)
            t[i + 1] = t[i] + dt
    else:
        # Runge-Kutta 2nd order
        for i in range(1, nmax):
            v1 = velocity[i] + 0.5 * dt * f(velocity[i], power, mass, c, density, area)
            velocity[i + 1] = velocity[i] + dt * f(v1, power, mass, c, density, area)
            t[i + 1] = t[i] + dt


def display():
    # Write to graph.out file
    with open('graph.out', 'w') as fout:
        fout.write('Time(s)           Velocity(m/s)\n')
        for i in range(1, nmax + 1):
            fout.write(f"{t[i]} {velocity[i]}\n")
    
    print('Data successfully written to graph.out for comparison.')


def main():
    initialize()
    calculate()
    display()


if __name__ == "__main__":
    main()