"""This script is used to generate ClearSMILES from a csv file,
it main use case is to be use during a SLURM job array 
"""
import os
import csv
import time
import re
from pathlib import Path
import argparse
from multiprocessing import Pool
from functools import partial
import numpy as np
from rdkit import Chem
import pyarrow as pa
import pyarrow.parquet as pq

def wrapper_csv_reader(csv_path : str,
                       first_idx : int,
                       last_idx : int,
                       extra_idx : int
                       ) -> list:
    """This function purpose is to read a chunk of data from a csv file

    Args:
        csv_path (string):  the path to the csv file
        first_idx (integer) : the first index to be read
        last_idx (integer) : the last index to be read 
        extra_idx (integer) :  optional,an extra index for load balancing 


    return:
        data_list (list of dictionnary): list of dictionaries containing columns names 
        as keys and and values of the row as values 
    """
    # declare local variables
    data_list= []
    temp_values=[]
    temp_dict={}

    # open file 
    with open(csv_path,encoding="utf-8") as csv_file: 
        csv_reader = csv.reader(csv_file)

        # get header
        header = next(csv_reader)  # Assuming the first row is the header
        keys_list= header
        nb_keys= len (keys_list)

        # iterate through file
        for i,row in enumerate(csv_reader):
            # declare loop variable
            read_line = False

            # assess if line should be read
            if i < first_idx :
                continue
            if  first_idx <=i<last_idx:
                read_line = True
            elif extra_idx:
                if  last_idx>= i < extra_idx:
                    continue
                if i ==extra_idx:
                    read_line=True
                elif i> extra_idx:
                    break
            else:
                break

            # read line and package it as a dictionnary
            if read_line:
                temp_values= row
                nb_values=len(temp_values)
                assert nb_values == nb_keys, f"Discrepancy between the number of values in row\
                    ({nb_values}) and number of columns detected in header \
                        ({nb_keys}), this happened for line : {i+1} "
                temp_dict= {keys_list[i]:temp_values[i] for i in range(nb_keys)}
                data_list.append(temp_dict)

    return data_list

def find_biggest_digits(smiles=str()):
    """
    find the biggest digits by iterating throught possible max digits 
    and test if there is a match in string
    input: smiles (string)
    output: max_digit (integer)
    """

    ### iterate through max digits possible solution
    for i in range(1,10):
        digit=10-i
        if smiles.find(str(digit))!=-1:
            return digit
    
    return 0

def get_semantic_mem_map(smiles :str,smiles_regex : re.compile) -> np.array :
    """
    This function will generate a semantic memory map of a SMILES, 
    i.e the number of semantic feature open for every token. 
    Semantic feature include  branches and  rings 
        smiles (string) : a valid SMILES 
        smiles_regex (compiled regular expression): compiled regular expression 
        used to tokenize SMILES
        bonds_set (set of strings): a set containing all the bonds tokens
    output :
        mem_map  (numpy array):  the semantic memory map of the input SMILES
    """

    ### declare local variables
    tokens_list=smiles_regex.findall(smiles)
    mem_map= np.zeros(len(tokens_list),dtype=int)
    digit_set=set()

    ### iterate throught tokens 
    for i,token in enumerate(tokens_list):
        if token=="(":
            mem_map[i]+= 1
        elif token==")":
            mem_map[i]-=1
        elif token.isdigit():
            if token in digit_set:
                digit_set.remove(token)
                mem_map[i]-= 1
            else:
                digit_set.add(token)
                mem_map[i]+= 1
   
    return mem_map.cumsum()

