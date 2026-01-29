a = int(input())
n = list(map(int ,input().split()))
max = -1000000000
min = 1000000000
index1 = 0
for i in range(a):
    if n[i] > max:          
        max = n[i]
        index1 = i


for i in range(a):
    if n[i] < min:
        min = n[i]

n[index1] = min

for k in range(a):
    if index1 == i:
        continue
    elif max == n[k]:
        index2 = k
        n[index2] = min
    else:
        continue

for k in range(a):
    print(n[i], end=" ")    