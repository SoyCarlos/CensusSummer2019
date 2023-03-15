#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import pandas as pd
import numpy as np

import math
import re

import sys


from .functionality import blocking, cleaning, file_proc, locations
from .similarity import compare, qgram
 

class frame_matcher:
    """Connects all functions to match 2 frames.
    To be used by app.py
    """
    frame1 = None
    frame2 = None
    
    block = None

    match = None 
    non_match = None

    matching_columns = {} 
    data_types = {}
    
    def __init__(self):
        """Initializes all variables
        """
        frame1 = None
        frame2 = None

        block = None

        match = None
        non_match = None

        matching_columns = {}
        data_types = {}

        print('Frame Matcher Initialized')
    
    def define_frames(self, file, filename, digit):
        """Passes in file from application and assigns them to appropriate frame.
        
        Arguments:
            file {FileStorage} -- File passed in by user to web app.
            filename {string} -- Name of the file, used to determine type.
            digit {int} -- Frame #. Used to assign file to correct frame.
        """
        if digit == 1:
            self.frame1 = file_proc.read_frame(file, file_proc.get_file_type(filename))
            self.frame1.rename(columns={col: col + " ("+ filename + " - Frame 1)" for col in self.frame1.columns}, inplace=True)
            self.frame1 = self.frame1.reset_index().rename(columns={'index': 'Frame1_Index'})
        elif digit == 2:
            self.frame2 = file_proc.read_frame(file, file_proc.get_file_type(filename))
            self.frame2.rename(columns={col: col + " ("+ filename + " - Frame 2)" for col in self.frame2.columns}, inplace=True)
            self.frame2 = self.frame2.reset_index().rename(columns={'index': 'Frame2_Index'})

    def choose_columns(self, column_1, column_2, data_type):
        """Chooses columns to create blocking on and starts actual matching.
        
        Arguments:
            column_1 {String} -- Column from frame1 matching the others.
            column_2 {String} -- Column from frame2 matching the others.
            data_type {String} -- Specifies data type, check app.py for details
        """
        self.matching_columns[column_1] = column_2
        self.data_types[data_type] = column_1

    def check_similarities(self):
        """Creates blocked frame and passes on to similarity calculation funcs.
        
        Returns:
            pandas DataFrame -- Frame with similarity score
        """
        del(self.matching_columns["None"])
        
        if 'zip' in self.data_types.keys():
            sub = self.data_types.get('zip')
            self.block = blocking.zipcode_block(
                self.frame1, 
                self.data_types.get('zip'), 
                self.frame2, 
                self.matching_columns.get(self.data_types.get('zip')))
        elif 'city' in self.data_types.keys():
            sub = self.data_types.get('city')
            self.block = blocking.region_blocking(
                self.frame1, 
                self.data_types.get('city'), 
                self.frame2, 
                self.matching_columns.get(self.data_types.get('city')))
        elif 'state' in self.data_types.keys():
            sub = self.data_types.get('state')
            st1 = self.data_types.get('state')
            st2 = self.matching_columns.get(self.data_types.get('state'))
            self.frame1[st1] = blocking.standardize_state(self.frame1[st1])
            self.frame2[st2] = blocking.standardize_state(self.frame2[st2])
            self.block = blocking.region_blocking(
                self.frame1, 
                st1, 
                self.frame2, 
                st2)
        elif 'state_abv' in self.data_types.keys():
            sub = self.data_types.get('state_abv')
            self.block = blocking.region_blocking(
                self.frame1, 
                self.data_types.get('state_abv'), 
                self.frame2, 
                self.matching_columns.get(self.data_types.get('state_abv')))
        elif 'id' in self.data_types.keys():
            pass
        elif 'add' in self.data_types.keys():
            sub = self.data_types.get('add')
            self.block = blocking.address_blocking(
                self.frame1, 
                self.data_types.get('add'), 
                self.frame2, 
                self.matching_columns.get(self.data_types.get('add')))
        else:
            sub = list(self.matching_columns.keys())[0]
            self.block = blocking.one_char_block(
                self.frame1,
                list(self.matching_columns.keys())[0],
                self.frame2,
                self.matching_columns.get(list(self.matching_columns.keys())[0])
            )
        for key,value in self.matching_columns.items():
            try:
                if self.block[key].dtype == 'O' and self.block[value].dtype == 'O':
                    self.block[key + ' Similarity'] = compare.qgram_comparison(self.block[key], self.block[value])
            except KeyError:
                key_ = key
                val_ = value
                if key in self.frame2.columns:
                    key_ = key + "_A"
                if value in self.frame1.columns:
                    val_ = value + "_B"
                if self.block[key_].dtype == 'O' and self.block[val_].dtype == 'O':
                    print("hacked the mainframe")
                    self.block[key + ' Similarity'] = compare.qgram_comparison(self.block[key_], self.block[val_])
        return self.matches(sub=sub)
    
    def calculate_similarity(self):
        """Takes the blocked frame and calculates the average similarity based on already calculated similarities per row.
        
        Returns:
            pandas Series -- [Pandas Series of the average similarity
        """
        sim_cols = [x for x in self.block.columns if " Similarity" in x]
        only_sim = self.block[sim_cols]

        return only_sim.apply(np.mean, axis=1)
        
    
    def matches(self, sub, thresh=0.80):
        """Splits up block into matches and non-matches depending on similarity scores.
        
        Keyword Arguments:
            thresh {float} -- User or default required threshold to determine similarity. (default: {0.80})
        """
        self.block['Average Similarity'] = self.calculate_similarity()

        self.match = self.block[self.block['Average Similarity'] >= thresh]

        self.non_match = self.block[self.block['Average Similarity'] < thresh]

        return cleaning.match_frames(self.match, self.non_match, self.matching_columns, self.frame1, self.frame2, sub)
