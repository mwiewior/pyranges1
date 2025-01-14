from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from pyranges1 import RangeFrame


def _relative_distance(scdf: "RangeFrame", ocdf: "RangeFrame", **_) -> "pd.Series[float]":
    if scdf.empty or ocdf.empty:
        return pd.Series([], dtype=np.double)

    midpoints_self = ((scdf.Start + scdf.End) / 2).astype(int).sort_values().to_numpy()
    midpoints_other = ((ocdf.Start + ocdf.End) / 2).astype(int).sort_values().to_numpy()

    left_idx = np.searchsorted(midpoints_other, midpoints_self)
    left_idx[left_idx >= len(midpoints_other)] -= 1
    left_idx_shift = (midpoints_other[left_idx] > midpoints_self) & (left_idx > 0)
    left_idx[left_idx_shift] -= 1
    left = midpoints_other[left_idx]
    right_idx = np.searchsorted(midpoints_other, midpoints_self, side="right")
    right_idx[right_idx >= len(midpoints_other)] -= 1

    if len(right_idx) == 0 or len(left_idx) == 0:
        return pd.Series([], dtype=np.double)

    right = midpoints_other[right_idx]

    left_distance = np.absolute(midpoints_self - left)
    right_distance = np.absolute(midpoints_self - right)

    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.minimum(left_distance, right_distance) / (right - left)

    result[np.isnan(result)] = 0

    return pd.Series(result[~np.isinf(result)])
