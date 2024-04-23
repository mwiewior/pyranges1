import pyranges as pr
from numpy import nan


def test_join_issue_4_right() -> None:
    import numpy as np

    chromsizes = pr.example_data.chromsizes
    query_regions = pr.tile_genome(chromsizes, int(1e6))
    signal_data = pr.example_data.chipseq
    signal_data["Score"] = np.random.randint(0, 100, len(signal_data))

    query_regions.join_ranges(signal_data)


def test_join_issue_8():
    gd = {
        "Chromosome": ["chr1", "chr1", "chr1", "chr1"],
        "Start": [157, 584, 731, 821],
        "End": [257, 684, 831, 921],
        "Strand": ["-", "-", "-", "-"],
    }
    md = {
        "Chromosome": ["chr1", "chr1", "chr1", "chr1"],
        "Start": [316, 793, 889, 795],
        "End": [416, 893, 989, 895],
        "Strand": ["+", "+", "+", "-"],
    }

    g = pr.PyRanges(gd)
    m = pr.PyRanges(md)

    j = m.join_ranges(g)
    expected_result = pr.PyRanges(
        {
            "Chromosome": ["chr1", "chr1"],
            "Start": [795, 795],
            "End": [895, 895],
            "Strand": ["-", "-"],
            "Start_b": [731, 821],
            "End_b": [831, 921],
        },
        index=[3, 3],
    )

    assert j.equals(expected_result)


def test_join_issue_8_right():
    gd = {
        "Chromosome": ["chr1", "chr1", "chr1", "chr1"],
        "Start": [157, 584, 731, 821],
        "End": [257, 684, 831, 921],
        "Strand": ["-", "-", "-", "-"],
    }
    md = {
        "Chromosome": ["chr1", "chr1", "chr1", "chr1"],
        "Start": [316, 793, 889, 795],
        "End": [416, 893, 989, 895],
        "Strand": ["+", "+", "+", "-"],
    }

    g = pr.PyRanges(gd)
    m = pr.PyRanges(md)

    j = m.join_ranges(g, join_type="right")

    expected_result = pr.PyRanges(
        {
            "Chromosome": ["chr1", "chr1", nan, nan],
            "Start": [795.0, 795.0, nan, nan],
            "End": [895.0, 895.0, nan, nan],
            "Strand": ["-", "-", nan, nan],
            "Start_b": [731, 821, 157, 584],
            "End_b": [831, 921, 257, 684],
        },
        index=[2, 3, 0, 1],
    )
    assert j.equals(expected_result)
