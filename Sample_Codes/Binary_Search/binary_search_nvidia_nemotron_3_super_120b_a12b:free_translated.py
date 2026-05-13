import sys

def binary_search(arr, n, target):
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
    return -1

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])
    result = binary_search(arr, n, target)
    sys.stdout.write(str(result))

if __name__ == "__main__":
    main()