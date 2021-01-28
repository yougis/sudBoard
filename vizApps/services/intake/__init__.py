from intake_sql import SQLSourceManualPartition, SQLSourceAutoPartition
import yaml

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

agb2= SQLSourceAutoPartition(uri='postgresql://admsig@pgsql2-prod.province-sud.prod:5432/ddr',
                            table='parcelle_fruits_prioritaires',
                            index='identifiant',
                            sql_kwargs={'schema':'agb', 'columns':['id','statut_code','nombre','paturage','aide']}

                            )

agb2.name = 'parcelle_fruits_prioritaires'
agb2.description = 'Parcelle fruits prioritaires'
pg = [agb1,agb2]

with open(r'vizApps/services/intake/catalog_demo.yml', 'w') as file:
    yaml.dump({'sources': {**agb1._yaml(with_plugin=True)['sources']}}, file)

with open(r'vizApps/services/intake/catalog_1.yml', 'w') as file:
    yaml.dump({'sources': {**agb2._yaml(with_plugin=True)['sources']}}, file)

with open(r'vizApps/services/intake/catalog.yml', 'w') as file:
    yaml.dump({'sources': {**agb1._yaml(with_plugin=True)['sources'], **agb2._yaml(with_plugin=True)['sources']}}, file)