# -*- coding: utf-8 -*-
"""
Helper tools for information retrieval for Neo4j data ingest
"""

from py2neo import authenticate, Node, Relationship, Graph





def get_files(facet_list):
    """
    call ESGF solr API for information retrieval
    or - alternatively - give path to root directory 
    ( for ingest from a large ENES replica site)
    """
    # prototyping static example:
    cordex_file_set1 = [
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20060101-20101231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20110101-20151231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20160101-20201231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20210101-20251231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20260101-20301231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20310101-20351231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20360101-20401231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20410101-20451231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20460101-20501231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20510101-20551231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20560101-20601231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20610101-20651231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20660101-20701231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20710101-20751231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20760101-20801231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20810101-20851231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20860101-20901231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20910101-20951231.nc",
    "tas_EUR-11_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_MPI-CSC-REMO2009_v1_day_20960101-21001231.nc"
    ]

    return cordex_file_set1
    
def get_servers():
    """
    call ESGF API to retrieve all ESGF data nodes
    """
    # prototyping static example:
    server_list = [
           ('carbon.dkrz','http://carbon.dkrz.de'),
           ('cordex.smhi','http://cordex.shmhi.se')
           ]
           
    return server_list 

def data_service_nodes(dataserver):
    data_services = [Node("data_access_service",name=dataserver,service_type="http", status='up'),
                     Node("data_access_service",name=dataserver,service_type="opendap",status='up'),
                     Node("data_access_service",name=dataserver,service_type="globus",status='up')
                     ]
    return data_services                 