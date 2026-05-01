import sys
import time
import psutil

DELTA = 30
ALPHA = {
    ('A','A'):0,   ('A','C'):110, ('A','G'):48,  ('A','T'):94,
    ('C','A'):110, ('C','C'):0,   ('C','G'):118, ('C','T'):48,
    ('G','A'):48,  ('G','C'):118, ('G','G'):0,   ('G','T'):110,
    ('T','A'):94,  ('T','C'):48,  ('T','G'):110, ('T','T'):0,
}

def generate_string(base, indices):
    s = base
    for idx in indices:
        s = s[:idx+1] + s + s[idx+1:]
    return s

def parse_input(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    i = 0
    s0 = lines[i]; i += 1
    s_indices = []
    while i < len(lines) and not lines[i].isalpha():
        s_indices.append(int(lines[i]))
        i += 1
    t0 = lines[i]; i += 1
    t_indices = []
    while i < len(lines):
        t_indices.append(int(lines[i]))
        i += 1
    return generate_string(s0, s_indices), generate_string(t0, t_indices)

def basic_alignment(X, Y):
    m, n = len(X), len(Y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i * DELTA
    for j in range(n + 1):
        dp[0][j] = j * DELTA
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = min(
                dp[i-1][j-1] + ALPHA[(X[i-1], Y[j-1])],
                dp[i-1][j] + DELTA,
                dp[i][j-1] + DELTA
            )
    mem_kb = psutil.Process().memory_info().rss / 1024
    aligned_X, aligned_Y = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + ALPHA[(X[i-1], Y[j-1])]:
            aligned_X.append(X[i-1])
            aligned_Y.append(Y[j-1])
            i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + DELTA:
            aligned_X.append(X[i-1])
            aligned_Y.append('_')
            i -= 1
        else:
            aligned_X.append('_')
            aligned_Y.append(Y[j-1])
            j -= 1
    aligned_X.reverse()
    aligned_Y.reverse()
    return dp[m][n], ''.join(aligned_X), ''.join(aligned_Y), mem_kb

def main():
    X, Y = parse_input(sys.argv[1])
    start = time.time()
    cost, align_X, align_Y, mem_kb = basic_alignment(X, Y)
    elapsed = (time.time() - start) * 1000
    with open(sys.argv[2], 'w') as f:
        f.write(f"{cost}\n{align_X}\n{align_Y}\n{elapsed}\n{mem_kb}\n")

if __name__ == '__main__':
    main()
