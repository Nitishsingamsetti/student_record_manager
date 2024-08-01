import random
import math

def genotp():
    otp=""
    for i in range(2):    
        otp+=str(math.floor(random.randint(0,9)))
        otp+=random.choice([chr(x) for x in range(ord('A'),ord('Z')+1)])
        otp+=random.choice([chr(y) for y in range(ord('a'),ord('z')+1)])
    return otp

#print(genotp())
    