from django.utils import timezone

vizInstancesList = []
vizInstancesSessionsList=[]


def clearInstances():
    vizInstancesList.clear()
    vizInstancesSessionsList.clear()

def clearInstancesForSession(session):
    instances = [inst for inst in vizInstancesSessionsList if inst[1] == session]
    for inst in instances:
        vizInstance = getVizAppInstancesById(inst[0])
        if vizInstance in vizInstancesList:
            vizInstancesList.remove(vizInstance)
            vizInstancesSessionsList.remove(inst)


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
    timeCreate = timezone.now()
    instance = getVizAppInstancesById(id)
    if instance:
        vizInstancesSessionsList.append((id, session,timeCreate))
    return None

def getVizAppInstancesByVizEntityAndSessionId(vizId, sessionId):
    instancesSession = getVizAppInstancesBySessionId(sessionId)
    instances = []
    if instancesSession:
        for inst in instancesSession:
            if inst.id == vizId:
                instances.append(inst)
    if len(instances) == 1:
        return instances[0]
    elif len(instances) > 1:
        return instances
    return None

def getVizByTraceIdAndSessionId(traceId, sessionId):
    instancesSession = getVizAppInstancesBySessionId(sessionId)
    instances = []
    for inst in instancesSession:
        for trace in inst.traces:
            if trace.id == traceId:
                instances.append(inst)
    if len(instances)>=1:
        return instances
    return None

def getExpiredSession(duration):
    instance = [inst for inst in vizInstancesSessionsList if inst[3] == duration]


