from typing import List, Dict

from osbot_utils.type_safe.Type_Safe import Type_Safe

class Schema__Text__Rating(Type_Safe):
    """Represents the rating assessment of a text with sentiment and topic."""
    hash      : str = None # Hash of text item
    positivity: float      # Positivity rating from 0 (negative) to 1 (positive), 0.5 is neutral
    topic     : str        # Main topic or subject of the text

class Schema__Text__Ratings(Type_Safe):
    ratings : List[Schema__Text__Rating]