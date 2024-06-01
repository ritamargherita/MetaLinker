import os
import re
import sys
import time
import json
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI

from queries_instructions import (
    assistant_instruction_hit1,
    query_template_hit1,
    assistant_instruction_hit5,
    query_template_hit5
)
#sys.path.append('./queries_and_instructions')
#from gpt_hit1 import assistant_instruction, query_template


def gpt_client(api_key):

    """
    llm_client

    """

    client = OpenAI(api_key=api_key)

    return client


def create_assistant(client, assistant_name, assistant_instruction, gpt_model, temperature):

    """
    create_assistant

    """

    assistant = client.beta.assistants.create(
        name = assistant_name,
        instructions=assistant_instruction,
        tools=[{"type": "file_search"}],
        model=gpt_model,
        temperature=temperature
    )

    return assistant


def get_file_paths(rag_input_path):

    """
    get_file_paths

    """

    file_paths = []

    # Iterate through all files in the folder
    for root, dirs, files in os.walk(rag_input_path):
        for file_name in files:
            # Get the absolute path of the file
            file_path = os.path.join(root, file_name)
            # Append the file path to the list
            file_paths.append(file_path)

    return file_paths


def add_file_to_vector_store(rag_input_path, client, vector_store):
    
    """
    add_file_to_vector_store

    """

    file_paths = get_file_paths(rag_input_path)
    file_streams = [open(path, 'rb') for path in file_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    return vector_store

def create_vector_store(client, vector_store_name, rag_input_path):

    """
    create_vector_store

    """

    vector_store = client.beta.vector_stores.create(name=vector_store_name)

    add_file_to_vector_store(rag_input_path, client, vector_store)

    return vector_store


def update_assistant(assistant, client, vector_store):
    
    """
    update_assistant

    """

    updated_assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )   

    return updated_assistant


def create_thread(client):

    """
    create_thread
    
    """

    thread = client.beta.threads.create()

    return thread


def get_response(query, client, updated_assistant, thread):

    """
    get_response

    """

    # add message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    # create a run
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=updated_assistant.id
    )

    # get messages
    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    return messages, run
    

def get_response_value(messages, run):

    """
    get_response_value
    
    """

    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")

    return message_content.value, run


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
    prop_ids = re.findall(r"'([^']+)'", raw_prop_ids)

    return [prop_id.strip() for prop_id in prop_ids]


def append_metadata_output(matches, output_file, data):

    """
    append_metadata_output

    """

    matched_metadata = []

    for match in matches:
        col_id, raw_prop_ids = match

        for entry in data:
            if col_id in entry['id']:
                prop_id_list = extract_property_ids(raw_prop_ids)
                result = {"id": col_id, "mappings": [{"id": prop_id, "score": ""} for prop_id in prop_id_list]}
                output_file.write(json.dumps(result)+ "\n")

                matched_metadata.append(entry)

    return matched_metadata


def append_usage_stats_output(output_stat_file, run):

    """
    append_stats_output
    
    """

    output_stat_file.write(f"Usage: {run.usage}\n")

    return


def extract_unmatched_data(matched_metadata_list, data):

    """
    extract_unmatched_data
    
    """

    matched_ids = {item['id'] for sublist in matched_metadata_list for item in sublist}
    
    return [entry for entry in data if entry['id'] not in matched_ids]


def main(query_template, assistant_name, assistant_instruction, gpt_model,
         rag_input_path, vector_store_name, metadata_file, split_size, secondary_split_size,
         api_key, temperature, output_folder, output_metadata, output_stats):
    
    start_time = time.time()
    
    client = gpt_client(api_key)
    assistant = create_assistant(client, assistant_name, assistant_instruction, gpt_model, temperature)
    vector_store = create_vector_store(client, vector_store_name, rag_input_path)
    updated_assistant = update_assistant(assistant, client, vector_store)
    thread = create_thread(client)

    make_output_folder(output_folder)
    remove_output_files_if_exist(output_metadata, output_stats)

    pattern_1 = re.compile(r'''['"](?:colID)['"]: ['"]([^']+?)['"],\s*['"]propID['"]: \[(.*?)\]''', re.DOTALL)
    pattern_2 = re.compile(r"'([^']+)'\s*:\s*\[([^\]]+)\]")

    with open(output_stats, 'a') as output_stat_file, open(output_metadata, 'a') as output_file:
        with open(metadata_file, "r") as file:
            data = [json.loads(line) for line in file]
            print(len(data))

            matched_metadata_list = []

            unmatched_data = data

            while unmatched_data:
                print(len(unmatched_data))
                for i in range(0, len(unmatched_data), split_size):
                    print(i)
                    split = unmatched_data[i:i + split_size]
                    input_metadata = make_input_metadata(split)

                    query = query_template.format(input_metadata=input_metadata)
                    messages, run = get_response(query, client, updated_assistant, thread)

                    if messages:
                        message_content_value, run = get_response_value(messages, run)
                        print(message_content_value)
                        matches_1 = pattern_1.findall(message_content_value)
                        if matches_1:
                            print(matches_1)
                            matched_metadata = append_metadata_output(matches_1, output_file, unmatched_data)
                            matched_metadata_list.append(matched_metadata)
                            append_usage_stats_output(output_stat_file, run)
                        else:
                            matches_2 = pattern_2.findall(message_content_value)
                            if matches_2:
                                print(matches_2)
                                matched_metadata = append_metadata_output(matches_2, output_file, unmatched_data)
                                matched_metadata_list.append(matched_metadata)
                                append_usage_stats_output(output_stat_file, run)

                unmatched_data = extract_unmatched_data(matched_metadata_list, unmatched_data)
                print("Unmatched data", "\n", unmatched_data)
                matched_metadata_list = []      

            end_time = time.time()
            elapsed_time = end_time - start_time
            output_stat_file.write(f"\nElapsed time: {elapsed_time:.2f} seconds\n")

    return


if __name__ == "__main__":

    load_dotenv()

    # IMPORT ENV
    gpt_model = os.getenv('GPT_MODEL')
    api_key = os.getenv('GPT_API_KEY')
    temperature = float(os.getenv('TEMPERATURE'))
    rag_input_path = os.getenv('RAG_FILE')
    metadata_file = os.getenv('METADATA_FILE')
    output_folder = os.getenv('OUTPUT_FOLDER')

    # SET ASSISTANT AND QUERY
    query_template = query_template_hit5
    assistant_instruction = assistant_instruction_hit5

    # SET NAMES
    assistant_name = 'sem-tab'
    vector_store_name = 'sem-tab-rag'

    # SET FOLDERS
    output_metadata = os.path.join(output_folder, 'output-metadata.json')
    output_stats = os.path.join(output_folder, 'output-stats.json')

    # SET SPLIT SIZE
    split_size = 25
    secondary_split_size = 10

    main(query_template, assistant_name, assistant_instruction, gpt_model, 
         rag_input_path, vector_store_name, metadata_file, split_size, secondary_split_size,
         api_key, temperature, output_folder, output_metadata, output_stats)