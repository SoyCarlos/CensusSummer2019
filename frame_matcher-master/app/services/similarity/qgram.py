# Copyright (c) 2018 luozhouyang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from .shingle_based import ShingleBased
from .string_distance import StringDistance
from itertools import chain



class QGram(ShingleBased, StringDistance):

    def __init__(self, k=2):
        super().__init__(k)

    def distance(self, s0, s1):
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 0.0

        profile0 = self.get_profile(s0)
        profile1 = self.get_profile(s1)
        return self.distance_profile(profile0, profile1)

    
    def similarity(self, s0, s1):
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 1

        profile0 = self.get_profile(s0)
        profile1 = self.get_profile(s1)
        expanded0 = self.expand(profile0)
        expanded1 = self.expand(profile1)
        intersection = self.intersection(expanded0, expanded1)
        print(intersection)
        # return len(intersection) / (len(expanded0) + len(expanded1) - len(intersection))
        if min(len(expanded0), len(expanded1)) == 0:
            return len(intersection) / max(len(expanded0), len(expanded1)), intersection
        else:
            print("here")
            return len(intersection) / min(len(expanded0), len(expanded1)), intersection
    
    @staticmethod
    def expand(dictionary):
        res=[[list(dictionary.keys())[i]] * list(dictionary.values())[i] for i in range(len(dictionary.keys()))]
        return list(chain.from_iterable(res))
    
    @staticmethod
    def intersection(lst1, lst2): 
        lst3 = [value for value in lst1 if value in lst2] 
        lst4 = [value for value in lst2 if value in lst1] 
        if len(lst3) > len(lst4):
            return lst4
        else:
            return lst3

    @staticmethod
    def distance_profile(profile0, profile1):
        union = set()
        for k in profile0.keys():
            union.add(k)
        for k in profile1.keys():
            union.add(k)
        agg = 0
        for k in union:
            v0, v1 = 0, 0
            if profile0.get(k) is not None:
                v0 = int(profile0.get(k))
            if profile1.get(k) is not None:
                v1 = int(profile1.get(k))
            agg += abs(v0 - v1)
        return agg
    
    @staticmethod
    def similarity_profile(profile0, profile1):
        union = set()
        for k in profile0.keys():
            union.add(k)
        for k in profile1.keys():
            union.add(k)
        agg = 0
        for k in union:
            v0, v1 = 0, 0
            if profile0.get(k) is not None:
                v0 = int(profile0.get(k))
            if profile1.get(k) is not None:
                v1 = int(profile1.get(k))
            agg += abs(v0 - v1)
        return agg

