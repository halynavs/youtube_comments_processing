import pandas as pd
import csv
import re
import nltk
import emoji
import numpy as np
from wiki_ru_wordnet import WikiWordnet
wikiwordnet = WikiWordnet()

from nltk.tokenize.toktok import ToktokTokenizer
tokenizer = ToktokTokenizer()

stopword_list = nltk.corpus.stopwords.words('russian')
# just to keep negation if any in bi-grams
stopword_list.remove('не')
stopword_list.remove('нет')

from spacy_stanza import StanzaLanguage
import stanza

stanza.download('ru')
stanza_nlp = stanza.Pipeline('ru')
snlp = stanza.Pipeline(lang="ru")
nlp = StanzaLanguage(snlp)


# 1
def create_df_from_input_labeled(file_name):
    df_of_comments = pd.DataFrame()
    comments = []
    label = []
    with open(f'{file_name}.csv', 'r', encoding="utf-8") as commentsfile:
        comment_file_reader = csv.reader(commentsfile)
        for row in comment_file_reader:
            if row != []:
                comments.append(row[0])
                label.append(row[1])

    df_of_comments['Comment'] = comments[1:]
    df_of_comments['Label'] = label[1:]
    #display settings
    pd.set_option('max_colwidth', 100)
    # pd.set_option('display.width', 500)

    return df_of_comments

# 2
def create_df_from_real_input(file_name):
    df_of_comments = pd.DataFrame()
    comments = []
    with open(f'{file_name}.csv', 'r', encoding="utf-8") as commentsfile:
        comments_file_reader = csv.reader(commentsfile)
        for row in comments_file_reader:
            if row != []:
                comments.append(row[0])

    df_of_comments['Comment'] = comments[1:]

    return df_of_comments


def find_timecode(text):
    timecode = re.findall('\d{2}:\d{2}|\d{1}:\d{2}', text)
    return timecode

def remove_url(text):
    text = re.sub(r"(http |http).*$", '', text)
    return text

def remove_special_characters(text):
    text = re.sub(r'[^а-яА-ЯёЁ\s]', '', text, re.I | re.A)
    return text

def find_emoji(text):
    emojis_in_comment = [char for char in text if char in emoji.UNICODE_EMOJI]
    return emojis_in_comment


def remove_repeated_characters(tokens):
    repeat_pattern = re.compile(r'(\w*)(\w)\2(\w*)')
    match_substitution = r'\1\2\3'

    def replace(old_word):
        if wikiwordnet.get_synsets(old_word):
            return old_word
        new_word = repeat_pattern.sub(match_substitution, old_word)
        return replace(new_word) if new_word != old_word else new_word

    correct_tokens = [replace(word) for word in tokens]
    text = ' '.join(correct_tokens)
    return text

def remove_stopwords(text, is_lower_case=False, stopwords=stopword_list):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopwords]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopwords]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

def lemmatisaze_document(doc):

    nlp = StanzaLanguage(snlp)
    doc = nlp(doc)

    filtered_tokens = [token.lemma_ for token in doc]
    doc = ' '.join(filtered_tokens)
    return doc


def normalize_corpus(corpus, extract_timecodes=True,
                     special_char_removal=True, use_emoji=True,
                     repeated_characters_remover=True, text_lower_case=True,
                     stop_words_remover = True, stopwords=stopword_list, text_lemmatization=True):

    normalized_corpus = []
    list_of_emoji = []
    timecode_list = []
    timecodes = []
    emoji = []

    # normalize each document in the corpus
    for doc in corpus:

        # remove extra newlines
        doc = doc.translate(doc.maketrans("\n\t\r", "   "))

        # remove extra whitespace
        doc = re.sub(' +', ' ', doc)
        doc = doc.strip()

        #extract emoji
        if use_emoji:
            emoji = find_emoji(doc)

        #extract timecode
        if extract_timecodes:
            timecodes = find_timecode(doc)


        #remove punct, special characters\whitespaces
        if special_char_removal:
            doc = remove_special_characters(doc)

         # lowercase the text
        if text_lower_case:
            doc = doc.lower()

        #remove repeated characters
        if repeated_characters_remover:
            tokens = tokenizer.tokenize(doc)
            doc = remove_repeated_characters(tokens)

        #lemmatize text
        if text_lemmatization:
            lemmatisaze_corpus = np.vectorize(lemmatisaze_document)
            doc = lemmatisaze_corpus(doc)

        #removing stop words
        if stop_words_remover:
            doc = remove_stopwords(doc, is_lower_case=text_lower_case, stopwords=stopwords)

        timecode_list.append(timecodes)
        list_of_emoji.append(emoji)
        normalized_corpus.append(doc)
    return normalized_corpus, list_of_emoji, timecode_list