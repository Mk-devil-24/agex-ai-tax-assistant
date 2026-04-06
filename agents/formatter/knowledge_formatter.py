def format_knowledge_response(data):
    if not data:
        return "I couldn’t find information for that."

    concept = data.get("concept")
    explanation = data.get("explanation")
    points = data.get("key_points", [])

    text_lines = []

    if concept:
        text_lines.append(concept)

    if explanation:
        text_lines.append("")
        text_lines.append(explanation)

    if points:
        text_lines.append("")
        text_lines.append("Key points:")
        for point in points:
            text_lines.append(f"• {point}")

    return "\n".join(text_lines)