import io

import pandas as pd
import pyranges as pr
from pyranges.names import PRESERVE_INDEX_COLUMN


def test_spliced_subsequence():
    p = pr.PyRanges(
        {
            "Chromosome": [1, 1, 2, 2, 3],
            "Strand": ["+", "+", "-", "-", "+"],
            "Start": [1, 40, 10, 70, 140],
            "End": [11, 60, 25, 80, 152],
            "transcript_id": ["t1", "t1", "t2", "t2", "t3"],
        },
    )

    result = p.spliced_subsequence(0, 5, use_strand=False, by="transcript_id")

    _expected_result = {
        "Chromosome":{
            "0":1,
            "1":1,
            "2":2,
            "3":2,
            "4":3
        },
        "Strand":{
            "0":"+",
            "1":"+",
            "2":"-",
            "3":"-",
            "4":"+"
        },
        "Start":{
            "0":1,
            "1":40,
            "2":10,
            "3":70,
            "4":140
        },
        "End":{
            "0":6,
            "1":45,
            "2":15,
            "3":5,
            "4":145
        },
        "transcript_id":{
            "0":"t1",
            "1":"t1",
            "2":"t2",
            "3":"t2",
            "4":"t3"
        }
    }
    expected_result = pd.DataFrame(_expected_result)
    print(result)
    print(expected_result)
    pd.testing.assert_frame_equal(result, expected_result)
