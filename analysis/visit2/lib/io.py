"""Bounded CSV reader with explicit logical-to-physical header mapping."""
import codecs
import csv
from pathlib import Path

import pandas as pd


def detect_encoding(path, candidates):
    with Path(path).open("rb") as handle:
        head = handle.read(65536)
    for encoding in candidates:
        try:
            # final=False tolerates a multi-byte character straddling byte 65536.
            codecs.getincrementaldecoder(encoding)(errors="strict").decode(head, final=False)
            return encoding
        except (UnicodeError, LookupError):
            continue
    raise ValueError("지원 인코딩으로 CSV를 읽을 수 없습니다")


def read_header(path, encoding):
    with Path(path).open("r", encoding=encoding, newline="") as handle:
        try:
            header = next(csv.reader(handle, strict=True))
        except StopIteration as exc:
            raise ValueError("빈 CSV: 헤더가 없습니다") from exc
    if not header or len(set(header)) != len(header) or any(not x.strip() for x in header):
        raise ValueError("CSV 헤더가 비었거나 중복되었습니다")
    return header


def iter_chunks(path, usecols_logical, cols_map, encoding, chunksize):
    header = read_header(path, encoding)
    missing = ["%s -> %s" % (key, cols_map.get(key, "<MISSING>"))
               for key in usecols_logical if cols_map.get(key) not in header]
    if missing:
        raise ValueError("컬럼 매핑 불일치: %s; 실제 헤더=%s" % (", ".join(missing), header))
    physical = [cols_map[key] for key in usecols_logical]
    if len(set(physical)) != len(physical):
        raise ValueError("서로 다른 논리 컬럼에 같은 실제 컬럼이 지정되었습니다")
    try:
        for df in pd.read_csv(path, encoding=encoding, dtype=str, keep_default_na=False,
                              usecols=physical, chunksize=chunksize):
            df = df.rename(columns={cols_map[key]: key for key in usecols_logical})
            for col in df:
                df[col] = df[col].str.strip().replace("", pd.NA)
            yield df
    except (pd.errors.ParserError, UnicodeError) as exc:
        raise ValueError("CSV 파싱 실패: 열 구조 또는 인코딩을 확인하세요") from exc
