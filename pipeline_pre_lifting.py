import shutil
import os
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
from refactor_data import Refactorization
from pre_processing import PreProcessing
from lifting_conditions import PreLifting
from run_DTs_learning import C50
from preconditions_from_DTs import Preconditions
from find_effects import Effects
from pddl_learning_noise import Pddl

logging.basicConfig(level=logging.INFO)


def pipeline_pre_lifting(traces, dataframes_path, domain_name, learned_domain_filename, actions, types):
    try:
        if os.path.isdir(dataframes_path):
            for filename in os.listdir(dataframes_path):
                file_path = os.path.join(dataframes_path, filename)
                
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                    logging.debug(f"File '{file_path}' successfully removed.")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    logging.debug(f"Directory '{file_path}' successfully removed.")
        else:
            print(f"The path '{dataframes_path}' is not a directory.")
    except Exception as e:
        print(f"An error occurred while removing files in '{dataframes_path}': {e}")
    

    logging.info("\nRunning Refactorization...")
    refactorization_obj =  Refactorization(traces)
    refactorization_obj.refactor_data_noise(traces)
    
    if not os.path.exists(dataframes_path):
        os.makedirs(dataframes_path)

    logging.info("\nRunning PreProcessing...")
    preproc_obg = PreProcessing(traces, dataframes_path)
    grounded_state_variables_path = preproc_obg.conditions_preproc(traces, dataframes_path)
    grounded_action_path =  preproc_obg.actions_preproc(traces, dataframes_path)

    logging.info("\nRunning Pre Lifting...")
    pre_lifting = PreLifting(dataframes_path)
    lifted_state_variables_path = pre_lifting.lifting_state_variables(dataframes_path, grounded_state_variables_path, "var")
    lifted_actions_path = pre_lifting.lifting(dataframes_path, grounded_action_path, "act")

    logging.info("\nRunning C50...")
    C50_object = C50(lifted_state_variables_path) 
    exit_loop = False   
    while not exit_loop:
        result = C50_object.run_c50(lifted_state_variables_path)
        
        if "empty" in str(result):
            logging.debug("The result is empty.")
            start_index = str(result).find('file ') + len('file ')
            end_index = str(result).find('.csv') + len('.csv')
            file_path = str(result)[start_index:end_index]            
            try:
                os.remove(file_path)
                logging.info(f"File '{file_path}' successfully removed.")
            except FileNotFoundError:
                logging.info(f"File '{file_path}' not found.")
            except Exception as e:
                logging.info(f"An error occurred while removing the file: {e}")
        else:
            logging.debug("The result is not empty. Exiting loop.")
            exit_loop = True

    logging.info("\nRunning Preconditions...")
    preconditions_obj = Preconditions(lifted_state_variables_path)
    preconditions = preconditions_obj.find_preconditions(lifted_state_variables_path)

    logging.info("\nRunning Effects...")
    effect_obj = Effects(traces, preconditions, dataframes_path)
    effects_percentages, effects = effect_obj.find_effects(preconditions, lifted_actions_path)

    logging.debug("Precondition\n", preconditions)
    logging.debug("\nEffects\n", effects)
    logging.debug("Effects_percentages\n", effects_percentages)

    logging.info("\nRunning Pddl...")
    pddl_obj = Pddl(preconditions, effects, domain_name, learned_domain_filename, actions)
    
    general_preconditions =  pddl_obj.update_with_action_type(preconditions, actions)
    general_effects =  pddl_obj.update_with_action_type(effects, actions)    

    domain_name = config.PDDL_DOMAIN_DIC[domain_name]
    pddl_obj.pddl(general_preconditions, general_effects, domain_name, learned_domain_filename, actions, types)

    return 


if __name__ == "__main__":

    sorted_domains = dict(sorted(config.DOMAINS.items(), key=lambda item: item[1]))


    for key, domain_name in sorted_domains.items():
        domain_name_NOLAM = config.DOMAINS_NOLAM[key].lower()

        with open('domain_mappings.json', 'r') as file:
                domain_mappings = json.load(file)
        types = domain_mappings[domain_name]["types"]
        actions = domain_mappings[domain_name]["actions"] 

        metrics = {}
        for p in config.NOISE_PROB: 
            dataframes_path =  config.DATA_FRAMES_PATH + f'\\{domain_name}\\{p}'
            if not os.path.exists(dataframes_path):
                os.makedirs(dataframes_path)
            traces = f"{config.DATA_PATH}\\{domain_name}\\Noisy\\{domain_name}-reconstructed-NOLAM-{p}-v2-full.csv"
            learned_domain_filename = config.LEARNED_DOMAIN_PATH + f"\\{domain_name}\\Noisy\\my-learned-domain-{p}.pddl"
            
            logging.debug(dataframes_path)

            pipeline_pre_lifting(traces, dataframes_path, domain_name, learned_domain_filename, actions, types)
            