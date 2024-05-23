""" 
Requirments
!pip install llama-index-llms-groq
%pip install llama-index-readers-file pymupdf
%pip install llama-index-embeddings-huggingface
%pip install llama-index-vector-stores-chroma
!pip install llama-index
!pip install llama-index-readers-json
!pip install python-dotenv

"""
import warnings
warnings.filterwarnings('ignore')

from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import os
from dotenv import load_dotenv


os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_response_from_llm(model, api_key, temperature,embed_model, rag_files, collection_name, user_query):
    """
    get_response_from_llm
    """
    llm = Groq(model= model, api_key=api_key)

    # create client and a new collection
    chroma_client = chromadb.EphemeralClient()
    # clear past collection
    try:
        chroma_client.delete_collection(collection_name)
    except:
        pass
    # create new collection
    chroma_collection = chroma_client.create_collection(collection_name)

    # define embedding function
    embed_model = HuggingFaceEmbedding(model_name=embed_model)

    # load documents from a specific path(file or folders)
    documents = SimpleDirectoryReader(rag_files).load_data()

    # set up ChromaVectorStore and load in data
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embed_model
    )
    Settings.llm = Groq(model = model, temperature=temperature)
    query_engine = index.as_query_engine(llm)
    response = query_engine.query(user_query)
    # display(Markdown(f"{response}"))
    return response

def main():
    # parameter setting
    load_dotenv('config/.env')

    assistant_instruction = os.getenv('ASSISTANT_INSTRUCTION')
    temperature = os.getenv('TEMPERATURE')
    model = 'llama3-70b-8192'
    embed_model = "BAAI/bge-small-en"
    rag_files = 'rag_files/'
    collection_name = 'sem-tab'
    api_key = os.getenv('GROQ_API_KEY')

    query = '{"id": "84548468_0_5955155464119382182_Year", "label": "Year", "table_id": "84548468_0_5955155464119382182", "table_name": "Film", "table_columns": ["Fans\' Rank", "Title", "Year", "Director(s)", "Overall Rank"]}'
    user_query = f'{assistant_instruction}\ntable metadata:{query}'

    response = get_response_from_llm(model,api_key, temperature,embed_model, rag_files, collection_name, user_query)
    print(response)
    return response


if __name__ == "__main__":

    main()