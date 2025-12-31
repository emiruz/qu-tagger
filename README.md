# Query understanding via evidence theory

This a proof-of-concept for a unsupervised query tagging system for OpenStreetMap
data which uses just gazeteers and evidence theory. It is a complement to the 
write-up to be posted (here)[https://emiruz.com/post/2026-01-03-qu-tagger/].

The proof-of-concept tags queries such as `fish and chip restaurant near leicester square`
with 5 tags: POI, GEO, FOOD, CAT, PROX. So the result for the example would be something
like: `fish and chip [FOOD] restaurant [CAT] near [PROX] leicester square [GEO].


## Contribution

1. Evidence theory based hypothesis selection. The evidence model has just 9 intuitive
   parameters: the results herein required almost no tuning.
   
2. Efficient binary coarsening inference using Yager rule: fast even with Python. See
   package https://github.com/emiruz/pyevidence/ .


## Setup

```
pip3 install git+https://github.com/emiruz/pyevidence.git
pip3 install osmium ntlk
wget -P data https://download.geofabrik.de/europe/united-kingdom/england-latest.osm.pbf
python3 parse-osm.py
```

## Running

The following command will read the queries in `query_tests.py`, strip all of the tags
and assert that the tagging is the same as the original labelled query. It serves to
demonstrate the impressive variety that such a simple system can achieve.

```
python3 query.py
```

## Examples

Here are some tagging examples from the `query.py` output:

```
[OK] kdjalksjdalkjd [POI]
[OK] N17 [GEO]
[OK] tesco extra [POI]
[OK] boots [POI]
[OK] costa [POI] coffee [FOOD]
[OK] greggs [POI]
[OK] pizza hut [POI]
[OK] waitrose [POI]
[OK] sainsburys local [POI]
[OK] burger king [POI]
[OK] caffe nero [POI]
[OK] london [GEO]
[OK] mcdonalds [POI]
[OK] starbucks [POI]
[OK] restaurant [CAT]
[OK] near me [PROX]
[OK] 16 high street oxford ox1 4ag [GEO]
[OK] 32 deansgate manchester m3 4lq [GEO]
[OK] 14 station road cambridge [GEO]
[OK] 27 the shambles york yo1 7lz [GEO]
[OK] 12 church lane leeds [GEO]
[OK] 3 market place norwich nr2 1nd [GEO]
[OK] 21 kings road brighton [GEO]
[OK] nearest [PROX] petrol station [CAT]
[OK] 47 tavistock road london n1 [GEO]
[OK] bella italia [POI] restaurant [CAT] high street manchester [GEO]
[OK] costa coffee drive thru [POI] restaurant [CAT] near [PROX] camden high street [GEO]
[OK] sainsburys [POI] supermarket [CAT] in [PROX] brighton [GEO]
[OK] five guys [POI] burgers [FOOD] restaurant [CAT] near [PROX] oxford [GEO]
[OK] closest [PROX] tesco [POI] in [PROX] plymouth [GEO]
[OK] nandos [POI] chicken [FOOD] restaurant [CAT] in [PROX] birmingham [GEO]
[OK] kfc [POI] fried chicken [FOOD] restaurant [CAT] nearest [PROX] bradford [GEO]
[OK] wagamama [POI] ramen [FOOD] restaurant [CAT] in [PROX] covent garden [GEO]
[OK] greggs [POI] bakery [CAT] near [PROX] newcastle [GEO]
[OK] pizzaexpress [POI] pizza [FOOD] restaurant [CAT] in [PROX] sheffield [GEO]
[OK] starbucks [POI] coffee shop [FOOD] near me [PROX]
[OK] nearest [PROX] dentist [CAT] in [PROX] norwich [GEO]
[OK] boots [POI] pharmacy [CAT] near [PROX] leicester [GEO]
[OK] burger king [POI] fast food restaurant [CAT] closest [PROX] southampton [GEO]
[OK] subway [POI] sandwiches [FOOD] restaurant [CAT] in [PROX] exeter [GEO]
[OK] dominos [POI] pizza [FOOD] in [PROX] sheffield [GEO]
[OK] nearest [PROX] train station [CAT] in [PROX] liverpool [GEO]
[OK] primark [POI] store [CAT] in [PROX] nottingham [GEO]
[OK] closest [PROX] sushi [FOOD] restaurant [CAT] in [PROX] canterbury [GEO]
[OK] mcdonalds [POI] fast food restaurant [CAT] in [PROX] blackpool [GEO]
[OK] aldi [POI] supermarket [CAT] near [PROX] derby [GEO]
[OK] morrisons [POI] supermarket [CAT] in [PROX] bolton [GEO]
[OK] pizza hut [POI] pizza [FOOD] restaurant [CAT] nearest [PROX] wakefield [GEO]
[OK] closest [PROX] petrol station [CAT] near me [PROX]
[OK] nearest [PROX] pub [CAT] in [PROX] windsor [GEO]
[OK] thai [FOOD] food restaurant [CAT] in [PROX] reading [GEO]
[OK] closest [PROX] chinese [FOOD] in [PROX] leeds [GEO]
[OK] the shard [POI] in [PROX] london bridge [GEO]
[OK] closest [PROX] museum [CAT] in [PROX] bristol [GEO]
[OK] harrods [POI] department store [CAT] in [PROX] knightsbridge [GEO]
[OK] closest [PROX] football stadium [CAT] in [PROX] manchester [GEO]
[OK] the ivy [POI] restaurant [CAT] in [PROX] cheltenham [GEO]
[OK] zizzi [POI] italian [FOOD] restaurant [CAT] nearest [PROX] chester [GEO]
[OK] closest [PROX] fish and chips [FOOD] in [PROX] whitby [GEO]
[OK] cinema [CAT] in [PROX] leicester [GEO]
[OK] closest [PROX] hospital [CAT] near me [PROX]
[OK] waterstones [POI] in [PROX] cambridge [GEO]
[OK] nearest [PROX] tourist information centre [POI] in [PROX] oxford [GEO]
[OK] lego [POI] store [CAT] in [PROX] london [GEO]
[OK] zoo [CAT] in [PROX] london [GEO]
[OK] mcdonalds [POI] in [PROX] stratford [GEO]
[OK] tube station [CAT] near [PROX] leicester square [GEO]
[OK] hotel [CAT] close to [PROX] brighton [GEO] peer [POI]
[OK] yo sushi [POI] restaurant [CAT] in [PROX] london [GEO]
[OK] burger [FOOD] restaurant [CAT] in [PROX] leicester [GEO]
[OK] italian [FOOD] restaurant [CAT] in [PROX] chester [GEO]
```
