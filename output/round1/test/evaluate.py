import argparse
import json
import csv

def read_jsonl_file(file_path):
    """
    Reads a JSONL file and returns a list of dictionaries (one dictionary per line).
    """
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def read_csv_file(file_path):
    """
    Reads a CSV file and returns a dictionary mapping IDs.
    Assumes the CSV has two columns: 'source_id' and 'target_id'.
    """
    id_mapping = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            id_mapping[row[0]] = row[1]
    return id_mapping

def calculate_score(mapping_data, ground_truth_mapping, k=5):
    """
    Calculates Hit@k scores.
    """
    total_objects = len(mapping_data)
    correct_top_k = 0
    correct_top_1 = 0

    for obj in mapping_data:
        # Sort mappings by score (highest to lowest)
        sorted_mappings = sorted(obj['mappings'], key=lambda x: x['score'], reverse=True)
        mapping_id = obj['id']
        ground_truth_id = ground_truth_mapping.get(mapping_id)

        if ground_truth_id:
            # Check if ground truth ID is in the top-n mappings
            top_k_ids = [m['id'] for m in sorted_mappings[:k]]
            if ground_truth_id in top_k_ids:
                correct_top_k += 1
                if top_k_ids.index(ground_truth_id) == 0:
                    correct_top_1 += 1

    hit_at_k = correct_top_k / total_objects
    hit_at_1 = correct_top_1 / total_objects

    return hit_at_1, hit_at_k

def main():
    parser = argparse.ArgumentParser(description="Calculate accuracy and hit scores for mapping_file given the ground_truth file.")
    parser.add_argument("-m", "--mapping_file", required=True, help="Path to the mapping JSONL file")
    parser.add_argument("-g", "--ground_truth", required=True, help="Path to the ground truth CSV file")
    args = parser.parse_args()

    # Read the JSONL and CSV files
    mapping_data = read_jsonl_file(args.mapping_file)
    ground_truth_mapping = read_csv_file(args.ground_truth)

    # Calculate scores
    hit_at_1, hit_at_5 = calculate_score(mapping_data, ground_truth_mapping)

    print(f"Hit@1: {hit_at_1:.2f}")
    print(f"Hit@5: {hit_at_5:.2f}")

if __name__ == "__main__":
    main()