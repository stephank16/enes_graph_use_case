'''
a package called provconv to support python based PROV template expansion
  (see: https://ieeexplore.ieee.org/document/7909036/)

see the associated jupyter notebooks for examples and documentation  
  
dependencies: 
    - python prov package (pip installable)
    - python3 (untested for python2)

purpose: a lightweight alternative to the java based ProvToolbox 
         (https://lucmoreau.github.io/ProvToolbox/) 
         for prototyping and for community use cases where the need to
         call an external java executible or an external REST interface 
         (e.g. https://openprovenance.org/services/view/expander )
         is disruptive to the workflow
         
Author: Stephan Kindermann

History: 
      - version 0.1    (11. July 2018)
        tests based on jinja templates and function based parametrization 
      - version 0.2    (20. July)
        redesigned initial version using python prov to generate result instance.
      - version 0.3    (26. July) 
        + support for PROV instantiation files 
        + support for multiple entity expansion
      - version 0.4    (27. July)
        + support for attribute attribute expansion
        + support for provdocs without bundles
      - version 0.5    (...)  
        + application to concrete ENES use case
        
        
Todo:
      - some more tests
      - later (if time allows): repackage functionality into object oriented 
        programming style with base classes hiding internal functionality 
        (import, export, helper functions for instantiation etc.) and 
        configurable higher level classes ..
        
Package provides:

- instantiate_template(input_template,variable_dictionary) 
  result: instantiated template

- make_binding(prov_doc,entity_dict, attr_dict):
  result: generate a PROV binding document based on an empty input document
     (with namespaces assigned) as well as variable settings for entities and
     attributes (python dictionaries) 
     
'''                        


import prov.model as prov
import six      
import itertools

def set_namespaces(ns, prov_doc):
    '''
    set namespaces for a given provenance document (or bundle)
    Args: 
        ns (dict,list): dictionary or list of namespaces
        prov_doc : input document or bundle
    Returns:
        Prov document (or bundle) instance with namespaces set
    '''    
    
    if isinstance(ns,dict):  
        for (sn,ln) in ns.items():
            prov_doc.add_namespace(sn,ln)         
    else:
        for nsi in ns:
            prov_doc.add_namespace(nsi)     
    return prov_doc  

def make_binding(prov_doc,entity_dict,attr_dict):
    ''' 
    generate a PROV binding doc from a dict
    
    Args: 
        prov_doc (ProvDocument): input document
        entity_dict (dictionary): entity var settings
             (dict values are lists in case of multiple instantiations)
        attr_dict (dictionary): 
    Returns:
        prov_doc (ProvDocument): prov document defining a PROV binding
        
    '''    
    prov_doc.add_namespace('tmpl','<http://openprovenance.org/tmpl#>')                         
    for var,val in entity_dict.items():
       index = 0 
       if isinstance(val,list): 
           for v in val: 
               prov_doc.entity(var,{'tmpl:value'+"_"+str(index):v})
               index += 1
       else:    
            prov_doc.entity(var,{'tmpl:value':val})

    for var,val in attr_dict.items():
        index = 0
        if isinstance(val,list): 
           for v in val: 
               prov_doc.entity(var,{'tmpl:2dvalue_'+str(index)+'_0':v})
               index +=1
        else:  
               prov_doc.entity(var,{'tmpl:2dvalue_0_0':val})

    return prov_doc

def make_prov(prov_doc): 
    ''' 
    function generating an example prov document for tests and for 
    demonstration in the associated jupyter notebooks
    
    Args: 
        prov_doc (ProvDocument): input prov document with namespaces set
        
    Returns:
        prov_doc (ProvDocument): a valid complete prov document 
        (with namspaces, entities, relations and bundles   
    
    ToDo: 
       for enes data ingest use case: use information from 
       dkrz_forms/config/workflow_steps.py
   
    '''
    bundle = prov_doc.bundle('vargen:bundleid')
    #bundle.set_default_namespace('http://example.org/0/')
    #bundle = prov_doc (for test with doc without bundles)
    quote = bundle.entity('var:quote',(
         ('prov:value','var:value'),
    ))    

    author = bundle.entity('var:author',(
        (prov.PROV_TYPE, "prov:Person"),
        ('foaf:name','var:name')
    )) 

    bundle.wasAttributedTo('var:quote','var:author')
    
    return prov_doc

def save_and_show(doc,filename):
    '''
    Store and show prov document
    
    Args:
        doc (ProvDocument): prov document to store and show
        filename (string) : präfix string for filename
    Returns:
        files stored in different output formats in:
            filename.provn filename.xml, filename.rdf
        prints additionally provn serialization format    
    '''
    doc1 = make_prov(doc)
    print(doc1.get_provn())

    with open(filename+".provn", 'w') as provn_file:
        provn_file.write(doc1.get_provn())
    with open(filename+".xml",'w') as xml_file:
        xml_file.write(doc1.serialize(format='xml'))
    with open(filename+".rdf",'w') as rdf_file:
        rdf_file.write(doc1.serialize(format='rdf'))    
    
    return doc1

