### GPT

assistant_instruction_hit1 = """
Your task is to match column metadata to a DBpedia property. 
The full set of DBpedia properties will be provided in the vector.
Columns metadata, instead, will be provided by the user and it will
contain the following information: column ID, column label, table ID,
table name and the labels of the other columns within that table.
The matching between the metadata and the DBpedia property is to be made 
based on the semantic similarities between the metadata (i.e. what 
the column express), and DBpedia properties.
Return the results in the following format:
'colID': '00000_0_0000_XXX', 'propID': ['http://dbpedia.org/ontology/PROPERTY_ID'].
Choose ONLY from the DBpedia properties.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""

query_template_hit1 = """
Based on the instruction given to you, find the most relevant DBpedia property, 
for each of the following metadata in json format: 
{input_metadata}
Each json element is an indipendent column metadata. The metadata do not have any
relationship, so the matching with the DBpedia properties should only be based 
on the information provided within its own metadata.
Return the results in the following format:
'colID': '00000_0_0000_XXX', 'propID': ['http://dbpedia.org/ontology/PROPERTY_ID'].
Choose ONLY from the DBpedia properties provided in the vector.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""

assistant_instruction_hit5 = """
Your task is to match column metadata to properties from a glossary.
The full set of glossary properties will be provided in the vector.
Columns metadata, instead, will be provided by the user and it will
contain the following information: column ID, column label, table ID,
table name and the labels of the other columns within that table.
The matching between the column and the glossary properties is to be made 
based on the semantic similarities between the metadata (i.e. what 
the column express), and glossary properties labels and descriptions.
You can add multiple properties, but no more 5.
Return the results in the following format:
'colID': 'XXXX-XXXX-XXXX##XXXX', 'propID': ['0', ..., '5'].
Sort the matched glossary properties in descending order of relevance, starting with the most relevant.
Choose ONLY from the glossary properties.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""

query_template_hit5 = """
Based on the instruction given to you, find the most relevant glossary properties, 
for each of the following metadata in json format: 
{input_metadata}
Each json element is an indipendent column metadata. The metadata do not have any
relationship, so the matching with the glossary properties should only be based 
on the information provided within its own metadata.
The matching between the column and the glossary properties is to be made 
based on the semantic similarities between the metadata (i.e. what 
the column express), and glossary properties labels and descriptions.
You can add multiple properties, but no more 5.
Return the results in the following format:
'colID': 'XXXX-XXXX-XXXX##XXXX', 'propID': ['0', ..., '5'].
Sort the matched glossary properties in descending order of relevance, starting with the most relevant.
Choose ONLY from the glossary properties provided in the vector.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""

"""
Your task is to classify column metadata with items from the glossary stored in the vector. The glossary contains descriptive metadata about each category and their respective identifier. Each entry contains: id (a unique identifier for the category), label (descriptive label for the category) and desc (description of what the category consists of).
The column metadata contains: id (a unique identifier of the column), label (descriptive label of the column), table_id (a unique identifier of the table containing the column), table_name (the name of the table) and table_columns (descriptive labels of the other columns within the table).
Based on column label, and the context provided by the other items within each metadata entry, return the appropriate category from the glossary. Up to 5 categories can be returned.
Return the results in the following format: 'id': COLUMN_ID, 'mappings': ['id': CATEGORY_ID, 'id': CATEGORY_ID]

"""