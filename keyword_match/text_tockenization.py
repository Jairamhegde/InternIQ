import re
from keyword_match.keywords_set import *

def generate_unigrams(text: str):
    text = text.lower().strip()
    text = re.sub(r"[/\-]", " ", text)
    text = re.sub(r"[^a-z\d\s.+#]", " ", text)
    return text.split()

def generate_bigrams(tokens):
    bigrams = set()
    for i in range(len(tokens) - 1):
        bigrams.add(tokens[i] + " " + tokens[i + 1])
    return bigrams


def get_matching_skills(ar):
    skill = set()
    for i in ar:
        if i == None:
            continue
        i = NORMALIZATION.get(i,i)
        if i in ALL_SKILLS:
            skill.add(i)

    return list(skill)


# unigrams = generate_unigrams(text)
# bigrams = generate_bigrams(unigrams)
# ngrams = set(unigrams) | bigrams
# 
# print(matchining)


