def binary_search(arr, target):
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
    import sys
    input = sys.stdin.read
    data = input().splitlines()

    try:
        n = int(data[0])  # Read the size of the array

        if n > 0:
            arr = list(map(int, data[1].split()))  # Read all elements in one line and convert to integers
        else:
            print(-1)
            return

        if len(data) > 2 and data[2].strip():
            target = int(data[2])
        else:
            print(-1)
            return

        print(binary_search(arr, target))
    except (ValueError, IndexError):
        print(-1)


if __name__ == "__main__":
    main()