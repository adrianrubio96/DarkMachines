# Read csv files and merge all 2nd lines into one csv file, and convert it to a latex table

import os
import pandas as pd 
import glob

INPUT_PATH = "/lhome/ific/a/adruji/DarkMachines/DataPreparation/acceptance/csv/"
version = "v02"

# Create a list of all the csv files in the current directory 
csv_list = glob.glob('%s/%s/*.csv' % (INPUT_PATH, version)) 
print(csv_list)

# Create an empty dataframe to store all the data 
df = pd.DataFrame() 

# Combined all the csv files into one dataframe
for csv in csv_list: 
    df = df.append(pd.read_csv(csv))

# Remove output file if it already exists
if os.path.exists('%s/%s/combined_data_%s.csv' % (INPUT_PATH, version, version)):
    os.remove('%s/%s/combined_data_%s.csv' % (INPUT_PATH, version, version))

# Write the combined dataframe to a new csv file  
df.to_csv('%s/%s/combined_data_%s.csv' % (INPUT_PATH, version, version), index=False)  

 # Convert the combined csv file into a latex table using pandas built-in function  
latex_table = df.to_latex()  

 # Write the latex table to a text file  
with open('tables/acceptance_%s.tex' % version, 'w') as f: 
    f.write(latex_table)


# 



