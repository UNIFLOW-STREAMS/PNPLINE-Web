# Shorten initial hoist ropes

User requests winding in the visible S1 starting ropes so the container starts close to the crane. Previous revision raised beam3m but cargo2.5m, increasing initial exposed ropes from0.20m to0.70m.

Use current v001 master SHA256c21292... as preserved input. Raise cargo, spreader and internal pallet another0.5m at f0; ease this additional offset to zero at f72. Initial ropes shorten0.70m to0.20m. Keep the camera fixed so the lift is visible in the frame. Preserve all static geometry and all f72+ motion. Regression must fail on old initial rope length, then pass on output. Check rope connections, pallet containment, head/spreader clearance and dense external/internal collision pairs, plus exact protected scope and before/after render.
