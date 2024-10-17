
def fun_generator( n ):
    if n != 10:
        for i in range(n):
            yield i 


for item in fun_generator(10):
    print(item)
 