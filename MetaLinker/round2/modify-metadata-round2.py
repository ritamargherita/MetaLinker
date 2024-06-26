import os
import json
import shutil

def process_json_files(input_directory, output_directory):
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    
    os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        input_filepath = os.path.join(input_directory, filename)
        output_filepath = os.path.join(output_directory, filename)

        table_data = {}

        with open(input_filepath, 'r') as file:
            lines = file.readlines()

        for line in lines:
            data = json.loads(line)
            table_name = data.get("table_name")
            column_label = data.get("label")
            column_id = data.get("id")
            if table_name in table_data:
                table_data[table_name].append({"id": column_id, "label": column_label})
            else:
                table_data[table_name] = [{"id": column_id, "label": column_label}]
        
        with open(output_filepath, 'w') as file:
            for table_name, items in table_data.items():
                output_data = {
                    "table_name": table_name,
                    "columns": items
                }

                json.dump(output_data, file, separators=(',', ':'))
                file.write('\n')
        
        
        print(f"Processed file: {filename}")

input_directory_path = '../../metadata/round2'
output_directory_path = '../../metadata/round2-processed'

process_json_files(input_directory_path, output_directory_path)
