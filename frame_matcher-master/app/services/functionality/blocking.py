#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import pandas as pd
import string
import os
from pathlib import Path, PurePath

def three_char_block(frame_1, col1, frame_2, col2):
    """
    Combines both frames into a single frame with blocks based on first 3 characters of chosen column.
    :param frame_1: First frame (pandas DataFrame)
    :param col1: First frame column name to be used for blocking (String)
    :param frame_2: Second frame (pandas DataFrame)
    :param col2: Second frame column name to be used for blocking (String)
    :return: Combined frame with blocking (pandas DataFrame)
    """
    try:
        frame_1[col1 + ' Subset'] = frame_1[col1].apply(lambda x: x[0:3])
        frame_2[col1 + ' Subset'] = frame_2[col2].apply(lambda x: x[0:3])
    except TypeError:
        frame_1[col1 + ' Subset'] = frame_1[col1].astype(str).apply(lambda x: x[0:3])
        frame_2[col1 + ' Subset'] = frame_2[col2].astype(str).apply(lambda x: x[0:3])

    fuzzy_blocking = frame_1.merge(frame_2, how='outer', on=col1 + ' Subset', suffixes=('_A', '_B'))

    return fuzzy_blocking.drop(labels=col1 + ' Subset', axis=1)  

def one_char_block(frame_1, col1, frame_2, col2):
    """
    Combines both frames into a single frame with blocks based on first 3 characters of chosen column.
    :param frame_1: First frame (pandas DataFrame)
    :param col1: First frame column name to be used for blocking (String)
    :param frame_2: Second frame (pandas DataFrame)
    :param col2: Second frame column name to be used for blocking (String)
    :return: Combined frame with blocking (pandas DataFrame)
    """
    try:
        frame_1[col1 + ' Subset'] = frame_1[col1].apply(lambda x: x[0])
        frame_2[col1 + ' Subset'] = frame_2[col2].apply(lambda x: x[0])
    except TypeError:
        frame_1[col1 + ' Subset'] = frame_1[col1].astype(str).apply(lambda x: x[0])
        frame_2[col1 + ' Subset'] = frame_2[col2].astype(str).apply(lambda x: x[0])    

    fuzzy_blocking = frame_1.merge(frame_2, how='outer', on=col1 + ' Subset', suffixes=('_A', '_B'))

    return fuzzy_blocking.drop(labels=col1 + ' Subset', axis=1)


def zipcode_block(frame_1, col1, frame_2, col2):
    """
    Combines both frames into a single frame with blocks based on first 3 digits of the zipcode column.
    :param frame_1: First frame (pandas DataFrame)
    :param col1: First frame column name to be used for blocking (String)
    :param frame_2: Second frame (pandas DataFrame)
    :param col2: Second frame column name to be used for blocking (String)
    :return: Combined frame with blocking (pandas DataFrame)
    """
    frame_1[col1 + ' Subset'] = frame_1[col1].apply(lambda x: str(x)[0:3])
    frame_2[col1 + ' Subset'] = frame_2[col2].apply(lambda x: str(x)[0:3])

    fuzzy_blocking = frame_1.merge(frame_2, how='outer', on=col1 + ' Subset', suffixes=('_A', '_B'))

    return fuzzy_blocking.drop(labels=col1 + ' Subset', axis=1)

def region_blocking(frame_1, col1, frame_2, col2):
    # frame_2.rename(columns={col2: col1}, inplace=True)
    fuzzy_blocking = frame_1.merge(frame_2, how='outer', left_on= col1, right_on=col2, suffixes=('_A', '_B'))
    
    return fuzzy_blocking#.drop(labels=[col1, col2], axis=1, errors='ignore')

def address_blocking(frame_1, col1, frame_2, col2):
    """Creates blocking based off the State found in a full address
    
    Arguments:
        frame_1 {pandas DataFrame} -- First frame given by user
        col1 {string} -- Name of column from first frame with addresses
        frame_2 {pandas DataFrame} -- Second frame given by user
        col2 {string} -- Name of column from second frame with addresses
    
    Returns:
        pandas DataFrame -- Returns blocked frame on states
    """
    script_dir = os.path.dirname(__file__)
    rel_path = 'data/states.csv'
    path = os.path.join(script_dir, rel_path)
    states = pd.read_csv(path)
    caps_set = set(states['caps'].values)
    caps_list = list(states['caps'].values)
    abv_set = set(states['abbreviation'].values)
    abv_list = list(states['abbreviation'].values)

    frame_1['abv'] = frame_1[col1].apply(state_finder, args=(caps_set, caps_list, abv_set, abv_list))
    frame_2['abv'] = frame_2[col2].apply(state_finder, args=(caps_set, caps_list, abv_set, abv_list))

    fuzzy_blocking = frame_1.merge(frame_2, how='outer', on='abv', suffixes=('_A', '_B'))
    frame_1.drop(labels='abv', axis=1, inplace=True)
    frame_2.drop(labels='abv', axis=1, inplace=True)
    return fuzzy_blocking.drop(labels='abv', axis=1, errors='ignore')


def standardize_state(column):
    """Standardizes states to abbreviation format.
    
    Arguments:
        column {pandas Series} -- Series containing states
    
    Returns:
        pandas Series -- Series containing states, all in abbreviation or in same format as before if weren't succesfully converted.
    """
    script_dir = os.path.dirname(__file__)
    rel_path = 'data/states.csv'
    path = os.path.join(script_dir, rel_path)
    states = pd.read_csv(path)
    states = states[['caps', 'abbreviation']]

    return column.map(lambda st: state_conversion(st, states))


def state_conversion(state, states):
    """Converts a state into an abbreviation of itself.
    
    Arguments:
        state {String} -- State
        states {pandas DataFrame} -- pandas DataFrame containing state names and their abbreviations
    
    Returns:
        String -- State in abbreviation or same as inputted if not converted.
    """
    if not states[states['caps'].isin([state.upper()])].empty:
        return states[states['caps'].isin([state.upper()])]['abbreviation'].values[0]
    elif not states[states['abbreviation'].isin([state.upper()])].empty:
        return states[states['abbreviation'].isin([state.upper()])]['abbreviation'].values[0]
    else:
        return state

def state_finder(address, caps_set, caps_list, abv_set, abv_list):
    """Finds the state within a full address and returns its abbreviation
    
    Arguments:
        address {string} -- A full address (street, city, state and possibly zip code)
        caps_set {set} -- Set of all state names in caps
        caps_list {list} -- List of all state names in caps
        abv_set {set} -- Set of abbreviation for all states
        abv_list {list} -- List of abbreviation for all states
    
    Returns:
        string -- State abbreviation
    """
    s = address.translate(str.maketrans(string.punctuation, "".join([' ' for x in range(32)]))).upper()
    s = s.split()
    s = set(s)
    res = s.intersection(caps_set)
    if len(res) == 1:
        index = caps_list.index(res.pop())
        return abv_list[index]
    else:
        res = s.intersection(abv_set)
        return res.pop() 
