import importlib
from utils.arg_parser import arg_parser

def main():
    CONFIG_ENV = arg_parser()
    
    job_name = f"jobs.{CONFIG_ENV['job_name']}.dataminer"
    job = importlib.import_module(job_name)
    job.run(CONFIG_ENV)

if __name__ == "__main__":
    main()