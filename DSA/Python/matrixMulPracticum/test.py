import time
import math
import concurrent.futures
import multiprocessing
import matplotlib.pyplot as plt

# ==========================================
# 1. OPERATION MATH COUNTERS (Unchanged)
# ==========================================
def calc_normal_ops(n): return n ** 3, (n - 1) * (n ** 2)

def calc_pure_strassen_ops(n):
    m = 2 ** math.ceil(math.log2(n)) if n > 1 else 1
    if m == 1: return 1, 0
    levels = int(math.log2(m))
    return 7 ** levels, 6 * (7 ** levels) - 6 * (m ** 2)

def calc_hybrid_ops(n, threshold=64):
    if n <= threshold: return calc_normal_ops(n)
    doublings = math.ceil(math.log2(n / threshold))
    m = threshold * (2 ** doublings)
    total_mults = (7 ** doublings) * (threshold ** 3)
    total_adds = (7 ** doublings) * ((threshold - 1) * (threshold ** 2)) + 6 * (m ** 2) * ((7/4)**doublings - 1)
    return total_mults, total_adds

# ==========================================
# 2. SEQUENTIAL HELPERS
# ==========================================
def add_mat(A, B): return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]
def sub_mat(A, B): return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]

def split_mat(A):
    k = len(A) // 2
    return [r[:k] for r in A[:k]], [r[k:] for r in A[:k]], [r[:k] for r in A[k:]], [r[k:] for r in A[k:]]

def pad_matrix(A, target_size):
    n = len(A)
    return [[A[i][j] if i < n and j < n else 0 for j in range(target_size)] for i in range(target_size)]

def normal_matrix_mul(A, B):
    return [[sum(a * b for a, b in zip(row_A, col_B)) for col_B in zip(*B)] for row_A in A]

# ==========================================
# 3. INTERNAL ALGORITHM WORKERS (Top-Level for Pickling)
# ==========================================
# ---- Normal Matrix Workers ----
def parallel_normal_worker(args):
    start_r, end_r, A, B_T = args
    return [[sum(a * b for a, b in zip(A[i], col_B)) for col_B in B_T] for i in range(start_r, end_r)]

def parallel_normal(A, B):
    n = len(A)
    cores = multiprocessing.cpu_count()
    if n < 128: return normal_matrix_mul(A, B) # Too small for multi-core overhead
    
    B_T = list(zip(*B)) # Transpose B once for column access
    chunk = math.ceil(n / cores)
    tasks = [(i, min(i + chunk, n), A, B_T) for i in range(0, n, chunk)]
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as exec:
        results = list(exec.map(parallel_normal_worker, tasks))
    
    return [row for chunk_res in results for row in chunk_res]

# ---- Strassen Core Workers ----
def hybrid_strassen_seq(A, B, threshold=64):
    """Standard sequential hybrid strassen for deep recursion."""
    if len(A) <= threshold: return normal_matrix_mul(A, B)
    A11, A12, A21, A22 = split_mat(A)
    B11, B12, B21, B22 = split_mat(B)
    
    M1 = hybrid_strassen_seq(add_mat(A11, A22), add_mat(B11, B22), threshold)
    M2 = hybrid_strassen_seq(add_mat(A21, A22), B11, threshold)
    M3 = hybrid_strassen_seq(A11, sub_mat(B12, B22), threshold)
    M4 = hybrid_strassen_seq(A22, sub_mat(B21, B11), threshold)
    M5 = hybrid_strassen_seq(add_mat(A11, A12), B22, threshold)
    M6 = hybrid_strassen_seq(sub_mat(A21, A11), add_mat(B11, B12), threshold)
    M7 = hybrid_strassen_seq(sub_mat(A12, A22), add_mat(B21, B22), threshold)

    C11 = add_mat(sub_mat(add_mat(M1, M4), M5), M7)
    C12 = add_mat(M3, M5)
    C21 = add_mat(M2, M4)
    C22 = add_mat(sub_mat(add_mat(M1, M3), M2), M6)
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]

def strassen_worker(args):
    # Unpack arguments and run sequential hybrid strassen
    X, Y, thresh = args
    return hybrid_strassen_seq(X, Y, thresh)

