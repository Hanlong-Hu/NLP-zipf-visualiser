# Output File for the final metrics
from collections import Counter

def get_word_count(words):
    """Returns total number of words."""
    return len(words)

def get_unique_word_count(words):
    """Returns number of unique words."""
    return len(set(words))

def get_most_frequent_words(words, n=None):
    """Returns the n most frequent words in a format suitable for charts."""
    counts = Counter(words).most_common(n)
    return {
        "labels": [word for word, count in counts],
        "values": [count for word, count in counts]
    }

def get_character_count(text):
    """Returns total number of characters in raw text."""
    return len(text)

def get_character_count_no_spaces(text):
    """Returns total number of characters in raw text excluding whitespace."""
    return len("".join(text.split()))
