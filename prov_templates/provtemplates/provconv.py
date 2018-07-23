import prov.model as prov
import six
import itertools

def set_namespaces(ns, prov_doc):
    if isinstance(ns,dict):
    
        for (sn,ln) in ns.items():
            prov_doc.add_namespace(sn,ln)
            
    else:
        for nsi in ns:
            prov_doc.add_namespace(nsi)    
    
    return prov_doc  


def make_binding(prov_doc,entity_dict,attr_dict):

    prov_doc.add_namespace('tmpl','<http://openprovenance.org/tmpl#>')

    for var,val in entity_dict.items():
       prov_doc.entity(var,{'tmpl:value':val})

    for var,val in attr_dict.items():
       prov_doc.entity(var,{'tmpl:2dvalue_0_0':val})

    return prov_doc




def make_prov(prov_doc): 
    # for enes data ingest use case: use information from dkrz_forms/config/workflow_steps.py
   
    
    bundle = prov_doc.bundle('vargen:bundleid')
    #bundle.set_default_namespace('http://example.org/0/')
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
    doc1 = make_prov(doc)
    print(doc1.get_provn())

    with open(filename+".provn", 'w') as provn_file:
        provn_file.write(doc1.get_provn())
    with open(filename+".xml",'w') as xml_file:
        xml_file.write(doc1.serialize(format='xml'))
    with open(filename+".rdf",'w') as rdf_file:
        rdf_file.write(doc1.serialize(format='rdf'))    
    
    return doc1


def add_records(old_entity, new_entity, instance_dict):
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
            new_node = new_entity.entity(prov.Identifier(neid),other_attributes=props)

        for rel in relations:
            args = rel.args
            (first,second) = args
            (nfirst,nsecond) = (match_qn(first,instance_dict),match_qn(second,instance_dict))
            if rel.get_type() == prov.PROV_ATTRIBUTION:
                new_rel = new_entity.wasAttributedTo(nfirst,nsecond)
            elif rel.get_type() == prov.PROV_ASSOCIATION:
                new_rel = new_entity.wasAttributedTo(nfirst,nsecond)
            elif rel.get_type() == prov.PROV_DERIVATION:
                new_rel = new_entity.wasDerivedFrom(nfirst,nsecond)
            elif rel.get_type() == prov.PROV_DELEGATION:
                new_rel = new_entity.actedOnBehalfOf(nfirst,nsecond)
            elif rel.get_type() == prov.PROV_GENERATION:
                new_rel = new_entity.wasGeneratedBy(nfirst,nsecond)
            elif rel.get_type() == prov.PROV_INFLUENCE:
                new_rel = new_entity.wasInfluencedBy(nfirst,nsecond)
            elif rel.get_type() == prov.PROV_COMMUNICATION:
                new_rel = new_entity.wasInformedBy(nfirst,nsecond)
            else:
                print("Warning! This relation is not yet supported. typeinfo: ",rel.get_type() )

            print(new_rel)


# To Do: condense matching functionality into one function/class
# To To: handle http prefix attributes: partition into namespace, localpart 
#        transform to QualifiedName
def match_qn(qn,mdict):
    lp = qn.localpart
    ns = qn.namespace.prefix
    source = ns+":"+lp
    target = match(source,mdict)
    return target

def match(eid,mdict):
    if eid in mdict:
        print("Match: ",eid)
        return mdict[eid]
    else:
        print("No Match: ",eid)
        return eid

def attr_match(attr_list,mdict):
    p_dict = {}
    for (pn,pv)  in attr_list:
        npn_new = match_qn(pn,mdict)  
        p_dict[npn_new] = match(pv,mdict)
        print("Attr dict:",p_dict)
    return p_dict 
#---------------------------------------------------------------

def instantiate_template(prov_doc,instance_dict):
    '''
    Instantiate a prov template based on a dictionary setting for
    the prov template variables
    To Do: Handle template expansion rules as described in
           https://ieeexplore.ieee.org/document/7909036/ 
           and maybe add additional expansion/composition rules for
           templates useful to compose ENES community workflow templates
    ''' 
    new_doc = set_namespaces(prov_doc.namespaces,prov.ProvDocument()) 
    
    records = prov_doc.get_records()
    blist = list(prov_doc.bundles)
    # To Do: handle matching of bundle attributes too ..
    if blist == []:
        print("Attention: no bundles to transform")
        new_doc = add_records(prov_doc,new_doc)
        #blist = [prov_doc]
    
    for bundle in blist:       
        new_bundle = new_doc.bundle(bundle.identifier)               
        new_bundle = add_records(bundle, new_bundle,instance_dict)      
            
    return new_doc

