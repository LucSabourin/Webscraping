from bs4 import BeautifulSoup
from numpy import double
import requests
import re

from cleanUpDataframe import cleanUpString, filterInText, dataFrameFromTable, mergeDataFrames

def extractTablesWithCaptions(url, filter, code = '') -> dict:
    """Extracts tables with captions corresponding to position codes
    and forms dataframes using those tables.

    Parameters:
    -----------
    url : str
        url containing tables with captions
    filter : str | list
        the value(s) used to filter captions

    Returns
    -------
    dict
        Dictionary of each subcategory of position (such as level) with
        subcategory as key and df of data as value layout:
            {<subcategory:str>: <df:DataFrame>}
    """

    captions = filterPage(url=url, section='caption')
    filteredCaptions = filterCaptions(captions=captions, code=code)

    tables = {}

    keptCaptions = []
    for caption in filteredCaptions:
        if filterInText(filter, caption.get_text().lower()):
            table = caption.find_parent('table')

            key = cleanUpString(caption.get_text().strip())
            keptCaptions.append(key)
            tables[key] = {}
            tables[key]['Notes'] = removeTableFooter(table)
            tables[key]['Table'] = dataFrameFromTable(table)

    tables = checkDoubleTables(tables, keptCaptions)

    return tables

def checkDoubleTables(tables: dict, keptCaptions: list) -> dict:
    """Checks tables to identify duplicate tables in a section, and merges
    tables together.

    Parameters:
    -----------
    tables: dict
        Dictionary of each subcategory of position (such as level) with
        subcategory as key and df of data as value layout:
            {<subcategory:str>: <df:DataFrame>}
    keptCaptions: list
        captions used as keys in the tables dictionary

    Returns:
    --------
    dict
        Dictionary of each subcategory of position (such as level) with
        subcategory as key and df of data as value layout:
            {<subcategory:str>: <df:DataFrame>}
    """

    doubleKeys = []
    for num, caption in enumerate(keptCaptions):
        if 'continue' in caption.lower():
            doubleKeys.append((keptCaptions[num - 1], keptCaptions[num]))

        elif 'steps' in caption.lower():
            if 'steps' in keptCaptions[num - 1].lower():
                if findStep(keptCaptions[num], True) == findStep(keptCaptions[num - 1], False) + 1 \
                    and keptCaptions[num][0:5] == keptCaptions[num - 1][0:5] \
                        and (keptCaptions[num - 1], keptCaptions[num]) not in doubleKeys:
                    doubleKeys.append((keptCaptions[num - 1], keptCaptions[num]))

            elif 'steps' in keptCaptions[num + 1].lower():
                if findStep(keptCaptions[num], False) == findStep(keptCaptions[num + 1], True) - 1 \
                    and keptCaptions[num][0:5] == keptCaptions[num + 1][0:5] \
                        and (keptCaptions[num], keptCaptions[num + 1]) not in doubleKeys:
                    doubleKeys.append((keptCaptions[num], keptCaptions[num + 1]))

    if len(doubleKeys) == 0:
        return tables

    for keyOne, keyTwo in doubleKeys:
        replacementDfs = {}
        key = keyOne
        key = key.split('Step')[0].strip()

        if '(' == key[-1]:
            key = key[0:-1]
            key.strip()

        if ',' == key[-1]:
            key = key[0:-1]
            key.strip()

        replacementDfs['Table'] = mergeDataFrames(dfOne=tables[keyOne]['Table'], dfTwo=tables[keyTwo]['Table'])
        replacementDfs['Notes'] = tables[keyOne]['Notes'] + '\n\n\n' + tables[keyTwo]['Notes']
        tables.pop(keyOne)
        tables.pop(keyTwo)
        tables[key] = {'Notes': replacementDfs['Notes'], 'Table': replacementDfs['Table']}
    
    return tables

def findStep(caption: str, first: bool) -> int:
    """
    """
    caption = caption.lower().split('steps')[-1]
    caption = caption.replace(')', '').replace(' ', '')
    caption = caption.replace('and', 'to')
    caption = caption.split('to')
    if first:
        return int(caption[0])
    else:
        return int(caption[1])
        
def filterCaptions(captions, code):
    """
    """

    if (len(captions) > 0) and (len(code) > 0):
        filteredCaptions = [caption for caption in captions if code in caption.get_text().strip()]
        if len(filteredCaptions) > 0:
            captions = filteredCaptions

    return captions

def removeTableFooter(table: BeautifulSoup) -> str:
    """Extracts footer from table, if it exists, and returns it as a string.

    Also strips footer from table so table can be converted to a dataframe.

    Parameters:
    -----------
    table: BeautifulSoup
        table from BeautifulSoup object

    Returns:
    --------
    str/None
        if a footer exists, returns footer, otherwise returns None
    """

    try:
        footer = table.tfoot
    except:
        footerClean = None
    else:
        if footer is not None:
            footerClean = cleanUpString(footer.get_text())
            table.tfoot.decompose()
        else:
            footerClean = None
    return footerClean

def filterPage(url, section, filterVariable : str = '', filterValue : str = '', findAll : bool = True) -> list:
    """Uses BeautifulSoup to extract html from a url in order to scape data.

    Can filter off a specific attribute value of a section of the html.

    Parameters:
    -----------
    url : str
        url to connected to and scraped.
    section : str
        section to be collected when scraping.
    filterVariable : str = ''
        attribute/subsection of section to be filtered when scraping.
    filterValue : str = ''
        value for filterVariable when scraping.
        Note: set up for contains, not exact match
    findAll : bool = True
        option to find and return first or find and return all html sections
        matching search parameters.

    Returns:
    --------
    list
        list of html sections matching search parameters.
        Note: if findAll = False, will return a list containing a single item.
    """

    htmlText = requests.get(url).text
    soup = BeautifulSoup(htmlText, 'lxml')
    select = {'name': section}

    if len(filterVariable) > 0 and len(filterValue) > 0:
        select[filterVariable] = re.compile(filterValue)

    if findAll:
        searched = soup.find_all(**select)
    else:
        searched = [soup.find(**select)]

    return searched

def extractMainPageHrefs(url, filterValue) -> dict:
    """Retrieves information regarding government pay scales from the main page
    published by the government, returning it as a dictionary.

    Parameters:
    -----------
    mainSource : str
        the url of the main page

    Returns:
    --------
    dict
        layout of dict is:
            {<code:str>: {'href': <href:str>, 'desc': <desc:str>}}
    """

    links = filterPage(url, 'a', 'href', filterValue)
    
    storedLinks = {}

    for link in links:
        href = extractMainHref(link['href'])
        desc = link.text
        code = link.text.split(' ')[0]

        keep = True
        for key in storedLinks.keys():
            if href == storedLinks[key]['href']:
                storedLinks[key]['desc'] += '/' + desc
                storedLinks[key]['codes'].append(code)
                keep = False
                break

        if keep:
            storedLinks[code] = {'desc': desc, 'href': href, 'codes': [code]}
    
    return storedLinks

def extractMainHref(href: str) -> str:
    """Extracts a a webpage from a webpage sections link (referenced by a '#' for section).

    Parameters:
    -----------
    href: str
        hyper reference embedded in webpage, which may have a section reference on the end

    Returns:
    --------
    str
        cleaned hyper reference
    """

    if '#' in href:
        splits = href.split('#')
        temp = ''
        for part in splits[0:-1]:
            temp += part

    else:
        temp = href

    return temp
