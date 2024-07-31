"""
This scripts is used to find the jobs that have failed during 
the jobs array so they can be relaunched
"""
import os
from pathlib import Path
import argparse
import glob


def main(search_pattern: str, output_filepath: str, job_array_range: str) -> None:
    """  This function will found all finished generation task and check them against
    against the regular number of code 

    Args:
        search_pattern (str):  the unix search filepath pattern used to find all finished jobs
        output_filepath (str): the outpout path for file with failed jobs indices
        job_array_range (str):  the range of 
    """

    # get  finished task
    finished_tasks = set(glob.glob(search_pattern))

    # get index range + data casting
    if "-" in job_array_range and "," in job_array_range:
        raise ValueError(
            'the job array should not contains both "-" and "," separator')
    if "-" in job_array_range:
        first_idx, last_idx = job_array_range.split("-")
        jobs2check = range(int(first_idx), int(last_idx)+1)
    elif "," in job_array_range:
        jobs2check = [int(idx)for idx in job_array_range.split(",")]
    else:
        raise ValueError("the range used for the jobs array, can be \
                        either a list of jobs,e.g: 1,14,30 or a range : 1-2000")

    # check failed task
    failed_task_id_list = [i for i in jobs2check
                           if not search_pattern.replace("*", str(i)) in finished_tasks]

    # write to file
    if failed_task_id_list:
        nb_succesful_task = job_array_range - len(failed_task_id_list)
        sucess_rate = nb_succesful_task/job_array_range * 100
        print(f"{sucess_rate:.2f}% tasks were successfully completed\n")
        print(f"writting task id of failed jobs in {output_filepath}")
        with open(output_filepath, "w", encoding="utf-8") as file:
            failed_task_id_list = [str(i) for i in sorted(failed_task_id_list)]
            file.write(f"{','.join(failed_task_id_list)}\n")
            file.close()
    else:
        print("all task were sucessfully completed, no file will be written")


if __name__ == '__main__':
    # argparser
    parser = argparse.ArgumentParser()

    # files & directory arguments
    parser.add_argument('--search_pattern', help="unix style pathname pattern \
                         to find finished task",
                        default="data/interim/ClearSMILES_MOSES_subset_*.parquet", type=str)
    parser.add_argument('--output_filepath', help="the output file should be a txt file",
                        default="data/external/failed_task_id.txt",
                        type=str)

    # data splitting argument
    parser.add_argument('--job_array_range', help="the range used for the jobs array, can be \
                        either a list of jobs,e.g: 1,14,30 or a range : 1-2000",
                        default="1-2000",
                        type=str)

    # parse and converto dict
    args, _ = parser.parse_known_args()
    args_dict = vars(args)

    # change the working directory to main folder
    project_dir = Path(__file__).resolve().parents[2]
    print(project_dir)
    os.chdir(project_dir)

    # execute main
    main(search_pattern=args_dict["search_pattern"],
         output_filepath=args_dict["output_filepath"],
         job_array_range=args_dict["job_array_size"]
         )
