import osmium, unicodedata as ud, itertools, sqlite3, pandas as pd
import json, math, re
from nltk.stem import SnowballStemmer


stem = SnowballStemmer("english").stem
conn = sqlite3.connect('data/reference.db')
cur  = conn.cursor()


def norm(x):
    if not x: return x
    x = ud.normalize('NFD', x.lower().strip())
    x = re.sub("['`]+", "", x)
    x = re.sub("[^a-z0-9 \\-]+", " ", x)
    x = re.sub(" +", " ", x)
    x = " ".join(stem(y) for y in x.split(" "))
    return x


class OSMHandler(osmium.SimpleHandler):
    def __init__(self, L):
        super(OSMHandler, self).__init__()
        self.L = L

    def node(self, n):
        highway_types = ["motorway", "trunk", "primary", "secondary", "tertiary",
                        "unclassified", "residential", "living_street", "service",
                        "road"]
        fields = ['addr:street', 'addr:postcode', 'addr:city']#, 'prow_ref']
        
        if "amenity" in n.tags or \
           "shop" in n.tags or \
           "tourism" in n.tags or \
           "leisure" in n.tags or \
           "sport"  in n.tags:
        
            name = n.tags.get('brand', n.tags.get('name', None))
            name = name if not isinstance(name, tuple) else name[0]

            if name is None: return

            cat  = [norm(n.tags.get('amenity', None)),
                    norm(n.tags.get('shop', None)),
                    norm(n.tags.get('tourism', None)),
                    norm(n.tags.get('leisure', None)),
                    norm(n.tags.get('sport', None))]
            cat  = ";".join(list(set(filter(None, cat))))

            self.L.append({
                'name': norm(name),
                'cuisine': norm(n.tags.get('cuisine', None)),
                'category': cat + (";shop" if "shop" in n.tags else ""),
                'type': 'poi' })

        elif "highway" in n.tags \
             and "name" in n.tags \
             and n.tags["highway"] in highway_types:

            self.L.append({
                'name': norm(n.tags.get("name", None)),
                'category': 'highway',
                'type': 'geo' })

        elif "railway" in n.tags \
             and "name" in n.tags \
             and n.tags["railway"] in ["station","stop"]:

            has_tube = "subway" in n.tags and n.tags["subway"] == "yes"
            
            self.L.append({
                'name': norm(n.tags.get("name", None)),
                'category': 'train station' + (";tube station" if has_tube else ""),
                'type': 'geo' })

        if any(f in n.tags for f in fields):
            names = set(filter(None, [norm(n.tags.get(f, None)) for f in fields]))
            for name in list(names):
                self.L.append({
                    'name': name,
                    'category': '',
                    'type': 'geo' })

L   = []
osm = OSMHandler(L); osm.apply_file('data/england.osm.pbf')
X   = pd.DataFrame(L)

# Proximity
cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS proximity USING fts4(name TEXT, n INT)')
terms = [
    "near", "near me", "nearby", "near by", "near here", "near to", "in", "nearest",
    "closest","closest to me", "close to me", "close by", "closest to here",
    "closest to", "close to", "around me", "in my area", "around my area",
    "within walking distance", "within driving distance"]
for term in terms:
    cur.execute('INSERT INTO proximity (name, n) VALUES (?,?);', (term, 1000,))

# GEO.
geos =  X[X["type"] == 'geo'].groupby('name').size().reset_index(name="n")
cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS geo USING fts4(name TEXT, n INT)')
for r in geos.itertuples(index=False):
    cur.execute('INSERT INTO geo (name, n) VALUES (?,?);', (r.name, math.log(1+r.n),))
conn.commit()

# POI.
cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS poi USING fts4(name TEXT, n INT)')

pois =  X[X["type"] == 'poi'].groupby('name').size().reset_index(name="n")

for r in pois.itertuples(index=False):
    cur.execute('INSERT INTO poi (name, n) VALUES (?,?);', (r.name, math.log(1+r.n),))
conn.commit()

# Categories.
cats = (r.category.split(';') \
           for _, r in X.iterrows() \
           if r.category)
cats = ( pd.DataFrame({"category": itertools.chain(*cats)})
  .groupby('category').size()
  .reset_index(name="n")
  .sort_values("n", ascending=False) )

cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS categories USING fts4(name TEXT, n INT)')
for r in cats.itertuples(index=False):
    cur.execute('INSERT INTO categories (name, n) VALUES (?,?);', (r.category, math.log(1+r.n)))
conn.commit()

# Cuisines.
cuisine = (r.cuisine.split(';') \
           for _, r in X[X.type=="poi"].iterrows() \
           if r.cuisine)
cuisine = ( pd.DataFrame({"cuisine": itertools.chain(*cuisine)})
  .groupby('cuisine').size()
  .reset_index(name="n")
  .sort_values("n", ascending=False) )

cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS cuisine USING fts4(name TEXT, n INT)')
for r in cuisine.itertuples(index=False):
    cur.execute('INSERT INTO cuisine (name, n) VALUES (?,?);', (r.cuisine, math.log(1+r.n)))
conn.commit()

conn.close()
