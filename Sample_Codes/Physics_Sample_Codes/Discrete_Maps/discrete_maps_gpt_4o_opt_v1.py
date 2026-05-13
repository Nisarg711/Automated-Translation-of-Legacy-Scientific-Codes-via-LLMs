# Optimized Code

def f(x, b):
    return 4.0 * b * x * (1.0 - x)

def g(x, a):
    return a * (1.0 - 2.0 * abs(x - 0.5))

def h(x, c):
    return c * (1.0 - (2.0 * x - 1.0) ** 4)

def initialize():
    map_type = int(input("which map? logistic (1), cusp (2), 4th order (3)? ").strip())
    if map_type == 1:
        b = float(input("b in f(x)=4bx(1-x) ? ").strip())
        a = c = 0.0
    elif map_type == 2:
        a = float(input("a in g(x)=a(1-2|x-1/2|) ? ").strip())
        b = c = 0.0
    else:
        c = float(input("c in h(x)=c[1-(2x-1)**4] ? ").strip())
        a = b = 0.0
    x0 = float(input("initial x ? ").strip())
    iter_count = int(input("how many iterations? ").strip())
    of = input("output file? ").strip()
    return x0, map_type, a, b, c, iter_count, of

def main():
    while True:
        x0, map_type, a, b, c, iter_count, of = initialize()
        with open(of, 'w') as file:
            x = x0
            if map_type == 1:
                func = lambda x: f(x, b)
            elif map_type == 2:
                func = lambda x: g(x, a)
            else:
                func = lambda x: h(x, c)
            for i in range(iter_count + 1):
                file.write(f"{i:12.5e}  {x:12.5e}\n")
                x = func(x)
        if input("another try ? (y/n) ").strip().lower() != 'y':
            break

if __name__ == "__main__":
    main()