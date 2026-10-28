# Crane height and payload repair

User: raise the crane so the container lowers from higher up; fix the green box descending through the container roof.

Baseline: currently saved previous latest master, copied to inputs/base.blend. SHA25664a206b9104e6c8f0cd0f4c2232bcac8789df47bd2e06cc3207743a87d70ce98. It was saved again since the previous delivery registry37fa14...; work uses the current saved file and preserves it.

Root cause reproduced in the supplied recording and scene: W01_NEW_PALLET is independent of A01_CONTAINER. Its obsolete S1 vertical motion puts the pallet origin1.31m above container center at f0 and-.49m at f72. Green box tops are2.105m above center at f0, outside the container, then pass through the roof. W01_REMAINING_CONTAINER_CARGO is correctly parented and stays inside.

Plan: regress payload containment; extend crane upper structure by3m with feet kept on land; lift starting container/camera by2.5m, taper to unchanged f72 landing; rebuild cable endpoints and empty-hoist return; keep internal payload at its f72 relative pose throughout S1; preserve f72+ cargo/pallet/camera and all other logistics. Dense internal/external/payload checks and visual comparison before registry adoption.

No visibility hiding is used to conceal the green box. It remains a real payload inside the container, available for the existing warehouse unloading sequence.
