import math

def init():
    """
    Initialize variables
    """
    print("Flow: input file name ?")
    ifile = input().strip()

    try:
        with open(ifile, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("File not found.")
        return None

    if not lines:
        print("File is empty.")
        return None

    rmin = 0.0
    rmax = 0.0
    n = 0
    x = []
    y = []
    z1 = []
    z2 = []
    r = []

    for line in lines:
        try:
            x_val, y_val, z1_val, z2_val = map(float, line.split())
            x.append(x_val)
            y.append(y_val)
            z1.append(z1_val)
            z2.append(z2_val)

            r_val = math.sqrt(z1_val ** 2 + z2_val ** 2)
            r.append(r_val)

            if r_val < rmin or n == 0:
                rmin = r_val
            if r_val > rmax:
                rmax = r_val

            n += 1
        except ValueError:
            break

    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)

    print("max vector length = ", rmax, ", min = ", rmin)

    if rmax != rmin:
        print("map the max and min lengths to: ")
        amax, amin = map(float, input().strip().split())
        afac = (amax - amin) / (rmax - rmin)
        aoff = amin
    else:
        print("map the arrow length to: ")
        amin = float(input().strip())
        afac = 0.0
        aoff = amin

    return ifile, rmin, afac, aoff, xmin, xmax, ymin, ymax, x, y, z1, z2, r, n


def disp(ifile, rmin, afac, aoff, xmin, xmax, ymin, ymax, x, y, z1, z2, r, n):
    """
    Display the results
    """
    if xmin != xmax:
        xfac = 5.0 / (xmax - xmin)
        xoff = 0.0
    else:
        xfac = 1.0
        xoff = 2.5

    if ymin != ymax:
        yfac = 5.0 / (ymax - ymin)
        yoff = 0.0
    else:
        yfac = 0.0
        yoff = 2.5

    with open('graph.out', 'w') as f:
        f.write('      x0            y0            a0            th\n')
        for i in range(n):
            x0 = xfac * (x[i] - xmin) + xoff
            y0 = yfac * (y[i] - ymin) + yoff
            r0 = math.sqrt(z1[i] ** 2 + z2[i] ** 2)
            a0 = afac * (r0 - rmin) + aoff

            if z1[i] != 0:
                th = math.degrees(math.atan(z2[i] / z1[i]))
            else:
                th = 90.0
                if z2[i] < 0:
                    th = 270.0

            if z1[i] < 0:
                th += 180.0

            if th < 0:
                th += 360.0

            f.write(f"{x0:15.5f} {y0:15.5f} {a0:15.5f} {th:15.5f}\n")

    print("Data successfully written to graph.out for comparison.")


def main():
    result = init()
    if result:
        ifile, rmin, afac, aoff, xmin, xmax, ymin, ymax, x, y, z1, z2, r, n = result
        disp(ifile, rmin, afac, aoff, xmin, xmax, ymin, ymax, x, y, z1, z2, r, n)


if __name__ == "__main__":
    main()