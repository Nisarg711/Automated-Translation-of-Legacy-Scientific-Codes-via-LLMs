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

    return -1  # Not found


def main():
    try:
        n = int(input().strip())  # Read the size of the array

        if n > 0:
            arr = list(map(int, input().strip().split()))  # Read all elements in one line and convert to integers
        else:
            arr = []

        target_input = input().strip()  # Read the target value
        if target_input:
            target = int(target_input)
        else:
            print(-1)
            return

        result = binary_search(arr, n, target)

        if result != -1:
            print(result)
        else:
            print(-1)
    except ValueError:
        print(-1)


if __name__ == "__main__":
    main()