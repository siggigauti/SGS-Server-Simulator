import math
c = 0.25
z = 0.69
f = 0.5
N = 10

e = (f + (math.pow(z,2)/2*N) + z * math.sqrt( (f/N) - (math.pow(f,2)/N) + (math.pow(z,2)/4*math.pow(N,2)) ) )/(1+(math.pow(z,2)/N))

print(e)