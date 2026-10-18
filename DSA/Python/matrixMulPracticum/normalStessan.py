import math
def add_matrices(A, B):
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(A, B)]

def sub_matrices(A, B):
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(A, B)]

def split_matrix(A):
    k = len(A) // 2
    A11 = [row[:k] for row in A[:k]]
    A12 = [row[k:] for row in A[:k]]
    A21 = [row[:k] for row in A[k:]]
    A22 = [row[k:] for row in A[k:]]
    return A11, A12, A21, A22

def merge_matrices(C11, C12, C21, C22):
    top = [row_11 + row_12 for row_11, row_12 in zip(C11, C12)]
    bottom = [row_21 + row_22 for row_21, row_22 in zip(C21, C22)]
    return top + bottom

def strassen(A, B):
    if len(A) == 1:
        return [[A[0][0] * B[0][0]]]

    A11, A12, A21, A22 = split_matrix(A)
    B11, B12, B21, B22 = split_matrix(B)

    # M1 = (A11 + A22) * (B11 + B22)
    M1 = strassen(add_matrices(A11, A22), add_matrices(B11, B22))
    
    # M2 = (A21 + A22) * B11
    M2 = strassen(add_matrices(A21, A22), B11)
    
    # M3 = A11 * (B12 - B22)
    M3 = strassen(A11, sub_matrices(B12, B22))
    
    # M4 = A22 * (B21 - B11)
    M4 = strassen(A22, sub_matrices(B21, B11))
    
    # M5 = (A11 + A12) * B22
    M5 = strassen(add_matrices(A11, A12), B22)
    
    # M6 = (A21 - A11) * (B11 + B12)
    M6 = strassen(sub_matrices(A21, A11), add_matrices(B11, B12))
    
    # M7 = (A12 - A22) * (B21 + B22)
    M7 = strassen(sub_matrices(A12, A22), add_matrices(B21, B22))

    C11 = add_matrices(sub_matrices(add_matrices(M1, M4), M5), M7)
    C12 = add_matrices(M3, M5)
    C21 = add_matrices(M2, M4)
    C22 = add_matrices(sub_matrices(add_matrices(M1, M3), M2), M6)

    return merge_matrices(C11, C12, C21, C22)

A = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]

B = [
    [16, 15, 14, 13],
    [12, 11, 10, 9],
    [8, 7, 6, 5],
    [4, 3, 2, 1]
]

C = strassen(A, B)