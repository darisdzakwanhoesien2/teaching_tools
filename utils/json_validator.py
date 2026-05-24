def validate_schema(data: dict):
    required_root = ["topic", "questions"]

    for key in required_root:
        if key not in data:
            return False, f"Missing root key: {key}"

    if not isinstance(data["questions"], list):
        return False, "questions must be a list"

    required_fields = {
        "filename",
        "question_number",
        "topic",
        "syllabus_codes",
        "question_summary",
        "physical_concepts",
        "variables_involved",
        "reasoning_focus",
        "calculation_required",
    }

    for i, question in enumerate(data["questions"], 1):
        if not isinstance(question, dict):
            return False, f"Question {i} must be an object"

        missing = required_fields - question.keys()
        if missing:
            return False, f"Question {i} missing fields: {sorted(missing)}"

    return True, "Schema valid ✅"