def parallel_hybrid_strassen(A, B, threshold=64):
    """Spawns the top 7 branches of Strassen to 7 different CPU cores."""
    if len(A) < 256: return hybrid_strassen_seq(A, B, threshold)
    
    A11, A12, A21, A22 = split_mat(A)
    B11, B12, B21, B22 = split_mat(B)
    
    # Define the 7 independent branches
    tasks = [
        (add_mat(A11, A22), add_mat(B11, B22), threshold),
        (add_mat(A21, A22), B11, threshold),
        (A11, sub_mat(B12, B22), threshold),
        (A22, sub_mat(B21, B11), threshold),
        (add_mat(A11, A12), B22, threshold),
        (sub_mat(A21, A11), add_mat(B11, B12), threshold),
        (sub_mat(A12, A22), add_mat(B21, B22), threshold)
    ]
    
    # Execute the 7 branches simultaneously across 7 cores
    with concurrent.futures.ProcessPoolExecutor(max_workers=min(7, multiprocessing.cpu_count())) as exec:
        results = list(exec.map(strassen_worker, tasks))
        
    M1, M2, M3, M4, M5, M6, M7 = results

    C11 = add_mat(sub_mat(add_mat(M1, M4), M5), M7)
    C12 = add_mat(M3, M5)
    C21 = add_mat(M2, M4)
    C22 = add_mat(sub_mat(add_mat(M1, M3), M2), M6)
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]

# ==========================================
# 4. SEQUENTIAL EXECUTION OF BENCHMARKS
# ==========================================
if __name__ == '__main__':
    multiprocessing.freeze_support()
    sizes = [2, 4, 16, 63, 64, 127, 128, 256, 500, 512, 1000, 1024, 2000, 2048]
    
    times_normal, times_pure, times_hybrid = [], [], []
    mults_normal, mults_pure, mults_hybrid = [], [], []
    adds_normal, adds_pure, adds_hybrid = [], [], []

    for n in sizes:
        print(f"Benchmarking N={n} on all cores...")
        
        # Math
        mn, an = calc_normal_ops(n)
        mp, ap = calc_pure_strassen_ops(n)
        mh, ah = calc_hybrid_ops(n, threshold=64)
        
        mults_normal.append(mn); adds_normal.append(an)
        mults_pure.append(mp); adds_pure.append(ap)
        mults_hybrid.append(mh); adds_hybrid.append(ah)

        mat = [[2 for _ in range(n)] for _ in range(n)]
        
        # 1. Parallel Normal
        start = time.perf_counter()
        parallel_normal(mat, mat)
        times_normal.append(time.perf_counter() - start)
        
        # 2. Pure Strassen (Still slow due to massive additions, uses Parallel Strassen logic with threshold=1)
        m_pure = 2 ** math.ceil(math.log2(n)) if n > 1 else 1
        mat_pure = pad_matrix(mat, m_pure)
        start = time.perf_counter()
        parallel_hybrid_strassen(mat_pure, mat_pure, threshold=1)
        times_pure.append(time.perf_counter() - start)
        
        # 3. Parallel Hybrid Strassen
        doublings = math.ceil(math.log2(n / 64)) if n > 64 else 0
        m_hybrid = 64 * (2 ** doublings) if doublings > 0 else n
        mat_hyb = pad_matrix(mat, m_hybrid)
        start = time.perf_counter()
        parallel_hybrid_strassen(mat_hyb, mat_hyb, threshold=64)
        times_hybrid.append(time.perf_counter() - start)

    # ==========================================
    # 5. PLOTTING
    # ==========================================
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].plot(sizes, mults_normal, label='Normal (O(N^3))', marker='o')
    axes[0].plot(sizes, mults_pure, label='Pure Strassen', marker='s')
    axes[0].plot(sizes, mults_hybrid, label='Hybrid (Thresh=64)', marker='^', linestyle='--')
    axes[0].set_title('Total Multiplications Required')
    axes[0].set_xscale('log', base=2); axes[0].set_yscale('log', base=10)
    axes[0].set_xlabel('Matrix Size (N)'); axes[0].set_ylabel('Multiplications (Log)')
    axes[0].legend(); axes[0].grid(True, which="both", ls="--", alpha=0.5)

    axes[1].plot(sizes, adds_normal, label='Normal (O(N^3))', marker='o')
    axes[1].plot(sizes, adds_pure, label='Pure Strassen', marker='s')
    axes[1].plot(sizes, adds_hybrid, label='Hybrid (Thresh=64)', marker='^', linestyle='--')
    axes[1].set_title('Total Additions Required')
    axes[1].set_xscale('log', base=2); axes[1].set_yscale('log', base=10)
    axes[1].set_xlabel('Matrix Size (N)'); axes[1].set_ylabel('Additions (Log)')
    axes[1].legend(); axes[1].grid(True, which="both", ls="--", alpha=0.5)

    axes[2].plot(sizes, times_normal, label='Parallel Normal', marker='o')
    axes[2].plot(sizes, times_pure, label='Parallel Pure Strassen', marker='s')
    axes[2].plot(sizes, times_hybrid, label='Parallel Hybrid Execution', marker='^', linestyle='--')
    axes[2].set_title('Multi-Core CPU Execution Time')
    axes[2].set_xscale('log', base=2); axes[2].set_yscale('log', base=10)
    axes[2].set_xlabel('Matrix Size (N)'); axes[2].set_ylabel('Seconds (Log)')
    axes[2].legend(); axes[2].grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    plt.show()