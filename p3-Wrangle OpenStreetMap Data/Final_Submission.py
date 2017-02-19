
# coding: utf-8

# # References
# 

# I am using the OpenStreetMap data of Rohini area downloaded from mapzen.
# Open Street Map- https://www.openstreetmap.org/relation/3509673
# It is a part of the capital city of India i.e., Delhi.
# The date I downloaded the data set is 18 January 2017.
# I live here,so I am curious to work upon this dataset.
# 
# The data file is in XML format, and here is a link to the description of the OpenStreetMap XML format.
# Link - http://wiki.openstreetmap.org/wiki/OSM_XML

# # Problems Encountered in the Map
# 

# After initially analyzing a small sample size of the Rohini area, I noticed following main problems with the data:
# 
# 1."k" attributes ("name" and "name:en") having same values.

# 2.Abbrevated Language codes.

# 3.Problem with Postal Codes

# ### 1.  "k" attributes ("name" and "name:en") having same values.
# 

# In some node elements with "tag" as a child element, the "k" attributes "name" and "name:en" has same corresponding "v" attributes. Since, they are showing the same information, I felt that "name:en" values of "k" attrbiute are more informative. So, I decided to keep only "name:en" values of "k" attributes if they have a same value as "name".
# A glimpse of the problem and correction has been included in the code section. 

# ### 2. Abbrevated Language codes

# Though, it is a best practice followed by OpenStreetMap to use language codes like en for english,hi for hindi etc. I found it confusing as I wasn't aware of this fact earlier and I didn't know all the language codes I could see in my sample file. 
# So, as a learning opportunity I decided to expand the language codes as a part of cleaning process.
# A glimpse of the problem and correction has been included in the code section. 

# ### 3.Problem with postal codes

#  A glance at the postal codes revealed some problems with the postal codes. The area that I have chosen has postal codes starting from 11 and followed by 4 numerical digits. However, there were few postal codes in my data set starting from "2". When I print those tags I found that don't beong to the chosen area. So, I chose to drop those child tags.
#  And, a case of 5 digit postal code is also observed. It was due to some error and I corrected it to its right value

# # Code and Results

# This section includes the codes to carry out the data wrangling tasks

# #### Loading Useful Libraries

# In[1]:

#Load Libraries
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import csv
import codecs
import cerberus
import schema
import sqlite3
import csv
from pprint import pprint
from time import time


# #### Some Regular expressions

# In[2]:

lower = re.compile(r'^([a-z]|_)*$') 
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# #### Files

# In[3]:

filename = "rohini.osm"
samplefile = "sample3.osm"


# #### Counting the various types of tags:

# In[4]:

#function to count tags
def count_tags(filename):
    tags = {} # creating an empty dictionary
    for event, element in ET.iterparse(filename):
        if element.tag not in tags:
            tags[element.tag] = 1
        else:
            tags[element.tag] += 1
    return tags


# In[5]:

#Counting number of tags
count_tags(filename)


# ## Auditing and correction problems in the data set

# The sub section deals includes auditing and correction of the mentioned problems in the dataset.

# ###  Auditing Tag types(Problem 1)

# Looking at the "tag" elements having both "name" and "name:en" attrbutes

# In[6]:

for event,element in ET.iterparse(filename):
    if element.tag == "tag":
        #checking whether "name" and "name:en" are attributes of "tag" element
        '''if ("name" == element.attrib["k"]) or ("name:en" == element.attrib["k"]):
            # printing "k" and "v" attributes
             print element.attrib["k"] , element.attrib["v"]'''
# Uncomment the if statement to print results                


# ### Cleaning "tag" elements

# Keeping only "name:en" attributes if they have same value as "name" attributes otherwise keeping them both.

# In[7]:

# Approach to retain only "name:en" as K attribute

