"""
Class definition of HUST Bearing dataset download and acquisitions extraction.
"""

import urllib.request
import scipy.io
import numpy as np
import os
from sklearn.model_selection import KFold, GroupKFold, StratifiedShuffleSplit, GroupShuffleSplit
import shutil
import zipfile
import sys
import ssl
import requests
from tqdm import tqdm
import os
import sys
from pathlib import Path
import requests

# Unpack Tools
from pyunpack import Archive

# Code to avoid incomplete array results
np.set_printoptions(threshold=sys.maxsize)

url = "https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/cbv7jyx4p9-2.zip"

def download_file(url, dirname, file_name):    
     
    full_path = os.path.join(dirname, file_name)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # doing download of file
    with requests.get(url, stream=True) as response, open(full_path, 'wb') as file:
        file_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

            # exception handling for KeyboardInterrupt
            try:
                progress_bar.refresh()
            except KeyboardInterrupt:
                print("Download stopped manually.")
                progress_bar.close()
                file.close()
                os.remove(full_path)
                raise


        progress_bar.close()

    print(f'The file has been downloaded to the : {full_path}')

import re

# extract the data from zip file
def extract_zip(zip_name, target_dir, relative_path=""):
    print("Extracting Bearings Data.")
    
    if not os.path.exists(zip_name):
        print(f"Zip file {zip_name} not found.")
        return
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            counter = 0
            for data in zip_ref.infolist():
                if data.filename.startswith(relative_path):
                    zip_ref.extract(data, target_dir)
                    counter += 1            
            print(f"{counter} files were extracted.")

        print(f'The file "{relative_path}" was extract from "{zip_name}" to "{target_dir}".')
    except KeyError:
        print(f'The file "{relative_path}" not be found in the zip file.')


# DATA FOR TEST
        
# dirname = "hust_raw"
# zip_name = "hust_bearing.zip"
# relative_path = os.path.join("HUST bearing", "HUST bearing dataset")

# zip_file_path = os.path.join(dirname, zip_name)

# download_file(url, "hust_raw", "hust_bearing.zip")
# extract_zip(zip_file_path, "hust_raw", relative_path)