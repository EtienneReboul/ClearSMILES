# -*- coding: utf-8 -*-
""" This script is used to convert a csv file to a parquet file, 
default behavior is to download the whole MOSES dataset dataset,
and save it as a parquet file 
"""
import logging
import argparse
import os
from pathlib import Path
import pandas as pd


def main(input_filepath : str, output_filepath: str, output_log : str) -> None:
    """ Is used to process the csv file containing smiles to a parquet file, 
    typical use case is the
    """
    # set logger
    logger = logging.getLogger(__name__)

    # write log
    if output_log:
        file_handler = logging.FileHandler(output_log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    logger.info('loading csv file')
    df= pd.read_csv(input_filepath)
    logger.info('writing to parquet')
    df.to_parquet(output_filepath)
    logger.info('finishing converting csv to parquet')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # argparser
    parser = argparse.ArgumentParser()

    # files
    parser.add_argument('--input_csv', help="the input file should be a csv",
                        default="https://media.githubusercontent.com/media/molecularsets/moses/master/data/dataset_v1.csv"
                        , type=str)
    parser.add_argument('--output_parquet', help="the output file should be a parquet",
                        default="data/raw/whole_original_MOSES.parquet", 
                        type=str)
    parser.add_argument('--output_log', help="the output log path",
                        default="logs/downloading_moses.log",
                        type=str)
    # parse and converto dict
    args, _ = parser.parse_known_args()
    args_dict = vars(args)
    
    # change the working directory to main folder
    project_dir = Path(__file__).resolve().parents[2]
    print(project_dir)
    os.chdir(project_dir)

    # ensure that log dir is created 
    log_dir= Path(__file__).resolve().parents[0]
    os.makedirs("logs/",exist_ok =True)
    main(input_filepath=args_dict["input_csv"],
         output_filepath=args_dict["output_parquet"],
         output_log=args_dict["output_log"]
         )
