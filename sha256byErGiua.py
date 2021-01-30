import math
import re

# Costants hard-coded defined as hexadecimal of the first 32 bits of fractional part square root of 8 first prime numbers
    # h0 := hex(int(math.modf(math.sqrt(2))[0]*(1<<32))) 
a = (h0 := 0x6a09e667)
b = (h1 := 0xbb67ae85)
c = (h2 := 0x3c6ef372)
d = (h3 := 0xa54ff53a)
e = (h4 := 0x510e527f)
f = (h5 := 0x9b05688c)
g = (h6 := 0x1f83d9ab)
h = (h7 := 0x5be0cd19)

# Costants hard-coded as before but with the cubic root of the 64 first prime numbers
frctCubic = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
             0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
             0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
             0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
             0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
             0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
             0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
             0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
# frctCubic calculated without hard-coding (already appended data for 2 and 3)
frctCubic = [int(math.modf(2**(1/3))[0]*2**32), int(math.modf(3**(1/3))[0]*2**32)]
num = 5
while len(frctCubic) < 64:
    for i in range(2, int(num/2)):
        if num % i == 0:
            break
    else:
        frctCubic.append(int(math.modf(num**(1/3))[0]*2**32))
    num += 1

# For an integer return a fixed binary with 8 bit
def getBin(num):
    return format(num, '08b')
def getBin32(num): 
    return format(num, '032b').replace("-","")[-32:]
def getBin64(num):
    return format(num, '064b').replace("-","")
def getHex(nums):
    return  "".join(["{0:8x}".format(n).replace(" ", "0") for n in nums])
# Remove the carry from a number to keep it 32 bit
def norm32(num):
    return int(getBin32(num), base=2)

# Circular shifting to the right
def RSHFT(strBin, n):
    return strBin[-n:] + strBin[:len(strBin)-n]

# Temp variable
rest, i = 0, 0

# Some string to check 
toConvertLong = "hello world, this string it's a very long long bytes string so I check another case"
toConvert = "giovanni furioso"
# At first I convert each char in his ascii rapresentation
ascii = [ord(c) for c in toConvert]
# Each ascii integer converted from decimal to binary
binary = [getBin(num) for num in ascii]
# Append 1 in tail (standard requirement)
binary.append(str(0b1))
# From array of binary numbers to string
fullStr = "".join(binary) 
# I have to check for multiple of 512 if len > (512 - 64)
while (toAdd := len(fullStr) - (512 * i - 64)) > 0:
    i += 1
# And add zeros in tail to reach -> (multiple of 512) - 64 (standard requirement)
withZeros = fullStr + "0" * abs(toAdd)
# Append at the end the binary length of original input as 64 bit value
withLenAppended = withZeros + getBin64(len(fullStr) - 1) #re.sub("0{%d}$" % len(lenInBin), lenInBin, withZeros)
# Creating an array of words
wordArr = [withLenAppended[N:N+32] for N in range(0, len(withLenAppended), 32)]
# Adding n words initialized to zero for have an array with 64 words in it
while len(wordArr) < 64:
    wordArr.append("0"*32)
# Shifting and xoring for i from w[16..63] 
for i in range(16, 64):
    s0 = int(RSHFT(wordArr[i-15], 7), base=2) ^ int(RSHFT(wordArr[i-15], 18), base=2) ^ (int(wordArr[i-15], base=2) >> 3)
    s1 = int(RSHFT(wordArr[i-2], 17), base=2) ^ int(RSHFT(wordArr[i-2], 19), base=2) ^ (int(wordArr[i-2], base=2) >> 10)
    # First 32 less significant bit (no carry)
    wordArr[i] = getBin32(int(wordArr[i-16], 2) + s0 + int(wordArr[i-7], 2) + s1)[-32:]
# Compression phase with a(h0), b(h1),..., h(h7)
for i in range(64):
    S1 = int(RSHFT(getBin32(e), 6), 2) ^ int(RSHFT(getBin32(e), 11), 2) ^ int(RSHFT(getBin32(e), 25), 2)
    ch = (e & f) ^ (~e & g) # Adding 2**32 to not e beacuse I want the unsigned int
    temp1 = norm32(h + S1 + ch + frctCubic[i] + int(wordArr[i], 2))
    S0 = int(RSHFT(getBin32(a), 2), 2) ^ int(RSHFT(getBin32(a), 13), 2) ^ int(RSHFT(getBin32(a), 22), 2)
    maj = (a & b) ^ (a & c) ^ (b & c)
    temp2 = norm32(S0 + maj)
    a, b, c, d, e, f, g, h = norm32(temp1 + temp2), a, b, c, norm32(d + temp1), e, f, g
# Final modification of values
a, b, c, d, e, f, g, h = norm32(a+h0), norm32(b+h1), norm32(c+h2), norm32(d+h3), norm32(e+h4), norm32(f+h5), norm32(g+h6), norm32(h+h7)
# Appending all and get SHA-256 result
result = getHex((a, b, c, d, e, f, g, h)).upper()
print("SHA-256:", result)