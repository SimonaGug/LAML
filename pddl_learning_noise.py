from collections import defaultdict
import os
import re

import logging
logging.basicConfig(level=logging.INFO)

class Pddl:
    preconditions : dict    
    effects : dict
    domain_name : str
    learned_domain_filename : str
    actions : dict

    def __init__(self, preconditions, effects, domain_name, learned_domain_filename, actions):
        self.preconditions = preconditions
        self.effects = effects
        self.domain_name = domain_name
        self.learned_domain_filename = learned_domain_filename
        self.actions = actions


    def convert_conditions_pddl(self, conditions):
        conditions_new = {}
        for key, values in conditions.items():
            cond_list = []
            for value in values:
                negation = False
                if "False" in value:
                    value = value.replace(" = False", "")
                    condition_name = "not (" + value.split(maxsplit=1)[0]
                    negation = True
                else:
                    value = value.replace(" = True", "")
                    condition_name = value.split(maxsplit=1)[0]
                
                if len(value.split(maxsplit=1)) > 1:
                    condition_expression = value.split(maxsplit=1)[1]
                else:
                    condition_expression = value
                condition_parameters = value.replace(" = ", "").split(" ")[1:]
                cond = ""
                for parameter in condition_parameters:
                    cond = cond + " ?" + parameter
                cond = condition_name + cond
                if negation:
                    cond = cond + ")"
                cond_list.append(cond)
            key_elements = key.split(" ")
            action_name = key_elements[0]
            action_parameters = key_elements[1:]
            action = ""
            for parameter in action_parameters:
                action = action + " ?" + parameter
            action = action_name + action
            conditions_new[action] = cond_list

        return conditions_new

    def find_predicates(self, preconditions, effects):
    #    predicates = {}
        predicates_list = []
        for action, conditions in preconditions.items():       
            for condition in conditions:
                condition = condition.replace("not ", "").replace("(", "")
                if len(condition.split(" ", 1))>1:
                    condition_name, condition_arg = condition.split(" ", 1)
                    new_cond =condition_name +  " " + ''.join(char for char in condition_arg if char.isalpha() or char.isspace() or char == '?' or char == '-' or char == '_')
                else:
                    new_cond = condition.replace(")", "").replace(" ", "")
                #counting 
                counts = {}
                parts = new_cond.split()
                objects = parts[1:]
                new_cond = parts[0]
                for o in objects:
                    if o in counts:
                        counts[o] += 1
                        new_cond += f" {o}{counts[o]}"
                    else:
                        counts[o] = 1
                        new_cond +=f" {o}"
                if new_cond not in predicates_list:
                    predicates_list.append(new_cond)
        for action, conditions in effects.items():
            for condition in conditions:
                condition = condition.replace("not ", "")
                new_cond =''.join(char for char in condition if char.isalpha() or char.isspace() or char == '?' or char == '-' or char == '_')
                #counting 
                counts = {}
                parts = new_cond.split()
                objects = parts[1:]
                new_cond = parts[0]
                for o in objects:
                    if o in counts:
                        counts[o] += 1
                        new_cond += f" {o}{counts[o]}"
                    else:
                        counts[o] = 1
                        new_cond +=f" {o}"
                if new_cond not in predicates_list:
                    predicates_list.append(new_cond)   
        return predicates_list


    def get_type_hierarchy(self, type_dict):
        # Group child types by their parent type
        hierarchy = defaultdict(list)
        for child, parent in type_dict.items():
            hierarchy[parent].append(child)

        # Build the formatted string
        sorted_parents = sorted(hierarchy.keys())
        result = []
        for parent in sorted_parents:
            children = sorted(hierarchy[parent])
            if parent == "object":
                # For the top-level parent "object"
                result.append(f"    {' '.join(children)} - {parent}")
            else:
                result.append(f"    {' '.join(children)} - {parent}")

        return f"  (:types\n{result[0]}\n" + "\n".join(result[1:]) +   ") \n"

    def generate_pddl_domain_file(self, preconditions, effects, domain_name, actions, types):
        pddl_domain = f"(define (domain {domain_name})\n"
        pddl_domain += "  (:requirements :strips)\n"
        
        pddl_domain += self.get_type_hierarchy(types)
        # Define predicates
        predicates = self.find_predicates(preconditions, effects)    
        pddl_domain += "  (:predicates\n"
        for predicate in predicates:
            parts = predicate.split()
            part_with_type = []
            for p in parts[1:]:
                t = re.split(r'\d', p)[0].replace("?", "")
                part_with_type.append(f"{p} - {t}")
            preficate_string = parts[0] + " " + f"{' '.join(part_with_type)}"
            pddl_domain += f"    ({preficate_string})\n"
        pddl_domain += "  )\n\n"
        for action, conditions in preconditions.items():
            action_name = action.split(maxsplit=1)[0]
            #for validation purposes
            #if domain_name == "satellite":
            #    action_name = action_name.replace("-", "_")
            pddl_domain += f"  (:action {action_name}\n"
            
            parts = action.split()[1:]
            part_with_type = []
            for p in parts:
                p = p.replace("_", "")
                t = re.split(r'\d', p)[0].replace("?", "")
                part_with_type.append(f"{p} - {t}")
            parameters = f"{' '.join(part_with_type)}"

            pddl_domain += f"    :parameters ({parameters})\n"
            pddl_domain += "    :precondition (and\n"
            for precondition in conditions:
                pddl_domain += f"      ({precondition})\n"
            pddl_domain += "    )\n"
            pddl_domain += "    :effect (and\n"
            for effect in effects[action]:
                pddl_domain += f"      ({effect})\n"
            pddl_domain += "    )\n"
            pddl_domain += "  )\n\n"
        
        pddl_domain += ")"
        return pddl_domain


    def get_type_mapping(self, action_name, actions):
        types = actions.get(action_name, [])
        return {f'o{i+1}': types[i] for i in range(len(types))}


    def update_with_action_type(self, condition_dic, actions):
        updated_conditions = {}
        for action_key, conditions_list in condition_dic.items():
            action_name = action_key.split()[0]
            type_mapping = self.get_type_mapping(action_name, actions)
            
            modified_action_key = action_key
            for o_key, o_value in type_mapping.items():
                modified_action_key = modified_action_key.replace(o_key, o_value)
            
            modified_cond_list = []
            for cond in conditions_list:
                modified_condition = cond
                for o_key, o_value in type_mapping.items():
                    modified_condition = modified_condition.replace(o_key, o_value)
                modified_cond_list.append(modified_condition)
            
            updated_conditions[modified_action_key] = modified_cond_list

        return updated_conditions



    def pddl(self, general_preconditions, general_effects, domain_name, learned_domain_filename, actions, types):
        

        
        general_preconditions_pddl = self.convert_conditions_pddl(general_preconditions)
        general_effects_pddl = self.convert_conditions_pddl(general_effects)

        pddl = self.generate_pddl_domain_file(general_preconditions_pddl, general_effects_pddl, domain_name, actions, types)


        directory = os.path.dirname(learned_domain_filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(learned_domain_filename, 'w+') as domain_file:
            domain_file.write(pddl)
