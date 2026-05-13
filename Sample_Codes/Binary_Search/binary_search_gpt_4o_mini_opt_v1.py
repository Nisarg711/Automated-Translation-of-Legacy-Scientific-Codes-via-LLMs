def binarySearch(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # Not found

def main():
    n = int(input().strip())
    arr = list(map(int, input().strip().split()))
    target = int(input().strip())

    result = binarySearch(arr, target)

    print(result)

if __name__ == "__main__":
    main()