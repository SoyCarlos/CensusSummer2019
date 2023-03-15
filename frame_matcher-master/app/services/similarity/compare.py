# Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
# from Keith Finlay and Elizabeth Willhide.
import pandas as pd
import math
import numpy as np
import re
# from .normalized_levenshtein import NormalizedLevenshtein
from .doublemeta import metaphone
from .qgram import QGram
# from gensim.models import KeyedVectors
import string
# import name_similarity as ns


def compare_metas(meta_1, meta_2):
    """
    Compares two double metaphone tuples.
    :param meta_1: Metaphone 1 (Tuple of 2 Strings)
    :param meta_2: Metaphone 2 (Tuple of 2 Strings)
    :return: Whether there is a match between keys in meta_1 and meta_2 (Boolean)
    """
    # Strong Similarity
    if meta_1[0] == meta_2[0]:
        return 1
    # Normal Similarity
    elif meta_1[0] == meta_2[1] or meta_1[1] == meta_2[0]:
        return 0.9
    # Weak Similarity
    elif meta_1[1] == meta_2[1]:
        return 0.75
    # No Similarity
    else:
        return 0


def name_sim_score(n1raw, n2raw, model):
    """
    Calculates the similarity between names n1 and n2 through a combination of word embeddings and double metaphone
    scores.
    :param n1raw: name 1 (String)
    :param n2raw: name 2 (String)
    :param model: embeddings model (KeyedVectors)
    :return:
    """
    if type(n1raw) is not string or type(n2raw) is not string:
        return math.nan
    simscore = 0
    name1 = re.split("\W+", n1raw)
    name1 = [n.lower() for n in name1]
    name1 = remove_stop_words(name1)
    name2 = re.split("\W+", n2raw)
    name2 = [n.lower() for n in name2]
    name2 = remove_stop_words(name2)
    shorter, longer = min(name1, name2, key=len), max(name2, name1, key=len)
    for word in shorter:
        try:
            embscore = 1 - model.distances(word, longer).min()
        except KeyError:
            embscore = -999999
        dmscore = max([compare_metas(metaphone.dm(word), metaphone.dm(w2)) for w2 in longer])
        simscore += max(embscore, dmscore)
    return simscore/len(shorter)

#
def compare_names(blockedframe, names_1, names_2, simcolumns, modelfile = "smaller_subset.word2vec"):
    """
    Double metaphone comparison of two series of names. Can add weights by multiplying each pass by corresponding value.
    :param names_1: Column header for names from first frame (String)
    :param names_2: Column header for names from second frame (String)
    :param modelfile: Location of the embeddings model (String)
    :return: blockedframe now containing the name similarity scores, updated simcolumns
    """
    model = KeyedVectors.load(modelfile)
    blockedframe[names_1+"_"+names2+"_Similarity"] = blockedframe.apply(lambda df:name_sim_score(df[names_1], df[names_2], model), axis=1)
    simcolumns.append(names_1+"_"+names2+"_Similarity")
    return blockedframe, simcolumns


def clean_string(name):
    """Remove all punctuation from a string.
    
    Arguments:
        name {String} -- Any string (facility name, person name, etc)
    
    Returns:
        String -- String without punctuation
    """
    try:
        return name.translate(str.maketrans(string.punctuation, "".join([' ' for x in range(32)])))
    except:
        return ""

def split_string(name):
    """Returns string split into list by whitespace
    
    Arguments:
        name {string} -- String
    
    Returns:
        list -- string split into list
    """
    try:
        return list(filter(None, name.split(" ")))
    except:
        return ""

def remove_stop_words(split_name):
    """Removes stop words from string
    
    Arguments:
        split_name {list} -- list of words
    
    Returns:
        list -- list without stopwords
    """
    stop_words1 = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough"]
    stop_words2 = ["etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thick", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]
    stop_words1 = set(stop_words1)
    stop_words2 = set(stop_words2)
    first_pass = set(split_name) - stop_words1
    result = first_pass - stop_words2
    return list(result)

