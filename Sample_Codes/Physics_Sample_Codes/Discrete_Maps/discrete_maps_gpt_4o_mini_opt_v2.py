import numpy as np

def f(x, b):
    return 4.0 * b * x * (1.0 - x)

def g(x, a):
    return a * (1.0 - 2.0 * abs(x - 0.5))

def h(x, c):
    return c * (1.0 - (2.0 * x - 1.0) ** 4)

def initialize():
    map_choice = int(input('which map? logistic (1), cusp (2), 4th order (3)?\n').strip())
    param = float(input(f'{["b in f(x)=4bx(1-x) ?", "a in g(x)=a(1-2|x-1/2|) ?", "c in h(x)=c[1-(2x-1)**4] ?"][map_choice - 1]}\n').strip())
    return param, map_choice

def main():
    param, map_choice = initialize()
    
    x0 = float(input('initial x ?\n').strip())
    iter_count = int(input('how many iterations?\n').strip())
    of = input('output file?\n').strip()
    
    x = x0
    write_data = [f"{i} {x:12.5e}\n" for i in range(iter_count + 1)]
    
    with open(of, 'w') as file_handle:
        for i in range(iter_count + 1):
            file_handle.write(write_data[i])
            if map_choice == 1:
                x = f(x, param)
            elif map_choice == 2:
                x = g(x, param)
            else:
                x = h(x, param)

    if input('another try ? (y/n)\n').strip().lower() == 'y':
        main()

if __name__ == "__main__":
    main()