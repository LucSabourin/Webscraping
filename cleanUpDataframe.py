from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pandas import DataFrame

utfCleanUp = {
    '\xa0': ' ',
    '\u2011': '-',
    '\u2010': '-',
    '\u00a0': ' ',
    '\u2013': '',
    '\u201c': '"',
    '\u201d': '"',
    '\u2019': '\'',
    '\u08ad': '"'
}

formatCleanUp = {
    '\r\n ': '\r\n',
    'note 2 /': 'note 2',
    'note 2 /': 'note 2',
    'note 3/': 'note 3'
}

def dataFrameFromTable(table: BeautifulSoup) -> DataFrame:
    """
    """

    df = pd.read_html(str(table))[0]
    
    cleanUpColumnNames(df)
    cleanUpText(df)
    cleanUpEmptyColumns(df)

    return df

def filterInText(filter, source : str):
    """
    """
    if type(filter) == str:
        if filter.lower() in source:
            return True
    elif type(filter) == list:
        for text in filter:
            if filterInText(text, source):
                return True
    return False

def addCleanColumns(df : DataFrame):
    """
    """
    cols = df.columns
    for col in cols:
        if type(col) == str:
            if ('date' in col.lower()) or ('step' in col.lower()):
                df[col.lower() + '.clean'] = np.nan

def repeatReplace(mainStr: str, origValue: str, newValue: str) -> str:
    """
    """

    while True:
        if origValue in mainStr:
            mainStr = mainStr.replace(origValue, newValue)
        else:
            break
    
    return mainStr

def cleanUpString(string: str) -> str:
    """
    """

    strTemp = string
    
    for origValue, newValue in utfCleanUp.items():
        strTemp = strTemp.replace(origValue, newValue)

    for origValue, newValue in formatCleanUp.items():
        strTemp = repeatReplace(strTemp, origValue, newValue)
    
    if 'table' in strTemp:
        strTemp = ' table'.join(strTemp.split('table'))
    strTemp = strTemp.replace('  ', ' ')
    
    return strTemp.strip()

def cleanUpColumnNames(df : DataFrame):
    """
    """
    cols = df.columns
    colsChanged = {}
    for col in cols:
        if type(col) == str:
            colsChanged[col] = cleanUpString(col)
    df.rename(columns=colsChanged, inplace=True)

def intAble(string: str) -> bool:
    """
    """
    try:
        int(string)
    except:
        return False
    else:
        return True

def cleanUpText(df : DataFrame):
    """
    """
    cols = df.columns
    for col in cols:
        dfTemp = df[col]
        for index in dfTemp.index:
            if not intAble(dfTemp.loc[index]):
                dfTemp.iloc[index] = cleanUpString(str(dfTemp.loc[index]))
        df.update(dfTemp)

def cleanUpEmptyColumns(df : DataFrame):
    """Removes empty columns from data frame if the whole column is empty
    (and so does not contain any relevant data).

    Parameters:
    -----------
    df : DataFrame
    """
    for col in df.columns:
        if (df[col].count() == 0) or ('Unnamed' in col):
            df.drop(columns=col, inplace=True)

def mergeDataFrames(dfOne: DataFrame, dfTwo: DataFrame) -> DataFrame:
    """
    """
    dfOne = addDateKey(pd.DataFrame(dfOne))
    dfTwo = addDateKey(pd.DataFrame(dfTwo))
    colsOne = dfOne.columns
    colsTwo = dfTwo.columns
    for colOne in colsOne:
        if colOne in colsTwo:
            mergeOn = colOne
            break
    df = pd.merge(dfOne, dfTwo, on=mergeOn)
    return df

def addDateKey(df: DataFrame) -> DataFrame:
    """
    """
    dfTemp = pd.DataFrame(df)
    cols = df.columns
    temp = dfTemp[cols[0]]
    
    for index in temp.index:
        refString = ''
        if 'table' in temp[index]:
            row = temp[index].split(' ')
            for num, string in enumerate(row):
                if string == 'table':
                    refString = row[num + 1]
                    break
        if len(refString) > 0:
            break
    notesName = cols[0] + ' Notes-Table ' + refString
    colsTemp = [cols[0], notesName]
    colsTemp.extend(cols[1:])
    
    dateTemp = dfTemp[cols[0]].apply(lambda x: x.split('table')[0].strip() if 'table' in x else x)
    noteTemp = dfTemp[cols[0]].apply(lambda x: 'Table ' + x.split('table')[1].strip() if 'table' in x else np.nan)
    dfTemp = dfTemp.drop(columns=cols[0])
    dfTemp = dfTemp.join(dateTemp.to_frame(name=cols[0]))
    dfTemp = dfTemp.join(noteTemp.to_frame(name=notesName))

    dfTemp = dfTemp[colsTemp]

    return dfTemp

