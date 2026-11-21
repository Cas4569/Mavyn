"""Static category taxonomy used to organize live market research."""

_CATEGORIES = [
    {
        "id": "sunscreens",
        "name": "Sunscreens",
        "description": "Broad-spectrum UV protection for Indian climate",
    },
    {
        "id": "serums",
        "name": "Serums",
        "description": "Targeted active ingredient treatments",
    },
    {
        "id": "moisturizers",
        "name": "Moisturizers",
        "description": "Hydration and barrier support",
    },
    {
        "id": "cleansers",
        "name": "Cleansers",
        "description": "Gentle cleansing for all skin types",
    },
    {
        "id": "toners",
        "name": "Toners & Essences",
        "description": "Prep and hydration boosters",
    },
]


def get_categories() -> list[dict]:
    """Return a copy of the supported category taxonomy."""
    return [category.copy() for category in _CATEGORIES]
