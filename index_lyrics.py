from elasticsearch import Elasticsearch
import csv

# Create ES client
es = Elasticsearch("https://localhost:9200", basic_auth=("elastic", "3M-NCGJjE1ry=YG*xB4t"), verify_certs=False)

# Create index
index_name = "lyrics"
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}
es.indices.create(index=index_name, body=index_settings, ignore=400)

# Define mapping
mapping = {
    "properties": {
        "Rank": {"type": "integer"},
        "Song": {"type": "text"},
        "Artist": {"type": "keyword"},
        "Year": {"type": "integer"},
        "Lyrics": {"type": "text"},
        "Source": {"type": "integer"}  
    }
}
es.indices.put_mapping(index=index_name, body=mapping)

# Index documents from CSV
with open('lyrics.csv', 'r', encoding='latin-1') as csvfile:  # Specify 'latin-1' encoding
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        try:
            source = int(row["Source"])  # Try to convert to integer
        except ValueError:
            source = None  # Set to None if conversion fails
        
        doc = {
            "Rank": int(row["Rank"]),
            "Song": row["Song"],
            "Artist": row['Artist'],
            "Year": int(row['Year']),
            "Lyrics": row['Lyrics'],
            "Source": source  # Assign the converted value or None
        }
        res = es.index(index=index_name, body=doc)
        print(res['result'])

print("Indexing completed!")
