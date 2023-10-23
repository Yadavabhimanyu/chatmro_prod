import pandas as pd

import openai
from openai.embeddings_utils import cosine_similarity
import os
from django.conf import settings
from asgiref.sync import sync_to_async

#load api key
with open(os.path.join(settings.BASE_DIR, "key.txt"),"r") as f:
    key = f.readline()

openai.api_key = key

# search_df = pd.read_pickle(os.path.join(settings.BASE_DIR, "productd_5k_embed.pkl"))
search_df = pd.read_pickle(os.path.join(settings.BASE_DIR, "productd_60k_embed.pkl"))
search_df.columns = ['text','embeddings']

#text to embedding function
def get_embedding(text_to_embed, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        model= "text-embedding-ada-002",
        input=[text_to_embed]
    )
    return response

#generate response using gpt model
def get_response(system_message, user_message, model='gpt-3.5-turbo'):

    response = openai.ChatCompletion.create(
        model = model,
        messages = [
            {"role":"system", "content": system_message},
            {"role":"user", "content": user_message}
        ]
    )

    return response

def shortlist_product(result_df,n=5):
    #top n
    result_df.sort_values(by=['similarity'])

    return result_df.iloc[:n].copy()


def search_products(query, search_df):
    query_embedding = get_embedding(query)['data'][0]['embedding']


    result_df = pd.DataFrame()
    result_df['text'] = search_df['text']
    result_df['similarity'] = search_df['embeddings'].apply(lambda x: cosine_similarity(x, query_embedding))

    result_df.sort_values(by=['similarity'], ascending=False, inplace=True)
    #print(result_df)
    return shortlist_product(result_df),result_df

# @sync_to_async
def chat_llm(query, search_df=search_df):
    print("Query : ",query)
    shortlist,result_df =search_products(query=query, search_df=search_df)
    #Generate Context
    context = '\n'.join(list(shortlist['text'].values))
    print("context\n",context)
    #Create user message
    user_message = "Products : \n"+context+"\nQuery : \n"+query
    #Create system message
    system_message = "You are a Product expert in MRO industry. Given the data on different products, help the user find all the products that matches with their query. Provide chain of thought, give proper details and ask relevant questions to help them further narrow down the product if required.Always return answer in HTML"
    #Generate response
    response = get_response(
        system_message=system_message,
        user_message=user_message
    )
    output = response["choices"][0]["message"]["content"]
    #output = "<p>" + output + "<strong>" + "</p>"
    system_message_2 = "string to html convertor"
    response_html = get_response(
        system_message=system_message_2,
        user_message=output
    )
    output = response_html["choices"][0]["message"]["content"]
    return output

if __name__=="__main__":
    from datetime import datetime
    start_time=datetime.now()
    print(chat_llm("suggeste me red cable?"))
    print("time taken:",datetime.now()-start_time)
    