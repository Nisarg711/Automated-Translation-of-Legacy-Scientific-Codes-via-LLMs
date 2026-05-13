def solve(arr):
    # Get the size of the array
    n = len(arr)
    
    # If there's only one house, return its value
    if n == 1:
        return arr[0]

    # prev stores the maximum sum till the previous index
    prev = arr[0]

    # prev2 stores the maximum sum till the index before previous
    prev2 = 0

    # Loop through houses starting from index 1
    for i in range(1, n):
        # Option 1: Pick the current house and add the value from prev2
        pick = arr[i]
        if i > 1:
            pick += prev2

        # Option 2: Skip the current house, take prev
        nonPick = prev

        # Choose the maximum of pick and nonPick
        cur_i = max(pick, nonPick)

        # Update prev2 and prev for the next iteration
        prev2 = prev
        prev = cur_i

    # prev will contain the maximum loot possible
    return prev


def robStreet(n, arr):
    # If there are no houses, return 0
    if n == 0:
        return 0

    # If there is only one house, return its value
    if n == 1:
        return arr[0]

    # Create two arrays:
    # arr1 excludes the first house
    # arr2 excludes the last house
    arr1 = arr[1:]
    arr2 = arr[:-1]

    # Compute maximum loot for both cases and return the maximum
    ans1 = solve(arr1)
    ans2 = solve(arr2)
    return max(ans1, ans2)


# Driver code
if __name__ == "__main__":
    t = int(input())  # number of test cases

    for _ in range(t):
        n = int(input())
        arr = [int(x) for x in input().split()]

        print(robStreet(n, arr))