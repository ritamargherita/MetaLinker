### GPT

assistant_instruction_hit1 = """
Your task is to match column metadata to a DBpedia property.
The full set of DBpedia properties will be provided in the vector.
Columns metadata, instead, will be provided by the user and it will
contain the following information: column ID, column label, table ID,
table name and the labels of the other columns within that table.
The matching between the column and the DBpedia property is to be made 
based on the semantic similarities between the metadata (i.e. what 
the column express), and DBpedia property.
Return the results in the following format:
'colID': '00000_0_0000_XXX', 'propID': ['http://dbpedia.org/ontology/PROPERTY_ID'].
Choose ONLY from the DBpedia properties.
Return ONLY one DBpedia property.
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
Return ONLY one DBpedia property.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""

assistant_instruction_hit5 = """
Your task is to match column metadata to DBpedia properties.
The full set of DBpedia properties will be provided in the vector.
Columns metadata, instead, will be provided by the user and it will
contain the following information: column ID, column label, table ID,
table name and the labels of the other columns within that table.
The matching between the column and the DBpedia properties is to be made 
based on the semantic similarities between the metadata (i.e. what 
the column express), and DBpedia properties.
You can add multiple properties, but no more 5.
Return the results in the following format:
'colID': '00000_0_0000_XXX', 'propID': ['http://dbpedia.org/ontology/PROPERTY_ID', ..., 'http://dbpedia.org/ontology/PROPERTY_ID'].
Sort the matched DBpedia in descending order of relevance, starting with the most relevant.
Choose ONLY from the DBpedia properties.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""

query_template_hit5 = """
Based on the instruction given to you, find the most relevant DBpedia property, 
for each of the following metadata in json format: 
{input_metadata}
Each json element is an indipendent column metadata. The metadata do not have any
relationship, so the matching with the DBpedia properties should only be based 
on the information provided within its own metadata.
You can add multiple properties, but no more 5.
Return the results in the following format:
'colID': '00000_0_0000_XXX', 'propID': ['http://dbpedia.org/ontology/PROPERTY_ID', ..., 'http://dbpedia.org/ontology/PROPERTY_ID'].
Sort the matched DBpedia in descending order of relevance, starting with the most relevant.
Choose ONLY from the DBpedia properties provided in the vector.
Return ONLY the results, no other text.
Return results for each and every single column metadata.
"""