# CS-Advanced Computer Science Practicum
## Data Structures and Algorithms
### T26049 - Yashank

### Algorithms Performed
#### Normal Matrix Multiplication
- __Core Implementation:__ The standard O(N^3) row-by-column iterative multiplication approach used as the foundational baseline for performance testing.
- __What was added:__ Algorithm-level multiprocessing. Introduced concurrent execution blocks (via `concurrent.futures`) to chunk the matrix rows and distribute the workload across multiple distinct CPU cores simultaneously for matrices larger than `128x128`.
- __What was removed:__ Removed the strictly sequential, single-core processing loop for large matrices. By chunking the workload, we bypassed the single-thread bottlenecks and Python's Global Interpreter Lock (GIL) to force maximum hardware utilization.

#### Normal Stressan Matrix Algorithm
- __Core Implementation:__ The pure, textbook divide-and-conquer approach that computes 7 intermediate matrices to achieve O(N^2.81) time complexity, strictly recursing all the way down to a 1x1 base case
- __What was added:__ Unconditional power-of-2 zero padding. Because pure Strassen requires perfect halving at every recursive step, wrapped the algorithm in logic that forces any arbitrarily sized matrix (e.g., 500x500) up to the nearest perfect power of 2 (512x512) before execution, stripping the zeroes off at the end.
- __What was removed:__ Removed manual dimension constraints, meaning the algorithm no longer crashes on non-perfect square inputs. However, explicitly did not remove the deep recursion, deliberately retaining the algorithm's massive addition-operation bloat to benchmark its theoretical limits against hardware reality.

#### Hybrid Matrix Multiplication
- __Core Implementation:__ A production-grade "meet-in-the-middle" architecture bridging asymptotic mathematical optimization with modern CPU cache constraints.
- __What was added:__
    * __Crossover Threshold (Cache Blocking):__ Introduced a hardware-optimized base case limit `threshold = 64`. Once the matrix quadrants shrink to this size, Strassen recursion completely halts and delegates the remaining work to cache-friendly normal multiplication.
    * __Smart Micro-Padding:__ Instead of padding up to massive powers of 2, added a calculated padding wrapper that only expands the matrix enough to be a clean multiple of the crossover threshold.
    * __Top-Level Parallel Branching:__ Dispatched the 7 primary Strassen branches to execute simultaneously across 7 independent CPU cores.
- __What was removed:__
    * __Addition Bloat:__ Entirely eliminated the millions of deep-level matrix additions and subtractions that choke the pure Strassen method.
    * __Memory Waste:__ Removed the excessive memory allocation caused by blind power-of-2 padding.
    * __Fringe Peeling:__ Deliberately discarded complex "matrix peeling" (edge-slicing) logic to ensure the CPU always receives perfectly square, predictable memory blocks for uninterrupted L1/L2 cache execution.

### Results
![results](https://i.ibb.co/vCnqfZvw/Screenshot-2026-10-18-173020.png)