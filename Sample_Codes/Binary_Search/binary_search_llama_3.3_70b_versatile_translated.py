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
    n = int(input())

    arr = [0] * 1000  # Maximum array size
    elements = input()
    elements = elements.split()
    for i in range(n):
        arr[i] = int(elements[i])

    target = int(input())

    result = binarySearch(arr, n, target)

    if result != -1:
        print(result)
    else:
        print(-1)


if __name__ == "__main__":
    main()