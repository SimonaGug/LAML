import os
import logging
import re
import pandas as pd

logging.basicConfig(level=logging.INFO)


class PreLifting:
    dataframes_path: str

    def __init__(self, dataframes_path):
        self.dataframes_path = dataframes_path

    def pre_lift_grounded_conditions(self, dataframes_path, grounded_state_variables_path):
        state_variables_files = [os.path.join(grounded_state_variables_path, file) for file in os.listdir(grounded_state_variables_path) if file.endswith('.csv')]
        pre_lifted_folder_path = os.path.join(dataframes_path, "pre_lifted_state_variables")
        if not os.path.exists(pre_lifted_folder_path):
            os.makedirs(pre_lifted_folder_path)
        for i, c in enumerate(state_variables_files):
            df = pd.read_csv(c)
            match = re.search(r'\(before (.+)\)', df.columns[2])
            if match:
                condition = match.group(1)
            else:
                print(f"Something is wrong with {c}")
            parts = condition.split()
            condition_name = parts[0]
            variables_dic = {parts[i+1]: f'arg{i+1}' for i in range(len(parts)-1)}
            
            new_df = df.copy()          

            last_col_name = new_df.columns[-1]
            new_last_col_name = last_col_name
            for key, value in variables_dic.items():
                if re.search(rf'\b{re.escape(key)}\b', last_col_name):
                    new_last_col_name = re.sub(rf'\b{re.escape(key)}\b', value, new_last_col_name)
            after_col_name = new_last_col_name.replace("before", "after")
            new_df.columns = list(new_df.columns[:-2]) + [after_col_name] + [new_last_col_name]
            for index, row in new_df.iterrows():

                for col in new_df.columns[:-2]:
                    cell_value = row[col]
                    new_value = cell_value
                    match = re.search(r'\(([a-zA-Z-_]+) (.+)\)', cell_value)
                    if match:
                        variables = match.group(2).split(" ")
                    else:
                        variables = []

                    i = 0
                    for v in variables:
                        if v in variables_dic:
                            new_value = re.sub(rf'\b{re.escape(v)}\b', variables_dic[v], new_value)
                        else:
                            new_value = re.sub(rf'\b{re.escape(v)}\b', f"c{i}", new_value)
                            i = i + 1

                    new_df.at[index, col] = new_value
            new_file_name = pre_lifted_folder_path + f"\\{condition}.csv"
            new_df.to_csv(new_file_name, index=False)
            logging.debug(f"Saved lifted dataset: {new_file_name}")
        return pre_lifted_folder_path

    def lifting(self, dataframes_path, grounded_path, state_variable_or_action):
        grounded_files = [os.path.join(grounded_path, file) for file in os.listdir(grounded_path) if file.endswith('.csv')]
        lifted_dic = {}
        if state_variable_or_action == "var":
            lifted_path  = dataframes_path + f"\\lifted_state_variables"
        elif state_variable_or_action == "act":
            lifted_path  = dataframes_path + f"\\lifted_action"
        if not os.path.exists(lifted_path):
            os.makedirs(lifted_path) 
        
        for file in grounded_files:
            condition = os.path.basename(file).replace('.csv', '').split(" ")
            condition_name = condition[0]
            if condition_name not in lifted_dic:
                lifted_dic[condition_name] = []
            lifted_dic[condition_name].append(file)

        for condition_name, files in lifted_dic.items():
            logging.debug(f"Processing condition: {condition_name}")
            dfs = []

            for file in files:
                df = pd.read_csv(file)
                dfs.append(df)
            
            condition_arguments =  len(os.path.basename(file).replace('.csv', '').split(" "))-1
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                arg = ""
                for i in range(1, condition_arguments+1):
                    if state_variable_or_action == "var":
                        arg = arg + "arg" + str(i) + " "
                    else:
                        arg = arg + "o" + str(i) + " "
                file_name = condition_name + " " + arg
                merged_file_path = os.path.join(lifted_path, f"{file_name}.csv")  
                merged_file_path = merged_file_path.replace(" .csv", ".csv")          
                combined_df.to_csv(merged_file_path, index=False)
                logging.debug(f"Saved merged dataset: {merged_file_path}")
            else:
                print(f"No valid files to merge for condition: {condition_name}")

        return lifted_path

    def lifting_state_variables(self, dataframes_path, grounded_state_variables_path, state_variable_or_action):
        pre_lifted_folder_path = self.pre_lift_grounded_conditions(dataframes_path, grounded_state_variables_path)
        lifted_path = self.lifting(dataframes_path, pre_lifted_folder_path, state_variable_or_action) 
        return lifted_path

