import numpy as np
import pandas as pd



def split_dataframe_x_y(df,l,m,n,type_or_travellage):
    '''

    This function takes as an argument a dataframe
    and splits into a variable table and a target vector

    :param df:
    :return: two arguments, a dataframe and a vector
    '''
    
    x = df[df.columns[2:2+1+n+m]]
    if type_or_travellage=='type':
        y=df[df.columns[0:2]]
    else: #ie travellage
        y = df[df.columns[-l:]]
    return x,y
    
    