
vizInstancesList = []
vizInstancesSessionsList=[()]

def getVizAppInstancesById(ident):
    instance = [inst for inst in vizInstancesList if id(inst) == ident]
    if len(instance)>=1:
        return instance[0]
    return None

def getVizAppInstancesBySessionId(sessionId):
    instances = [inst for inst in vizInstancesList if inst._session == sessionId]
    if len(instances)>=1:
        return instances
    return None

def setVizAppInstancesSessionfromId(id, session):
    instance = getVizAppInstancesById(id)
    if instance:
        vizInstancesSessionsList.append((id, session))
    return None

