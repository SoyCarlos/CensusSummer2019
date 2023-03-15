#Developed by Shohini Saha and Carlos Eduardo Ortega with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import numpy as np
import re
# from .doublemeta import metaphone

# from gensim.scripts.glove2word2vec import glove2word2vec
# glove_input_file='glove.6B.300d.txt'
# word2vec_output_file='glove.6B.300d.txt.word2vec'
# glove2word2vec(glove_input_file, word2vec_output_file)

from gensim.models import KeyedVectors
print("imported")
import os 
cwd = os.getcwd()
print(cwd)
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = "smaller_subset.word2vec" #"./app/services/similarity/smaller_subset.word2vec"
model = KeyedVectors.load(filename)
print("loaded")

class WordEmbedding:
    def __init__(self, w, emb=None):
        """
        Initializes a word embedding class for a word w.
        :param w: the word itself: lowercase only string
        self.embedvec: word2vec embedding of the word
        self.count: total count of all occurrences of the word w that call this instance of the WordEmbedding
        """
        if emb != None:
            self.embedvec = emb
        else:
            self.embedvec = model.get_vector(w)
        self.word = w
        self.count = 1

    def weightedemb(self, totalwords):
        return self.embedvec * np.log(self.count/totalwords)

class Name:
    def __init__(self, name, embdict):
        if type(name) == str:
            words = re.split("\W+", name)
            words = [w.lower() for w in words]
        else:
            words = list(name)
        self.words = words
        self.embedwords = []
        for w in words:
            if w in embdict.keys():
                self.embedwords.append(w)

    def __len__(self):
        return len(self.words)


def initialize(dataframe, col, filename = "smaller_subset.word2vec"):
    """
    Initializes correct word counts and embedding storage of all the words in names in the dataframe as well as representation of the names.
    :param dataframe: dataframe considered (type: pandas DataFrame)
    :param col: name of the column containing names
    :return:
    """
    wordembs = dict()
    doublemetaphones = dict()
    model = KeyedVectors.load(filename)
    #TODO: Clean column to standardized form

    #Iterate through names, add words to dictionary of words with embeddings, find double metaphones of all words
    totalwords = 0
    for index, row in dataframe.iterrows():
        fullname = row[col]
        for word in re.split("\W+", fullname):
            if word not in wordembs.keys():
                try:
                    wordembs[word] = WordEmbedding(word, model.get_vector(word))
                except KeyError:
                    pass
            else:
                wordembs[word].count += 1
            if word not in doublemetaphones.keys():
                doublemetaphones[word] = metaphone.dm(word)
            totalwords += 1
    dataframe['NameObj'] = dataframe[col].apply(lambda name: Name(name, wordembs))
    return dataframe, wordembs, doublemetaphones, totalwords
#
# def similarity(n0, n1):
#     """
#     Calculates the similarity between names n0 and n1 through a combination of word embeddings and double metaphone
#     scores.
#     :param n0: name 1 (String)
#     :param n1: name 2 (String)
#     :return:
#     """
#     simscore = 0
#     # Embedding similarity
#     for word0 in n0.words:
#         for word1 in n1.words:
#             dmscore = metaphone.
#     if len(n0.embedwords) < len(n1.embedwords):
#         shorter, longer = n0.embedwords, n1.embedwords
#     else:
#         shorter, longer = n1.embedwords, n0.embedwords
#     for word in shorter:
#         simscore += 1 - model.distances(word, longer).min()
#     return simscore/len(shorter)

# embdict = {"the": 0, "red": 0, "car": 0, "van": 0, "unrelated": 0, "word": 0, "sequence": 0}
# sent0 = Name("the red car", embdict)
# sent1 = Name("the red van", embdict)
# sent2 = Name("unrelated word sequence", embdict)
# print(similarity(sent0, sent1))
# print(similarity(sent0, sent2))
# print(similarity(sent1, sent2))
# print(similarity(sent0, sent0))