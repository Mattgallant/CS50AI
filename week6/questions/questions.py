import re

import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    files = {}
    for filename in os.listdir(directory):
        file = open(os.path.join(directory, filename), encoding="utf8")
        file_contents = file.read()
        files[filename] = file_contents
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = []
    text = document.lower()
    for word in nltk.word_tokenize(text):
        if word not in string.punctuation and word not in nltk.corpus.stopwords.words("english") and re.search('[a-zA-Z]', word):
            words.append(word)
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    total_docs = len(documents)
    num_docs_containing = {}
    idf = {}

    # Compute NumDocsContaining dictionary
    for document in documents:
        already_counted = set()
        for word in documents[document]:
            if word in already_counted:
                # Word already counted for this document
                continue
            if word in num_docs_containing:
                # Have come across this word in documents before, but not in this document
                num_docs_containing[word] += 1
            else:
                # First time we come across this word in the documents as a whole
                num_docs_containing[word] = 1
            already_counted.add(word)

    # Calculate IDF values
    for word in num_docs_containing:
        idf[word] = math.log((total_docs/num_docs_containing[word]))

    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = {}

    # Calculate tf-idf value for each file and populate dictionary
    for file in files:
        # Calculate term_frequency
        term_frequency = {}
        for word in files[file]:
            if word in term_frequency:
                term_frequency[word] += 1
            else:
                term_frequency[word] = 1
        # Calculate tf-idf
        tf_idf = 0
        for query_word in query:
            if query_word in term_frequency:
                tf_idf += term_frequency[query_word] * idfs[query_word]
        tf_idfs[file] = tf_idf

    # Sort tf_idf values and turn into list, taking top n
    ranked_docs = sorted(tf_idfs.items(), key=lambda x: x[1], reverse=True)
    ranked_docs = ranked_docs[0:n]
    ranked_docs = [doc[0] for doc in ranked_docs]
    return ranked_docs


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    mwm_values = {}  # Holds sentences mapped to their "matching word measure" value
    # Calculate matching word measure value for each sentence
    for sentence in sentences:
        mwm_value = 0
        for word in sentences[sentence]:
            if word in query:
                mwm_value += idfs[word]
        mwm_values[sentence] = mwm_value

    ranked_sentences = sorted(mwm_values.items(), key=lambda x: x[1], reverse=True)
    ranked_sentences = [sentence[0] for sentence in ranked_sentences]

    # Check query term density, compile a list of last items that are the same and would be cutoff
    if len(ranked_sentences) > n:
        same_mwm = []
        last_item = ranked_sentences[n-1]
        same_mwm.append(last_item)
        last_item_mwm = mwm_values[last_item]
        for item in ranked_sentences[n:]:
            if mwm_values[item] == last_item_mwm:
                same_mwm.append(item)
            elif mwm_values[item] < last_item_mwm:
                break

    # Now have a list of items at end of ranking w/ same mwm values
    if len(same_mwm) > 1:
        qtd_values = {}
        words_in_query = len(query)
        # Calculate number of words in the query and sentence
        for sentence in same_mwm:
            qtd = 0
            for word in sentence:
                if word in query:
                    qtd += 1
            qtd_values[sentence] = qtd
        # Calculate qtd values
        for sentence in qtd_values:
            qtd_values[sentence] = qtd_values[sentence]/len(sentence)
        if qtd_values[ranked_sentences[n-1]] < qtd_values[ranked_sentences[n]]:
            # Do a swap, for now this only looks at two values at the end.... TODO: Implement this to be more robust.
            qtd_values[ranked_sentences[n-1]], qtd_values[ranked_sentences[n]] = qtd_values[ranked_sentences[n]], qtd_values[ranked_sentences[n-1]]

    ranked_sentences = ranked_sentences[0:n]
    return ranked_sentences

if __name__ == "__main__":
    main()
