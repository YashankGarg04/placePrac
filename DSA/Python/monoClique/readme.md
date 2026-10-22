# CS-515 Advanced CS Practicum Lab
## Objective 2
### t26049 - Yashank

### Problem Statement
In computational graph theory, determining exact two-color Ramsey numbers $R(s, t)$ is notoriously difficult due to combinatorial explosion. The search space for evaluating all possible red/blue edge colorings of a complete graph $K_N$ grows exponentially at a rate of $2^{N(N-1)/2}$, making naive brute-force search computationally intractable even for small values of $N$. The objective of this project is to design and implement a highly optimized algorithmic solver that systematically finds counterexamples to establish lower bounds, or strictly proves exact Ramsey numbers. This requires overcoming the exponential time-complexity barrier by implementing advanced algorithmic techniques, including bitwise clique-detection, strict degree-bound pruning, symmetry breaking, and fast heuristic pattern-matching via circulant graphs.

### Algorithm
```
ALGORITHM Find_Ramsey_Number(s, t, budget)
    U = Calculate_Upper_Bound(s, t)
    
    // Pre-compute largest pattern-based counterexample (Threshold: N <= 31)
    big_pattern = Find largest Circulant_Search for N from 31 down to 5
    
    FOR N = 1 TO U:
        counterexample = NULL
        
        // 1. Fast Heuristic Search (Threshold: 5 <= N <= 31)
        IF 5 <= N <= 31 THEN
            counterexample = Circulant_Search(N, s, t)
            
        // 2. Exhaustive Backtracking (If heuristic fails)
        IF counterexample IS NULL THEN
            counterexample = Exhaustive_Backtracking(N, s, t, budget)
            // Note: Internally uses Bitwise Clique & Degree-Bound Pruning
            
        // 3. Budget Fallback (If backtracking runs out of time)
        IF counterexample IS NULL AND budget_is_exhausted THEN
            IF N <= size(big_pattern) THEN
                counterexample = First N vertices of big_pattern
                
        // 4. Evaluate Checkpoint
        IF counterexample IS NULL THEN
            // No counterexample exists -> Clique is mathematically forced
            RETURN "R(s, t) = " + N
            
    RETURN "R(s, t) = " + U
```
### Result
![ramsey2,2](https://i.ibb.co/k2fdJC58/image.png)
- for R(2,2) number of minimum vertices require are 2 as we can say 2 vertices will either know each other or will not know each other
![ramsey3,3](https://i.ibb.co/TDM5XJyM/image.png)
- for R(3,3) algorithm was able to find counter Example till N = 5 but for N = 6 even using exhaustive search we could not find the counterExample so we can safely say 6 is the required N for R(3,3)
![ramsey4,4](https://i.ibb.co/cS7VBKRd/image.png)
- similarly for R(4,4) as we can notice how fast we were able to find the result using circulant algorithm till N=13 though it took some time to find the result for n = 14 to 16 algorithms was collectively able to determine N = 18 using the mathematical formula for upper bound in ramsey search
- R(s,t) <= R(s-1,t) + R(s,t-1), as exhaustive search must not exceed this budget
![ramsey5,5](https://i.ibb.co/7N1TZNgS/image.png)
![ramseyresult](https://i.ibb.co/mrcH8Mxj/image.png)
- R(5,5) is still an open problem we were able to find counter example till N = 31 because of circulant search but because we have an upper bound till n=31 on circulant search we have to use exhaustive backtracking which used up all the budget and was still unable to find counterExample for N=32 and because we exited because of budget we can safely say that for N=32 it is undecided
- there is a upper bound on circulant search because it requires 2^N//2 test operations to run and a computer can evaluate upto 32000 test operation within fraction of a second but after 2^15 things go beyond this limit taking a lot of extra time 
