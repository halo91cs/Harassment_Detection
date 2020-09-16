#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

class Configuration():
    # Not needed at this time.

    #x = "(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z0-9-_]+[A-Za-z0-9-_]+)"
    #y = "RT @[A-Za-z0-9-_]+"
    #url = '"(?P<url>https?://[^\s]+)"'
    
    #def getMentioned(self, text):
    #    return re.compile(self.x)
    
    #def getRetweeted(self):
    #    return re.compile(self.y)

    #def getUrl(self, text):
    #    return re.search(self.url, text)

    def removeListDuplicates(self, lst):
        return list(dict.fromkeys(lst))

    def removeEmptyItemsDict(self, dct):
        return {k: v for k, v in dct.items() if v != []}
    
    def stringReplace(self, text, replaced, replaced_with):
        return text.replace(replaced, replaced_with)

    def splitLowerText(self, text):
        return text.lower().split()
       

