# list Multiplication Bag
grid = [[0] * 4 for _ in range(3)]
grid[0][0] = 100
print(grid)

#2: Mutable Default Arguments in Functions
def addTask(task, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(task)
    return bucket
print(addTask("A"))
print(addTask("B"))

#3: String Concatenation in Loops
pieces = []
for i in range(5):
    pieces.append(f"step_{i}")
final_str = ", ".join(pieces)

from collections import defaultdict, Counter
# Default Dictionary
lst = defaultdict(list)
intg = defaultdict(int)

lst["Yashank"].append("login")
intg["Yashank"] += 10
print(lst)
print(intg)

# Counter
words = ['rag', 'llm', 'rag', 'agent', 'rag', 'llm']
n = Counter(words)
print(n['rag'])
print(n['a'])
print(n.most_common(2))

#heap
import heapq
pq =[]

heapq.heappush(pq,(-0.92, "doc_b"))
heapq.heappush(pq, (-0.92, "doc_a"))
heapq.heappush(pq, (-0.84, "doc_c"))

print(pq[0])
n, best_doc = heapq.heappop(pq)
print(-n, best_doc)
print(pq[0])

#sorted()
records = [
    {"id": "doc_2", "score": 0.85},
    {"id": "doc_1", "score": 0.95},
    {"id": "doc_3", "score": 0.95},
]

ranked = sorted(records, key=lambda x: (-x["score"], x["id"]))
print(ranked)

# Comprehension
#list
even_squares = [x*x for x in range(10) if x%2==0]
print(even_squares)

#dictionary
id_to_idx = {doc_id: idx for idx, doc_id in enumerate(["a","b","c"])}

# Generator Expression
#sum
total_squared = sum(x*x for x in range(1_000_000))
print(total_squared)

#all
is_all_valid = all(len(tok) > 0 for tok in ["hello", "world"])
