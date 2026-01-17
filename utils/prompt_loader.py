from pathlib import Path

PROMPT_DIR = Path("prompts")


def list_prompts():
    """
    Returns prompt filenames without extension.
    Example: ["week01", "week02"]
    """
    PROMPT_DIR.mkdir(exist_ok=True)
    return sorted([p.stem for p in PROMPT_DIR.glob("*.txt")])


def load_prompt(prompt_name: str) -> str:
    """
    Loads prompt text by name.
    """
    path = PROMPT_DIR / f"{prompt_name}.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

# from pathlib import Path

# PROMPT_DIR = Path("prompts")


# def list_prompts():
#     PROMPT_DIR.mkdir(exist_ok=True)
#     return sorted([p.stem for p in PROMPT_DIR.glob("*.txt")])


# def load_prompt(prompt_name: str) -> str:
#     path = PROMPT_DIR / f"{prompt_name}.txt"
#     if not path.exists():
#         return ""
#     return path.read_text(encoding="utf-8")