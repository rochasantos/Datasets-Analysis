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

def download_file(url, sub_path, zip_name):    

    home_path = Path.cwd()    

    filesize = int(requests.head(url).headers["Content-Length"])

    filename = zip_name #os.path.basename(url)

    os.makedirs(os.path.join(home_path, sub_path), exist_ok=True)

    dl_path = os.path.join(home_path, sub_path, filename)
    chunk_size = 1024

    with requests.get(url, stream=True) as r, open(dl_path, "wb") as f, tqdm(
            unit="B",  
            unit_scale=True,  
            unit_divisor=1024,  
            total=filesize,  
            file=sys.stdout,  
            desc=filename  
    ) as progress:
        for chunk in r.iter_content(chunk_size=chunk_size):
            datasize = f.write(chunk)
            progress.update(datasize)


download_file(url, "experiments", "HUST bearing.zip")