import pandas as pd
import logging
import config
import numpy as np

logging.basicConfig(level=logging.INFO)

class Refactorization:
    traces : str
    only_current_state : bool

    def __init__(self, traces, only_current_state=False):
        self.traces = traces


    def refactor_data_noise(self, traces, seed = 0):
        # Load the dataset and set random seed for reproducibility
        df = pd.read_csv(traces, low_memory=False)
        np.random.seed(seed)
        logging.debug("initial shape %s", df.shape)
        
        df = df.map(lambda x: True if str(x).lower() == 'true' 
                              else False if str(x).lower() == 'false' 
                              else x)
        
        actions = df.pop('action')      
        
        columns_to_drop = []
        columms_same_value = []
        for col in df.columns:
            parts = col.replace("(before ", "").replace(")", "").split()
            variables = parts[1:]
            if len(variables) != len(set(variables)):
                columns_to_drop.append(col)
            else:
                unique_values = df[col].unique()
                if 'before' in col.lower() and (set(unique_values) <= {True, ' '} or set(unique_values) <= {False, ' '}):
                    non_null_indices = df.index[df[col].apply(lambda x: isinstance(x, bool))].tolist()
                    if non_null_indices:
                        idx_to_change = np.random.choice(non_null_indices)
                        # Introduce synthetic noise by flipping the value at a random index
                        if df.loc[idx_to_change, col] == True:
                            df.loc[idx_to_change, col] = False
                        elif df.loc[idx_to_change, col] == False:
                            df.loc[idx_to_change, col] = True
                    columms_same_value.append(col)           

        df = df.drop(columns=columns_to_drop)
        df = df.copy()
        df["Decision"] = actions
        df = df.drop_duplicates()       
        logging.debug("final shape %s", df.shape)
        logging.debug("Number of unique rows %s", df.shape[0])

        df.to_csv(traces.replace("-full.csv", "-refactored.csv"), index=False)


