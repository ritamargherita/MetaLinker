import os
import time

from dotenv import load_dotenv
from openai import OpenAI


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
        temperature=temperature,
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
    print(messages)
    message_content = messages[0].content[0].text
    
    # print(f'message_content: {message_content}')
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    # print(message_content.value)
    # print("\n".join(citations))

    return message_content.value, citations, run


def main():

    load_dotenv()

    assistant_name = 'sem-tab'
    assistant_instruction = os.getenv('ASSISTANT_INSTRUCTION')
    gpt_model = os.getenv('GPT_MODEL')
    metadata_input_path = os.getenv('METADATA_FILE')
    rag_input_path = os.getenv('RAG_FILE')
    vector_store_name = 'sem-tab-rag'
    api_key = os.getenv('API_KEY')
    temperature = float(os.getenv('TEMPERATURE'))
    output_folder = os.getenv('OUTPUT_FOLDER')
    output_metadata = os.path.join(output_folder, 'output-metadata.txt')
    output_stats = os.path.join(output_folder, 'output-stats.txt')

    client = gpt_client(api_key)
    assistant = create_assistant(client, assistant_name, assistant_instruction, gpt_model, temperature)
    vector_store = create_vector_store(client, vector_store_name, rag_input_path)
    updated_assistant = update_assistant(assistant, client, vector_store)
    thread = create_thread(client)

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
                message_content_value, citations, run = get_response(query, client, updated_assistant, thread)
                output_file.write(message_content_value + "\n")
                #time.sleep(2)

    end_time = time.time()

    with open(output_stats, 'w') as stats_file:
        elapsed_time = end_time - start_time
        stats_file.write(f"Elapsed time: {elapsed_time:.2f} seconds\n")
        stats_file.write(f"Usage: {run.usage}\n")

    return


if __name__ == "__main__":

    main()