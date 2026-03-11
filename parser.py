import os
import csv
from typing import List, Dict

# Function to parse a single credit file and return processed data
def parse_credit_file(file_path: str) -> List[Dict[str, object]]:
    """
    Parses a single credit transactions CSV file and returns the processed data.

    Parameters:
    - file_path (str): The path to the credit CSV file.

    Returns:
    - List[Dict[str, object]]: A list of dictionaries containing the parsed data.
    """
    # Open the CSV file in read mode
    with open(file_path, mode='r', newline='') as file:
        # Create a CSV reader object using DictReader to read the file
        reader = csv.DictReader(file)
        # Initialize an empty list to store processed rows
        parsed_data = []
        # Iterate over each row in the CSV file
        for row in reader:
            # Process each row by extracting relevant fields and converting 'Amount' to float
            processed_row = {
                'date': row['Posted Date'],
                'reference': row['Reference Number'],
                'payee': row['Payee'],
                'address': row['Address'],
                'amount': float(row['Amount'])
            }
            # Append the processed row to the parsed_data list
            parsed_data.append(processed_row)
    # Return the list of processed rows
    return parsed_data

# Function to aggregate data from all CSV files in a specified directory
def aggregate_credit_files(directory: str) -> List[Dict[str, object]]:
    """
    Aggregates data from all credit CSV files in a specified directory.

    Parameters:
    - directory (str): The path to the directory containing the credit CSV files.

    Returns:
    - List[Dict[str, object]]: A list of dictionaries containing the aggregated data.
    """
    # Initialize an empty list to store aggregated data
    aggregated_data = []
    # Iterate over each file in the specified directory
    for filename in os.listdir(directory):
        # Check if the file is a CSV file for my credit account
        if filename.endswith('_3653.csv'):
            # Construct the full path to the file
            file_path = os.path.join(directory, filename)
            # Parse the credit file and get the processed data
            parsed_data = parse_credit_file(file_path)
            # Extend the aggregated data list with the parsed data
            aggregated_data.extend(parsed_data)
    # Return the aggregated data
    return aggregated_data

# Function to save the aggregated data to a single CSV file
def save_to_csv(data: List[Dict[str, object]], output_file: str) -> None:
    """
    Saves the aggregated data to a single CSV file.

    Parameters:
    - data (List[Dict[str, object]]): The list of dictionaries containing the aggregated data.
    - output_file (str): The path to the output CSV file.
    """
    # Define the fieldnames for the output CSV file
    fieldnames = ['date', 'reference', 'payee', 'address', 'amount']
    # Open the output CSV file in write mode
    with open(output_file, mode='w', newline='') as file:
        # Create a CSV writer object using DictWriter to write the file
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write the header row to the CSV file
        writer.writeheader()
        # Iterate over each row in the aggregated data and write it to the CSV file
        for row in data:
            writer.writerow(row)

# Main function to coordinate the parsing and aggregation process
def main() -> None:
    """
    Main function to coordinate the parsing and aggregation process.
    """
    # Define the directory containing the credit files
    directory = 'finances/credit'
    # Define the output file name for the aggregated data
    output_file = 'creditTransactions.csv'

    # Aggregate data from all CSV files in the specified directory
    aggregated_data = aggregate_credit_files(directory)
    # Save the aggregated data to a single CSV file
    save_to_csv(aggregated_data, output_file)

# Check if the script is run as the main module and execute the main function
if __name__ == '__main__':
    main()
