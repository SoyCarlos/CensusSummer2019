import numpy as np
import re
import pandas as pd
from gensim.models import KeyedVectors
print("imported")
filename = "glove.6B.300d.txt.word2vec"
model = KeyedVectors.load_word2vec_format(filename, binary=False)
print("loaded")

files = [["M:\\BJS Business Development\\Frames\\GMAF\\Unit.xlsx", ["NAME", ]],
         ["M:\\BJS Business Development\\Frames\\GMAF\\address.xlsx", ["TITLE",]],
         ["M:\\BJS Business Development\\Frames\\SSV\\SJIC 2018 frame.csv", ["Name_of_Facility", "Type", "Title", "NewContact_Title"]],
         ["M:\\BJS Business Development\\Frames\\SSV\\PrisCen_SSV-2016_2017-05-08_for Census.xlsx", ["F_Name", "FC_Title"]],
         ["M:\\BJS Business Development\\Frames\\SGRD Frame\\SGRD_Frame.xlsx", ["Name in Steps", "ContactTitle_Steps", "ContactName_Steps", "CTITLE", "_2CTIT"]],
         ["M:\\BJS Business Development\\Frames\\SGRD Frame\\SGRD_GMAF_Linked.xlsx", ["AgencyName", "CurrentStatus"]]]

minimodel = KeyedVectors(300)
wordsincluded = set()
missingwords = set()
for f in files:
    print(f)
    if f[0][-5:] == ".xlsx":
        df = pd.read_excel(f[0])
    else:
        df = pd.read_csv(f[0])
    print("loaded dataframe " + f[0])
    for index, row in df.iterrows():
        for col in f[1]:
            raw = re.split("\W+", str(row[col]))
            for word in raw:
                word = word.lower()
                if word not in wordsincluded and word not in missingwords:
                    try:
                        emb = model.get_vector(word)
                        wordsincluded.add(word)
                        minimodel.add([word,], [emb, ])
                    except KeyError:
                        missingwords.add(word)

minimodel.save("smaller_subset.word2vec")

test = KeyedVectors.load("smaller_subset.word2vec")
print(test.get_vector("assistant"))