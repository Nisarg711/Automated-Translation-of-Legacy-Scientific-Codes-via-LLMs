# Discrete Maps
# Iteration of discrete map, not ODE integration
# Python version translated from Fortran code by H. Nakanishi

def f(x, b):
    return 4.0 * b * x * (1.0 - x)

def g(x, a):
    return a * (1.0 - 2.0 * abs(x - 0.5))

def h(x, c):
    return c * (1.0 - (2.0 * x - 1.0) ** 4)

def initialize():
    print("which map? logistic (1), cusp (2), 4th order (3)?")
    map_type = int(input().strip())
    a = b = c = 0.0
    if map_type == 1:
        print("b in f(x)=4bx(1-x) ?")
        b = float(input().strip())
    elif map_type == 2:
        print("a in g(x)=a(1-2|x-1/2|) ?")
        a = float(input().strip())
    else:
        print("c in h(x)=c[1-(2x-1)**4] ?")
        c = float(input().strip())
    print("initial x ?")
    x0 = float(input().strip())
    print("how may iterations?")
    iter_count = int(input().strip())
    print("output file?")
    of = input().strip()
    return x0, map_type, a, b, c, iter_count, of

def main():
    yes = 'y'
    while True:
        x0, map_type, a, b, c, iter_count, of = initialize()
        with open(of, 'w') as file:
            x = x0
            iter1 = iter_count + 1
            if map_type == 1:
                for i in range(iter1):
                    file.write(f" {float(i):12.5e}  {x:12.5e}\n")
                    x = f(x, b)
            elif map_type == 2:
                for i in range(iter1):
                    file.write(f" {float(i):12.5e}  {x:12.5e}\n")
                    x = g(x, a)
            else:
                for i in range(iter1):
                    file.write(f" {float(i):12.5e}  {x:12.5e}\n")
                    x = h(x, c)
        print("another try ?")
        ans = input().strip()
        if ans != yes:
            break

if __name__ == "__main__":
    main()