def list_metas(lst):
    """Takes in list of words and returns their metaphones.
    
    Arguments:
        lst {list} -- List of words
    
    Returns:
        list -- List of metaphones
    """
    lst = np.array(list(map(lambda x: x.split(), lst))).ravel()
    return set(filter(None, np.array(list(map(metaphone.dm, lst))).ravel()))

def meta_similarity(tbl):
    """Takes in a row and calculates the similarity between two different list of metaphones.
    
    Arguments:
        tbl {row} -- Row from table
    
    Returns:
        int -- Metaphone similarity score
    """
    try:
        return len(tbl['metas1'].intersection(tbl['metas2'])) / np.mean([len(tbl['metas1']), len(tbl['metas2'])])
    except Exception as e:
        print(e)
        return 0

def string_comparisons_hack(col1, col2):
    """Takes in two columns with strings and calculates their similarities.
    
    Arguments:
        col1 {string} -- Name of column from first frame
        col2 {string} -- Name of column from second frame
    
    Returns:
        pandas Series -- Similarity score between two columns of strings
    """
    col1 = col1.apply(clean_string).apply(split_string).apply(remove_stop_words)
    col1metas = col1.apply(list_metas)
    col2 = col2.apply(clean_string).apply(split_string).apply(remove_stop_words)
    col2metas = col2.apply(list_metas)
    inp = pd.DataFrame()
    inp['metas1'] = col1metas
    inp['metas2'] = col2metas
    sim = inp.apply(meta_similarity, axis=1)
    return sim


def qgram_helper(row):
    """Takes in a row and calculates the qgram similarity between two strings.
    
    Arguments:
        tbl {row} -- Row from table
    
    Returns:
        int -- QGram similarity score
    """
    try:
        qgram = QGram()
        return qgram.similarity(row['col1'], row['col2'])
    except Exception as e:
        print(row, e)
        return 0


def qgram_comparison(col1, col2):
    qgram = QGram()
    inp = pd.DataFrame()
    col1 = col1.apply(clean_string).str.lower()
    col2 = col2.apply(clean_string).str.lower()
    inp['col1'] = col1
    inp['col2'] = col2
    sim = inp.apply(qgram_helper, axis=1)
    return sim
    


def coord_dist(long1, lat1, long2, lat2):
    """
    Calculates birds-eye distance between two locations in miles using longitude and latitude.
    :param long1: longitude of location 1 (float)
    :param lat1: latitude of location 1 (float)
    :param long2: longitude of location 2 (float)
    :param lat2: latitude of location 2 (float)
    :return: distance between the two locations (miles)
    """
    if isinstance(long1, (int, float, complex)) and isinstance(lat1, (int, float, complex)) and isinstance(long2, (int, float, complex)) and isinstance(lat2, (int, float, complex)):
        latdist = abs(lat1 - lat2) * 69
        longdist = abs(long1 - long2) * math.cos(0.5 * abs(lat1 + lat2) * 2 * math.pi / 360) * 69.172
        return math.sqrt(math.pow(latdist, 2) + math.pow(longdist, 2))
    else:
        return math.nan

def location_similarities(blocked_frame, long1, lat1, long2, lat2, similarity_col):
    """
    Calculates similarity scores between locations (denoted by their longitudes and latitudes) in a frame that have
    a ZIP code match. Appends 'Location Similarity' to the similarity_col list.
    :param blocked_frame1: Combined frame made of both original frames (pandas DataFrame)
    :param long1: Column name containing longitudes from the first data frame (string)
    :param lat1: Column name containing latitudes from the first data frame (string)
    :param long2: Column name containing longitudes from the second data frame (string)
    :param lat2: Column name containing latitudes from the second data frame (string)
    :param similarity_col: List of column names used to display similarities per row/category (list of strings)
    :return: frame that now includes similarities and list of similarity column names (pandas DataFrame, list of strings)
    """
    blocked_frame['Location Similarity'] = blocked_frame.apply(lambda df: 100 - coord_dist(df[long1], df[lat1], df[long2], df[lat2]), axis=1)
    similarity_col.append('Location Similarity')
    return blocked_frame, similarity_col
