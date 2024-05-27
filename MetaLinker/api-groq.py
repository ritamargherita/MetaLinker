""" 
Requirments
!pip install llama-index-llms-groq
%pip install llama-index-readers-file pymupdf
%pip install llama-index-embeddings-huggingface
%pip install llama-index-vector-stores-chroma
!pip install llama-index
!pip install llama-index-readers-json
!pip install python-dotenv


.env setting
LLM_NAME = 'llama3-70b-8192'
GPT_MODEL = 'gpt-3.5-turbo'
API_KEY = 'your gpt api key'
GROQ_API_KEY = 'your groq api key'
TEMPERATURE = '1'
RAG_FILE = 'glossary/'
METADATA_FILE = 'metadata/r2_sample_metadata.jsonl'
OUTPUT_FOLDER = 'xueli-test/output/'
ASSISTANT_INSTRUCTION = 'You will be provided with table metadata only (i.e. column ID, column label, table ID, table name and the labels of the other columns within that table), and your task is to match it to a knowledge graph. The knowledge graph, provided as .jsonl file, contains entries of label such as {"id": "id name", "label": "label name", "desc": "Description of the label"}. The matching is supposed to be done based on the semantic similarities between the table metadata and what the column express within such table, and a specific Description of the label within the knowledge graph.
Provide your answer in Json format, with the column ID and the label ID, such as {“columnID”: “ENTER HERE THE COLUMN ID”, “labelID”: “ENTER HERE THE LABEL ID”}
Choose ONLY from the properties provided to you.
Return ONLY the Json result, no other text.'

"""
import warnings
warnings.filterwarnings('ignore')


import time
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
    metadata_input_path = os.getenv('METADATA_FILE')
    rag_input_path = os.getenv('RAG_FILE')
    collection_name = 'sem-tab'
    api_key = os.getenv('GROQ_API_KEY')
    output_folder = os.getenv('OUTPUT_FOLDER')
    output_metadata = os.path.join(output_folder, 'output-metadata.txt')
    output_stats = os.path.join(output_folder, 'output-stats.txt')

    os.makedirs(output_folder, exist_ok=True)

    if os.path.exists(output_metadata):
        os.remove(output_metadata)

    with open(output_metadata, 'w') as output_file:
        pass

    if os.path.exists(output_stats):
        os.remove(output_stats)

    with open(output_stats, 'w') as stats_file:
        pass

    start_time = time.time()

    with open(output_metadata, 'a') as output_file:

        with open(metadata_input_path, 'r') as input_metadata:
            for metadata in input_metadata:
                query = str(metadata)
                print(f"QUERY: {query}")
                user_query = f'{assistant_instruction}\ntable metadata:{query}'
                response = get_response_from_llm(model,api_key, temperature,embed_model, rag_input_path, collection_name, user_query)
                print(f"RESPONSE: {response}")
                output_file.write(f'{response}\n')
                print(f"******************************\n")
                #time.sleep(2)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"ELASPSED TIME: {elapsed_time}")

    with open(output_stats, 'w') as stats_file:
        elapsed_time = end_time - start_time
        stats_file.write(f"Elapsed time: {elapsed_time:.2f} seconds\n")

    return


if __name__ == "__main__":

    main()