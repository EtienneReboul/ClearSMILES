"""
This scripts is used to find the jobs that have failed during 
the jobs array so they can be relaunched
"""
import os
from pathlib import Path
import argparse
import glob


def main(search_pattern: str, output_filepath: str, nb_task: int) -> None:
    """  This function will found all finished generation task and check them against
    against the regular number of code 

    Args:
        search_pattern (str):  the unix search filepath pattern used to find all finished jobs
        output_filepath (str): the outpout path for file with failed jobs indices
        nb_task (int):  the number of task in the job array  for the gen of ClearSMILES
    """

    # get  finished task
    finished_tasks = set(glob.glob(search_pattern))

    # check failed task
    failed_task_id_list = [i for i in range(
        nb_task) if not search_pattern.replace("*", str(i)) in finished_tasks]

    # write
    if failed_task_id_list:
        nb_succesful_task = nb_task - len(failed_task_id_list)
        sucess_rate = nb_succesful_task/nb_task * 100
        print(f"{nb_task-len(failed_task_id_list)}/{nb_task} tasks were successfully completed\n")
        print(f"Thus,there is a {sucess_rate:.2f}% success rate\n")
        with open(output_filepath, "w",encoding="utf-8") as file:
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
    print(project_dir)
    os.chdir(project_dir)

    # execute main
    main(search_pattern=args_dict["search_pattern"],
         output_filepath=args_dict["output_filepath"],
         nb_task=args_dict["job_array_size"]
         )
