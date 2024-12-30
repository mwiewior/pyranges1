"""Module for pyranges1concat method."""

from collections.abc import Iterable
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pyranges1 import RangeFrame


def concat[T: "RangeFrame"](grs: Iterable[T], *args, **kwargs) -> T:
    """Concatenate pyranges1.

    Parameters
    ----------
    grs: iterable of PyRanges
        pyranges1to concatenate.

    args:
        Arguments passed to pandas.concat.

    kwargs:
        Keyword arguments passed to pandas.concat.

    Returns
    -------
    pyranges1.PyRanges

    Examples
    --------
    >>> import pyranges1 as pr
    >>> gr1 = pr.example_data.f2
    >>> gr2 = pr.example_data.f1
    >>> pr.concat([gr1, gr2])
      index  |    Chromosome      Start      End  Name         Score  Strand
      int64  |    category        int64    int64  object       int64  category
    -------  ---  ------------  -------  -------  ---------  -------  ----------
          0  |    chr1                1        2  a                0  +
          1  |    chr1                6        7  b                0  -
          0  |    chr1                3        6  interval1        0  +
          1  |    chr1                5        7  interval2        0  -
          2  |    chr1                8        9  interval3        0  +
    pyranges1with 5 rows, 6 columns, and 1 index columns (with 2 index duplicates).
    Contains 1 chromosomes and 2 strands.

    >>> pr.concat([gr1, gr2.remove_strand()])
      index  |    Chromosome      Start      End  Name         Score  Strand
      int64  |    category        int64    int64  object       int64  category
    -------  ---  ------------  -------  -------  ---------  -------  ----------
          0  |    chr1                1        2  a                0  +
          1  |    chr1                6        7  b                0  -
          0  |    chr1                3        6  interval1        0  nan
          1  |    chr1                5        7  interval2        0  nan
          2  |    chr1                8        9  interval3        0  nan
    pyranges1with 5 rows, 6 columns, and 1 index columns (with 2 index duplicates).
    Contains 1 chromosomes and 2 strands (including non-genomic strands: nan).

    >>> r = pr.RangeFrame(gr1)
    >>> pr.concat([r, gr1])
    Traceback (most recent call last):
    ...
    ValueError: Can only concatenate RangeFrames of the same type. Got: PyRanges, RangeFrame

    >>> pd.testing.assert_frame_equal(pr.concat([r]), r)  # would throw if they were not equal

    """
    input_class = assert_all_classes_are_the_same_and_retrieve_it(grs)

    concatenated = input_class(pd.concat([pd.DataFrame(gr) for gr in grs]), *args, **kwargs)

    from pyranges1 import RangeFrame

    if isinstance(concatenated, RangeFrame):
        return input_class(concatenated)
    msg = "Concatenation should result in a RangeFrame."
    raise TypeError(msg)


def assert_all_classes_are_the_same_and_retrieve_it[T: "RangeFrame"](grs: Iterable[T]) -> type:
    """Ensure that all Ranges are of the same type and return the type."""
    all_classes = {gr.__class__ for gr in grs}
    if len(all_classes) != 1:
        classnames = [c.__name__ for c in sorted(all_classes, key=lambda x: x.__name__)]
        msg = f"Can only concatenate RangeFrames of the same type. Got: {', '.join(classnames)}"
        raise ValueError(msg)
    return all_classes.pop()
