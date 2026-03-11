import csv                                                                                                                                                                                                      
import os                                                                                                                                                                                                                
                                                                                                                                                                                                                
                                                                                                                                                                                                                
def parse_csv(file_path):                                                                                                                                                                                       
                                                                                                                                                                                                                
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)                                                                                                                                                                      
                                                                                                                                                                                                                
        for row in reader:                                                                                                                                                                                                   
            print(f"Posted Date: {row['Posted Date']}")                                                                                                                                                         
                                                                                                                                                                                                                
            print(f"Reference Number: {row['Reference Number']}")                                                                                                                                               
                                                                                                                                                                                                                
            print(f"Payee: {row['Payee']}")                                                                                                                                                                     
                                                                                                                                                                                                                
            print(f"Address: {row['Address']}")                                                                                                                                                                 
                                                                                                                                                                                                                
            print(f"Amount: ${float(row['Amount'])}")                                                                                                                                                             
                                                                                                                                                                                                                
            print("-" * 40)                                                                                                                                                                                     
                                                                                                                                                                                                                
                                                                                                                                                                                                                
                                                                                                                                                                                                                
if __name__ == '__main__':                                                                                                                                                                                      
                                                                                                                                                                                                                

    folder = "finances/bofa/credit"

    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            parse_csv(filepath) 