'''

def cleanUpLastRow(df : DataFrame):
    """Remove last row if value is the same in all columns (not useful info)

    Paramters:
    ----------
    df : DataFrame
    """
    dfTemp = df.iloc[-1]
    valueTemp = ''
    same = True
    for col in df.columns[1:]:
        if 'Pay' in str(dfTemp[col]).strip():
            break
        if len(valueTemp) == 0:
            valueTemp = str(dfTemp[col]).strip()
        elif valueTemp != str(dfTemp[col]).strip():
            same = False
            break
    if same:
        df.drop(df.tail(1).index, inplace=True)

def cleanUpDates(df : DataFrame, dropLast = True) -> DataFrame:
    """Removes clutter from date columns and drop duplicate rows which do not
    contain relevant wage adjustment.

    Paramters:
    ----------
    df : DataFrame

    Returns:
    --------
    DataFrame
    """
    dfTemp = df
    col = dfTemp.columns[0]
    if 'date' not in col.lower():
        return
    dates = dfTemp[col]
    dates.rename(col.lower() + '.clean', inplace=True)
    if dropLast:
        dates.iloc[-1] = np.nan
    for index in dates.index:
        if type(dates.loc[index]) == str:
            dates.iloc[index] = dates.loc[index].lower().encode('ascii', 'ignore').decode('utf-8')
            if 'table' in dates.loc[index]:
                dates.iloc[index] = dates.loc[index].split('table')[0]
            if ')' in dates.loc[index]:
                dates.iloc[index] = dates.loc[index].split(')')[1]
            if ':' in dates.loc[index]:
                dates.iloc[index] = dates.loc[index].split(':')[1]
            if '-' in dates.loc[index]:
                temp = dates.loc[index].split('-')
                if 'wage' in temp[0].lower():
                    dates.iloc[index] = temp[1]
                else:
                    dates.iloc[index] = temp[0]
            dates.iloc[index] = dates.loc[index].replace('effective', '')
            dates.iloc[index] = dates.loc[index].replace('wage', '')
            dates.iloc[index] = dates.loc[index].replace('adjustment', '')
            dates.iloc[index] = dates.loc[index].replace(' ', '')
            dates.iloc[index] = dates.loc[index].replace('\xa0', '').strip()
    df.update(dates)
    
def fixRangeSteps(df : DataFrame) -> DataFrame:
    """
    """
    dfTemp = df
    cols = [col for col in dfTemp.columns if 'Range' in col]
    if len(cols) > 0:
        for col in cols:
            ranges = dfTemp[col]
            lower = ranges.apply(lambda x: x.split('to')[0].strip())
            upper = ranges.apply(lambda x: x.split('to')[1].strip())
            if 'Step' not in col:
                lower.rename('Step 1.0', inplace=True)
                upper.rename('Step 1.1', inplace=True)
            else:
                colTemp = col
                if 'table' in colTemp:
                    colTemp = colTemp.split('table')[0].strip()
                if '/' in colTemp:
                    colTemp = colTemp.split('/')[1].strip()
                lower.rename(colTemp + '.0', inplace=True)
                upper.rename(colTemp + '.1', inplace=True)
            dfTemp = pd.merge(dfTemp, lower, left_index=True, right_index=True)
            dfTemp = pd.merge(dfTemp, upper, left_index=True, right_index=True)
            if len(cols) == 1:
                dfCols = [col for col in dfTemp.columns]
                dfCols = [dfCols[0]] + dfCols[-2:] + dfCols[1:-2]
                dfTemp[dfCols]
                break
    return dfTemp

def cleanUpData(df : DataFrame):
    """
    """
    dfTemp = df
    cols = dfTemp.columns[1:]
    for col in cols:
        if ('Step' in col) or (('Step' not in col) and ('Range' in col)):
            for index in dfTemp.index:
                dfTemp.loc[index, col] = int(str(dfTemp.loc[index, col]).replace(',','').split('(')[0].split('table')[0].strip())
    return dfTemp
'''