import sys

defmain():
    it = iter(sys.stdin.read().split())
    map_type = int(next(it))

    if map_type == 1:
        b = float(next(it))
        step = lambda x: 4.0 * b * x * (1.0 - x)
    elif map_type == 2:
        a = float(next(it))
        step = lambda x: a * (1.0 - 2.0 * abs(x - 0.5))
    else:
        c = float(next(it))
        step = lambda x: c * (1.0 - (2.0 * x - 1.0) ** 4)

    x0 = float(next(it))
    n_iter = int(next(it))
    ofile = next(it)

    with open(ofile, "w") as out:
        x = x0
        for i in range(n_iter + 1):
            out.write(f"{i:12.5e}{x:12.5e}\n")
            x = step(x)

if __name__ == "__main__":
    main()