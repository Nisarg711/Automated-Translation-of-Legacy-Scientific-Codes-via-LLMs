import sys

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
    data = sys.stdin.read().split()
    idx = 0

    n = int(data[idx]); idx += 1

    arr = [0] * 1000  # Maximum array size
    for i in range(n):
        arr[i] = int(data[idx]); idx += 1

    target = int(data[idx]); idx += 1

    result = binarySearch(arr, n, target)

    if result != -1:
        sys.stdout.write(str(result))
    else:
        sys.stdout.write(str(-1))

if __name__ == "__main__":
    main()