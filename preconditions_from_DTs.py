import pandas as pd
import re
import os
import config
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)

class Preconditions:  
    domain_name : str

    def __init__(self, domain_name):
        self.domain_name = domain_name    

    def extract_rules_from_C50(self, rules, preconditions_dic, condition):
       
        rule_line = 10000
        decision = ""
        rule = ""
        no_preconditions = True
        with open (rules, 'rt') as myfile:   
            for Ln, current_line in enumerate(myfile,1): 
                if "has only one value" in current_line:
                    value = re.search(r"has only one value `([^']+)'", current_line).group(1)
                    csv_file = rules.replace(" .txt", ".csv")
                    df = pd.read_csv(csv_file)
                    if value == "True" or value == "False":
                        action_list = df.iloc[:, 0].unique()
                        for a in action_list:
                            a = a.replace("(","").replace(")","")
                            if a not in preconditions_dic:
                                preconditions_dic[a] = []
                            preconditions_dic[a].append(condition + " = " + value)  
                            no_preconditions = False
                        return preconditions_dic
                    else: 
                        a = value.replace("(", "").replace(")", "")
                        value = str(df.iloc[:, -1].value_counts().idxmax())
                        if a not in preconditions_dic:
                            preconditions_dic[a] = []
                        preconditions_dic[a].append(condition + " = " + value) 
                        no_preconditions = False
                        return preconditions_dic
                            
                elif "Rule " in current_line:
                    decision = ""
                    rule_line = Ln 
                    action_list=[]             
                #action line
                elif "-> " in current_line:
                    rule_line = Ln + 1
                    decision = current_line.split("class ")[1].split("  [")[0]
                    if decision == "True":
                        for a in action_list:
                            if a not in preconditions_dic:
                                preconditions_dic[a] = []
                            preconditions_dic[a].append(condition + " = True")  
                            no_preconditions = False
                        action_list=[]  
                elif "Default class" in current_line:
                    if no_preconditions:
                        value = re.search(r"Default class: (True|False)", current_line).group(1)
                        csv_file = rules.replace(" .txt", ".csv")
                        df = pd.read_csv(csv_file)
                        action_list = df.iloc[:, 0].unique()
                        for a in action_list:
                            a = a.replace("(","").replace(")","")
                            if a not in preconditions_dic:
                                preconditions_dic[a] = []
                            preconditions_dic[a].append(condition + " = " + value)  
                    return preconditions_dic
                #Rule conditions
                elif Ln > rule_line: 
                    rule_elements = current_line.replace("\t", "").replace("}","").replace("\t", "").replace("\n", "").replace("   ", "").replace("  ", "").replace("Decision in {", "").replace("}", "").replace("Decision = ", "").replace("Feature in {", "").replace("Feature = ", "")
                    rule_elements_set = rule_elements.split(", ")
                    for idx, el in enumerate(rule_elements_set):
                        el = el.replace("(","").replace(")","").replace(",","")
                        action_list.append(el)
    
    def merge_preconditions(self, preconditions):
        new_preconditions = {}
        for key, values in preconditions.items():
            key_parts = key.split()
            key_name = key_parts[0]
            key_variables = key_parts[1:]
            variable_mapping  = {}
            for i, v in enumerate(key_variables):
                variable_mapping [v] = "o" + str(i+1)
            if len(key_variables)> len(variable_mapping.keys()):
                continue
            normalized_key = key
            for original_var, normalized_var in variable_mapping.items():
                normalized_key = normalized_key.replace(original_var, normalized_var)
            normalized_values = []
            for condition in values:
                for original_var, normalized_var in variable_mapping.items():
                    condition = condition.replace(original_var, normalized_var)
                normalized_values.append(condition) 
            if normalized_key not in new_preconditions:
                new_preconditions[normalized_key] = []
            new_preconditions[normalized_key].extend(normalized_values)
        return new_preconditions
        

    def find_preconditions(self, dataframes_path):
        preconditions_dic = {}
        rule_files = [os.path.join(dataframes_path, file) for file in os.listdir(dataframes_path) if file.endswith('.txt')]
        for file_path in rule_files:
            logging.debug(file_path)
            with open(file_path, 'rt') as file:
                content = file.read()
                if "attribute `Decision' has only one value" in content:
                    try:
                        os.remove(file_path)
                        os.remove(file_path.replace(".txt", ".csv"))
                        logging.info(f"File '{file_path}' successfully removed.")
                    except FileNotFoundError:
                        logging.info(f"File '{file_path}' not found.")
                    except Exception as e:
                        logging.info(f"An error occurred while removing the file: {e}")
                    continue
                else:
                    condition = file_path.replace(dataframes_path, "").replace(" .txt", "").replace("\\", "")
                    preconditions_dic = self.extract_rules_from_C50(file_path, preconditions_dic, condition)

        preconditions_dic_sorted = dict(sorted(preconditions_dic.items()))
        preconditions = self.merge_preconditions(preconditions_dic_sorted)
    
        
        return preconditions
