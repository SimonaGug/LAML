import pandas as pd
import logging
import os
import re

logging.basicConfig(level=logging.INFO)

class PreProcessing:
    domain_name : str
    folder_path: str

    def __init__(self, traces, folder_path):
        self.traces = traces
        self.folder_path = folder_path

    def conditions_preproc(self,traces, dataframes_path):

        grounded_state_variables_path = f"{dataframes_path}" + "\\grounded_state_variables"
        if not os.path.exists(grounded_state_variables_path):
            os.makedirs(grounded_state_variables_path)

        traces = traces.replace("-full.csv", "-refactored.csv")
        df_full = pd.read_csv(traces, low_memory=False)
        df_full = pd.DataFrame(df_full)

        num_before_columns = sum(df_full.columns.str.count('before'))
        df = pd.concat([df_full.iloc[:, :num_before_columns], df_full.iloc[:, -1]], axis=1)

        for i, col in enumerate(df.columns[:-1]):
            condition = col.replace("(before ", "").replace(")","")
            logging.debug(condition)
            conditions_varibles = condition.split(" ")[1:]
            raws_to_remove =[]
            action_names = []
            for index, j in df[df.columns[-1]].items():
                action = j.replace("(", "").replace(")","")
                action_variable = action.split(" ")[1:] 
                action_name = action.split(" ")[0] 
                if not all(elem in action_variable for elem in conditions_varibles):
                    raws_to_remove.append(index)
                action_names.append(action_name)
            df_actions = pd.DataFrame(action_names, columns=['Name'])
            
            df_hot_encoded = df_full[[df.columns[-1], df_full.columns[i+num_before_columns], col ]]

            df_hot_encoded = df_hot_encoded.drop(raws_to_remove)
            

            file_name = f'{grounded_state_variables_path}/' + str(condition) + '.csv'
            df_hot_encoded.to_csv(file_name, encoding='utf-8', index=False)
        return grounded_state_variables_path
    
    def actions_preproc(self, traces, dataframes_path):
        grounded_action_path = f"{dataframes_path}" + "\\grounded_actions"
        if not os.path.exists(grounded_action_path):
            os.makedirs(grounded_action_path)   
        traces = traces.replace("-full.csv", "-refactored.csv")
        df = pd.read_csv(traces, low_memory=False)
        action_names = df['Decision'].unique()
        for a in action_names:
            action_df = pd.DataFrame(df)
            action_df = action_df[action_df["Decision"] == str(a)]

            action_parts = a.replace("(","").replace(")", "").split()
            action_name = action_parts[0]
            action_variables = action_parts[1:]
            variable_mapping = {}
            for i, v in enumerate(action_variables):
                variable_mapping [v] = "o" + str(i+1)
                action_df['Decision'] = action_df['Decision'].str.replace(rf'\b{re.escape(v)}\b', f"o{i+1}", regex=True)

            
            columns_to_drop = []
            for col in action_df:
                col_parts = col.replace("(","").replace(")", "").replace("before ","").replace("after ","").split()
                col_name = col_parts[0]
                col_variables = col_parts[1:]
                if len(col_variables)>0 and not all(var in variable_mapping for var in col_variables):
                    columns_to_drop.append(col)
                else:
                    col_new = col
                    for original_var, normalized_var in variable_mapping.items():
                        col_new = re.sub(rf'\b{re.escape(original_var)}\b', normalized_var, col_new)
                    
                    action_df.rename(columns={col: col_new}, inplace=True)

            action_df = action_df.drop(columns=columns_to_drop)
            file_name = grounded_action_path + "\\" + str(a.replace("(", "").replace(")", "")) + '.csv'
            action_df.to_csv(file_name, encoding='utf-8', index=False)
        return grounded_action_path