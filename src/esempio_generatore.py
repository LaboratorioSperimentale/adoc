def foo(x):
    i = 1
    while i < x:
        yield i
        i+=1

def foo_function(x):
    i=1
    ret = []
    while i < x:
        ret.append(i)
        i+=1
    return ret


for number in foo_function(10):
    print(number)