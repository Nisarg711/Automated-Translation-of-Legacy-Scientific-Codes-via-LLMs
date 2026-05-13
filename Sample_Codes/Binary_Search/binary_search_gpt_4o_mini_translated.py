import sys
import time

def binarySearch(arr, n, target):
    left = 0
    right = n - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # Not found

def main():
    # --- I/O TIMING START ---
    t_io_start = time.perf_counter()
    
    # Read everything, replace literal "\n" strings with spaces, then split
    raw_input = sys.stdin.read()
    input_data = raw_input.replace('\\n', ' ').split()
    
    if not input_data: 
        return
        
    n = int(input_data[0])
    arr = [int(x) for x in input_data[1:n+1]]
    target = int(input_data[n+1])

    # --- I/O TIMING END ---
    t_io_end = time.perf_counter()


    # --- CALC TIMING START ---
    t_calc_start = time.perf_counter()

    result = binarySearch(arr, n, target)

    # --- CALC TIMING END ---
    t_calc_end = time.perf_counter()


    # Standard output for the test suite
    if result != -1:
        sys.stdout.write(str(result))
    else:
        sys.stdout.write(str(-1))

    # Print metrics to standard error
    sys.stderr.write(f"\nPython I/O Time:   {(t_io_end - t_io_start) * 1000:.3f} ms\n")
    sys.stderr.write(f"Python Calc Time: {(t_calc_end - t_calc_start) * 1000:.3f} ms\n")

if __name__ == "__main__":
    main()