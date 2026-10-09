
#include <iostream>
#include <vector>
using namespace std;

using Matrix = vector<vector<int>>;

// Normal multiplication: C = A * B
Matrix normalMultiply(const Matrix& A, const Matrix& B) {
    int rows = A.size();
    int mid = B.size();
    int cols = B[0].size();

    Matrix C(rows, vector<int>(cols, 0));

    for (int i = 0; i < rows; i++) {
        for (int k = 0; k < mid; k++) {
            for (int j = 0; j < cols; j++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    return C;
}

Matrix add(const Matrix& A, const Matrix& B) {
    int n = A.size();
    Matrix C(n, vector<int>(n, 0));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = A[i][j] + B[i][j];

    return C;
}

Matrix subtract(const Matrix& A, const Matrix& B) {
    int n = A.size();
    Matrix C(n, vector<int>(n, 0));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = A[i][j] - B[i][j];

    return C;
}

// Strassen multiplication for power-of-two square matrices
Matrix strassen(const Matrix& A, const Matrix& B) {
    int n = A.size();

    // Cutoff: use normal multiplication for small matrices
    if (n <= 2)
        return normalMultiply(A, B);

    int k = n / 2;

    Matrix A11(k, vector<int>(k));
    Matrix A12(k, vector<int>(k));
    Matrix A21(k, vector<int>(k));
    Matrix A22(k, vector<int>(k));

    Matrix B11(k, vector<int>(k));
    Matrix B12(k, vector<int>(k));
    Matrix B21(k, vector<int>(k));
    Matrix B22(k, vector<int>(k));

    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) {
            A11[i][j] = A[i][j];
            A12[i][j] = A[i][j + k];
            A21[i][j] = A[i + k][j];
            A22[i][j] = A[i + k][j + k];

            B11[i][j] = B[i][j];
            B12[i][j] = B[i][j + k];
            B21[i][j] = B[i + k][j];
            B22[i][j] = B[i + k][j + k];
        }
    }

    Matrix M1 = strassen(add(A11, A22), add(B11, B22));
    Matrix M2 = strassen(add(A21, A22), B11);
    Matrix M3 = strassen(A11, subtract(B12, B22));
    Matrix M4 = strassen(A22, subtract(B21, B11));
    Matrix M5 = strassen(add(A11, A12), B22);
    Matrix M6 = strassen(subtract(A21, A11), add(B11, B12));
    Matrix M7 = strassen(subtract(A12, A22), add(B21, B22));

    Matrix C11 = add(subtract(add(M1, M4), M5), M7);
    Matrix C12 = add(M3, M5);
    Matrix C21 = add(M2, M4);
    Matrix C22 = add(add(subtract(M1, M2), M3), M6);

    Matrix C(n, vector<int>(n, 0));

    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) {
            C[i][j] = C11[i][j];
            C[i][j + k] = C12[i][j];
            C[i + k][j] = C21[i][j];
            C[i + k][j + k] = C22[i][j];
        }
    }

    return C;
}

// Hybrid multiplication for any square dimension
Matrix hybridMultiply(const Matrix& A, const Matrix& B) {
    int n = A.size();

    // Largest power of 2 not greater than n
    int p = 1;
    while (p * 2 <= n)
        p *= 2;

    Matrix C(n, vector<int>(n, 0));

    // Multiply the top-left p x p blocks using Strassen
    Matrix A0(p, vector<int>(p));
    Matrix B0(p, vector<int>(p));

    for (int i = 0; i < p; i++) {
        for (int j = 0; j < p; j++) {
            A0[i][j] = A[i][j];
            B0[i][j] = B[i][j];
        }
    }

    Matrix C0 = strassen(A0, B0);

    for (int i = 0; i < p; i++)
        for (int j = 0; j < p; j++)
            C[i][j] = C0[i][j];

    // Add contributions from the remaining inner dimensions
    for (int k = p; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    // Handle output rows/columns outside the p x p block
    for (int k = 0; k < p; k++) {
        for (int i = 0; i < n; i++) {
            if (i < p)
                continue;

            for (int j = 0; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
        }

        for (int i = 0; i < p; i++) {
            for (int j = p; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }

    return C;
}

int main() {
    int n;
    cout << "Enter matrix size: ";
    cin >> n;

    if (n <= 0) {
        cout << "Invalid matrix size\n";
        return 0;
    }

    Matrix A(n, vector<int>(n,1));
    Matrix B(n, vector<int>(n,2));
    Matrix C = hybridMultiply(A, B);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++)
            cout << C[i][j] << " ";
        cout << "\n";
    }

    return 0;
}
