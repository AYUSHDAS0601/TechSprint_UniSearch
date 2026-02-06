from typing import List
from .utils import setup_logging

logger = setup_logging("Classifier")

class NoticeClassifier:
    def __init__(self):
        self.categories = {
            "Examination": ["exam", "test", "assessment", "schedule", "mid-term", "final", "date sheet"],
            "Scholarship": ["scholarship", "financial aid", "grant", "stipend", "bursary", "income"],
            "Transport": ["bus", "route", "transport", "vehicle", "shuttle", "pickup"],
            "Academic": ["syllabus", "course", "lecture", "lab", "curriculum", "book", "reference"],
            "Administrative": ["notice", "circular", "announcement", "office", "regulation", "fee", "deadline"],
            "Events": ["fest", "competition", "workshop", "seminar", "hackathon", "cultural"]
        }

    def classify(self, text: str) -> List[str]:
        """
        Classifies text into known categories based on keywords.
        """
        text_lower = text.lower()
        detected_categories = []

        for category, keywords in self.categories.items():
            # Simple keyword matching, could be improved with TF-IDF or counts
            if any(keyword in text_lower for keyword in keywords):
                detected_categories.append(category)

        if not detected_categories:
            detected_categories.append("General")

        return detected_categories
