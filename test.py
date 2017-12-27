a = 1

def b():
    global a
    a += 2
    print(a)
    if a > 10:
        exit(str(a)+ '1111')
    return b()


b()