import pandas as pd
import lifelines 
from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter


def kmftest(data,part):
    kmf = KaplanMeierFitter()
    kmf.fit(df['time'], event_observed = df['status'])
    #filter dataset on part
    dataframe = pd.read_json(data)
    dataframe = dataframe[dataframe["sex"] == part]
    #dataframe = dataframe[dataframe['part'] == part]
    #TODO: change to duration later
    T = dataframe['time']
    #TODO: chagne this key to the right dataset.
    E = dataframe['censored']
    kmf.fit(data['time'], event_observed = data['status'])
    kmf.plot_survival_function()


def cphtest(data,part):
    cph = CoxPHFitter()
    #filter dataset on part
    dataframe = pd.read_json(data)
    #TODO: change to duration later
    T = dataframe['time']
    #TODO: chagne this key to the right dataset.
    E = dataframe['censored']
    cph.fit(duration_col = T, event_col = E)
