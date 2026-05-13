#include <stdio.h>
#include <time.h> // Required for clock_gettime

int binarySearch(int arr[], int n, int target) {
    int left = 0, right = n - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (arr[mid] == target)
            return mid;
        else if (arr[mid] < target)
            left = mid + 1;
        else
            right = mid - 1;
    }

    return -1;  // Not found
}

int main() {
    struct timespec start_io, end_io, start_calc, end_calc;

    // --- I/O TIMING START ---
    clock_gettime(CLOCK_MONOTONIC, &start_io);

    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    int arr[1000];  // Maximum array size
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int target;
    scanf("%d", &target);

    // --- I/O TIMING END ---
    clock_gettime(CLOCK_MONOTONIC, &end_io);


    // --- CALC TIMING START ---
    clock_gettime(CLOCK_MONOTONIC, &start_calc);

    int result = binarySearch(arr, n, target);

    // --- CALC TIMING END ---
    clock_gettime(CLOCK_MONOTONIC, &end_calc);


    // Standard output for the test suite
    if (result != -1)
        printf("%d", result);
    else
        printf("%d", -1);

    // Calculate elapsed time in milliseconds
    double io_time = (end_io.tv_sec - start_io.tv_sec) * 1000.0 + 
                     (end_io.tv_nsec - start_io.tv_nsec) / 1000000.0;
    double calc_time = (end_calc.tv_sec - start_calc.tv_sec) * 1000.0 + 
                       (end_calc.tv_nsec - start_calc.tv_nsec) / 1000000.0;

    // Print metrics to stderr so it doesn't break your test suite!
    fprintf(stderr, "\nC Legacy I/O Time:   %.3f ms\n", io_time);
    fprintf(stderr, "C Legacy Calc Time: %.3f ms\n", calc_time);

    return 0;
}