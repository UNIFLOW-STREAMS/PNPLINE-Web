"""Monotone shared timing; nonzero-rate scene joins and bounded action intervals."""
import math
class TimeMap:
    def __init__(self, end, easing=(), compression=()):
        if not math.isfinite(end) or end<=0:raise ValueError('Invalid source duration')
        self.end=end;self.easing=list(easing);self.compression=list(compression)
        for a,b,amount in self.easing+self.compression:
            if not all(math.isfinite(x) for x in (a,b,amount)) or not 0<=a<b<=end or amount<0:raise ValueError('Invalid interval')
        if min(self.derivative(end*i/10000) for i in range(10001))<=.05:raise ValueError('Time must advance with positive rate')
        self.output_end=self.forward(end)
    def forward(self, source):
        if not math.isfinite(source) or not 0<=source<=self.end:raise ValueError('Outside source domain')
        result=source
        for a,b,strength in self.easing:
            if a<source<b:
                u=(source-a)/(b-a)
                result+=strength*(b-a)*(math.sin(2*math.pi*u)/(2*math.pi)-math.sin(4*math.pi*u)/(4*math.pi))
        for a,b,removed in self.compression:
            if source>=b:result-=removed
            elif source>a:
                u=(source-a)/(b-a)
                result-=removed*(u-math.sin(2*math.pi*u)/(2*math.pi))
        return result
    def inverse(self, output):
        if not math.isfinite(output) or not 0<=output<=self.output_end:raise ValueError('Outside output domain')
        low,high=0.,self.end
        for _ in range(45):
            mid=(low+high)/2
            if self.forward(mid)<output:low=mid
            else:high=mid
        return (low+high)/2
    def derivative(self, source):
        result=1.
        for a,b,strength in self.easing:
            if a<source<b:
                u=(source-a)/(b-a);result+=strength*(math.cos(2*math.pi*u)-math.cos(4*math.pi*u))
        for a,b,removed in self.compression:
            if a<source<b:result-=removed/(b-a)*(1-math.cos(2*math.pi*(source-a)/(b-a)))
        return result
def hermite(p,q,v,w,t,h):
    return (2*t**3-3*t*t+1)*p+(t**3-2*t*t+t)*h*v+(-2*t**3+3*t*t)*q+(t**3-t*t)*h*w
def patch_tangent(previous,following,dt):return (following-previous)/dt
