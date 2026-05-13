import sys
import bisect

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])
    idx = bisect.bisect_left(arr, target)
    if idx < n and arr[idx] == target:
        sys.stdout.write(str(idx))
    else:
        sys.stdout.write("-1")

if __name__ == "__main__":
    main()