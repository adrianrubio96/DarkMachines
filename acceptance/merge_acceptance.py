# Read csv files and merge all 2nd lines into one csv file, and convert it to a latex table

import pandas as pd 
import glob

INPUT_PATH = "/lhome/ific/a/adruji/DarkMachines/DataPreparation/acceptance/csv/"

# Create a list of all the csv files in the current directory 
csv_list = glob.glob('%s/*.csv' % INPUT_PATH) 
print(csv_list)

# Create an empty dataframe to store all the data 
df = pd.DataFrame() 

# Write the combined dataframe to a new csv file  
df.to_csv('combined_data.csv', index=False)  

 # Convert the combined csv file into a latex table using pandas built-in function  
latex_table = df.to_latex()  

 # Write the latex table to a text file  
with open('latex_table.tex', 'w') as f: 
    f.write(latex_table)




