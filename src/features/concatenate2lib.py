""" This script is used to concatenate all the subset 
from the experiment into a unique database
"""
import os
from pathlib import Path
import argparse
import glob
from multiprocessing import Pool
import pandas as pd


def main(search_pattern: str, output_filepath: str) -> None:
    """  This function is used to aggregate all the data into a single parquet
    file

    Args:
        search_pattern (str):  the unix search filepath pattern used to find all finished jobs
        output_filepath (str): the outpath of the concatenated database
    """

    # get path of subset
    subset_path_set = set(glob.glob(search_pattern))

    # get the number of available cores
    nb_worker=len(os.sched_getaffinity(0))

    # get subsets
    with Pool(nb_worker) as pool:
        df_list = pool.map(pd.read_parquet, subset_path_set)
        pool.close()
        pool.join()

    # concatenate df
    aggregated_df = pd.concat(df_list, ignore_index=True)

    # writing file
    aggregated_df.to_parquet(output_filepath)


if __name__ == '__main__':
    # argparser
    parser = argparse.ArgumentParser()

    # files & directory arguments
    parser.add_argument('--search_pattern', help="unix style pathname pattern to \
                        find finished task",
                        default="data/interim/ClearSMILES_MOSES_subset_*.parquet", type=str)
    parser.add_argument('--output_filepath', help="the output file should be a txt file",
                        default="failed_task_id.txt",
                        type=str)

    # data splitting argument
    parser.add_argument('--job_array_size', help="the number of jobs in the job array",
                        default=2000,
                        type=int)

    # parse and converto dict
    args, _ = parser.parse_known_args()
    args_dict = vars(args)

    # change the working directory to main folder
    project_dir = Path(__file__).resolve().parents[2]
    os.chdir(project_dir)

    # execute main
    main(search_pattern=args_dict["search_pattern"],
         output_filepath=args_dict["output_filepath"],
         )
