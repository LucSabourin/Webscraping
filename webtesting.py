import pandas
from govPayScales import govPayScales, govPaySources

def loadHTML(location):
    dfs = pandas.read_html(location)
    if type(dfs) != list:
        dfs = [dfs]
    return dfs

def checkDF(dfs: dict, df):
    temp = df
    for key, dataframes in dfs.items():
        for dataframe in dataframes:
            if temp.equals(dataframe):
                    return key
    return None

if __name__ == '__main__':
    dfsMaster = {}
    for key, value in govPaySources.items():
        dfs = loadHTML(value)
        matchKey = checkDF(dfsMaster, dfs[0])
        if matchKey is None:
            dfsMaster[key] = dfs
            print(key)
        else:
            print(matchKey + ' --> ' + key)