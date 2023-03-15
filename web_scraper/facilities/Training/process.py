import pandas as pd
from os import listdir
from os.path import isfile, join
import os
import numpy as np

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, "training_data//clean_files//")
files = [directory + f for f in listdir(directory) if isfile(join(directory, f)) and f[0] != "."]

save_directory = os.path.join(dirname, "training_data//")

for file in files:
    extension = file.split('.')[-1]
    if extension == 'csv':
        temp = pd.read_csv(file, encoding='ISO-8859-1')
        temp.columns = ['url', 'text']
        temp['relevant'] = np.zeros(len(temp))
        filename = save_directory + file.split('.')[0].split('//')[-1] + ".xlsx"
        temp.to_excel(filename, index=False)
    elif extension == 'xlsx':
        temp = pd.read_excel(file)
        temp['relevant'] = np.zeros(len(temp))
        filename = save_directory + file.split('.')[0].split('//')[-1] + ".xlsx"
        temp.to_excel(filename, index=False)