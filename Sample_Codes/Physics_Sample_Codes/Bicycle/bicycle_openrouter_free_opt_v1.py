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
    method = int(sys.stdin.readline().strip())
    
    if method != 1 and method != 2:
        print('must select 1 or 2 ..')
        sys.exit()
    
    print('initial velocity -> ')
    velocity[1] = float(sys.stdin.readline().strip())
    t[1] = 0
    
    print('time step -> ')
    dt = float(sys.stdin.readline().strip())
    
    print('max time -> ')
    tmax = float(sys.stdin.readline().strip())
    
    nmax = min(int(tmax / dt), 5000)
    
    print('constant power -> ')
    power = float(sys.stdin.readline().strip())
    
    mass = 70.0
    c = 0.5
    area = 0.33
    density = 1.29
    
    print('set line, symbol?')
    ans = sys.stdin.readline().strip()
    
    if ans == yes:
        print('line and symbol numbers -> ')
        lsym = int(sys.stdin.readline().strip())
        nsym = int(sys.stdin.readline().strip())
    else:
        lsym = -1
        nsym = 1


def calculate():
    global t, velocity, method, dt, power, mass, c, density, area
    
    c_r = c * density * area
    
    if method == 1:
        # Euler method - inline f calculation
        for i in range(1, nmax):
            v = velocity[i]
            if v == 0.0:
                dv = float('inf')
            else:
                dv = (power / v - c_r * v * v) / mass
            velocity[i + 1] = v + dt * dv
            t[i + 1] = t[i] + dt
    else:
        # Runge-Kutta 2nd order - inline f calculation
        for i in range(1, nmax):
            v = velocity[i]
            if v == 0.0:
                dv = float('inf')
            else:
                dv = (power / v - c_r * v * v) / mass
            v1 = v + 0.5 * dt * dv
            if v1 == 0.0:
                dv1 = float('inf')
            else:
                dv1 = (power / v1 - c_r * v1 * v1) / mass
            velocity[i + 1] = v + dt * dv1
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