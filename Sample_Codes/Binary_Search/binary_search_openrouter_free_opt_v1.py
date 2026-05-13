import sys

def binarySearch(arr, n, target):
    left, right = 0, n - 1
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
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    arr = [0] * 1000
    for i in range(n):
        arr[i] = int(data[idx]); idx += 1
    target = int(data[idx])
    result = binarySearch(arr, n, target)
    print(result if result != -1 else -1)

if __name__ == "__main__":
    main()