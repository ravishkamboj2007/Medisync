DOCUMENTS = [
    "Diabetes is a chronic disease affecting blood sugar levels. Regular monitoring and medication are essential.",
    "Hypertension (high blood pressure) can lead to heart disease. Lifestyle changes and medication help manage it.",
    "Regular checkups are important for early detection and prevention of diseases.",
    "A balanced diet and regular exercise are key to maintaining good health.",
    "Common symptoms of fever include high temperature, chills, and fatigue.",
]


def retrieve_context(query: str) -> str:
    query_lower = query.lower()
    matched = [doc for doc in DOCUMENTS if any(word in doc.lower() for word in query_lower.split())]
    return "\n".join(matched[:2]) if matched else "\n".join(DOCUMENTS[:2])
