n = "321"
m = n[0:2]  

if m.isdigit():
    m = list(m)  
    m.append("?")
    print(m[0], m[1], sep="") 

else:
    m = list(map(int, m))
    print(max(m))