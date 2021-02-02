from intake_sql import SQLSourceManualPartition, SQLSourceAutoPartition
from cartopy import crs

from intake_geopandas import PostGISSource
import yaml

postgisAgb = PostGISSource(uri = 'postgresql://admsig@pgsql2-prod.province-sud.prod:5432/ddr',
                        sql_expr='select * from agb.autorisation_ouvrage_eau',
                        table='agb.autorisation_ouvrage_eau',
                        geopandas_kwargs=None,
                        metadata=None)

postgisAgb.name = 'geom_autorisation_ouvrage_eau'
postgisAgb.description = 'Donnée spatiale Autorisation d\'ouvrage eau'

postgisAgb.metadata['plots'] = {'graphique_default':
                              {
                                  'tiles' :'EsriTerrain',
                                  'hover_cols':'all',
                                  'projetction':crs.GOOGLE_MERCATOR,
                                  'height': 600,
                               }
                          }

pg = SQLSourceManualPartition(uri='postgresql://admsig@pgsql2-prod.province-sud.prod:5432/ddr',
                              sql_expr='select * from agb.autorisation_ouvrage_eau',
                              where_values=[[0,100],[100,"(SELECT count(*) FROM agb.autorisation_ouvrage_eau)"]],
                              where_template='WHERE id >= {} AND id < {}')


with open(r'vizApps/services/intake/catalog_manual_partitionning.yml', 'w') as file:
    yaml.dump(pg._yaml(with_plugin=True), file)


agb1 = SQLSourceAutoPartition(uri='postgresql://admsig@pgsql2-prod.province-sud.prod:5432/ddr',
                            table='autorisation_ouvrage_eau',
                            index='id',
                            sql_kwargs={'schema':'agb'})
agb1.name ='autorisation_ouvrage_eau'
agb1.description = 'Autorisation d\'ouvrage eau'
#agb1.metadata['plot'] = {'datashade': True}
agb1.metadata['plots'] = {'graphique_default':
                              {
                                  'kind':'scatter',
                                  'x':"Type ouvrage",
                                  'y':"Débit de prélèvement  maximum autorisé m3/J",
                                  'height': 600,
                               }
                          }


agb2= SQLSourceAutoPartition(uri='postgresql://admsig@pgsql2-prod.province-sud.prod:5432/ddr',
                            table='parcelle_fruits_prioritaires',
                            index='identifiant',
                            sql_kwargs={'schema':'agb', 'columns':[
                                'id',
                                'statut',
                                'date_realisation',
                                'production',
                                'etiquette',
                                'exploitation',
                                'surface_estimee',
                                'coeff_technicite',
                                'variete',
                                'nombre',
                                'paturage',
                                'aide',
                                'faire_valoir',
                                'certification_bio'
                                #'date_plantation',
                                #'date_recolte'
                            ]}
                             )

agb2.name = 'parcelle_fruits_prioritaires'
agb2.description = 'Parcelle fruits prioritaires'
#agb2.metadata['plot'] = {'datashade': True}
agb2.metadata['plots'] = {'graphique_default':
                              {'kind':'scatter',
                               'x':"aide",
                               'y':"nombre",
                               'by':'etiquette',
                               #'groupby':'etiquette',
                               'cmap':'Category20',
                               'alpha':0.5,
                               'height': 600,
                               'width':600
                               }
                          }

pg = [agb1,agb2]

with open(r'vizApps/services/intake/catalog.yml', 'w') as file:
    yaml.dump({'sources': {**postgisAgb._yaml(with_plugin=True)['sources'],**agb1._yaml(with_plugin=True)['sources'], **agb2._yaml(with_plugin=True)['sources']}}, file)

