#include <stdio.h>
#include <stdlib.h>

void nextGreaterElement(int arr[], int n) {
    int stack[n];
    int top = -1;

    stack[++top] = arr[0];

    for (int i = 1; i < n; i++) {
        int next = arr[i];

        while (top >= 0 && stack[top] < next) {
            printf("%d --> %d\n", stack[top--], next);
        }

        stack[++top] = next;
    }

    while (top >= 0) {
        printf("%d --> -1\n", stack[top--]);
    }
}

int main() {
    int n;
    scanf("%d", &n);
    
    if (n <= 0) {
        return 0;
    }
    
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }

    nextGreaterElement(arr, n);

    return 0;
}
