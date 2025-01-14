from typing import TYPE_CHECKING, Optional

from pyranges1.core.names import VALID_OVERLAP_TYPE, VALID_STRAND_BEHAVIOR_TYPE
from pyranges1.core.pyranges_helpers import mypy_ensure_pyranges
from pyranges1.methods import concat

if TYPE_CHECKING:
    from pyranges1.core.pyranges_main import PyRanges


def count_overlaps(
    grs: dict[str, "PyRanges"],
    features: Optional["PyRanges"] = None,
    strand_behavior: VALID_STRAND_BEHAVIOR_TYPE = "auto",
    by: list[str] | None = None,
    how: VALID_OVERLAP_TYPE = "all",
) -> "PyRanges":
    """Count overlaps in multiple pyranges1.

    Parameters
    ----------
    grs : dict of PyRanges
        The pyranges1to use as queries.

    features : PyRanges, default None
        The pyranges1to use as subject in the query. If None, the pyranges1themselves are used as a query.

    strand_behavior : {None, "same", "opposite", False}, default None, i.e. auto
        Whether to compare pyranges1on the same strand, the opposite or ignore strand
        information. The default, None, means use "same" if both pyranges1are stranded,
        otherwise ignore the strand information.

     how : {None, "all", "containment", "first"}, default None, i.e. all
        What intervals to report. By default reports all overlapping intervals. "containment"
        reports intervals where the overlapping is contained within it.

    by : list of str, default None
        Columns to group by.

    how: {"all", "first", "containment"}, default "all"
        What intervals to report. By default reports all overlapping intervals. "containment"
        reports intervals where the overlapping is contained within it.

    Examples
    --------
    >>> import pyranges1 as pr
    >>> a = '''Chromosome Start End
    ... chr1    6    12
    ... chr1    10    20
    ... chr1    22    27
    ... chr1    24    30'''

    >>> b = '''Chromosome Start End
    ... chr1    12    32
    ... chr1    14    30'''

    >>> c = '''Chromosome Start End
    ... chr1    8    15
    ... chr1    10    14
    ... chr1    32    34'''

    >>> grs = {n: pr.from_string(s) for n, s in zip(["a", "b", "c"], [a, b, c])}
    >>> for k, v in grs.items():
    ...     print("Name: " + k)
    ...     print(v)
    Name: a
      index  |    Chromosome      Start      End
      int64  |    object          int64    int64
    -------  ---  ------------  -------  -------
          0  |    chr1                6       12
          1  |    chr1               10       20
          2  |    chr1               22       27
          3  |    chr1               24       30
    pyranges1with 4 rows, 3 columns, and 1 index columns.
    Contains 1 chromosomes.
    Name: b
      index  |    Chromosome      Start      End
      int64  |    object          int64    int64
    -------  ---  ------------  -------  -------
          0  |    chr1               12       32
          1  |    chr1               14       30
    pyranges1with 2 rows, 3 columns, and 1 index columns.
    Contains 1 chromosomes.
    Name: c
      index  |    Chromosome      Start      End
      int64  |    object          int64    int64
    -------  ---  ------------  -------  -------
          0  |    chr1                8       15
          1  |    chr1               10       14
          2  |    chr1               32       34
    pyranges1with 3 rows, 3 columns, and 1 index columns.
    Contains 1 chromosomes.

    >>> pr.count_overlaps(grs)
    index    |    Chromosome    Start    End      a        b        c
    int64    |    object        int64    int64    int64    int64    int64
    -------  ---  ------------  -------  -------  -------  -------  -------
    0        |    chr1          6        8        1        0        0
    1        |    chr1          8        10       1        0        1
    2        |    chr1          10       12       2        0        2
    3        |    chr1          12       14       1        1        2
    ...      |    ...           ...      ...      ...      ...      ...
    8        |    chr1          24       27       2        2        0
    9        |    chr1          27       30       1        2        0
    10       |    chr1          30       32       0        1        0
    11       |    chr1          32       34       0        0        1
    pyranges1with 12 rows, 6 columns, and 1 index columns.
    Contains 1 chromosomes.

    >>> gr = pr.PyRanges({"Chromosome": ["chr1"], "Start": [0], "End": [40]}).tile(10)
    >>> gr
      index  |    Chromosome      Start      End
      int64  |    object          int64    int64
    -------  ---  ------------  -------  -------
          0  |    chr1                0       10
          0  |    chr1               10       20
          0  |    chr1               20       30
          0  |    chr1               30       40
    pyranges1with 4 rows, 3 columns, and 1 index columns (with 3 index duplicates).
    Contains 1 chromosomes.

    >>> pr.count_overlaps(grs, gr)
      index  |    Chromosome      Start      End        a        b        c
      int64  |    object          int64    int64    int64    int64    int64
    -------  ---  ------------  -------  -------  -------  -------  -------
          0  |    chr1                0       10        5        5        4
          0  |    chr1               10       20        5        5        4
          0  |    chr1               20       30        5        5        4
          0  |    chr1               30       40        5        5        4
    pyranges1with 4 rows, 6 columns, and 1 index columns (with 3 index duplicates).
    Contains 1 chromosomes.

    """
    concated = concat.concat(grs.values())
    features = concated.split(between=True) if features is None else features.copy()

    from pyranges1.methods.overlap import _count_overlaps

    for name, gr in grs.items():
        features = features.apply_pair(
            gr.remove_nonloc_columns(),
            _count_overlaps,
            by=by,
            strand_behavior=strand_behavior,
            how=how,
            return_indexes=True,
            skip_if_empty=False,
            name=name,
        )
    return mypy_ensure_pyranges(features.astype({k: int for k in grs}))
