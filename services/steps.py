import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')
nltk.download('stopwords')
# Steps for the text analysis (filtering, cleaning, etc.)
# Each step should ideally take a list of words and return a list of words.

import string

def tokenize_step(text):
    """Converts raw text into a list of tokens using NLTK."""
    return word_tokenize(text)

def remove_punctuation_step(words):
    """Removes punctuation from each word in the list."""
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in words]
    # Filter out empty strings that were just punctuation
    return [w for w in stripped if w]

def lowercase_step(words):
    """Converts all words to lowercase."""
    return [w.lower() for w in words]

def filter_alpha_step(words):
    """Removes non-alphabetic characters except apostrophes."""
    # We apply this to each word in the list
    cleaned = [re.sub(r"[^a-zA-Z']", '', w) for w in words]
    # Filter out any resulting empty strings
    return [w for w in cleaned if w]

def filter_alphanumeric_step(words):
    """Removes non-alphanumeric characters except apostrophes."""
    cleaned = [re.sub(r"[^a-zA-Z0-9']", '', w) for w in words]
    return [w for w in cleaned if w]

def remove_stop_words_step(words):
    """Removes common english stop words (based on nltk library)"""
    stop_words = set(stopwords.words('english'))
    return [w for w in words if w.lower() not in stop_words]

def create_exclusion_step(words_to_exclude):
    exclusion_set = set(w.lower() for w in words_to_exclude)
    
    def filter_step(words):
        return [w for w in words if w.lower() not in exclusion_set]
    
    # such that processor.py runs filter_step(data)
    return filter_step