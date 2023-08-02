from textwrap import indent
import pandas as pd
#from unidecode import unidecode

from cleanUpDataframe import *
from htmlWork import *
from payScaleWork import govPayCodes

import os
import json

#### TO DO:
####    -> Fix Removal of Empty Columns -> Done
####    -> Pull and Merge Multiple Tables
####    -> Verify ALL codes are being pulled (and see what can be done if not)
####    -> Fix clean up of 'Key' for tables
####    -> Cache routing to tables to speed up process (so you don't have to retrieve everything each time)
####    -> Work on Filter to return specific values based on search parameters
####    -> Update TO DO list when done above.

#### NICE TO HAVE
####    -> Fix separation of last row/notes/table footer -> OP and PG do not have them being removed, not sure why.
####    -> Split 'Range' Steps -> Done

def cleanUpFiles():
    """Removes old files since files will have contents appended rather than
    overwritten.
    """

    try:
        os.remove('PayScaleLinks.json')
    except:
        print('Could not remove "PayScaleLinks.json"')

    try:
        os.remove('PayScaleTables.json')
    except:
        print('Could not remove "PayScaleTables.json"')

    try:
        os.remove('FoundCodes.json')
    except:
        print('Could not remove FoundCodes.json')
        
if __name__ == '__main__':
    cleanUpFiles()
    mainUrl = 'https://www.tbs-sct.gc.ca/pubs_pol/hrpubs/coll_agre/rates-taux-eng.asp'
    mainFilterValue = 'https://www.tbs-sct.gc.ca/agreements-conventions/view-visualiser-eng.aspx?'

    govPayScaleLinks = extractMainPageHrefs(mainUrl, mainFilterValue)
    
    govPayScales = {}
    govPayTables = {}
    foundCodes = {}

    for key, value in govPayScaleLinks.items():
        #govPayScales[key] = value
        tables = extractTablesWithCaptions(url=value['href'], filter=[value['codes'], 'pay'])
        
        captionsAll = [captions for captions in tables.keys()]
        foundCodes[key] = captionsAll

        govPayScaleLinks[key]['captions'] = {}
        for code in govPayScaleLinks[key]['codes']:
            captions = [caption for caption in captionsAll if code in caption]
            if len(captions) > 0:
                govPayScaleLinks[key]['captions'][code] = captions
                captionsAll = [caption for caption in captionsAll if caption not in captions]
        if len(captionsAll) > 0:
            govPayScaleLinks[key]['captions']['other'] = captionsAll

        govPayScaleLinks[key]['missing'] = []
        for code in govPayScaleLinks[key]['codes']:
            keys = [keyCode for keyCode in govPayScaleLinks[key]['captions'].keys()]
            if code not in keys and 'other' not in keys:
                govPayScaleLinks[key]['missing'].append(code)

        #govPayScales[key]['tables'] = tables

        govPayTables[key] = {}

        for keyTable, value in tables.items():
            data = json.loads(value['Table'].to_json(orient='records', indent=4))
            govPayTables[key][keyTable] = {}
            govPayTables[key][keyTable]['Table'] = data
            try:
                govPayTables[key][keyTable]['Notes'] = value['Notes']
            except:
                govPayTables[key][keyTable]['Notes'] = None

    #print(govPayScaleLinks)

    with open('PayScaleLinks.json', 'w', encoding="utf-8") as f:
        json.dump(govPayScaleLinks, f, indent=4)
    with open('PayScaleTables.json', 'w', encoding="utf-8") as f:
        json.dump(govPayTables, f, indent=4)
    with open('FoundCodes.json', 'w', encoding="utf-8") as f:
        json.dump(foundCodes, f, indent=4)
