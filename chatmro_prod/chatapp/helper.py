import os
import numpy as np
import pandas as pd
import time
import json

import openai
from openai.embeddings_utils import cosine_similarity
from rank_bm25 import BM25Okapi
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()
#load api key

openai.api_key = os.getenv("OPENAI_API_KEY")




def load_search_df():
    global search_df
    global bm25
    if 'search_df' not in globals():
        print("loading searcf df")
        # Load search_df only if it has not been loaded yet
        search_df = pd.read_pickle(r"D:\chatMRO_V1\data\productd_60k_embed.pkl")
        search_df.columns = ['text','embeddings']
        json_df = search_df['text'].apply(lambda x: json.loads(x))
        tokenized_corpus = [tokenize_dict(json) for json in json_df.values]
        bm25 = BM25Okapi(tokenized_corpus)
    else:
        print("search_df already loaded.")
    if 'bm25' not in globals():
        print("loading bm25 ")
        # Load bm25 only if it has not been loaded yet
        bm25 = BM25Okapi(tokenized_corpus)
    else:
        print("bm25 already loaded.")
    return search_df,bm25

#text to embedding function
def get_embedding(text_to_embed, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        model= "text-embedding-ada-002",
        input=[text_to_embed]
    )
    return response

#Shortlist top 10 products
def shortlist_product(result_df,n=10):
    #top n
    result_df.sort_values(by=['match', 'similarity'], ascending=[False, False], inplace=True)

    return result_df.iloc[:n].copy()

#Generate ranking 
def search_products(query):
    search_df,bm25=load_search_df()
    query_embedding = get_embedding(query)['data'][0]['embedding']

    tokenized_query = query.split(" ")

    result_df = pd.DataFrame()
    result_df['text'] = search_df['text']
    result_df['similarity'] = search_df['embeddings'].apply(lambda x: cosine_similarity(x, query_embedding))
    result_df['match'] = bm25.get_scores(tokenized_query)

    #print(result_df)
    return shortlist_product(result_df),result_df
    #return result_df

#Display results
def display_results(shortlist):
    print("Top 10 results : ")
    result=[]
    for i,sh in enumerate(shortlist.values):
        product = json.loads(sh[0])
        result.append(product)
        print(f"\t{i+1}. {product['brand_name']}, {product['mpn']}, {product['title']}, {product['product_url']}")
    return result

#Tokenize the document
def tokenize_dict(dict):
    tokenized = []
    for key in dict:
        if (key not in ['price', 'product_url']):
            temp_tokenized = [key]
            value = dict[key]
            if(value):
                if(type(value) == type(dict)):
                    temp_tokenized = temp_tokenized + tokenize_dict(value)
                else:
                    temp_tokenized = temp_tokenized + value.split(" ")

            tokenized = tokenized + temp_tokenized
    
    return tokenized



# # search_df = pd.read_pickle(os.path.join(settings.BASE_DIR, "productd_60k_embed.pkl"))
# search_df = pd.read_pickle(r"D:\chatMRO_V1\data\productd_60k_embed.pkl")
# # search_df = pd.read_pickle("data/dump/productd_60k_embed.pkl")
# search_df.columns = ['text','embeddings']
# json_df = search_df['text'].apply(lambda x: json.loads(x))
# tokenized_corpus = [tokenize_dict(json) for json in json_df.values]
# bm25 = BM25Okapi(tokenized_corpus)
