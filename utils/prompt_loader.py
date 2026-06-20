from pathlib import Path

PROMPT_DIR = Path("prompts")


def list_prompts():
    """Return prompt filenames without extensions."""
    PROMPT_DIR.mkdir(exist_ok=True)
    return sorted(p.stem for p in PROMPT_DIR.glob("*.txt"))


def load_prompt(prompt_name: str) -> str:
    """Load prompt text by its stem name."""
    # Sanitize input to prevent path traversal (extract only the file name)
    safe_name = Path(prompt_name).name
    path = PROMPT_DIR / f"{safe_name}.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
