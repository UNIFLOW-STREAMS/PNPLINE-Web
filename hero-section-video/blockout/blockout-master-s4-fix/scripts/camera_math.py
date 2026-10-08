import math
def orientation_degrees(a,b):
 # q and -q encode the same orientation; choose the shortest physical arc.
 dot=abs(a.normalized().dot(b.normalized()))
 return math.degrees(2*math.acos(min(1.,max(0.,dot))))
