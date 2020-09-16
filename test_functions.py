import unittest
import ExtractData
import RegexConfig
#from ExtractData import Extract
from RegexConfig import Configuration
from unittest.mock import patch
import os.path
# We want to inherit from unittest.TestCase
# Inheriting from unittest.TestCase will give us access to a lot of different testing capabilities within that class

class TestConfig(unittest.TestCase):
    con = Configuration()
    def test_removeListDuplicates(self): # RegexConfig

        lst = [1,2,1,4,5,3,2,2,1,1,1,6,7]
        result = self.con.removeListDuplicates(lst)
        self.assertEqual(result, [1,2,4,5,3,6,7])

    def test_removeEmptyItemsDict(self): # RegexConfig 

        dct = {'a': ['test11', 'test12'], 'b': ['test21', 'test22'], 'c':[], 'd':[]}
        result = self.con.removeEmptyItemsDict(dct)
        self.assertEqual(result, {'a': ['test11', 'test12'], 'b': ['test21', 'test22']})

    def test_stringReplace(self):

        text = "__hale__tweets.json"
        result = self.con.stringReplace(text, '_tweets.json', '')
        self.assertEqual(result, '__hale_')

    def test_splitLowerText(self):

        text = "This iS a saMple tweet WiTh Upper Cased LetTers"
        result = self.con.splitLowerText(text)
        self.assertEqual(result, ['this', 'is', 'a', 'sample', 'tweet', 'with', 'upper', 'cased', 'letters'])


if __name__ == "__main__":
    
    unittest.main()
