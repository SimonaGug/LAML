from pathlib import Path

#insert here the folder path
HOME = "C:\\Users\\sgut6y\\Desktop\\PhD\\Code\\LAML"

LEARNED_DOMAIN_PATH = f"{HOME}\\LearnedDomains"
DATA_FRAMES_PATH = f"{HOME}\\DataFrames"
DATA_PATH = f"{HOME}\\GeneratedTriples"



DOMAINS = {1: 'driverlog', 2: 'depot', 4: 'zenotravel', 5: 'blocks', 6: 'gripper',  7: 'transport',  8: 'satellite',  9: 'floortile',  10: 'parking', 11: 'sokoban', 13: 'barman', 14: 'elevators', 15: 'ferry', 16: 'n-puzzle', 17: 'tpp', 18: 'hanoi', 19: 'spanner', 20: 'gold-miner', 21: 'nomystery',  22: 'rover', 23: 'grid', 24: 'miconic', 25: 'matching-bw'}
DOMAINS_NOLAM = {1: 'driverlog', 2: 'depots', 4: 'zenotravel', 5: 'blocksworld', 6: 'gripper', 7: 'transport',  8: 'satellite',  9: 'floortile',  10: 'parking', 11: 'sokoban', 13: 'barman', 14: 'elevators', 15: 'ferry', 16: 'n-puzzle', 17: 'tpp', 18: 'hanoi', 19: 'spanner',  20: 'gold-miner', 21: 'nomystery',  22: 'rover', 23: 'grid', 24: 'miconic',  25: 'matching-bw'}


PDDL_DOMAIN_DIC = {'elevator-example': 'elevator-example' , 'driverlog': 'driverlog', 'depot': 'depots', 'dwr':'dwr', 'zenotravel':'zeno-travel', 'blocks':'blocks', 'gripper':'gripper-strips',  'transport':'transport',  'satellite':'satellite',  'floortile':'floor-tile',  'parking':'parking', 'sokoban':'typed-sokoban', 'elevators':'elevators-sequencedstrips', 'barman':'barman', 'ferry':'ferry', 'n-puzzle': 'n-puzzle-typed', 'tpp': 'TPP-Propositional', 'hanoi': 'hanoi', 'spanner': 'spanner', 'gold-miner': 'gold-miner-typed', 'nomystery': 'transport-strips', 'rover': 'rover', 'grid': 'grid', 'miconic' : 'miconic',  'matching-bw': 'matching-bw-typed'}




NOISE_PROB = [0.0 , 0.1, 0.2, 0.3, 0.4]