def get_clearsmiles(params_dict : dict, nb_random : int, smiles_regex : re.compile("")) -> dict :
    """
    This function will get a set of ClearSMILES, this is a stochastic process, 
    thus the number of ClearSMILES may vary. A high number of random search  should yield 
    a stable number of ClearSMILES
    input :
        smiles (string): a valid SMILES 
        nb_random (integer): the number of randomized kekule SMILES to generate,
        i.e the number of random search
        smiles_regex (compiled regex):  regex pattern used to tokenize SMILES 
    output: 
    results dict with string as keys and  various type of values 
         nb_random  input is pass as such in 
        max digit (integer), indicating the lowest maximum digit found in random SMILES
        lowest_mem_score (float), indicates the lowest score obtained 
        by one or more ClearSMILES, currently the mean of semantic memory per token
        nb_unique_random_smiles (integer), number of unique randomized kekule SMILES
        found by random search 
        nb_lowest_max_digit_smiles (integer), number of randomized kekule SMILES 
        with the lowest max digit found
        nb_equivalent_solution  (integer) , which indicate the number of solution 
        which achieved the lowest memory score 
        ClearSMILES_set, value is (string): concatenation of the ClearSMILES_set 
        as a string using "_" as a separator 
        all keys including keyword time contains the duration of each stage of the pipeline,
        and value associated are float
        
    """
    # assert that there is a smiles key 
    assert "SMILES" in params_dict, " the SMILES key was not found in param_dict \
        please, ensure that the columns with smiles is named as SMILES in uppercase"

    ### declare local variable 
    mol = Chem.MolFromSmiles(params_dict["SMILES"])
    lowest_digit_smiles_set= set()
    lowest_mem_score_smiles_set=set()
    results_dict={
        "nb_random" : nb_random,
        "max_digit" : 9 ,
        "lowest_mem_score" : np.inf,
        "nb_unique_random_smiles" : int,
        "nb_lowest_max_digit_smiles" : int,
        "nb_equivalent_solution" : 0,
        "ClearSMILES_set" : str,
        "random_gen_time" : float,
        "min_max_digit_time" : float,
        "mem_map_time" : float,
        "total_time" : time.perf_counter(), # neglect the time to instantiate mol + empty sets
    }
    results_dict.update(params_dict)

    ### generate randomized kekule SMILES
    start_time= time.perf_counter()
    randomized_kekule_smiles_set= set(Chem.MolToRandomSmilesVect(mol,nb_random, kekuleSmiles=True))
    results_dict["nb_unique_random_smiles"]= len(randomized_kekule_smiles_set)
    results_dict["random_gen_time"]= time.perf_counter() -start_time

    ### find SMILES with lowest maximum digit
    start_time= time.perf_counter() 
    for rd_smiles in randomized_kekule_smiles_set:

        ### declare loop variable 
        temp_max_digit= find_biggest_digits(rd_smiles)

        ### if a new minimum is reach clear the set
        if temp_max_digit < results_dict["max_digit"]:
            lowest_digit_smiles_set.clear()
            results_dict["max_digit"]=temp_max_digit

        ### discard smiles if above current threshold
        elif temp_max_digit > results_dict["max_digit"]:
            continue

        lowest_digit_smiles_set.add(rd_smiles)
    results_dict["nb_lowest_max_digit_smiles"]= len(lowest_digit_smiles_set)
    results_dict["min_max_digit_time"]= time.perf_counter() -start_time    

    ### Keep SMILES with lowest maximum digit for which the semantic memory score is minimal
    start_time= time.perf_counter() 
    for ld_smiles in lowest_digit_smiles_set:

        ### declare loop variable
        mem_map = get_semantic_mem_map(ld_smiles,smiles_regex)
        temp_mem_score= np.mean(mem_map)

        ### if a new minimum is reached, clear the set
        if temp_mem_score< results_dict["lowest_mem_score"] :
            lowest_mem_score_smiles_set.clear()
            results_dict["lowest_mem_score"]= temp_mem_score

        ### discard SMILES if mem score threshold is passed 
        elif temp_mem_score > results_dict["lowest_mem_score"]:
            continue

        lowest_mem_score_smiles_set.add(ld_smiles)
    results_dict["mem_map_time"]= time.perf_counter() -start_time  

    ### concatenate found ClearSMILES as string
    results_dict["ClearSMILES_set"] = "_".join(lowest_mem_score_smiles_set)
    results_dict["nb_equivalent_solution"]= len(lowest_mem_score_smiles_set)

    ### compute total time duration 
    results_dict["total_time"]= time.perf_counter() - results_dict["total_time"]

    return results_dict

