def initialize(x0, map, a, b, c, iter, of):
    print('which map? logistic (1), cusp (2), 4th order (3)?')
    map = int(input().strip())
    if map == 1:
        print('b in f(x)=4bx(1-x) ?')
        b = float(input().strip())
    elif map == 2:
        print('a in g(x)=a(1-2|x-1/2|) ?')
        a = float(input().strip())
    else:
        print('c in h(x)=c[1-(2x-1)**4] ?')
        c = float(input().strip())
    print('initial x ?')
    x0 = float(input().strip())
    print('how may iterations?')
    iter = int(input().strip())
    print('output file?')
    of = input().strip()
    return x0, map, a, b, c, iter, of

def f(x, b):
    return 4.0 * b * x * (1.0 - x)

def g(x, a):
    return a * (1.0 - 2.0 * abs(x - 0.5))

def h(x, c):
    return c * (1.0 - (2.0 * x - 1.0)**4)

def main():
    ans = ''
    yes = 'y'
    of = ''
    x0 = 0.0
    map = 0
    a = 0.0
    b = 0.0
    c = 0.0
    iter = 0
    x = 0.0
    iter1 = 0

    x0, map, a, b, c, iter, of = initialize(x0, map, a, b, c, iter, of)

    with open(of, 'w') as outfile:
        x = x0
        iter1 = iter + 1
        if map == 1:
            for i in range(1, iter1 + 1):
                outfile.write(f" {i-1:12.5e}  {x:12.5e}\n")
                x = f(x, b)
        elif map == 2:
            for i in range(1, iter1 + 1):
                outfile.write(f" {i-1:12.5e}  {x:12.5e}\n")
                x = g(x, a)
        else:
            for i in range(1, iter1 + 1):
                outfile.write(f" {i-1:12.5e}  {x:12.5e}\n")
                x = h(x, c)

    print('another try ?')
    ans = input().strip()
    if ans == yes:
        main()

if __name__ == "__main__":
    main()