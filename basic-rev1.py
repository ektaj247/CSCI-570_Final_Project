import sys
import time
import psutil

# Gap penalty
delta = 30

# Mismatch cost matrix
alpha = {
    ('A','A'): 0, ('A','C'): 110, ('A','G'): 48, ('A','T'): 94,
    ('C','A'): 110, ('C','C'): 0, ('C','G'): 118, ('C','T'): 48,
    ('G','A'): 48, ('G','C'): 118, ('G','G'): 0, ('G','T'): 110,
    ('T','A'): 94, ('T','C'): 48, ('T','G'): 110, ('T','T'): 0
}


def generate_string(base, indices):
    s = base

    for idx in indices:
        # split at idx (inclusive)
        left = s[:idx + 1]
        right = s[idx + 1:]

        # insert full copy of current string
        s = left + s + right

    return s

def read_and_generate(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    i = 0

    # First string
    base1 = lines[i]
    i += 1
    indices1 = []

    while i < len(lines) and lines[i].isdigit():
        indices1.append(int(lines[i]))
        i += 1

    # Second string
    base2 = lines[i]
    i += 1
    indices2 = []

    while i < len(lines) and lines[i].isdigit():
        indices2.append(int(lines[i]))
        i += 1

    s1 = generate_string(base1, indices1)
    s2 = generate_string(base2, indices2)

    return( s1, s2 )
   
# DP Alignment
def needleman_wunsch(X, Y):
    m, n = len(X), len(Y)

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    back = [[None] * (n + 1) for _ in range(m + 1)]

    # Base cases
    for i in range(1, m + 1):
        dp[i][0] = i * delta
        back[i][0] = 'U'

    for j in range(1, n + 1):
        dp[0][j] = j * delta
        back[0][j] = 'L'

    # Fill DP
    for i in range(1, m + 1):
        for j in range(1, n + 1):

            cost_diag = dp[i-1][j-1] + alpha[(X[i-1], Y[j-1])]
            cost_up = dp[i-1][j] + delta
            cost_left = dp[i][j-1] + delta

            dp[i][j] = min(cost_diag, cost_up, cost_left)

            if dp[i][j] == cost_diag:
                back[i][j] = 'D'
            elif dp[i][j] == cost_up:
                back[i][j] = 'U'
            else:
                back[i][j] = 'L'

    return dp, back    

# Backtracking
def backtrack(X, Y, back):
    i, j = len(X), len(Y)

    align_X = []
    align_Y = []

    while i > 0 or j > 0:
        if i > 0 and j > 0 and back[i][j] == 'D':
            align_X.append(X[i-1])
            align_Y.append(Y[j-1])
            i -= 1
            j -= 1

        elif i > 0 and (j == 0 or back[i][j] == 'U'):
            align_X.append(X[i-1])
            align_Y.append('-')
            i -= 1

        else:
            align_X.append('-')
            align_Y.append(Y[j-1])
            j -= 1

    return ''.join(reversed(align_X)), ''.join(reversed(align_Y))

def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024) 
    return memory_consumed


def main():
    file_path = sys.argv[1]

    # Generate strings
    X, Y = read_and_generate(file_path)

    # Runtime Measure BEFORE
    start_time = time.perf_counter_ns()

    # Run DP
    dp, back = needleman_wunsch(X, Y)

    # Backtrack
    aligned_X, aligned_Y = backtrack(X, Y, back)

    end_time = time.perf_counter_ns() #time of program running

    MCost = dp[len(X)][len(Y)]
    Alignment = (aligned_X, aligned_Y)
    Runtime = (end_time - start_time) / 1_000_000
    MemUsuage = process_memory()

    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(f"Cost of Alignment: {MCost}\nFirst String: {Alignment[0]}\nSecond String: {Alignment[1]} \nRuntime: {Runtime:.2f} ms\nMemory Usage: {MemUsuage:.2f} KB\n")

if __name__ == "__main__":
    main()