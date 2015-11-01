
# coding: utf-8

# # ENES use case graph example


# Fill database with data-hierarchy from ENES metadata index queries
#
# walk through the hierarchical data tree (inefficient solution)
# later: generate offline csv and bulk upload to graph db

from py2neo import authenticate, Node, Relationship, Graph
authenticate("localhost:7474", 'neo4j', 'prolog16')
graph = Graph("http://localhost:7474/db/data/")

from pyesgf.search import SearchConnection
PCMDI_SERVICE = 'http://pcmdi9.llnl.gov/esg-search/search'
conn = SearchConnection(PCMDI_SERVICE,distrib=True)
project = u'CMIP5'
ctx = conn.new_context(project=project,replica=False,latest=True)
root_node = Node("Collection",name='cmip5',level=10, identifier = 'project')

products = conn.new_context(project=project,replica=False,latest=True).facet_counts['product'].keys()
for product in products:
    product_node = Node("Collection",name=product, level=9)
    rel = Relationship(product_node,"belongs_to",root_node)
    graph.create(rel)
    #for institute in facet_counts['institute']:
    
    institutes = conn.new_context(project=project,product=product,replica=False,latest=True).facet_counts['institute'].keys()
    print "Institutes:",institutes
    for institute in [u'MPI-M']:
         institute_node = Node("Collection",name=institute, level=8, identifier = 'institute')
         rel = Relationship(institute_node,"belongs_to",product_node)
         graph.create(rel)
         models = conn.new_context(project=project,product=product,institute=institute,replica=False,latest=True).facet_counts['model'].keys()
         print "Models:",models 
         for model in models: 
                institute_node = Node("Collection",name=institute, level=7, identifier = 'institute')
                rel = Relationship(institute_node,"belongs_to",product_node)
                graph.create(rel) 
                experiments = conn.new_context(project=project,product=product,institute=institute,model=model,replica=False,latest=True).facet_counts['experiment'].keys()
                print "Experiments:", experiments
                for experiment in experiments:
                    institute_node = Node("Collection",name=institute, level=6, identifier = 'institute')
                    rel = Relationship(institute_node,"belongs_to",product_node)
                    graph.create(rel) 
                    time_frequencies = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,replica=False,latest=True).facet_counts['time_frequency'].keys()
                    print "time_frequencies",time_frequencies
                    for time_frequency in time_frequencies:
                        frequency_node = Node("Collection",name=time_frequency, level=5, identifier = 'time_frequency')
                        rel = Relationship(frequency_node,"belongs_to",institute_node)
                        graph.create(rel) 
                        realms = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,replica=False,latest=True).facet_counts['realm'].keys()
                        print "Realms:",realms
                        for realm in realms:
                            realm_node = Node("Collection",name=institute, level=4, identifier = 'realm')
                            rel = Relationship(realm_node,"belongs_to",frequency_node)
                            graph.create(rel)
                            mips = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,replica=False,latest=True).facet_counts['cmor_table'].keys()
                            print "cmor_table:",mips
                            for mip in mips:
                                mip_node = Node("Collection",name=mip, level=3, identifier = 'cmor_table')
                                rel = Relationship(mip_node,"belongs_to",realm_node)
                                graph.create(rel) 
                                ensembles = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,cmor_table=mip,replica=False,latest=True).facet_counts['ensemble'].keys()
                                print "Ensembles:",ensembles
                                for ensemble in ensembles:
                                    ensemble_node = Node("Collection",name=ensemble, level=2, identifier = 'ensemble')
                                    rel = Relationship(ensemble_node,"belongs_to",mip_node)
                                    graph.create(rel)
                                    variables = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,cmor_table=mip,ensemble=ensemble,replica=False,latest=True).facet_counts['variable'].keys()
                                    print "Variables: ", variables
                                    ctx = conn.new_context(project=project,product=product,institute=institute,model=model,experiment=experiment,time_frequency=time_frequency,realm=realm,cmor_table=mip,ensemble=ensemble,replica=False,latest=True)
                                    results = ctx.search()
                                    
                                    for variable in variables:
                                        variable_node = Node("Collection",name=variable, level=1, identifier = 'variable')
                                        rel = Relationship(variable_node,"belongs_to",ensemble_node)
                                        graph.create(rel)    
                                        print "Results for facets:",model,experiment,time_frequency,realm,mip,ensemble,variable
                                        
                                        if len(results) > 1:
                                           print " vor file access Such-Ergebinisse:",len(results)
                                        #print len(results)
                                        #print results
                                        #print 'Hits:', ctx.hit_count
                                        print "============files=========================="
                                        for i in range(0,len(results)):
                                            file_ctx = results[i].file_context()
                                            files = file_ctx.search()
                                            print "Anzahl files:",len(files)
                                            size = files.batch_size
                                            file_nodes = []
                                            for file in files:
                                                if file.filename.startswith(variable+'_'):
                                                    #print file
                                                    file_node = Node("File",name=file.file_id, level = 0, checksum=file.checksum, identifier = 'file')
                                                    rel = Relationship(file_node,"belongs_to",variable_node)
                                                    graph.create(rel)
                                                    print file.filename
                                                    # other: size,checksum_type,file_id
                                                    #print size
                                        print "======================================"
                                        