# This function will yield element if it is right type of tag
def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = ET.iterparse(filename, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
            
# This function will clean the list of names attributes
def clean_names_2(name_attrib):
    # if there is only one item in the list, just return it
    if len(name_attrib) == 1:
        return name_attrib
    # otherwise, check if the 'v' attributes are the same
    # if they are, select one, if not return the list
    else:
        if name_attrib[0]["name"] == name_attrib[1]["name:en"]:
            return [name_attrib[1]]
        else:
            return name_attrib


for element in get_element(samplefile):
    # create an empty list to capture the name attributes
    name_attrib = []
    for child in element:
        if child.tag == "tag":
            # the condition on the 'k' attribute of the tag element
            if "name" == child.attrib["k"] or "name:en" == child.attrib["k"]:
                # append both the 'k' and 'v' attributes as a dictionary
                name_attrib.append({child.attrib["k"]:child.attrib["v"]})

    # if the list is still empty, this condition will not be met
    # (empty lists have a truth value of 'False'), so this
    # section will be skipped
    '''
    if name_attrib:
        print "\n", "BEFORE"
        print name_attrib
        # call the clean function
        name_attrib = clean_names_2(name_attrib)
        print "\n", "AFTER"
        print name_attrib
        '''
# Uncomment the last if statement to print results 


# ### Auditing Types of language codes(Problem 2)

# In[8]:

for event, element in ET.iterparse(filename, events=("start",)):
    # looking for node and relation elements
    if element.tag == "node" or element.tag == "relation":
        #looking if they have "tag" as a child element
        for tag in element.iter("tag"):
            # searching for "name:language codes" and skipping "name:en" as we have seen such pairs above
            '''
            if re.search("name:", tag.attrib["k"]) and "name:en" not in tag.attrib["k"]:
                print tag.attrib["k"]
                '''
# Uncomment the last if statement to print results            


# ### Correction Strategy(Problem 2)

# Correcting those language codes to their expanded form using a mapping dictionary and a function

# In[9]:

#A dictionary for language codes
mapping = { "name:en": "name:english",
            "name:hi": "name:hindi",
            "name:de" : "name:German",
            "name:ja" : "name:japanese",
            "name:ko" : "name:korean",
            "name:ru" : "name:Russian",
           "name:kn" : "name:kannada",
            }


# In[10]:

# Function to expand the language codes
def update_name(name, mapping):
    #Searching for "k" attribut in mapping dictionary
    if name in mapping:      
        #replacing code with expanded form
        name = mapping[name]       
        return name 
    else:
      return name


# In[11]:

# Looping over the node and relation element to apply the correction.
for event, element in ET.iterparse(filename, events=("start",)):
    if element.tag == "node" or element.tag == "relation":
        #Searching for "tag" as child element
        for tag in element.iter("tag"):
         '''  
            if 'name:' in tag.attrib['k']:
                #Calling function on "k" attribute
                tag.attrib['k'] = update_name(tag.attrib['k'], mapping)
                print tag.attrib["k"]
                '''
# Uncomment the if statement to print results        


# ### Auditing postal codes(Problem 3)

# In[12]:

# Function to return the postal code attributeof tag element.
def is_postal_name(element):
    return (element.attrib['k'] == "addr:postcode")


# In[13]:

# Storing postal codes in a set()
postal_codes = set()
for event, element in ET.iterparse(filename, events=("start",)):
    # looking for node and way elements with "tag" as their child element
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter("tag"):
            if is_postal_name(tag):
                postal_codes.add(tag.attrib['v'])
print postal_codes


# ### Correcting Postal Codes

# In[14]:

for event, element in ET.iterparse(filename, events=("start",)):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if is_postal_name(tag):
        # postcode "110089" has been incorrectly entered as"10089"           
                    if tag.attrib['v'] == "10089":
        # Correcting postcode to its right value
                        tag.attrib["v"] = "110089"
        # postcodes starting from "2" are wrong so omit the postcode tag 
                    elif tag.attrib['v'][0] == "2":
                        continue


# ## Processing XML file to load it into database

# This subsection contains the code used to create the csv files from the dataset.

# Although two problems have been identified and correction strategy has been depicted above to correct the issues with the dataset.
# Only, coorection to second problem i.e. correction for the language code has been included in the final shape function to show the skills acquired in this course.

# #### Resulting File names

# In[15]:

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"


# In[16]:

SCHEMA = schema.schema
# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
OSM_PATH = filename
PROBLEMCHARS =problemchars

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=problemchars, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for i in NODE_FIELDS:
            node_attribs[i] = element.attrib[i]
        for tag in element.iter("tag"):
            tag_dict= {}
            # Applying correction for post code in node element
            if is_postal_name(tag):
            # postcode "110089" has been incorrectly entered as"10089"           
                    if tag.attrib['v'] == "10089":
            # Correcting postcode to its right value
                        tag.attrib["v"] = "110089"
            # postcodes starting from "2" are wrong so omit the postcode tag 
                    elif tag.attrib['v'][0] == "2":
                        continue
            # Calling the function to clean the language code problems
            tag.attrib['k'] = update_name(tag.attrib['k'], mapping)
            tag_dict['id'] = node_attribs['id']
            key = tag.attrib['k']
            if re.search(problemchars, tag.attrib['k']):
                pass
            if re.search(lower_colon, tag.attrib['k']):
                pass
            if ':' in tag.attrib['k']:
                type = key[: key.index(':')]
                key = key[key.index(':')+1 :]   
            else:
                type = 'regular'   
            tag_dict['key'] = key
            tag_dict['value'] = tag.attrib['v']
            tag_dict['type'] = type
            tags.append(tag_dict)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for way in WAY_FIELDS:
            way_attribs[way] = element.attrib[way]
        for tag in element.iter("tag"):
            tag_dict1= {}
             # Applying correction for post code in node element
            if is_postal_name(tag):
            # postcode "110089" has been incorrectly entered as"10089"           
                    if tag.attrib['v'] == "10089":
            # Correcting postcode to its right value
                        tag.attrib["v"] = "110089"
            # postcodes starting from "2" are wrong so omit the postcode tag 
                    elif tag.attrib['v'][0] == "2":
                        continue
            tag_dict1['id'] = way_attribs['id']
            key = tag.attrib['k']
            if re.search(PROBLEMCHARS, tag.attrib['k']):
                pass
            if re.search(PROBLEMCHARS, tag.attrib['k']):
                pass
            if ':' in tag.attrib['k']:
                type = key[: key.index(':')]
                key = key[key.index(':')+1 :]
            else:
                type = 'regular' 
            tag_dict1['key'] = key
            tag_dict1['value'] = tag.attrib['v']
            tag_dict1['type'] = type
            tags.append(tag_dict1) 
        i= 0
        for tag in element.iter("nd"):
            way_dict = {}
            way_dict["id"] = way_attribs["id"]
            way_dict["node_id"] = tag.attrib["ref"]
            way_dict["position"] = i
            way_nodes.append(way_dict)
            i +=1    
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}    
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)


