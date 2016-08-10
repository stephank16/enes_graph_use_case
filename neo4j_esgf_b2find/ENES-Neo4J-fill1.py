
# coding: utf-8

# # ENES use case graph example


# Fill database with data-hierarchy from ENES metadata index queries
# stop above file level (otherwise graph gets too large)
# all graph related use cases can probably handled above file granularity
# walk through the hierarchical data tree 
# later this could be improved by bulk upload mechanisms e.g. from replica db dump

from enes_settings import *


from py2neo import authenticate, Node, Relationship, Graph
authenticate("localhost:7474", 'neo4j', 'prolog16')
graph = Graph("http://localhost:7474/db/data/")

from pyesgf.search import SearchConnection
#SEARCH_SERVICE = 'http://pcmdi9.llnl.gov/esg-search'
SEARCH_SERVICE = 'http://esgf-data.dkrz.de/esg-search'
conn = SearchConnection(SEARCH_SERVICE,distrib=True)
project = u'CMIP5'
ctx = conn.new_context(project=project,replica=True,latest=True)
project_node = Node("Collection",name='cmip5',level=10, identifier = 'project')

try:
    products 
except NameError: 
    products = conn.new_context(project=project,replica=True,latest=True).facet_counts['product'].keys()
    
for product in products:
    product_node = Node("Collection",name=product, level=9)
    rel = Relationship(product_node,"belongs_to",project_node)
    graph.create(rel)
#for institute in facet_counts['institute']:
print products
try:
    institutes
except NameError:   
    print "...................................."
    institutes = conn.new_context(project=project,product=product,replica=True,latest=True).facet_counts['institute'].keys()
 
print "Institutes:",institutes
for institute in institutes:
     institute_node = Node("Collection",name='cmip5/'+institute, level=8, identifier = 'institute')
     rel = Relationship(institute_node,"belongs_to",product_node)
     graph.create(rel)
     try:
         models
     except NameError:
         models = conn.new_context(project=project,product=product,institute=institute,replica=True,latest=True).facet_counts['model'].keys()
    
     print "Models:",models 
     for model in models: 
         model_node = Node("Collection",name='cmip5/'+institute+'/'+model, level=7, identifier = 'model')
         rel = Relationship(model_node,"belongs_to",institute_node)
         graph.create(rel) 
         try: 
             experiments
         except NameError:
            experiments = conn.new_context(project=project,product=product,institute=institute,model=model,replica=True,latest=True).facet_counts['experiment'].keys()
       
         print "Experiments:", experiments
         for experiment in experiments:
            experiment_node = Node("Collection",name='cmip5/'+institute+'/'+model+'/'+experiment, level=6, identifier = 'experiment')
            rel = Relationship(experiment_node,"belongs_to",model_node)
            graph.create(rel) 
            try: 
                time_frequencies
            except NameError:
                time_frequencies = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,replica=True,latest=True).facet_counts['time_frequency'].keys()
     
            print "time_frequencies",time_frequencies
            for time_frequency in time_frequencies:
                frequency_node = Node("Collection",name='cmip5/'+institute+'/'+model+'/'+experiment+'/'+time_frequency, level=5, identifier = 'time_frequency')
                rel = Relationship(frequency_node,"belongs_to",experiment_node)
                graph.create(rel) 
                try:
                    realms
                except NameError:
                    realms = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,replica=True,latest=True).facet_counts['realm'].keys()
            
                print "Realms:",realms
                for realm in realms:
                    realm_node = Node("Collection",name='cmip5/'+institute+'/'+model+'/'+experiment+'/'+time_frequency+'/'+realm, level=4, identifier = 'realm')
                    rel = Relationship(realm_node,"belongs_to",frequency_node)
                    graph.create(rel)
                    try:
                        mips
                    except NameError:
                        mips = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,replica=True,latest=True).facet_counts['cmor_table'].keys()
                
                    print "cmor_table:",mips
                    for mip in mips:
                        mip_node = Node("Collection",name='cmip5/'+institute+'/'+model+'/'+experiment+'/'+time_frequency+'/'+realm+'/'+mip,level=3, identifier = 'cmor_table')
                        rel = Relationship(mip_node,"belongs_to",realm_node)
                        graph.create(rel) 
                        try:
                            ensembles
                        except NameError:   
                            ensembles = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,cmor_table=mip,replica=True,latest=True).facet_counts['ensemble'].keys()
                    
                        print "Ensembles:",ensembles
                        for ensemble in ensembles:
                            ensemble_node = Node("Collection",name='cmip5/'+institute+'/'+model+'/'+experiment+'/'+time_frequency+'/'+realm+'/'+mip+'/'+ensemble, level=2, identifier = 'ensemble')
                            rel = Relationship(ensemble_node,"belongs_to",mip_node)
                            graph.create(rel)
                            try:
                                variables
                            except NameError:
                                variables = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,cmor_table=mip,ensemble=ensemble,replica=True,latest=True).facet_counts['variable'].keys()
                          
                            print "Variables: ", variables
                            #ctx = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,cmor_table=mip,ensemble=ensemble,replica=True,latest=True)
                            #results = ctx.search()
                            for variable in variables:
                                variable_node = Node("Collection",name='cmip5/'+institute+'/'+model+'/'+experiment+'/'+time_frequency+'/'+realm+'/'+mip+'/'+ensemble+'/'+variable, level=1, identifier = 'variable')
                                rel = Relationship(variable_node,"belongs_to",ensemble_node)
                                graph.create(rel)    
                            
                                        
#                                        print "Results for facets:",model,experiment,time_frequency,realm,mip,ensemble,variable
#                                        
#                                        if len(results) > 1:
#                                           print " vor file access Such-Ergebinisse:",len(results)
#                                        #print len(results)
#                                        #print results
#                                        #print 'Hits:', ctx.hit_count
#                                        print "============files=========================="
#                                        for i in range(0,len(results)):
#                                            file_ctx = results[i].file_context()
#                                            files = file_ctx.search()
#                                            print "Anzahl files:",len(files)
#                                            size = files.batch_size
#                                            file_nodes = []
#                                            for file in files:
#                                                if file.filename.startswith(variable+'_'):
#                                                    #print file
#                                                    file_node = Node("File",name=file.file_id, level = 0, checksum=file.checksum, identifier = 'file')
#                                                    rel = Relationship(file_node,"belongs_to",variable_node)
#                                                    graph.create(rel)
#                                                    print file.filename
#                                                    # other: size,checksum_type,file_id
#                                                    #print size
#                                        print "======================================"
#                                        



