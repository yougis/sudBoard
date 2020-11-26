import json
import param



class DicoUtils():

    def excludingkeys(self, dico ,excludingKey):
        return {x: dico[x] for x in dico  if x not in excludingKey}



class ParamsUtils():

    def recursiveParamToJsonDict(self, parameters):
        dic = dict(parameters)
        for key, elem in dic.items():
            if type(elem).__class__ == param.Parameterized.__class__:
                subDic = self.recursiveParamToJsonDict(self, parameters=elem.param.get_param_values())
                dic[key] = subDic
        return dic



    def jsonParamsContructor(self,dictionnary):
        this=self
        result_dict = []
        for x in dictionnary:
            tupleVal = (x, dictionnary[x])
            if type( dictionnary[x])!=list:
                result_dict.append(tupleVal)
            else:
                tupleVal = (tupleVal[0],(tupleVal[1][0],tupleVal[1][1]))
                result_dict.append(tupleVal)
        return result_dict

