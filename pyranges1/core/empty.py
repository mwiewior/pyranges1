import typing
from collections.abc import Iterable

import pandas as pd
from pandas import Series

from pyranges1.core import names
from pyranges1.core.pyranges_helpers import mypy_ensure_pyranges

if typing.TYPE_CHECKING:
    from pyranges1.core.pyranges_main import PyRanges


def empty_df(
    columns: Iterable[str] | None = None,
    dtype: Series | None = None,
    *,
    with_strand: bool = False,
) -> pd.DataFrame:
    """Create an empty DataFrame that is valid as a pyranges1.

    Parameters
    ----------
    columns : Iterable of str, default None
        Columns to create. If None, the default columns Chromosome, Start, and End are used.

    dtype: Series, default None
        Dtype for the columns.

    with_strand: bool, default False
        Whether to create a pyranges1with strand information.

    """
    empty = pd.DataFrame(
        columns=list(columns)
        if columns is not None
        else (names.GENOME_LOC_COLS_WITH_STRAND if with_strand else names.GENOME_LOC_COLS),
    )
    return empty.astype(dtype) if dtype is not None else empty


def empty(
    columns: Iterable[str] | None = None,
    dtype: Series | None = None,
    *,
    strand: bool = False,
) -> "PyRanges":
    """Create an empty pyranges1.

    Parameters
    ----------
    columns : Iterable of str, default None
        Columns to create. If None, the default columns Chromosome, Start, and End are used.

    dtype: Series, default None
        Dtype for the columns.

    strand: bool, default False
        Whether to create a pyranges1with strand information.

    """
    return mypy_ensure_pyranges(empty_df(with_strand=strand, columns=columns, dtype=dtype))
