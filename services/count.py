import re
from collections import Counter

def clean_text(text, case_sensistive=False, remove_stop_words=False):
    if not case_sensistive:
        text = text.lower()

    # filter non-alphabetic characters but keep apostrophes and spaces
    text = re.sub(r"[^a-zA-Z' ]", '', text)

    words = text.split()
    if remove_stop_words:
        stop_words = {"the", "is", "at", "which", "on"} # example stop words, import from nltk if needed
        words = [word for word in words if word not in stop_words]
    return words

# Maintains Captials
def clean_text_A(text):
    text = re.sub(r'[^a-zA-Z]', "", text)
    return text

def count_words(text):
    text = clean_text(text)
    return len(text.split())

def count_characters(text):
    return len(text)

def count_most_frequent_words(text, n=10):
    words = clean_text(text).split()
    return Counter[str](words).most_common(n)

def count_unique_words(text):
    words = clean_text(text).split()
    return len(set[str](words))



