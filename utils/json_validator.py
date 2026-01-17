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

    for i, q in enumerate(data["questions"], 1):
        missing = required_fields - q.keys()
        if missing:
            return False, f"Question {i} missing fields: {missing}"

    return True, "Schema valid ✅"

# def validate_schema(data: dict) -> tuple[bool, str]:
#     required_root = ["topic", "questions"]

#     for key in required_root:
#         if key not in data:
#             return False, f"Missing root key: {key}"

#     if not isinstance(data["questions"], list):
#         return False, "questions must be a list"

#     required_fields = {
#         "filename",
#         "question_number",
#         "topic",
#         "syllabus_codes",
#         "question_summary",
#         "physical_concepts",
#         "variables_involved",
#         "reasoning_focus",
#         "calculation_required",
#     }

#     for idx, q in enumerate(data["questions"]):
#         missing = required_fields - q.keys()
#         if missing:
#             return False, f"Question {idx+1} missing fields: {missing}"

#     return True, "Schema valid ✅"