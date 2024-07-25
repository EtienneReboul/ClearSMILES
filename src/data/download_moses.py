# -*- coding: utf-8 -*-
""" This script is used to download a csv file, 
default behavior is to download the whole MOSES dataset,
and save it as a csv file 
"""
import logging
import argparse
import os
from pathlib import Path
from urllib import request
from urllib.error import URLError, HTTPError


def main(input_url: str, output_filepath: str, output_log: str) -> None:
    """ Download a csv file containing the SMILES, 
    typical use case is to donwload MOSES from github repo
    """
    # set logger
    logger = logging.getLogger(__name__)

    # write log
    if output_log:
        file_handler = logging.FileHandler(output_log)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    logger.info('Downloading csv file')
    try:
        # Open the URL and retrieve the data
        with request.urlopen(input_url) as response:
            csv_data = response.read()

        # Save the data to a local CSV file
        logger.info('writing to file')
        with open(output_filepath, 'wb') as csv_file:
            csv_file.write(csv_data)

        logger.info("CSV file downloaded successfully to %s", output_filepath)

    except HTTPError as error:
        logger.debug("HTTP Error (%s): %s", error.code, error.reason)

    except URLError as error:
        logger.debug("URL Error: %s", error.reason)

    logger.info('finished')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # argparser
    parser = argparse.ArgumentParser()

    # files & directory arguments
    parser.add_argument('--input_url', help="the url of the MOSES dataset",
                        default="https://media.githubusercontent.com/media/\
                            molecularsets/moses/master/data/dataset_v1.csv", type=str)
    parser.add_argument('--output_filepath', help="the output file should be a csv",
                        default="data/raw/whole_original_MOSES.csv",
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
    log_dir = Path(__file__).resolve().parents[0]
    os.makedirs("logs/", exist_ok=True)

    # execute main
    main(input_url=args_dict["input_url"],
         output_filepath=args_dict["output_filepath"],
         output_log=args_dict["output_log"]
         )
