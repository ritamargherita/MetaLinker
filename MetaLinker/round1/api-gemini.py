import time
from llama_index.llms.gemini import Gemini
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import chromadb
import os
import re
import json
from dotenv import load_dotenv


os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_response_from_llm(model, api_key, temperature,embed_model, rag_files, collection_name, user_query):
    """
    get_response_from_llm
    """
    llm = Gemini(model= model, api_key=api_key)

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
    Settings.llm = Gemini(model = model, temperature=temperature)
    query_engine = index.as_query_engine(llm)
    response = query_engine.query(user_query)
    # display(Markdown(f"{response}"))
    
    return response


def make_output_folder(output_folder):
    
    """
    make_output_folder

    """

    os.makedirs(output_folder, exist_ok=True)

    return 


def remove_output_files_if_exist(output_metadata, output_stats):

    """
    make_output_files
    
    """

    if os.path.exists(output_metadata):
        os.remove(output_metadata)

    if os.path.exists(output_stats):
        os.remove(output_stats)

    return 



def main(query_template, model, metadata_input_path, rag_input_path,
         api_key, temperature, output_folder, output_metadata, 
         output_stats, collection_name, embed_model):

    make_output_folder(output_folder)
    remove_output_files_if_exist(output_metadata, output_stats)

    start_time = time.time()

    with open(output_stats, 'a') as output_stat_file:
        with open(output_metadata, 'a') as output_file:

            metadata_not_matched = {}
            metadata_not_matched_stats = {}

            column_id_pattern = r'"id": "([^"]+)"'
            dbpedia_property_pattern = r'http://dbpedia\.org/ontology/\w+'

            with open(metadata_input_path, 'r') as input_metadata:
                for metadata in input_metadata:
                    query = query_template.format(query_column=metadata)

                    response = str(get_response_from_llm(model,api_key, temperature, embed_model, 
                                                         rag_input_path, collection_name, query))

                    if response:
                        column_id = re.findall(column_id_pattern, metadata)
                        property_ids = re.findall(dbpedia_property_pattern, response)

                        if property_ids:
                            mappings = [{"id": pid, "score": ""} for pid in property_ids]
                            output_dict = {"id": column_id[0], "mappings": mappings}
                            json_output = json.dumps(output_dict)
                            output_file.write(json_output+ "\n")

                        if not property_ids:
                            metadata_not_matched[str(metadata)] = 0

                    if not response:
                        metadata_not_matched[str(metadata)] = 0

            while metadata_not_matched:
                metadata_matched = []
                for key,value in metadata_not_matched.items():
                    query = query_template.format(query_column=key)  

                    response = str(get_response_from_llm(model,api_key, temperature, embed_model, 
                                                         rag_input_path, collection_name, query))

                    if response:
                        metadata_matched.append(key)

                        column_id = re.findall(column_id_pattern, key)
                        property_ids = re.findall(dbpedia_property_pattern, response)    

                        metadata_not_matched_stats[column_id[0]] = value + 1   

                        if property_ids:
                            mappings = [{"id": pid, "score": ""} for pid in property_ids]
                            output_dict = {"id": column_id[0], "mappings": mappings}
                            json_output = json.dumps(output_dict)
                            output_file.write(json_output+ "\n")         

                        if not property_ids:
                            metadata_not_matched[str(metadata)] = 0  

                    else:
                        metadata_not_matched[key] += 1  

                for item in metadata_matched:
                    del metadata_not_matched[item]                       


        end_time = time.time()
        elapsed_time = end_time - start_time
        output_stat_file.write(f"\nElapsed time: {elapsed_time:.2f} seconds\n")
        output_stat_file.write(f"Items not matched: \n {metadata_not_matched_stats}")

    return


if __name__ == "__main__":

    load_dotenv()

    temperature = os.getenv('TEMPERATURE')
    model = os.getenv('GOOGLE_MODEL')
    embed_model = "BAAI/bge-small-en"
    metadata_input_path = os.getenv('METADATA_FILE')
    rag_input_path = os.getenv('RAG_FILE')
    collection_name = 'sem-tab'
    api_key = os.getenv('GOOGLE_API_KEY')
    output_folder = os.getenv('OUTPUT_FOLDER')
    output_metadata = os.path.join(output_folder, 'output-metadata.json')
    output_stats = os.path.join(output_folder, 'output-stats.json')
    query_template = os.getenv("QUERY_HIT5")

    main(query_template, model, metadata_input_path, rag_input_path,
         api_key, temperature, output_folder, output_metadata, 
         output_stats, collection_name, embed_model)