# app.py
from flask import Flask, render_template, request, redirect, url_for
from elasticsearch import Elasticsearch
import urllib3

app = Flask(__name__)

# Disable SSL certificate verification
urllib3.disable_warnings()

# Initialize Elasticsearch client with SSL context
es = Elasticsearch("https://localhost:9200", basic_auth=("elastic", "3M-NCGJjE1ry=YG*xB4t"), verify_certs=False)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Search route
@app.route('/search', methods=['GET'])
def search():
    # Get query from request parameters
    query = request.args.get('query')

    # Define Elasticsearch query
    es_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["Song^3", "Artist", "Lyrics"]
            }
        },
        "size": 10  # Limit to 10 results
    }

    # Execute search query
    search_results = es.search(index="lyrics", body=es_query)['hits']['hits']

    # Extract relevant information from search results
    results = []
    for hit in search_results:
        result = {
            "rank": hit['_source']['Rank'],
            "title": hit['_source']['Song'],
            "artist": hit['_source']['Artist'],
            "year": hit['_source']['Year'],
            "lyrics": hit['_source']['Lyrics'],
            "snippet": hit['_source']['Lyrics'][:200] + '...',  # Display first 200 characters as snippet
            "full_lyrics_url": url_for('show_lyrics', rank=hit['_source']['Rank'])
        }
        results.append(result)

    return render_template('search_results.html', query=query, results=results)

# Route to display full lyrics
@app.route('/lyrics/<int:rank>')
def show_lyrics(rank):
    # Retrieve song details from Elasticsearch using rank as the identifier
    es_query = {
        "query": {
            "match": {
                "Rank": rank
            }
        }
    }
    search_results = es.search(index="lyrics", body=es_query)['hits']['hits']
    if not search_results:
        return "Lyrics not found for this song rank."
    song_doc = search_results[0]['_source']
    return render_template('lyrics.html', song=song_doc)


if __name__ == '__main__':
    app.run(debug=True)
