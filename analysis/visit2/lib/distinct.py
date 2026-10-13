"""Exact cross-chunk counts; missing identifiers do not count as a person/shop."""
import pandas as pd


class DistinctAccumulator:
    def __init__(self, keys, max_rows=5000000):
        self.keys = list(keys)
        self.max_rows = max_rows
        self.frames = []
        self.rows = 0
        self.id_col = None

    def update(self, df, id_col):
        if self.id_col is not None and self.id_col != id_col:
            raise ValueError("한 누적기에 다른 ID 열을 섞을 수 없습니다")
        self.id_col = id_col
        part = df[self.keys + [id_col]].dropna(subset=[id_col]).drop_duplicates()
        self.frames.append(part)
        self.rows += len(part)
        if self.rows > self.max_rows:
            combined = pd.concat(self.frames, ignore_index=True).drop_duplicates()
            self.frames = [combined]
            self.rows = len(combined)

    def finalize(self):
        if not self.frames:
            return pd.DataFrame(columns=self.keys + ["nunique"])
        data = pd.concat(self.frames, ignore_index=True).drop_duplicates()
        if not self.keys:
            return pd.DataFrame({"nunique": [len(data)]})
        return data.groupby(self.keys, dropna=False).size().rename("nunique").reset_index()


class CountAccumulator:
    def __init__(self, keys):
        self.keys = list(keys)
        self.total = None
        self.scalar = 0

    def update(self, df):
        if not self.keys:
            self.scalar += len(df)
            return
        part = df.groupby(self.keys, dropna=False).size()
        self.total = part if self.total is None else self.total.add(part, fill_value=0)

    def finalize(self):
        if not self.keys:
            return pd.DataFrame({"n": [self.scalar]})
        if self.total is None:
            return pd.DataFrame(columns=self.keys + ["n"])
        return self.total.astype("int64").rename("n").reset_index()
