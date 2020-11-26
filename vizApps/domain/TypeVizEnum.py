from enum import Enum
class TypeVizEnum(Enum):
#ennumeration Publication
    BASE_MAP = 'Carte simple'
    CHOROPLETH_MAP = 'Carte choropleth'
    POINT_MAP = 'Carte cercle proportionnel'
    TABLE = 'Table'
    BAR_GRAPH = 'Graphique en barre'
    LINE_GRAPH = 'Graphique en ligne'
    POINT_GRAPH = 'Graphique de point'
    PARAM = 'Ensemble de paramettre'
