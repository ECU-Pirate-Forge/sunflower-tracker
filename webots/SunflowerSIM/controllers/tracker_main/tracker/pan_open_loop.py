# pan_open_loop.py
from typing import List, Tuple

def step_pattern(
    index: int,
    elapsed: int,
    timestep: int,
    pattern: List[Tuple[float, int]],
):

    elapsed += timestep
    target, dwell = pattern[index]

    if elapsed >= dwell:
        elapsed = 0
        index = (index + 1) % len(pattern)
        target, _ = pattern[index]

    return index, elapsed, target