# Following sections involves creating SQL database and running SQL queries

# # Parsing file into the sql database

# In[17]:

sqlite_file = 'vcdb.db'    # name of the sqlite database file

# Connect to the database
conn = sqlite3.connect(sqlite_file)


# In[18]:

# Get a cursor object
cur = conn.cursor()


# In[19]:

cur.execute('DROP TABLE IF EXISTS nodes')
conn.commit()


# In[20]:

cur.execute('''
    CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT,type TEXT)
''')
# commit the changes
conn.commit()


# #### First, working with nodes_tags

# In[21]:

# Read in the csv file as a dictionary, format the
# data as a list of tuples:
with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'].decode('utf-8'), i['key'].decode('utf-8'),i['value'].decode('utf-8'), i['type'].decode('utf-8')) for i in dr]


# In[22]:

# insert the formatted data
cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()


# In[23]:

# Create the table, specifying the column names and data types:
cur.execute('''
    CREATE TABLE nodes(id INTEGER, lat INTEGER, lon INTEGER, uid INGETER, version INTEGER, changeset TEXT,timestamp TEXT)
''')
# commit the changes
conn.commit()


# #### Now, working with nodes.csv file

# In[24]:

with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [ (i["id"], i['lat'],i['lon'], i['uid'], i["version"], i["changeset"], i["timestamp"]) for i in dr]


# In[25]:

# insert the formatted data
cur.executemany("INSERT INTO nodes(id,lat,lon,uid,version,changeset,timestamp) VALUES (?,?,?,?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()


# #### Time for ways.csv file

# In[26]:

# Create the table, specifying the column names and data types:
cur.execute('''
    CREATE TABLE ways(id INTEGER, user INTIGER, uid INGETER, version INTEGER, changeset TEXT,timestamp TEXT)
''')
# commit the changes
conn.commit()
with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [ (i["id"], i['user'], i['uid'], i["version"], i["changeset"], i["timestamp"]) for i in dr]
# insert the formatted data
cur.executemany("INSERT INTO ways(id,user,uid,version,changeset,timestamp) VALUES (?,?,?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()    


# #### Ways_tags.csv

# In[27]:

cur.execute('''
    CREATE TABLE ways_tags(id INTEGER, key TEXT, value TEXT,type TEXT)
''')
# commit the changes
conn.commit()
# Read in the csv file as a dictionary, format the
# data as a list of tuples:
with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'].decode('utf-8'), i['key'].decode('utf-8'),i['value'].decode('utf-8'), i['type'].decode('utf-8')) for i in dr]
# insert the formatted data
cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()  


# #### Ways_nodes.csv

# In[28]:

cur.execute('''
    CREATE TABLE ways_nodes(id INTEGER,node_id INTEGER,position INTEGER)
''')
# commit the changes
conn.commit()
# Read in the csv file as a dictionary, format the
# data as a list of tuples:
with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['node_id'],i['position']) for i in dr]
# insert the formatted data
cur.executemany("INSERT INTO ways_nodes(id,node_id,position) VALUES ( ?, ?, ?);", to_db)
# commit the changes
conn.commit()  


