#include <stdio.h>
#define MAX 100

int main() {
    int r1, c1, r2, c2;
    
    // Read dimensions of first matrix
    scanf("%d %d", &r1, &c1);
    
    int A[MAX][MAX], B[MAX][MAX], C[MAX][MAX];
    
    // Read first matrix
    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c1; j++) {
            scanf("%d", &A[i][j]);
        }
    }
    
    // Read dimensions of second matrix
    scanf("%d %d", &r2, &c2);
    
    // Read second matrix
    for (int i = 0; i < r2; i++) {
        for (int j = 0; j < c2; j++) {
            scanf("%d", &B[i][j]);
        }
    }
    
    // Check if multiplication is possible
    if (c1 != r2) {
        printf("Matrix multiplication not possible\n");
        return 1;
    }

    // Multiply matrices
    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c2; j++) {
            C[i][j] = 0;
            for (int k = 0; k < c1; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    // Print result matrix
    printf("Result matrix:\n");
    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c2; j++)
            printf("%d ", C[i][j]);
        printf("\n");
    }

    return 0;
}
