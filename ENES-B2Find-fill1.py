
# import ENES information from B2Find into graph db
#
# 1) find IPCC tagged data
# 2) extract collection information for data
# 3) identify collection in existing neo4j grap
# 3) add nodes and relations for citation information of collection 
#    (authors, DOI, ..)

# 1) 
import ckanclient
from pprint import pprint
q = 'tags:IPCC'
ckan = ckanclient.CkanClient('http://b2find.eudat.eu/api/3/')
d = ckan.action('package_search', q=q, rows=2)

# 2)
# collection pattern (neo4j nodes for pattern parts)
# <activity>/<product>/<institute>/<model>/<experiment>/<frequency>/ 
# <modeling realm>/<mip table>/<ensemble member>/
# <version number>/<variable name>/<CMORfilename.nc>
for result in d['results']:
    print result['title']
    # example title:   cmip5    output1   LASG-CESS FGOALS-g2 historicalNat
    # collection info: activity product   institute model     experiment
    print result['url']
    for part in result:
        print part, result[part]
