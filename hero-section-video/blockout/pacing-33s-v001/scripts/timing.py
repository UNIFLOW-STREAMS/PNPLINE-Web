"""One monotone C1 clock for every animation channel. No per-shot stop/start."""
import bisect
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))

class TimeMap:
    def __init__(self, config=CONFIG):
        self.x = [a[1] * config['fps'] for a in config['anchors']]
        self.y = [float(a[0]) for a in config['anchors']]
        h = [b-a for a,b in zip(self.x,self.x[1:])]
        d = [(b-a)/w for a,b,w in zip(self.y,self.y[1:],h)]
        assert min(h) > 0 and min(d) > 0
        # Weighted harmonic tangents preserve monotonicity without zero velocity
        # at section boundaries. The endpoint derivative is the adjacent secant.
        self.m = [d[0]]
        for i in range(1,len(self.x)-1):
            w1,w2 = 2*h[i]+h[i-1],h[i]+2*h[i-1]
            self.m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
        self.m.append(d[-1])

    def source(self, output_frame):
        t = min(max(float(output_frame),self.x[0]),self.x[-1])
        i = min(bisect.bisect_right(self.x,t)-1,len(self.x)-2)
        width = self.x[i+1]-self.x[i]
        u = (t-self.x[i])/width
        return ((2*u**3-3*u*u+1)*self.y[i] + (u**3-2*u*u+u)*width*self.m[i]
                + (-2*u**3+3*u*u)*self.y[i+1] + (u**3-u*u)*width*self.m[i+1])

    def output(self, source_frame):
        if source_frame <= self.y[0]: return self.x[0]
        if source_frame >= self.y[-1]: return self.x[-1]
        lo,hi = self.x[0],self.x[-1]
        for _ in range(48):
            mid=(lo+hi)*0.5
            if self.source(mid)<source_frame: lo=mid
            else: hi=mid
        return (lo+hi)*0.5

    def speed(self, output_frame):
        h=1e-4
        a=max(self.x[0],output_frame-h)
        b=min(self.x[-1],output_frame+h)
        return (self.source(b)-self.source(a))/(b-a)

def section_at(frame):
    return next(row[0] for row in CONFIG['sections'] if row[3] <= frame < row[4])
