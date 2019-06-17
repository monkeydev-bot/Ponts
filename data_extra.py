'''
reading the bridges excel files ( 1 excel file per bridge) for every excel in the directory
'''

from os import listdir
from os.path import isfile, join
import math

# *** Could someone create a directory inside our main repository with the files,
# so we can normalize the "mypath" variable ?
def compute_df(n,m,l,mypath='données_systra_kfolds\\'):
    
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # ***
    #test com

    # data is a dictionary of the following form : data['name_of_bridge'] = 'pandas_file_for_bridge'
    import pandas as pd
    data = {}
    for sheet in onlyfiles:
        data[sheet] = pd.read_excel(mypath+sheet)

    # drops all unused rows of the excel files

    for key in data:
        data[key] = data[key].dropna(how ='all')


    '''
    This is the data preparation:
    
    Our machine learning table will consist of the following columns, for each bridge:
    
    - n (parameter) columns for profil, which is a sampling of n points of the bridge to measure its height
    
    - m (parameter) columns for obstacles, which for m intervals, gives 1 if there is an object, 0 otherwise
    
    - l (parameter) columns for travelage, which for l intervals, gives the number of travelages
    '''
    
    #In capital letters, are the list of all the bridges type columns

    PROFIL = []
    OBSTACLES_BIN = []
    TRAVELAGE_NUM = []
    LONGUEUR = []
    TYPE_texte=[] #type de pont dans le titre des excels, par exemple F12
    liste_type_pont=[]#énumère les types de ponts possibles
    for i in range(5,len(data)):
        teste = data[onlyfiles[i]]
        teste.columns = ['longueur','profil','obstacles','travelage']
        
        #travelage num
        longueur = teste['longueur'][3]
        LONGUEUR.append([longueur])
        # reduction of column number
        positions = [ longueur*i/n for i in range(1,n+1) ]
        profil = [ teste['profil'][int(math.ceil(s) + 2) ] for s in positions]
        #determiner le type
        titre=onlyfiles[i]
        k=6 #tous les fichiers finissent par les 6 mêmes dernières lettres, pas besoin de les comparer
        type_pont=''
        while titre[-k]!='F'or k>10:
            type_pont=titre[-k]+type_pont
            k+=1
        type_pont=titre[-k]+type_pont
        if type_pont not in liste_type_pont:
            liste_type_pont.append(type_pont)
        TYPE_texte.append(type_pont)
        # obstacle binaries
        obstacles_bin = [ 0 for i in range(m)]
        obstacles = []
        for s in teste['obstacles']:
            if type(s) == float and s > 0:
                obstacles.append(s)
        c = 0
        for i in range(m):
            for s in obstacles:
                if s < longueur*(i+1)/m and s > longueur*i/m:
                    c = (c + 1) % 2
                    obstacles_bin[i] = 1
            if c == 1:
                obstacles_bin[i] = 1
        travelage_num = [ 0 for i in range(l)]
        travelage = []
        for s in teste['travelage']:
            if type(s) == float and s > 0:
                travelage.append(s)
        for i in range(len(travelage)-1):
            travelage[i+1] = travelage[i+1] + travelage[i]
        for i in range(l):
            for s in travelage:
                if s < longueur*(i+1)/l and s > longueur*i/l:
                    travelage_num[i] = travelage_num[i] + 1
        PROFIL.append(profil)
        OBSTACLES_BIN.append(obstacles_bin)
        TRAVELAGE_NUM.append(travelage_num)

    import numpy as np
    #Passage type_texte vers entier
    nbr_type_pont=len(liste_type_pont)
    h=len(TYPE_texte)
    TYPE_int=np.zeros(h)
    for i in range(len(TYPE_texte)):
        k=liste_type_pont.index(TYPE_texte[i])
        TYPE_int[i]=k
        
    # Function to correctly create an empty dataframe with specified data type

    def df_empty(columns, dtypes, index=None):
        assert len(columns)==len(dtypes)
        df = pd.DataFrame(index=index)
        for c,d in zip(columns, dtypes):
            df[c] = pd.Series(dtype=d)
        return df
    
    #Creates column names
    
    type_name=['type_nom']
    type_int=['type_int']
    profil_name = [ 'p{}'.format(i) for i in range(n)]
    obstacles_name = [ 'o{}'.format(i) for i in range(m)]
    travelage_name = [ 't{}'.format(i) for i in range(l)]
    longueur_name = ['longueur']
    columns = type_name+type_int+longueur_name + profil_name + obstacles_name + travelage_name

    df = df_empty(columns, dtypes=[str,int]+[float for i in range(1+l+n+m)])
    # For each bridge, we insert it in our final table

    for i,data in enumerate(zip(TYPE_texte,TYPE_int,LONGUEUR,PROFIL,OBSTACLES_BIN,TRAVELAGE_NUM)):
        row = [data[0]] + [data[1]] + data[2] + data[3]+ data[4]+ data[5]
        df.loc[i] = row

    '''
    Each df_i attempts to predict (l = 5) with a given data,
    if there is going to be a travelage in a specific range of the bridge
    '''
    return df
