import math

def initialize():
    """Get user input for map type, parameters, and output file."""
    print("Which map? logistic (1), cusp (2), 4th order (3)?")
    map_val = int(input())
    if map_val == 1:
        print("b in f(x)=4bx(1-x) ?")
        b = float(input())
        a = None
        c = None
    elif map_val == 2:
        print("a in g(x)=a(1-2|x-1/2|) ?")
        a = float(input())
        b = None
        c = None
    else:
        print("c in h(x)=c[1-(2x-1)**4] ?")
        c = float(input())
        a = None
        b = None
    print("Initial x ?")
    x0 = float(input())
    print("How many iterations?")
    iter_val = int(input())
    print("Output file?")
    of = input()
    return x0, map_val, a, b, c, iter_val, of

def f(x, b):
    """Logistic map function."""
    return 4.0 * b * x * (1.0 - x)

def g(x, a):
    """Cusp map function."""
    return a * (1.0 - 2.0 * abs(x - 0.5))

def h(x, c):
    """4th order map function."""
    return c * (1.0 - (2.0 * x - 1.0) ** 4)

def main():
    """Main program loop."""
    yes = 'y'
    while True:
        x0, map_val, a, b, c, iter_val, of = initialize()
        with open(of, 'w') as output_file:
            x = x0
            for i in range(iter_val + 1):
                output_file.write(f"{float(i):12.5e} {x:12.5e}\n")
                if map_val == 1:
                    x = f(x, b)
                elif map_val == 2:
                    x = g(x, a)
                else:
                    x = h(x, c)
        print("Another try ?")
        ans = input()
        if ans != yes:
            break

if __name__ == "__main__":
    main()