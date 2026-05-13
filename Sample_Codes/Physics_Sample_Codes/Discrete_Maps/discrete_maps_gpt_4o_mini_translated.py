import numpy as np

def f(x, b):
    return 4.0 * b * x * (1.0 - x)

def g(x, a):
    return a * (1.0 - 2.0 * abs(x - 0.5))

def h(x, c):
    return c * (1.0 - (2.0 * x - 1.0) ** 4)

def initialize():
    print('which map? logistic (1), cusp (2), 4th order (3)?')
    map_choice = int(input().strip())
    
    if map_choice == 1:
        print('b in f(x)=4bx(1-x) ?')
        b = float(input().strip())
        return b, map_choice
    elif map_choice == 2:
        print('a in g(x)=a(1-2|x-1/2|) ?')
        a = float(input().strip())
        return a, map_choice
    else:
        print('c in h(x)=c[1-(2x-1)**4] ?')
        c = float(input().strip())
        return c, map_choice

def main():
    param, map_choice = initialize()
    
    print('initial x ?')
    x0 = float(input().strip())
    print('how may iterations?')
    iter_count = int(input().strip())
    print('output file?')
    of = input().strip()
    
    x = x0
    iter1 = iter_count + 1
    
    with open(of, 'w') as file_handle:
        if map_choice == 1:
            for i in range(1, iter1 + 1):
                file_handle.write(f"{i - 1:1.0f} {x:12.5e}\n")
                x = f(x, param)
        elif map_choice == 2:
            for i in range(1, iter1 + 1):
                file_handle.write(f"{i - 1:1.0f} {x:12.5e}\n")
                x = g(x, param)
        else:
            for i in range(1, iter1 + 1):
                file_handle.write(f"{i - 1:1.0f} {x:12.5e}\n")
                x = h(x, param)

    print('another try ?')
    ans = input().strip()
    if ans == 'y':
        main()

if __name__ == "__main__":
    main()