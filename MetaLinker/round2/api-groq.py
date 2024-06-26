import warnings
warnings.filterwarnings('ignore')

import os
import re
import sys
import time
import json
import numpy as np
import chromadb

from dotenv import load_dotenv

from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

sys.path.append('../../')

# from MetaLinker.round2.queries_instructions_r2 import (
#     assistant_instruction_hit1,
#     query_template_hit1,
#     assistant_instruction_hit5,
#     query_template_hit5
# )

assistant_instruction_hit5 = """
Your task is to map column metadata to glossary entities. 
You are provided with several glossaries, stored in a vector, 
each unique and describing a distinct topic and context. 
The user will input the metadata for each column, but all
those columns belong to the same dataset. Therefore, the 
metadata can be considered to be the full metadata of a dataset, 
provided column by column. The column metadata will contain the 
following information: column ID, column label, table ID, 
table name, and the labels of the other columns within that table.
The mapping between the column metadata and the glossary entities is to 
be made based on semantic similarities and relevance. 
This mapping process must be performed 5 times. 
Ensure that each column receives exactly five mappings.
The mappings should follow the same order of glossaries, 
ensuring consistency. For example, if the first mapping of the first 
column is from glossary X, the first mapping of all subsequent columns 
should also be from glossary X, and so on.
Each time, select a different glossary and map the column metadata to 
only items within that glossary.
Return the results in the following format:
'id': COLUMN_ID, 'mappings': [{'id': GLOSSARY_ENTITY_ID_NUMBER}, ...., {'id': GLOSSARY_ENTITY_ID_NUMBER}]
Sort the mapped glossary entities in descending order of relevance, starting 
with the most relevant.
Return ONLY the results, no other text.
Return results for every single column metadata.
"""

query_template_hit5 = """
Based on the instruction given to you, find the most relevant DBpedia property, 
for each of the following metadata in json format: 
{input_metadata}
Each json element is a column metadata belonging to the same dataset. 
Therefore, the overall metadata can be considered to be the full metadata 
of a dataset, provided column by column.
Return the results in the following format:
'id': COLUMN_ID, 'mappings': ['id': GLOSSARY_ENTITY_ID_NUMBER, ...., 'id': GLOSSARY_ENTITY_ID_NUMBER]
Sort the mapped glossary entities in descending order of relevance, starting 
with the most relevant.
Return ONLY the results, no other text.
Return results for every single column metadata.
"""


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

def get_file_paths(input_path):

    """
    get_file_paths

    """

    file_paths = []

    # Iterate through all files in the folder
    for root, dirs, files in os.walk(input_path):
        for file_name in files:
            # Get the absolute path of the file
            file_path = os.path.join(root, file_name)
            # Append the file path to the list
            file_paths.append(file_path)

    return file_paths


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


def make_input_metadata(split):

    """
    make_input_metadata
    
    """

    input_metadata = '\n'.join([
        '{' + "'id': '{}', 'label': '{}', 'table_id': '{}', 'table_name': '{}', 'table_columns': {}".format(
        item['id'], item['label'], item['table_id'], item['table_name'], item['table_columns']
        ) + '}' for item in split])
    
    return input_metadata


def extract_property_ids(raw_prop_ids):

    """
    extract_property_ids
    
    """
    prop_id_list = re.findall(r"\d+", raw_prop_ids)

    return prop_id_list


def append_metadata_output(matches, output_file):

    """
    append_metadata_output

    """

    for match in matches:
        col_id, raw_prop_ids = match
        prop_id_list = extract_property_ids(raw_prop_ids)
        result = {"id": col_id, "mappings": [{"id": prop_id, "score": ""} for prop_id in prop_id_list]}
        output_file.write(json.dumps(result)+ "\n")

    return 


def extract_unmatched_data(matched_metadata_list, data):

    """
    extract_unmatched_data
    
    """

    matched_ids = {item['id'] for sublist in matched_metadata_list for item in sublist}
    
    return [entry for entry in data if entry['id'] not in matched_ids]



def main(query_template, assistant_instruction, model, metadata_input_path, rag_input_path,
         api_key, temperature, output_folder, output_metadata, 
         output_stats, collection_name, embed_model):

    metadata_file_paths = get_file_paths(metadata_input_path)
    start_time = time.time()

    make_output_folder(output_folder)
    remove_output_files_if_exist(output_metadata, output_stats)

    pattern_1 = re.compile(
        r'''['"]id['"]: ['"]([^']+?)['"],\s*['"]mappings['"]: \[([^\]]+?)\]''', 
        re.DOTALL
    )
    #pattern_2 = re.compile(r"'([^']+)'\s*:\s*\[([^\]]+)\]")

    with open(output_stats, 'a') as output_stat_file, open(output_metadata, 'a') as output_file:
        for metadata_file in metadata_file_paths:
            with open(metadata_file, 'r') as file:
                data = [json.loads(line) for line in file]
                
                input_metadata = '\n'.join([
                        '{' + "'id': '{}', 'label': '{}', 'table_id': '{}', 'table_name': '{}', 'table_columns': {}".format(
                        item['id'], item['label'], item['table_id'], item['table_name'], item['table_columns']
                        ) + '}' for item in data])
                # print(input_metadata)
                query = query_template.format(input_metadata=input_metadata)
                user_query = f"Instruction: {assistant_instruction}\n{query}"
                print(user_query)
                # print("****************")
                response = str(get_response_from_llm(model, api_key, temperature,embed_model, rag_input_path, collection_name, user_query))
                # print(f'\nresponse: {response}')
                if response:
                    print(response)
                    matches_1 = pattern_1.findall(response)
                    if matches_1:
                        append_metadata_output(matches_1, output_file)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            output_stat_file.write(f"\nElapsed time: {elapsed_time:.2f} seconds\n")

    return


if __name__ == "__main__":

    load_dotenv()

    temperature = os.getenv('TEMPERATURE')
    model = os.getenv('LLAMA_MODEL')
    embed_model = "BAAI/bge-small-en"
    metadata_input_path = os.getenv('METADATA_FILE')
    rag_input_path = os.getenv('RAG_FILE')
    collection_name = 'sem-tab'
    api_key = os.getenv('GROQ_API_KEY')
    output_folder = os.getenv('OUTPUT_FOLDER')
    output_metadata = os.path.join(output_folder, 'output-metadata.json')
    output_stats = os.path.join(output_folder, 'output-stats.json')
    
    query_template = query_template_hit5
    assistant_instruction = assistant_instruction_hit5

    print("start....")

    main(query_template, assistant_instruction, model, metadata_input_path, rag_input_path,
         api_key, temperature, output_folder, output_metadata, 
         output_stats, collection_name, embed_model)