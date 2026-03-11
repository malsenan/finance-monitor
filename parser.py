import os                                                                                                                                                                                        
import csv                                                                                                                                                                                       
                                                                                                                                                                                                 
def parse_credit_file(file_path):                                                                                                                                                                
    with open(file_path, mode='r', newline='') as file:                                                                                                                                          
        reader = csv.DictReader(file)                                                                                                                                                            
        parsed_data = []                                                                                                                                                                         
        for row in reader:                                                                                                                                                                       
            processed_row = {                                                                                                                                                                    
                'date': row['Posted Date'],                                                                                                                                                                                                                                                                                                 
                'payee': row['Payee'],                                                                                                                                                           
                'address': row['Address'],                                                                                                                                                       
                'amount': float(row['Amount'])                                                                                                                                                   
            }                                                                                                                                                                                    
            parsed_data.append(processed_row)   
        print(parsed_data)                                                                                                                                                 
    return parsed_data                                                                                                                                                                           
                                                                                                                                                                                                 
def aggregate_credit_files(directory):                                                                                                                                                           
    aggregated_data = []                                                                                                                                                                         
    for filename in os.listdir(directory):                                                                                                                                                       
        if filename.endswith('.csv'):                                                                                                                                                            
            file_path = os.path.join(directory, filename)                                                                                                                                        
            parsed_data = parse_credit_file(file_path)                                                                                                                                           
            aggregated_data.extend(parsed_data)                                                                                                                                                  
    return aggregated_data                                                                                                                                                                       
                                                                                                                                                                                                 
def save_to_csv(data, output_file):                                                                                                                                                              
    fieldnames = ['date', 'payee', 'address', 'amount']                                                                                                                             
    with open(output_file, mode='w', newline='') as file:                                                                                                                                        
        writer = csv.DictWriter(file, fieldnames=fieldnames)                                                                                                                                     
        writer.writeheader()                                                                                                                                                                     
        for row in data:                                                                                                                                                                         
            writer.writerow(row)                                                                                                                                                                 
                                                                                                                                                                                                 
def main():                                                                                                                                                                                      
    directory = 'finances/credit'                                                                                                                                                                
    output_file = 'creditTransactions.csv'                                                                                                                                                       
                                                                                                                                                                                                 
    aggregated_data = aggregate_credit_files(directory)                                                                                                                                          
    save_to_csv(aggregated_data, output_file)                                                                                                                                                    
                                                                                                                                                                                                 
if __name__ == '__main__':                                                                                                                                                                       
    main() 