import io
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


STORAGE_DIR = Path("data/saved_results")
MANIFEST_PATH = STORAGE_DIR / "manifest.json"

EXPECTED_COLUMNS = [
    "Question ID",
    "Question",
    "Main Chapter",
    "Subchapter",
    "Secondary Subchapters",
    "Reasoning",
]


def strip_markdown(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.fillna("").copy()
    normalized.columns = [strip_markdown(column) for column in normalized.columns]
    for column in EXPECTED_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = ""
    return normalized


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "saved_results"


def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    try:
        with MANIFEST_PATH.open("r", encoding="utf-8") as file:
            manifest = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []
    return manifest if isinstance(manifest, list) else []


def write_manifest(manifest: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)


def save_result(df: pd.DataFrame, dataset_name: str) -> dict:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_stem = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{slugify(dataset_name)}"
    csv_path = STORAGE_DIR / f"{file_stem}.csv"
    df.to_csv(csv_path, index=False)

    entry = {
        "name": dataset_name.strip() or "Untitled results",
        "saved_at": saved_at,
        "rows": int(len(df)),
        "test": str(df["Test"].iloc[0]) if "Test" in df.columns and not df.empty else "",
        "source": str(df["Source"].iloc[0]) if "Source" in df.columns and not df.empty else "",
        "file": str(csv_path),
    }
    manifest = [entry] + load_manifest()
    write_manifest(manifest)
    return entry


def load_saved_result(entry: dict) -> pd.DataFrame:
    csv_path = Path(entry["file"])
    if not csv_path.exists():
        raise FileNotFoundError(f"Saved file is missing: {csv_path}")
    return normalize_columns(pd.read_csv(csv_path, dtype=str))


def saved_option_label(entry: dict) -> str:
    test = f" [{entry.get('test')}]" if entry.get("test") else ""
    return f"{entry.get('name', 'Untitled results')}{test} - {entry.get('rows', 0)} rows"


def split_markdown_row(line: str) -> list[str]:
    cells = []
    current = []
    escaped = False

    for char in line.strip():
        if char == "\\" and not escaped:
            escaped = True
            current.append(char)
            continue
        if char == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        escaped = False

    cells.append("".join(current).strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_markdown_table(raw_text: str) -> pd.DataFrame:
    rows = []
    for line in raw_text.splitlines():
        if "|" not in line:
            continue
        cells = split_markdown_row(line)
        if not cells or is_separator_row(cells):
            continue
        rows.append(cells)

    if len(rows) < 2:
        raise ValueError("Paste a Markdown table with a header row and at least one data row.")

    header = [strip_markdown(cell) for cell in rows[0]]
    width = len(header)
    data = []
    for row in rows[1:]:
        padded = row[:width] + [""] * max(0, width - len(row))
        data.append([strip_markdown(cell) for cell in padded])

    return pd.DataFrame(data, columns=header)


def parse_delimited_table(raw_text: str, delimiter: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(raw_text), sep=delimiter).fillna("")


def parse_input(raw_text: str, input_format: str) -> pd.DataFrame:
    if not raw_text.strip():
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    if input_format == "Markdown table":
        df = parse_markdown_table(raw_text)
    elif input_format == "CSV":
        df = parse_delimited_table(raw_text, ",")
    elif input_format == "TSV":
        df = parse_delimited_table(raw_text, "\t")
    else:
        try:
            df = parse_markdown_table(raw_text)
        except Exception:
            try:
                df = parse_delimited_table(raw_text, ",")
            except Exception:
                df = parse_delimited_table(raw_text, "\t")

    df = normalize_columns(df)
    ordered_columns = EXPECTED_COLUMNS + [column for column in df.columns if column not in EXPECTED_COLUMNS]
    
    # Map strip_markdown element-wise in a pandas version-safe way (map was added in 2.1.0, applymap is older)
    df_subset = df[ordered_columns]
    if hasattr(df_subset, "map"):
        return df_subset.map(strip_markdown)
    return df_subset.applymap(strip_markdown)


def add_metadata(df: pd.DataFrame, test_name: str, source_label: str) -> pd.DataFrame:
    enriched = df.copy()
    enriched.insert(0, "Test", test_name.strip() or "Untitled Test")
    enriched.insert(1, "Source", source_label.strip())
    enriched.insert(2, "Parsed At", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return enriched


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Main Chapter" not in df.columns:
        return pd.DataFrame(columns=["Main Chapter", "Questions", "Subchapters"])

    grouped = (
        df.groupby("Main Chapter", dropna=False)
        .agg(
            Questions=("Question ID", "count"),
            Subchapters=("Subchapter", lambda values: ", ".join(sorted({value for value in values if value}))),
        )
        .reset_index()
        .sort_values(["Questions", "Main Chapter"], ascending=[False, True])
    )
    return grouped


def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_json(df: pd.DataFrame) -> bytes:
    return df.to_json(orient="records", indent=2, force_ascii=False).encode("utf-8")
