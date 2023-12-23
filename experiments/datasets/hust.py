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

def download_file(url, dir_name, file_name):    
     
    full_path = os.path.join(dir_name, file_name)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

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




download_file(url, "hust_raw", "hust_bearing.zip")