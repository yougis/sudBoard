import numpy as np
import pandas as pd
from pandas_profiling import ProfileReport

class DataFrameProfile():

    def __init__(self, dataframe):
        self.dataframe = dataframe
        pass

    def describe(self):
        self.desciption = self.data.describe()
        return self.desciption

    def makeProfile(self, title="Rapport d'analyse de donnée",explorative=True, minimal=True,progress_bar=True):
        self.profile = ProfileReport(self.dataframe, title=title,explorative=explorative, minimal=minimal,progress_bar=progress_bar)
        return self.profile

    def export(self):
        return self.profile.to_file("output.html")
