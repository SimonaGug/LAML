import pandas as pd
import os
import glob
import config
from preconditions_from_DTs import Preconditions 
from lifting_conditions import PreLifting 


import logging
logging.basicConfig(level=logging.INFO)

class Effects:
    traces: str
    preconditions: dict
    new_data: bool
    dataframes_path: str

    def __init__(self, traces, preconditions, dataframes_path, new_data = True):
        self.traces = traces
        self.preconditions = preconditions
        self.dataframes_path = dataframes_path
        self.new_data = new_data

    def compute_effect_one_action(self, traces):

        data = pd.read_csv(traces)
        #print(data.shape)

        counters_dic = dict()
        percentages_dic = dict()
        numeric_sum = dict()

        columns_variables_idx = [i for i, col in enumerate(data.columns) if 'before' in col.lower()]
        #counters dic count how many times the state variable changes to the key value 

        for c in data.iloc[:, columns_variables_idx]:
            counters_dic[c] = {}
            counters_dic[c]['Unchanged_False'] = 0
            counters_dic[c]['Unchanged_True'] = 0

        for index, row in data.iterrows():
            for c in data.iloc[:, columns_variables_idx]:                  
                if row[c] != row[str(c).replace("before", "after")]: 
                    if isinstance(row[c], bool):
                        key = str(row[str(c).replace("before", "after")])
                        if str(row[str(c).replace("before", "after")]) not in counters_dic[c]:
                            counters_dic[c][key] = 1
                        else:
                            counters_dic[c][key] += 1                    
                    elif isinstance(row[c], float):
                        continue
                    else:
                        if isinstance(counters_dic[c], dict):
                            counters_dic[c] = 0
                            numeric_sum[c] = 0
                        counters_dic[c] += 1
                        numeric_sum[c] += (row[str(c).replace("before", "after")] - row[c])
                else:
                    if row[c] == False:
                        counters_dic[c]['Unchanged_False'] += 1
                    else:
                        counters_dic[c]['Unchanged_True'] += 1

        percentages_dic = {}
        deltas_dic = {}
        effect_list = []
        NoData= False
        for c in data.iloc[:, columns_variables_idx]:
            if counters_dic[c]:
                state_variable = c.replace("(before ", "").replace(")", "")
                if state_variable not in percentages_dic:
                    percentages_dic[state_variable]= {}        
                for key in counters_dic[c]:
                    if index != 0:
                        percentages_dic[state_variable][key] = counters_dic[c].get(key)/(index+1)*100 
                    else:
                        NoData = True
                        percentages_dic[state_variable][key] = 100                
                
                max_value = max(percentages_dic[state_variable].values())
                most_common_keys = [key for key, value in percentages_dic[state_variable].items() if value == max_value]
                for most_common in most_common_keys:   
                    if most_common != "Unchanged_False" and most_common!= "Unchanged_True":
                        effect_list.append(state_variable + " = " + str(most_common))     
        if NoData:
            logging.debug(f"You have only one datapoint in this file: {traces}")    
        return percentages_dic, effect_list
            


    def find_effects(self, preconditions, action_path):
    
        effects_percentages_dic = dict()
        effects_dic = dict()

        csv_files = [os.path.join(action_path, file) for file in os.listdir(action_path) if file.endswith('.csv')]

        for i, a in enumerate(csv_files):
            logging.debug("Beginning of the main for loop\n")
            a = a.replace(action_path + "\\", "").replace(".csv", "")
            logging.debug(a)
            data = csv_files[i]
        
            if a in preconditions:
                preconditions_list = preconditions[a]
                effects_percentages_dic[a], effects_dic[a] = self.compute_effect_one_action(data)
            else:
                print("Action ", a, "does not have any precondition, therefore it is not learned")
            logging.debug(a)     
            logging.debug("End of the main for loop\n")
        logging.debug(effects_percentages_dic)
        logging.debug(effects_dic)
        return effects_percentages_dic, effects_dic

