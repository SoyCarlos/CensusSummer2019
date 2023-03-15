#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import pandas as pd

def ln_fn(name):
    """
    Takes in a name in format Lastname, Firstname and changes it to Firstname Lastname.
    :param name: A name (String)
    :return: A name (String)
    """
    name = name.replace(",", " ")
    split = name.split(" ")
    return split[-1] + " " + split[0]


def standardize_names(names):
    """
    Takes in a list or series of names and standardizes them into Firstname Lastname format.
    :param names: List of names (List or pandas Series)
    :return: List of names (List or pandas Series)
    """
    for i in range(len(names)):
        if "," in names[i]:
            names[i] = ln_fn(names[i])
    return names

def clear_duplicates(match_frame, non_match_frame, source):
    """
    Removes all rows from non_match_frame that have found a match in match_frame.
    :param match_frame: Frame with all matches (pandas DataFrame)
    :param non_match_frame: Frame with no matches (pandas DataFrame)
    :param source: Column name for Source, e.g. 'Source 1' (String)
    :return: Returns non_match_frame with rows in match_frame removed (pandas DataFrame)
    """
    non_match_frame = non_match_frame[~non_match_frame[source].isin(match_frame[source])]
    return non_match_frame


def match_frames(match_frame, non_match_frame, matching_columns, frame_1, frame_2, sub):
    """
    Combines frame with matches and no matches into a single frame.
    :param match_frame: Frame with matches (pandas DataFrame)
    :param non_match_frame: Frame with no matches (pandas DataFrame)
    :param matching_columns: Dictionary of pairs of column names that match (Dictionary of Strings)
    :param frame_1: Original first frame (pandas DataFrame)
    :param frame_2: Original second frame (pandas DataFrame)
    :return: Returns the final result for the combination of all matches and non-matches (pandas DataFrame)
    """
    final = match_frame
    final['one'] = final.duplicated("Frame1_Index")
    final['one'] = final['one'].replace(False, "").replace(True, "Frame 1 Duplicate ")
    final['two'] = final.duplicated("Frame2_Index")
    final['two'] = final['two'].replace(False, "").replace(True, "Frame 2 Duplicate")
    final['Flag'] = final['one'] + final['two']
    final.drop(labels=['one', 'two'], axis = 1, inplace=True)

    sim = sub 
    temp1 = frame_1.drop(labels=sim + ' Subset', errors='ignore', axis=1)
    temp2 = frame_2.drop(labels=sim + ' Subset', errors='ignore', axis=1)
    keep_s1 = [col if col not in frame_2.columns else col + '_A' for col in temp1.columns]
    non_match_s1 = non_match_frame[keep_s1].dropna(subset=['Frame1_Index'])

    keep_s2 = [col if col not in frame_1.columns else col + '_B' for col in temp2.columns]
    non_match_s2 = non_match_frame[keep_s2].dropna(subset=['Frame2_Index'])
    non_match_s1 = clear_duplicates(match_frame, non_match_s1, 'Frame1_Index')
    non_match_s2 = clear_duplicates(match_frame, non_match_s2, 'Frame2_Index')
    non_match_s1.drop_duplicates(subset=['Frame1_Index'], inplace=True)
    non_match_s2.drop_duplicates(subset=['Frame2_Index'], inplace=True)

    final = final.append(non_match_s1, ignore_index=True)
    final = final.append(non_match_s2, ignore_index=True)

    remove = [col for col in final.columns if "Similarity" in col]
    remove.remove('Average Similarity')

    final['Average Similarity'].fillna("Unmatched", inplace=True)

    final['Frame1_Index'].fillna("Unmatched", inplace=True)
    final['Frame2_Index'].fillna("Unmatched", inplace=True)


    return final.drop(labels=remove, errors='ignore', axis=1)
