

def filehandle(f):

    if f.lower().endswith(".gz"):
        import gzip
        fh = gzip.open(f)
    else:
        fh = open(f)

    return fh

def guess_delim(f):

    fh = filehandle(f)

    # in case there is a header
    lines = [fh.readline() for i in range(0, 11)]

    fh.close()

    import re
    from collections import Counter

    counts = []
    for l in lines[1:]:
        no_floats = re.sub(r"\d*\.\d+", "", l)
        stripped_line = re.sub(r"[a-z0-9]+", "", no_floats)
        counts.append(Counter(stripped_line))

    chars_in_all_lines = set.intersection(*[set(c) for c in counts])

    # find the chars that have the same number of counts in all lines
    same_number_in_all_lines = []

    for c in chars_in_all_lines:
        for i in range(10):
            if i == 0:
                first = counts[i][c]
            else:
                if first != counts[i][c]:
                    break

            if i == 9:
                same_number_in_all_lines.append(c)

    # find the most common chars
    most_common = Counter({c: counts[0][c] for c in same_number_in_all_lines}).most_common()

    # several chars are equally common
    equally_common = [c for c in most_common if c[1] == most_common[0][1]]

    if len(equally_common) > 1:
        _equally_common = [c[0] for c in equally_common]
        if " " in _equally_common and "\t" in _equally_common: 
            guess = "\s+"
        else:
            import csv
            guess = csv.Sniffer("".join(lines)).sniff().delimiter
    else:
        guess = most_common[0][0]

    return guess



def guess_header(f, delim):

    df = pd.read_csv(f, sep=delim, nrows=10, header=None)
    df2 = pd.read_csv(f, sep=delim, nrows=10, header=0)

    if all(df.dtypes.values == df2.dtypes.values):
        return False

    return True


def guess_strand(df, number_unique):

    strand_cols = []
    for k, v in number_unique.items():

        # strand must be cateory or object
        if str(df[k].dtype) not in ["category", "object"]:
            continue

        # strand col has at most 3 values
        if v <= 3:
            # strand col can only contain "+, -, or ."
            if df[k].str.contains("\+|-|\.").all():
                strand_cols.append(k)

    guess = strand_cols[0]

    # bedpe for example
    if len(strand_cols) > 1:
        all_equal = True
        first = df[strand_cols[0]]
        for strand_col in strand_cols[1:]:
            if not (first == df[strand_col]).all():
                all_equal = False

        if not all_equal:
            print("More than one possible strand column found:", ", ".join(strand_cols),
                  "arbitrarily choosing:", guess)

    return guess


def guess_start_end(df, number_unique):

    position_cols = []
    at_least = (90 * len(df)) / 100

    for k, v in number_unique.items():

        # starts and ends should be int
        if df[k].dtype not in [np.int32, np.int64]:
            continue

        # should be at least 90% of original length, not too many equal starts/ends ==
        # position col has at least 90 percent original values
        # and all positions are above 0
        if v >= at_least and (df[k] >= 0).all():
            position_cols.append(k)

    if len(position_cols) < 2:
        raise Exception("Not enough possible location columns to deduct format.")

    elif len(position_cols) == 2:
        res = df[position_cols[0]] < df[position_cols[1]]
        if res.all():
            starts, ends = position_cols
        elif not res.any():
            ends, starts = position_cols
        else:
            raise Exception("No possible position cols; one should always be smaller than the other.")

    else:
        raise NotImplementedError("Finding position cols with more than two possible position cols not implemented yet.")

    return starts, ends


def guess_chromosome(df, number_unique):

    # should be at most 10% of length of df
    chromosome_cols = []
    at_most = (10 * len(df)) / 100

    for k, v in number_unique.items():

        # starts and ends should be str, cat or int
        if str(df[k].dtype) not in ["object", "category"] and "int" not in str(df[k].dtype):
            print(str(df[k].dtype))
            print(k)
            print(v, at_most)
            continue

        # chromosome col has at most 10 percent original values
        if v <= at_most:
            chromosome_cols.append(k)

    if not len(chromosome_cols):
        raise Exception("Found no potential chromosome col candidates.")

    guess = chromosome_cols[0]

    if len(chromosome_cols) == 1:
        return chromosome_cols[0]

    else:
        all_equal = True
        first = df[chromosome_cols[0]]
        for chromosome_col in chromosome_cols[1:]:
            if not (first == df[chromosome_col]).all():
                all_equal = False

        if not all_equal:
            print("More than one possible chromosome column found:", ", ".join(chromosome_cols),
                  "arbitrarily choosing:", guess)

    return guess


def parse_file(f):

    sep = guess_delim(f)
    header = guess_header(f, sep)

    df = pd.read_csv(f, sep=sep,
                     header={True: 0, False: None}[header])

    # all necessary columns found
    if header and df.columns.isin(["Chromosome", "Start", "End"]).sum() == 3:
        return df


    # helps find out which should be categorical and also which could be chromosome, strand or other
    number_unique = {c: len(df[c].unique()) for c in df}

    # guessing
    strand_guess = guess_strand(df, number_unique)
    start_guess, end_guess = guess_start_end(df, number_unique)

    return df




def guess_columns(f):

    df = parse_file(f)

    chromosome_idx = guess_chromosome_col(df)