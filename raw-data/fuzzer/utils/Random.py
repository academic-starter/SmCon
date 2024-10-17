import random
import time
import math
random.seed(time.time())

def rand_float():
    return random.random()

def rand_uint(n):
    return math.floor(n*rand_float())

def rand_int(min, max):
    return math.floor((max-min)*rand_float()) + min 


# reverse single bit
def bit_swap(n: int):
    bin_str = bin(n)
    if n>=0:
        index = rand_uint(len(bin_str)-2)
        c = "0" if bin_str[index+2]=="1" else "1"
        result = ""
        cnt = 0
        for _c in bin_str:
            if cnt == index+2:
                result = result + c
            else:
                result = result + _c
            cnt += 1
        bin_str = result
    else:
        index = rand_uint(len(bin_str)-3)
        c = "0" if bin_str[index+3]=="1" else "1"
        result = ""
        cnt = 0
        for _c in bin_str:
            if cnt == index+3:
                result = result + c
            else:
                result = result + _c
            cnt += 1
        bin_str = result
    return int(bin_str, base=0)

UINT_MAX = dict()
UINT_MIN = dict()
for i in range(8, 257, 8):
    UINT_MAX["uint"+str(i)] = 2**i-1
    UINT_MIN["uint"+str(i)] = 0
UINT_MAX["uint"] = 2**256-1
UINT_MIN["uint"] = 0

INT_MAX = dict()
INT_MIN = dict()
for i in range(8, 257, 8):
    INT_MAX["int"+str(i)] = 2**(i-1)
    INT_MIN["int"+str(i)] = - (2**(i-1) -1)
INT_MAX["int"+str(i)] =  2**255
INT_MIN["int"+str(i)] = -(2**255-1)

STR_CORPUS=[
    "",
    "hello"
]

