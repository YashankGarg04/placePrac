def normal_matrix_mul(A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    rows_B = len(B)
    cols_B = len(B[0])

    # Validate dimensions
    if cols_A != rows_B:
        raise ValueError("Incompatible matrices: A columns must match B rows.")

    # Initialize the result matrix C with zeros
    C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]

    # Standard O(N^3) multiplication
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                C[i][j] += A[i][k] * B[k][j]

    return C