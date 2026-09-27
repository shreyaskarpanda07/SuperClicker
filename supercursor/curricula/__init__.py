from .coding_ml import CURRICULUM as CODING_ML
from .davinci import CURRICULUM as DAVINCI
from .figma import CURRICULUM as FIGMA
from .fl_studio import CURRICULUM as FL_STUDIO

ALL_CURRICULA = {
    "coding_ml": CODING_ML,
    "davinci": DAVINCI,
    "figma": FIGMA,
    "fl_studio": FL_STUDIO,
}

def get_curriculum_for_app(app_type: str):
    """Returns curriculum matching app type, or None."""
    return ALL_CURRICULA.get(app_type)

def list_all_lessons():
    """Returns all lessons across all domains."""
    lessons = []
    for cat, curr in ALL_CURRICULA.items():
        for lesson in curr.get("lessons", []):
            lessons.append({
                "category": curr["name"],
                "category_id": cat,
                **lesson
            })
    return lessons
