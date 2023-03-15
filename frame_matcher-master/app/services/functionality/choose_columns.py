#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import pandas as pd

def man_detect_columns(frame_1, frame_2):
    """
    While loop providing user option to manually choose matching columns.
    :param frame_1: First frame (pandas DataFrame)
    :param frame_2: Second frame (pandas DataFrame)
    :return: Pairs of column names matched from each frame (Dictionary of Strings)
    """
    matching_columns = {}
    while True:
        print("Columns in the first frame:", frame_1.drop(labels=['Source 1', 'Source 2'], axis=1, errors='ignore').columns.values)
        print("Columns in the second frame:", frame_2.drop(labels=['Soure 1', 'Source 2'], axis=1, errors='ignore').columns.values)

        col1 = input("Choose a column from the first frame to match: \n")
        if col1 not in frame_1.columns.values:
            print(col1, "does not exist in the first frame.")
            continue
        else:
            while True:
                col2 = input("Choose a column from the second frame to match to " + col1 + " in the first: \n")
                if col2 in frame_2.columns.values:
                    col1_index = frame_1.columns.get_loc(col1)
                    col2_index = frame_2.columns.get_loc(col2)
                    matching_columns[col1] = col2
                    break
                else:
                    print(col2, "does not exist in the second frame.")

        print("Do you want to match more columns? (Yes/No)")
        answer = input()
        if str.lower(answer[0]) == 'n':
            break
    
    return matching_columns


def auto_detect_columns(frame_1, frame_2):
    """
    Auto Detects Matching Columns.
    Currently only skeleton code.
    :param frame_1: First frame (pandas DataFrame)
    :param frame_2: Second frame (pandas DataFrame)
    :return: Pairs of column names matched from each frame (Dictionary of Strings)
    """
    return 0
