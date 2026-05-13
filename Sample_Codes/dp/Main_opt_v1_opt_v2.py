def solve(arr):
    """Calculate the maximum loot in a street where the first and last houses are not adjacent."""
    if not arr:
        return 0
    if len(arr) <= 2:
        return max(arr)

    # Initialize dynamic programming table with the first two elements
    a, b = arr[0], max(arr[0], arr[1])

    # Fill up the dynamic programming table
    for i in range(2, len(arr)):
        a, b = b, max(b, a + arr[i])

    # The last element in the table will contain the maximum loot possible
    return b


def robStreet(n, arr):
    """Calculate the maximum loot in a circular street by considering two cases: 
    one where the first house is robbed and one where the last house is robbed."""
    if n == 0:
        return 0
    if n == 1:
        return arr[0]

    # Create two arrays: one excluding the first house and one excluding the last house
    return max(solve(arr[1:]), solve(arr[:-1]))


# Driver code
if __name__ == "__main__":
    t = int(input())  # number of test cases

    for _ in range(t):
        n = int(input())
        arr = [int(x) for x in input().split()]

        print(robStreet(n, arr))