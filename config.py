import os

class Config:
    ELASTICSEARCH_URI = os.getenv('ELASTICSEARCH_URI', 'http://localhost:9200')
