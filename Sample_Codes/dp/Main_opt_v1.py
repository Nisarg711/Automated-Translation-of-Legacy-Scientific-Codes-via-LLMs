def solve(arr):
    # Base cases
    if not arr:
        return 0
    if len(arr) == 1:
        return arr[0]
    if len(arr) == 2:
        return max(arr)

    # Initialize dynamic programming table
    dp = [0] * len(arr)
    dp[0] = arr[0]
    dp[1] = max(arr[0], arr[1])

    # Fill up the dynamic programming table
    for i in range(2, len(arr)):
        dp[i] = max(dp[i-1], dp[i-2] + arr[i])

    # The last element in the table will contain the maximum loot possible
    return dp[-1]


def robStreet(n, arr):
    # Base cases
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