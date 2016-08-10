# tools to transform w3c prov standard based provenance descriptions
# into a graph representation, which can directly filled into a neo4j graph database
# Version: 0.2 (August 2016)
# Author: Stephan Kindermann
#   - takes w3c prov xml and prov json representations as input
#   - generates neo4j graph 
#   - code makes heavy use of the python prov software (https://github.com/trungdong/prov)
#   - the gen_graph_model function to generate neo4j graph follows the generic structure
#     of the prov_to_dot functon to generate dot graphs (in prov/dot.py)

"""
=============================================
W3C PROV / neo4j graph tools
=============================================

Provided functionality:

* generate neo4j graph representation from W3C prov descriptions (xml and json) 
* tests
* helper functions
* Jupyter notebook demo

Configuration:

* include this package into your path (pypi installation in next version) 

     from neo4j-prov import provio

"""


# import all dependencies

from prov.model import ProvDocument
from prov.dot import prov_to_dot
from IPython.display import Image
from prov.model import (
    PROV_ACTIVITY, PROV_AGENT, PROV_ALTERNATE, PROV_ASSOCIATION,
    PROV_ATTRIBUTION, PROV_BUNDLE, PROV_COMMUNICATION, PROV_DERIVATION,
    PROV_DELEGATION, PROV_ENTITY, PROV_GENERATION, PROV_INFLUENCE,
    PROV_INVALIDATION, PROV_END, PROV_MEMBERSHIP, PROV_MENTION,
    PROV_SPECIALIZATION, PROV_START, PROV_USAGE, Identifier,
    PROV_ATTRIBUTE_QNAMES, sorted_attributes, ProvException
)

import six
from py2neo import Graph, Node, Relationship, authenticate



def get_provdoc(format,infile):
    if format == "json":
       return ProvDocument.deserialize(infile)
    elif format == "xml":
       return ProvDocument.deserialize(infile,format='xml')
    else:
       print "Error: unsupported format (xml and json are supported"



def visualize_prov(prov_doc):
    dot = prov_to_dot(prov_doc)
    dot.write_png('tmp1.png')
    dot.write_pdf('tmp1.pdf')
    
    return Image('tmp1.png')


def gen_graph_model(prov_doc):

    node_map = {}
    count = [0, 0, 0, 0] # counters for node ids
    records = prov_doc.get_records()
    relations = []
    use_labels = True
    show_relation_attributes = True
    other_attributes = True
    show_nary = True

    def _add_node(record):
       count[0] += 1
       node_id = 'n%d' % count[0]
       if use_labels:
          if record.label == record.identifier:
              node_label = '"%s"' % six.text_type(record.label)
          else:
            # Fancier label if both are different. The label will be
            # the main node text, whereas the identifier will be a
            # kind of suptitle.

              node_label = six.text_type(record.label)+','+six.text_type(record.identifier)
       else:
           node_label = six.text_type(record.identifier)

       uri = record.identifier.uri
    
       node = Node(node_id, label=node_label, URL=uri)
       node_map[uri] = node
    
     ## create Node ... ##dot.add_node(node)
       return node

    def _get_node(qname):
       if qname is None:
          print "ERROR: _get_node called for empty node"
        #return _get_bnode()
       uri = qname.uri
       if uri not in node_map:
          _add_generic_node(qname)
       return node_map[uri]
         
    for rec in records:
         if rec.is_element():
                _add_node(rec)
         else:
        # Saving the relations for later processing
            relations.append(rec)
        
                   
    neo_rels = []            
    for rec in relations:
                args = rec.args
                # skipping empty records
                if not args:
                    continue
                # picking element nodes
                nodes = [
                    value for attr_name, value in rec.formal_attributes
                    if attr_name in PROV_ATTRIBUTE_QNAMES
                ]
                other_attributes = [
                    (attr_name, value) for attr_name, value in rec.attributes
                    if attr_name not in PROV_ATTRIBUTE_QNAMES
                ]
                add_attribute_annotation = (
                    show_relation_attributes and other_attributes
                )
                add_nary_elements = len(nodes) > 2 and show_nary
                
                if len(nodes) < 2:  # too few elements for a relation?
                    continue  # cannot draw this           
                
                if add_nary_elements or add_attribute_annotation:
                    # a blank node for n-ary relations or the attribute annotation
                
                    # the first segment
                    
                    rel = Relationship(_get_node(nodes[0]), rec.get_type()._str,_get_node(nodes[1]))
                    #print "relationship: ",rel
                    neo_rels.append(rel)
                       
                    if add_nary_elements:   
                        for node in nodes[2:]:
                            if node is not None:
                                relx = Relationship(_get_node(nodes[0]), "...rel_name",_get_node(node))
                                neo_rels.append(relx)
                else:
                    # show a simple binary relations with no annotation
                    rel =  Relationship(_get_node(nodes[0]), rec.get_type()._str,_get_node(nodes[1]))
                    neo_rels.append(rel)

    return neo_rels