def main(input_csv: str,
         output_filepath : str,
         nb_smiles : int,
         nb_random : int,
         nb_core : int,
         job_id : int ,
         job_array_size : int,
         ) -> None:
    """ generate ClearSMILES for a chunck of csv database 

    """
    # declare local variables
    PATTERN =  "(\[[^\]]+]|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\(|\)|\.|=|#|-|\+|\\\\|\/|_|:|~|@|\?|>|\*|\$|\%[0-9]{2}|[0-9])"
    SMILES_REGEX = re.compile(PATTERN)

    # compute the indices of data to be read
    chunk_size= nb_smiles // job_array_size
    nb_unatributed_smiles= nb_smiles % job_array_size
    first_idx= job_id * chunk_size
    last_idx= min((job_id+1)*chunk_size,nb_smiles)
    if job_id <  nb_unatributed_smiles:
        extra_idx= nb_smiles - (job_id+1)
    else:
        extra_idx= None

    # load data
    data_list= wrapper_csv_reader(csv_path=input_csv,
                                  first_idx=first_idx,
                                  last_idx=last_idx,
                                  extra_idx=extra_idx)

    # generate ClearSMILES
    gen_clearsmiles= partial(get_clearsmiles,
                              nb_random = nb_random,
                             smiles_regex = SMILES_REGEX)
    with Pool(nb_core) as pool :
        results_list= pool.map(gen_clearsmiles,data_list)
        pool.close()
        pool.join()

    # convert into pyarrow table then to parquet file
    table = pa.Table.from_pylist(results_list) # not seting schema due to csv content incertainty
    pq.write_table(table,output_filepath)



if __name__ == '__main__':
    # argparser
    parser = argparse.ArgumentParser()

    # files & directory arguments
    parser.add_argument('--input_csv', help="the inputh path to csv database",
                        default="data/raw/whole_original_MOSES.csv"
                        , type=str)
    parser.add_argument('--output_filepath', help="the output file should be a parquet",
                        default="data/interim/ClearSMILES_MOSES_subset_0.parquet",
                        type=str)


    # data spliting argument
    parser.add_argument('--nb_smiles', help="the number of molecules/smiles for the WHOLE database",
                        default=1_936_962,
                        type=int)
    parser.add_argument('--job_id', help="the job id in the job array",
                        default=0,
                        type=int)
    parser.add_argument('--job_array_size', help="the number of jobs in the job array",
                        default=2000,
                        type=int)

    # computation argument
    parser.add_argument('--nb_core', help="number of core to allocate for multiprocressing",
                        default=4,
                        type=int)
    parser.add_argument('--nb_random', help="number of randomized kekule SMILES to use",
                        default=1_00_000,
                        type=int)


    # parse and converto dict
    args, _ = parser.parse_known_args()
    args_dict = vars(args)

    # change the working directory to main folder
    project_dir = Path(__file__).resolve().parents[2]
    print(project_dir)
    os.chdir(project_dir)

    # ensure that log dir is created
    log_dir = Path(__file__).resolve().parents[0]
    os.makedirs("logs/", exist_ok=True)

    # execute main
    main(input_csv=args_dict["input_csv"],
         output_filepath=args_dict["output_filepath"],
         nb_smiles= args_dict["nb_smiles"],
         nb_random= args_dict["nb_random"],
         nb_core= args_dict["nb_core"],
         job_id=args_dict["job_id"],
         job_array_size=args_dict["job_array_size"]
         )