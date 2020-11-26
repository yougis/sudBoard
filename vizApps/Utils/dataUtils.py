

class DataUtils():


    def dataCleaner(self, data):

        # convertir les types automatiquement
        data = data.convert_dtypes()

        # conversion des NA en chaine vide et en 0
        for col in data.columns.values:

            if data[col].isnull().values.any():
                try:
                    data[col].fillna('',inplace=True)
                except:
                    try:
                        data[col].fillna(0,inplace=True)
                    except:
                        pass

        return data