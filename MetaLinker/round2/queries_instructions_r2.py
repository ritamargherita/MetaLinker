### GPT

assistant_instruction_hit1 = """

"""

query_template_hit1 = """

"""

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