# # Data Overview and Additional Ideas

# This section contains the overview of data and SQL queries used to fetch them and some additional ideas about the data 

# rohini.osm ......... 63.2 MB
# 

# vcdb.db .......... 33.2 MB
# 

# nodes.csv ............. 24 MB
# 

# nodes_tags.csv ........ 70 kB
# 

# ways.csv .............. 4 MB
# 

# ways_tags.csv ......... 8 MB
# 

# ways_nodes.cv ......... 2.5 MB

# # SQL Queries

# In this section various queries have been made to the database to learn about the characteristics of dataset

# #### Making a connection with the database to run queries :- 

# In[29]:

sqlite_file = 'mydb.db'    # change this to the name of your sqlite database file

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()


# #### Counting number of nodes_tags

# In[30]:

# Make a query 
query1 = '''SELECT COUNT(*) as count  FROM nodes_tags '''
#Execute the query
result1 = c.execute(query1)
#print results
print list(result1)


# #### Number of ways

# In[31]:

query2 = '''SELECT COUNT(*) as count FROM ways'''
result2 = c.execute(query2)
print list(result2)


# #### Number of ways_tags

# In[32]:

query3 = '''SELECT COUNT(*) as count FROM ways_tags'''
result3 = c.execute(query3)
print list(result3)


# #### Number of ways_nodes

# In[33]:

query4 = '''SELECT COUNT(*) as count FROM ways_nodes'''
result4 = c.execute(query4)
print list(result4)


# #### Number of nodes

# In[34]:

query5 = '''SELECT COUNT(*) as count FROM nodes'''
result5 = c.execute(query5)
print list(result2)


# 
# #### Number of Unique users

# In[35]:

query = ''' SELECT COUNT(DISTINCT(uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways)'''
result= c.execute(query)
print list(result)


# #### Top ten contributing user id's

# In[36]:

query = ''' SELECT uid, COUNT(*) as num
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) 
GROUP BY uid
ORDER BY num DESC
LIMIT 10'''
result= c.execute(query)
print list(result)


# #### Users with sinlge contribution only

# In[37]:

query= ''' SELECT COUNT(*) 
FROM
    (SELECT uid, COUNT(*) as num
     FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) 
     GROUP BY uid
     HAVING num=1) '''
result= c.execute(query)
print list(result)


# ## Additional data exploration

# #### Most popular Ammenities

# In[38]:

query = ''' SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10'''
result= c.execute(query)
print list(result)


# #### Most Popular Religion

# In[39]:

query= ''' SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='place_of_worship') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='religion'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 20'''
result= c.execute(query)
print list(result)


# #### Favourite Cuisines

# In[40]:

query = ''' SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC'''
result= c.execute(query)
print list(result)


# #### Most popular Bank

# In[41]:

query = '''SELECT nodes_tags.value, COUNT(*) as num
        FROM nodes_tags
            JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='bank') i
            ON nodes_tags.id=i.id
        WHERE nodes_tags.key='name'
        GROUP BY nodes_tags.value
        ORDER BY num DESC
        LIMIT 5'''
result= c.execute(query)
print list(result)


# ## Additional Suggestions for improvement of analysis

# There are still several opportunities for cleaning and validation that I left unexplored. Of note, the data set is populated only from one source: OpenStreetMaps. While this crowdsourced repository pulls from multiple sources, some of data is potentially outdated. 
# It would have been an interesting exercise to validate and/or pull missing information (i.e. names) from the Google Maps API, since every node has latitude-longitude coordinates.
# 
# 

# For analysis, I was interested to perform the analysis of data set of complete city Delhi. However, due to huge file size and very poor PC performance, I had to limit my analysis to a very small part i.e. Rohini, where I live in.
# But, During the analysis, I thought that I would be cool to analyse and create database from various parts of the city and do a comparative study. For ex. we can look for particular type of cuisine restraunts or malls concentration in various part of Delhi and that study can help us to make a machine learning algorithm that can predict whether a particular type of shop/restraunt can be opened in a place or not. 
# I would really like to use all the skills learnt in udacity to come up with this model. Though, the data has to be backed by some additional information like purchasing power of people in that area etc. So, there are a lot of difficulties to handle too.

# In[ ]:




# In[ ]:




# In[ ]:



