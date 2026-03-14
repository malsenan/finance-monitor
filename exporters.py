import csv
from typing import List, Dict


def save_to_csv(data: List[Dict[str, object]], output_file: str) -> None:
    """
    Saves the aggregated data to a single CSV file.

    Parameters:
    - data (List[Dict[str, object]]): The list of dictionaries containing the aggregated data.
    - output_file (str): The path to the output CSV file.
    """
    # Define the fieldnames for the output CSV file
    fieldnames = list(data)[0].keys()
    # Open the output CSV file in write mode
    with open(output_file, mode="w", newline="") as file:
        # Create a CSV writer object using DictWriter to write the file
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write the header row to the CSV file
        writer.writeheader()
        # Iterate over each row in the aggregated data and write it to the CSV file
        for row in data:
            writer.writerow(row)
