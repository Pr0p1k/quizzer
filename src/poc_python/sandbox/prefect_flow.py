import os
import json
from os.path import join

from prefect import task, flow, Flow
from prefect.filesystems import LocalFileSystem

from src.poc_python import ROOT_DIR


@task()
def compute_data(x, y):
    cache_path = f"./results/{x}-{y}.json"
    if os.path.exists(cache_path):
        print("Result already exists. Loading from cache...")
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        print("Running computation...")
        result = {"result": x + y}
        return result

@flow(result_storage=LocalFileSystem(basepath='~/.my-results/'))
def my_flow():
    result = compute_data(10, 20)

my_flow()

# with Flow(fn=lambda x: str(x), result_storage="./results") as my_flow:
#     compute_data(4, 8)
#
# my_flow.run()

# TODO try joblib or dask