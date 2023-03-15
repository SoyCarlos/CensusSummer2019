import string
import numpy as np
from os import listdir
from os.path import isfile, join
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
import pickle
import os
import pandas as pd
import sys

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'training_data/')
files = [directory + f for f in listdir(directory) if isfile(directory+f)]
starting = True
frame = 0

for file in files:
    if starting:
        starting = False
        frame = pd.read_excel(file)
    else:
        frame = frame.append(pd.read_excel(file), ignore_index=True, sort=False)
    
use = frame[['text', 'relevant']]
use.reset_index(drop=True, inplace=True)
relevant, non_relevant = use[use['relevant'] == 1], use[use['relevant'] == 0]

print("Total in use:", len(use), "\nTotal Relevant:", len(relevant), "\nTotal Non Relevant:", len(non_relevant))


def create_classifier():
    clf_sgd = Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                alpha=0.001, random_state=42,
                                max_iter=100, tol=0.19))
        ])

    msk = np.random.rand(len(use)) < 0.7
    train, test = use[msk], use[~msk]
    clf_sgd.fit(train['text'].values, train['relevant'].values)  
    prediction_sgd = clf_sgd.predict(test['text'])
    accuracy_sgd = np.mean(prediction_sgd == test['relevant'].values) 
    
    print("Accuracy:", accuracy_sgd)
    print(metrics.classification_report(test['relevant'].values, prediction_sgd, labels=[1,0], 
                                        target_names=['Relevant', 'Non Relevant']))
    return clf_sgd


classifier = create_classifier()
in_progress = True

while in_progress:
    response = input("Are you satisfied with this classifier? (Yes, No, Quit)\n")
    r = response[0].lower()
    if r == 'y':
        in_progress = False
        break
    elif r == 'n':
        classifier = create_classifier()
        continue
    elif r == 'q':
        print("Goodbye")
        sys.exit()
    else:
        continue

dirname = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'facilities/classify/'))
classifier_filename = os.path.join(dirname, 'classifier.pkl')
classifier_model = open(classifier_filename, 'wb')
pickle.dump(classifier.get_params()['clf'], classifier_model)
classifier_model.close()

vect_filename = os.path.join(dirname, 'vectorizer.pkl')
vect_model = open(vect_filename, 'wb')
pickle.dump(classifier.get_params()['vect'], vect_model)
vect_model.close()

tf_filename = os.path.join(dirname, 'transformer.pkl')
tf_model = open(tf_filename, 'wb')
pickle.dump(classifier.get_params()['tfidf'], tf_model)
tf_model.close()

print("Goodbye")