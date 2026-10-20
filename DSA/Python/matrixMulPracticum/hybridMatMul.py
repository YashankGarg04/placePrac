import math

def normal_matrix_mul(A, B):
    """
    Standard O(N^3) multiplication.
    In a real production environment (like NumPy/C++), this is where 
    SIMD vectorization and L1 cache blocking happen.
    """
    return [[sum(a * b for a, b in zip(row_A, col_B)) for col_B in zip(*B)] for row_A in A]

def add_matrices(A, B):
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(A, B)]

def sub_matrices(A, B):
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(A, B)]

def split_matrix(A):
    k = len(A) // 2
    return [row[:k] for row in A[:k]], [row[k:] for row in A[:k]], \
           [row[:k] for row in A[k:]], [row[k:] for row in A[k:]]

def hybrid_strassen_core(A, B, threshold=64):

    n = len(A)
    
    if n <= threshold:
        return normal_matrix_mul(A, B)

    A11, A12, A21, A22 = split_matrix(A)
    B11, B12, B21, B22 = split_matrix(B)

    M1 = hybrid_strassen_core(add_matrices(A11, A22), add_matrices(B11, B22), threshold)
    M2 = hybrid_strassen_core(add_matrices(A21, A22), B11, threshold)
    M3 = hybrid_strassen_core(A11, sub_matrices(B12, B22), threshold)
    M4 = hybrid_strassen_core(A22, sub_matrices(B21, B11), threshold)
    M5 = hybrid_strassen_core(add_matrices(A11, A12), B22, threshold)
    M6 = hybrid_strassen_core(sub_matrices(A21, A11), add_matrices(B11, B12), threshold)
    M7 = hybrid_strassen_core(sub_matrices(A12, A22), add_matrices(B21, B22), threshold)

    C11 = add_matrices(sub_matrices(add_matrices(M1, M4), M5), M7)
    C12 = add_matrices(M3, M5)
    C21 = add_matrices(M2, M4)
    C22 = add_matrices(sub_matrices(add_matrices(M1, M3), M2), M6)

    top = [row_11 + row_12 for row_11, row_12 in zip(C11, C12)]
    bottom = [row_21 + row_22 for row_21, row_22 in zip(C21, C22)]
    return top + bottom

def efficient_matmul(A, B, threshold=64):
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    
    if cols_A != rows_B:
        raise ValueError("Incompatible matrices.")
    max_dim = max(rows_A, cols_A, rows_B, cols_B)
    
    if max_dim <= threshold:
        optimal_dim = max_dim
    else:
        doublings = math.ceil(math.log2(max_dim / threshold))
        optimal_dim = threshold * (2 ** doublings)
    A_padded = [[A[i][j] if i < rows_A and j < cols_A else 0 
                 for j in range(optimal_dim)] for i in range(optimal_dim)]
    
    B_padded = [[B[i][j] if i < rows_B and j < cols_B else 0 
                 for j in range(optimal_dim)] for i in range(optimal_dim)]

    C_padded = hybrid_strassen_core(A_padded, B_padded, threshold)

    return [row[:cols_B] for row in C_padded[:rows_A]]