def set_rel(new_entity,rel,nfirst,nsecond):
    '''
       helper function to add specific relations according to relation type
       implements cartesian expansion only (no "linked" restrictions) by now
    '''    
    if not isinstance(nfirst,list):
        nfirst = [nfirst]
    if not isinstance(nsecond,list):
        nsecond = [nsecond]
    
    # ToDo: bad programming style - make this more intuitive 
    nf = -1
    for aitem in nfirst: 
        nf += 1
        ns = -1
        for bitem in nsecond: 
            ns += 1
            
            if rel.get_type() == prov.PROV_ATTRIBUTION:
                new_rel = new_entity.wasAttributedTo(nfirst[nf],nsecond[ns])
            elif rel.get_type() == prov.PROV_ASSOCIATION:
                new_rel = new_entity.wasAttributedTo(nfirst[nf],nsecond[ns])
            elif rel.get_type() == prov.PROV_DERIVATION:
                new_rel = new_entity.wasDerivedFrom(nfirst[nf],nsecond[ns])
            elif rel.get_type() == prov.PROV_DELEGATION:
                new_rel = new_entity.actedOnBehalfOf(nfirst[nf],nsecond[ns])
            elif rel.get_type() == prov.PROV_GENERATION:
                new_rel = new_entity.wasGeneratedBy(nfirst[nf],nsecond[ns])
            elif rel.get_type() == prov.PROV_INFLUENCE:
                new_rel = new_entity.wasInfluencedBy(nfirst[nf],nsecond[ns])
            elif rel.get_type() == prov.PROV_COMMUNICATION:
                new_rel = new_entity.wasInformedBy(nfirst[nf],nsecond[ns])
            else:
                print("Warning! This relation is not yet supported. typeinfo: ",rel.get_type() )
                # ToDo: unsufficient error handling for now .. 
                new_rel = new_entity("ex:missing relation")
    return new_rel    

def prop_select(props,n):
    '''
    helper function to select individual values if dict value is a list
    '''
    nprops = {}
    #print("Props and n: ",props,n)
    for key,val in props.items():
        if isinstance(val,list):
            nprops[key] = val[n]
        else:
            nprops[key] = val 
    return nprops        

def add_records(old_entity, new_entity, instance_dict):
    '''
    function adding instantiated records (entities and relations) to a 
    prov document and containing bundles
    
    calls the match() and attr_match() functions for the instantiation
    
    Args:
        old_entity (bundle or ProvDocument): Prov template for structre info
        
        new_entity (bundle or ProvDocument): Instantiated entity with matched 
          records (entities and relations)
           
        instance_dict: Instantiation dictionary   
    Returns:   
        new_entity (bundle or ProvDocument): Instantiated entity
        
    Todo: change return values of functions (this one and the ones called)    
    
    '''
    relations = []
    nodes = []
    
    # for late use:
    # node_label = six.text_type(record.identifier)
    # uri = record.identifier.uri
    # uri = qname.uri

    for rec in old_entity.records:
        if rec.is_element():
           nodes.append(rec)
           #print(rec)
        elif rec.is_relation():
           relations.append(rec)
        else:
            print("Warning: Unrecognized element type: ",rec)

    for rec in nodes:
        eid = rec.identifier
        attr = rec.attributes
        args = rec.args
        props = attr_match(attr,instance_dict)
        neid = match(eid._str,instance_dict)
        
        if isinstance(neid,list):
            i = 0
            for n in neid: 
                new_node = new_entity.entity(prov.Identifier(n),other_attributes=prop_select(props,i))
                i += 1
        else:
             new_node = new_entity.entity(prov.Identifier(neid),other_attributes=props)

    for rel in relations:
        args = rel.args
        (first,second) = args     
        (nfirst,nsecond) = (match_qn(first,instance_dict),match_qn(second,instance_dict))           
        new_rel = set_rel(new_entity,rel,nfirst,nsecond)        
    return new_entity   


# To Do: condense matching functionality into one function/class
# To To: handle http prefix attributes: partition into namespace, localpart 
#        transform to QualifiedName
def match_qn(qn,mdict):
    '''
    helper function for Prov QualifiedName matching 
    (temporary workaround ..)
    
    Args: 
        qn (QualifiedName): A prov QualifiedName
        mdict (dict) : a dictionary to match with
    Returns:
        target (String): the result of matching the QualifiedName
             (same as input or value of matching key in dict)            
    '''
    lp = qn.localpart
    ns = qn.namespace.prefix
    source = ns+":"+lp
    target = match(source,mdict)
    return target

def match(eid,mdict):
    '''
    helper function to match strings based on dictionary
    
    Args:
        eid (string): input string
        mdict (dict): match dictionary
    Returns:
        meid: same as input or matching value for eid key in mdict
    '''
    if eid in mdict:
        #print("Match: ",eid)
        meid = mdict[eid]
    else:
        #print("No Match: ",eid)
        meid = eid
    return meid

def attr_match(attr_list,mdict):
    '''
    helper function to match a tuple list
    Args:
        attr_list (list): list of qualified name tuples
        mdict (dict): matching dictionary
        
    ToDo: improve attr_match and match first version helper functions    
    '''      
    p_dict = {}
    for (pn,pv)  in attr_list:
        npn_new = match_qn(pn,mdict)  
        p_dict[npn_new] = match(pv,mdict)
        #print("Attr dict:",p_dict)
    return p_dict 
#---------------------------------------------------------------

def instantiate_template(prov_doc,instance_dict):
    '''
    Instantiate a prov template based on a dictionary setting for
    the prov template variables
    
    Supported:
        entity and attribute var: matching
        multiple entity expansion
        
    Unsupported by now:
        linked entities
        multiple attribute expansion
        
    To Do: Handle core template expansion rules as described in
           https://ieeexplore.ieee.org/document/7909036/ 
           and maybe add additional expansion/composition rules for
           templates useful to compose ENES community workflow templates
           
    Args: 
        prov_doc (ProvDocument): input prov document template
        instance_dict (dict): match dictionary
    ''' 
    new_doc = set_namespaces(prov_doc.namespaces,prov.ProvDocument()) 
    
    new_doc = add_records(prov_doc,new_doc,instance_dict)
    
    blist = list(prov_doc.bundles)
   
    for bundle in blist:       
        new_bundle = new_doc.bundle(bundle.identifier)               
        new_bundle = add_records(bundle, new_bundle,instance_dict)      
            
    return new_doc

