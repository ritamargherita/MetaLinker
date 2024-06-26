### GPT

assistant_instruction_hit5 = """
Your task is to map column metadata to glossary entities. 
Each table's metadata represents a distinct table. 
Therefore, each table and its columns are to be mapped 
to a separate glossary from the predefined set 
provided to you in the vector, where each vector file
corresponds to a distinct glossary.

You will receive multiple inputs of table metadata, 
where tables are independent of each other. 
Each table metadata includes the table name, 
followed by metadata for each column consisting of its ID and label.

The mapping between the table metadata and the glossary is to 
be made based on semantic similarities and relevance.

First, identify the 5 most relevant glossaries for each table metadata. 
Once the most relevant glossaries are determined, map each column within 
the table to the 5 most relevant entities found in the glossaries. 
Ensure that each column receives exactly five different mappings, 
from different glossaries.

Return the results exactly in the following format:
'id': COLUMN_ID, 'mappings': [{'id': GLOSSARY_ENTITY_ID_NUMBER}, ...., {'id': GLOSSARY_ENTITY_ID_NUMBER}]
Sort the mapped glossary entities in descending order of relevance, starting 
with the most relevant.
Return ONLY the results, no other text.
Return results for every single column metadata.
"""

query_template_hit5 = """
Based on the instruction given to you, find the most relevant glossary entities, 
for each of the following metadata in json format: 

{input_metadata}

Each table's metadata represents a distinct table. 
Therefore, each table and its columns are to be mapped 
to a separate glossary from the predefined set 
provided to you in the vector, where each vector file
corresponds to a distinct glossary.

The mapping between the table metadata and the glossary is to 
be made based on semantic similarities and relevance.

First, identify the 5 most relevant glossaries for each table metadata. 
Once the most relevant glossaries are determined, map each column label 
to the 5 most relevant entities found in the glossaries. 
Ensure that each column receives exactly five different mappings, 
from 5 different glossaries.

Return the results exactly in the following format:
'id': COLUMN_ID, 'mappings': ['id': GLOSSARY_ENTITY_ID_NUMBER, ...., 'id': GLOSSARY_ENTITY_ID_NUMBER]
Sort the mapped glossary entities in descending order of relevance, starting 
with the most relevant.
Return ONLY the results, no other text.
Do not skip any column metadata, return results for every single column.
"""