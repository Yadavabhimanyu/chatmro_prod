from datetime import datetime
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
import qdrant_client
import os
import openai
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from dotenv import load_dotenv
load_dotenv()


client = qdrant_client.QdrantClient(
        os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

embeddings = OpenAIEmbeddings()
vectorstore = Qdrant(
        client=client,
        collection_name=os.getenv("QDRANT_COLLECTION"),
        embeddings=embeddings
    )


llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
memory=ConversationTokenBufferMemory(llm=llm, max_token_limit=2000,return_messages=True)


prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            f"""You are MRO, industrial industry procurement expert. I am someone who is either looking to buy MRO product or looking for MRO related information, this information that I am seeking might be related to products, their usages and features, comparisons, alternatives, spares, accessories, kits, installation, working mechanism and other things. Classify my query in one of the mentioned asks of mine and answer accordingly. I am providing some data that is relevant to the query, data includes mro ecommerce product data and category data, you can create answer from this data.
Answer must have following characteristics
1.Always put answer in html tags so that i can display on website without processing. Keep it simple, no colors, same font size throughout, only the text with embedded product url should be hyperlinks font. If you face any problems, never mentioned it in the answer just display the raw text.
2.If query is generic and not about specific product then you can ask further relevant questions to narrow down the search.
3.Give answer in tables if things like comparison, specifications are in answer
4.If user asks for products more than what I give in context below than just put a message saying that you can't do it because answer is too long.
5.Primarily use given data to answer but you can your own knowledge as well for generic part of answer, just don't do it for things like MPN, price etc"""

        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ]
)


conversation_with_token = ConversationChain(
    llm=llm,
    memory=memory,
    prompt = prompt,
    # max_token_length = 1000,
    verbose=True
)

def get_embedding(query, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        model=model,
        input=query
    )
    return response["data"][0]["embedding"]

def chat_llm(user_query):
    query_embedding = get_embedding(user_query)
    find_match = client.search(
        collection_name=os.getenv("QDRANT_COLLECTION"),
        query_vector=query_embedding,
        with_payload=True,
        limit=5
        )

    find_match2 = client.search(
        collection_name=os.getenv("QDRANT_COLLECTION_2"),
        query_vector=query_embedding,
        with_payload=True,
        limit=3
        )
    file_match_str = "\n".join([str(i) for i in find_match])
    file_match_str2 = "\n".join([str(i) for i in find_match2])
    start_time = datetime.now()
    llm_input=f"Context for the Query: \n 1. Category Descriptions:\n {file_match_str2} \n\n 2. Products Details:\n {file_match_str}  \n\n Query:\n{user_query} \n\n "    
    response = conversation_with_token.predict(input=llm_input) 


    return response


