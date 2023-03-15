#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import pandas as pd
import numpy as np
from functionality import blocking, choose_columns, cleaning, file_proc, locations
from similarity import compare

# Initialize variables
frame1 = None
frame2 = None

while frame1 is None:
    file1 = input("Type the path to the old file here: \n")
    file_type_1 = file_proc.get_file_type(file1)
    try:
        frame1 = file_proc.read_frame(file1, file_type_1)
    except FileNotFoundError:
        print("File does not exist.")
frame1 = frame1.reset_index().rename(columns={'index': 'Source 1'})

while frame2 is None:
    file2 = input("Type the path to the new file here: \n")
    file_type_2 = file_proc.get_file_type(file2)
    try:
        frame2 = file_proc.read_frame(file2, file_type_2)
    except FileNotFoundError:
        print("File does not exist.")

    if file2 == file1:
        print("The new file must be different from the old file.")
        frame2 = None

frame2 = frame2.reset_index().rename(columns={'index': 'Source 2'})

while True:
    print("Do you want to MANUALLY (M) choose columns that match or do you wish "
          + "the program to AUTOMATICALLY (A) find them.")
    auto_man = input()

    if str.lower(auto_man[0]) == 'a':
        columns = choose_columns.auto_detect_columns(frame1, frame2)
        break
    elif str.lower(auto_man[0]) == 'm':
        columns = choose_columns.man_detect_columns(frame1, frame2)
        break
    else:
        print("Decision not understood. Automatic or Manual.")

# Check similarities for all columns provided
start = 1
similar_cols = []
for keys in columns:
    if start:
        block = blocking.three_char_block(frame1, keys, frame2, columns[keys])
        block, similar_cols = compare.string_similarities(block, keys, columns[keys], similar_cols, frame1, frame2)
        start = 0
    else:
        block, similar_cols = compare.string_similarities(block, keys, columns[keys], similar_cols, frame1, frame2)

avg_similarities = []
for index, row in block.iterrows():
    temp = []
    for column in similar_cols:
        temp.append(row[column])
    avg_similarities.append(np.mean(temp))

block['Average Similarity'] = avg_similarities

match = block[block['Average Similarity'] >= 0.85]
match = match.drop(labels=[list(columns.keys())[0] + ' Subset'], axis=1)

non_match = block[block['Average Similarity'] < 0.85]
non_match = non_match.drop(labels=[list(columns.keys())[0] + ' Subset'], axis=1)

result = cleaning.match_frames(match, non_match, columns, frame1, frame2)
result.to_csv("result.csv")