import importlib
from utils.arg_parser import arg_parser

def main():
    ENV_CONFIG = arg_parser()
    
    job_exec_type = ENV_CONFIG['job_exec_type']

    option = {
        "dataminer": ENV_CONFIG['job_name'],
        "datadry": ENV_CONFIG['job_name'],
        "bulkload": "general",
    }

    job_dir = option.get(job_exec_type)

    job_path = f"jobs.{job_dir}.{job_exec_type}"
    job = importlib.import_module(job_path)
    job.run(ENV_CONFIG)

if __name__ == "__main__":
    main()