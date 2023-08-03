# Merge numpy arrays properly and convert it to h5 file
import numpy as np
import h5py
import os
import sys

def main():
    
    # Path to the directory containing the numpy arrays
    INPUT_PATH = sys.argv[1]

    # Path to the directory where the h5 file will be saved
    OUTPUT_PATH = sys.argv[2]
    
    # Create output directory
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    # Define arrays to store data
    arrays = {'X_train': np.array([]), 'Y_train': np.array([]), 'X_val': np.array([]), 'Y_val': np.array([]), 'X_test': np.array([]), 'Y_test': np.array([])}
    
    # Loop over train/val/test subdirs
    for dataset in ['train','val','test']:
    
        # List of input files 
        input_files = os.listdir(os.path.join(INPUT_PATH, dataset))

        # Loop over input files
        for input_file in input_files:

            # Read the input file
            input_array = np.load(os.path.join(INPUT_PATH, dataset, input_file))

            # Create numpy array for labels
            if ('susy' in input_file) or ('gluino' in input_file):
                labels_array = np.ones(np.shape(input_array)[0],)
            else:
               labels_array = np.zeros(np.shape(input_array)[0],)

            # Merge numpy arrays
            if arrays['X_'+dataset].size == 0: 
                arrays['X_'+dataset] = input_array
                arrays['Y_'+dataset] = labels_array 
            else:
                arrays['X_'+dataset] = np.concatenate((arrays['X_'+dataset], input_array))
                arrays['Y_'+dataset] = np.concatenate((arrays['Y_'+dataset], labels_array)) 

    # Rename keys to fit Roberto's code
    arrays['y_val'] = arrays.pop('Y_val')
    arrays['y_test'] = arrays.pop('Y_test')

    # Print the shape of the arrays
    print('Shape of X_train:', np.shape(arrays['X_train']))
    print('Shape of Y_train:', np.shape(arrays['Y_train']))
    print('Shape of X_val:', np.shape(arrays['X_val']))
    print('Shape of y_train:', np.shape(arrays['y_val']))
    print('Shape of X_test:', np.shape(arrays['X_test']))
    print('Shape of y_test:', np.shape(arrays['y_test']))

    # Count number of signal and background events in y_test
    
    print('Number of signal events in train: ', np.count_nonzero(arrays['Y_train']))
    print('Number of background events in train: ', np.count_nonzero(arrays['Y_train'] == 0))
    print('Number of signal events in val: ', np.count_nonzero(arrays['y_val']))
    print('Number of background events in val: ', np.count_nonzero(arrays['y_val'] == 0))
    print('Number of signal events in test: ', np.count_nonzero(arrays['y_test']))
    print('Number of background events in test: ', np.count_nonzero(arrays['y_test'] == 0))

    # Convert to h5 file
    with h5py.File(os.path.join(OUTPUT_PATH, 'DarkMachines.h5'), 'w') as hf:
        for k, v in arrays.items():
            hf.create_dataset(k, data=v)

if __name__ == "__main__":
    print("Example: python make_h5.py /data/ML/DarkMachines/arrays /data/ML/DarkMachines/h5")
    main()
