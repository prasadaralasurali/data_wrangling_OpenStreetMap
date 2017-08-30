import xml.etree.cElementTree as ET

OSMFILE = "edmonton_canada.osm"

def audit(osmfile):
    osm_file = open(osmfile, "r")
    k_values = set([])
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):                
                    k_values.add(tag.attrib['k'])
    osm_file.close()
    return k_values


k_values = audit(OSMFILE)
print "k values with 'addr' tag"
print "------------------------"

for i in k_values:
    if 'addr' in i:
        print i


print "all k values"
print "-------------"
for j in sorted(k_values):
    print j
