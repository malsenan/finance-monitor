import csv

def parse_csv(file_path):
    try:
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                print(f"Posted Date: {row.get('Posted Date', 'N/A')}")
                print(f"Reference Number: {row.get('Reference Number', 'N/A')}")
                print(f"Payee: {row.get('Payee', 'N/A')}")
                print(f"Address: {row.get('Address', 'N/A')}")
                print(f"Amount: ${row.get('Amount', '0.00'):,.2f}")
                print("-" * 40)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    file_path = 'finances/bofa/credit/May2025_3653.csv'
    parse_csv(file_path)
