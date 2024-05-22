import os

from dotenv import load_dotenv
from openai import OpenAI


def llm_client(api_key):

    """
    llm_client

    """

    client = OpenAI(api_key=api_key)

    return client


def create_assistant(client, assistant_name, assistant_instruction, llm_model, temperature):

    """
    create_assistant

    """

    assistant = client.beta.assistants.create(
    name = assistant_name,
    instructions=assistant_instruction,
    tools=[{"type": "file_search"}],
    model=llm_model,
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

    print(file_batch.status)
    print(file_batch.file_counts)

    return vector_store

def create_vector_store(client, vector_store_name, rag_input_path):

    """
    create_vector_store

    """

    vector_store = client.beta.vector_stores.create(name=vector_store_name)

    add_file_to_vector_store(rag_input_path, client, vector_store)

    print(vector_store)

    return vector_store



def main():

    load_dotenv()

    assistant_name = 'sem-tab'
    assistant_instruction = os.getenv('ASSISTANT_INSTRUCTION')
    llm_model = 'gpt-4-turbo'
    rag_input_path = '.rag_files'
    vector_store_name = 'sem-tab-rag'
    api_key = os.getenv('API_KEY')
    temperature = os.get('TEMPERATURE')

    client = llm_client(api_key)
    assistant = create_assistant(client, assistant_name, assistant_instruction, llm_model, temperature)
    vector_store = create_vector_store(client, vector_store_name, rag_input_path)

    return


if __name__ == "__main__":

    main()