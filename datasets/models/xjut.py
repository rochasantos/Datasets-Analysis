"""
Class definition of HUST Bearing dataset download and acquisitions extraction.
"""

import scipy.io
import numpy as np
import os
import zipfile
import sys
import scipy.io
import numpy as np
import os
import zipfile
import sys
import requests
from tqdm import tqdm
import os
import sys
import requests
import csv
import re
import rarfile

import os, zipfile, pyunpack
from io import BytesIO
import patoolib
import rarfile

import pandas as pd

from .dataset_base import DatasetBase


# Code to avoid incomplete array results
np.set_printoptions(threshold=sys.maxsize)

def download_file(url, dirname, file_name, progress_bar=None):    
     
    full_path = os.path.join(dirname, file_name)

    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    if progress_bar is None:
        # doing download of file
        with requests.get(url, stream=True) as response, open(full_path, 'wb') as file:
            file_size = int(response.headers.get('content-length', 0))
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

            print(f"Downloading {file_name} dataset...")
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                progress_bar.update(size)

                try:
                    progress_bar.refresh()
                except KeyboardInterrupt:
                    print("Download stopped manually.")
                    progress_bar.close()
                    file.close()
                    os.remove(full_path)
                    raise


            progress_bar.close()
    else:
        print("A download is already in progress.")

    print(f'The file has been downloaded to the : {full_path}')


# extract the data from zip file
def extract_rar(rar_file_path, target_dir, pattern=r'([^/]+\.csv)$'):
    print("Extracting and merging Bearings Data...")

    if not os.path.exists(rar_file_path):
        print(f"RAR file {rar_file_path} not found.")
        return

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    regex = re.compile(pattern)

    # Extração
    filename_list = []
    with rarfile.RarFile(rar_file_path, "r") as rar_ref:
        for file_info in rar_ref.infolist():
            filename = file_info.filename
            file_size = file_info.file_size
            filename_list.append(filename)

        for filename in tqdm(filename_list, desc="Extracting CSV files", unit="file"):
            match = regex.search(filename)
            if match:
                matched_part = match.group()
                output_path = os.path.join(target_dir, matched_part)
                if not os.path.exists(output_path):
                    with open(output_path, 'wb') as output_file:
                        output_file.write(rar_ref.read(filename))

    print(f'{len(filename_list)} files were extracted into {target_dir} directory.')



def generate_metadata(files_path, output_dir, header=["label", "file"], pattern=r'/(\d+Hz)(\d+kN)/([^/]+)/([^/]+)$'):

    detail_info = {
            "O": ["Bearing1_1", "Bearing1_2", "Bearing1_3", "Bearing2_2", "Bearing2_4", "Bearing2_5", "Bearing3_1", "Bearing3_5"],
            "I": ["Bearing2_1", "Bearing3_3", "Bearing3_4"],
            "C": ["Bearing1_4", "Bearing2_3"],
            "IO": ["Bearing1_5"],
            "IOCB": ["Bearing3_2"]        
        }

    pattern = re.compile(pattern)

    filename_list = os.listdir(files_path)
    print("len of list:::::::::::", len(filename_list))

    data = [header]

    for filename in filename_list:
        match = pattern.search(filename)
        if match:
            info = list(match.groups())
            
            for key, value in detail_info.items():
                if info[2] in value:
                    info[2] = key
            
            data.append(info)
    
    metadata_path = os.path.join(output_dir, "xjut_bearings.csv")
    with open(metadata_path, mode='w', newline='') as csv_file:
        print("Creating Matadata File...")

        csv_writer = csv.writer(csv_file)

        for line in data:
            csv_writer.writerow(line)
    
    print('Metadata file created successfully.')
    

class XJUT(DatasetBase):
    """
    OTTAWA class wrapper for database download and acquisition.

    ...
    Attributes
    ----------
    rawfilesdir : str
      directory name where the files will be downloaded
    url : str
      website from the raw files are downloaded
    files : dict
      the keys represent the conditions_acquisition and the values are the files names

    Methods
    -------
    download()
      Download and extract raw files from CWRU website
    load_acquisitions()
      Extract vibration data from files
    """

    """
    Associate each file name to a bearing condition in a Python dictionary. 
    The dictionary keys identify the conditions.

    This dataset contains 99 raw vibration data with 6 types of fault and 5 types
    of bearing at 3 working conditions. The sample rate is 51,200 samples per second.
    """

    def __init__(self):
        super().__init__()
   

    def download(self, target_dir=None):
        """
        Download and extract compressed files from CWRU website.
        """
        urls = ["https://drive.usercontent.google.com/download?id=1ATvZuD6j3bPxhyR07Zm-PURmOC4b4uRn&export=download&authuser=0&confirm=t&uuid=715681a9-727b-429b-a511-f8368830ea09&at=APZUnTUucSZM_9YN8oYfmMDeDA2-%3A1704932584998",
                "https://drive.usercontent.google.com/download?id=162KvWNIpBGtd7EDWo4yP1j5XsaoNHOYU&export=download&authuser=0&confirm=t&uuid=a782352b-fb28-4196-9549-437685388e9d&at=APZUnTV2vWugKzYbu77_wCZ5Qp9P:1704933063838",
                "https://drive.usercontent.google.com/download?id=1NvzrGW-KOSy48OZmiFxlE3TPV4CKAcw0&export=download&authuser=0&confirm=t&uuid=d4eca333-fa30-46a6-959f-4368f475776b&at=APZUnTUROhO9_MvvWO1lxL-HELSh:1704934447610",
                "https://drive.usercontent.google.com/download?id=1VuQ5-mK11p1S2pTxUZaH_IxOwUlsmN0S&export=download&authuser=0&confirm=t&uuid=e79cca02-07df-4784-8baf-6c642d183a40&at=APZUnTVAoSbbvvAmZMloeS-y3-2B:1704934505758",
                "https://drive.usercontent.google.com/download?id=1WH4OU4MLaMGQkbh6DghxPA5Dwvsq8tEf&export=download&authuser=0&confirm=t&uuid=31c012f4-099e-46e4-876e-66f8972feca8&at=APZUnTUCeCmREz81KMrE2xzVPf5N:1704934542074",
                "https://drive.usercontent.google.com/download?id=1wzQzQUx6-J8DuGczT81OkrkTgOUwL-I_&export=download&authuser=0&confirm=t&uuid=2ad1ea60-df05-4745-a210-d4a714c790dc&at=APZUnTUTjy5tISJirbBBhflBYier:1704934563057"]

        if not target_dir:
            target_dir = self._dataset_dir
            print(f"target_dir value is: {target_dir}")
       
        dataset_files_dir = f"{self.dataset_name}_bearing"

        dataset_files_path = os.path.join(target_dir, dataset_files_dir)
        rar_file_path = os.path.join(target_dir, f"{self.dataset_name}_bearing.part01.rar")

        # Download
        n = 1
        for url in urls:
            rar_filename = f"{self.dataset_name}_bearing.part0{n}.rar"
            if not os.path.exists(os.path.join(target_dir, rar_filename)):
                download_file(url, target_dir, rar_filename)
            n += 1

        # Extract
        extract_rar(rar_file_path, dataset_files_path)
        generate_metadata(dataset_files_path, os.path.dirname(target_dir), header=["frequency", "load", "fault element", "file"])


    def load_acquisitions(self):
        """
        Extracts the acquisitions of each file in the dictionary files_names.
        """   
      
        pattern = re.compile(r'[^,]+')
        self._files_path = self.get_files_path()
        print("Loading data...")
        for key in self._files_path:
            path = self._files_path[key]
            df = pd.read_csv(path)
            data_dict = {col: np.array(df[col]) for col in df.columns}
            data = data_dict["Horizontal_vibration_signals"].reshape(1, -1)[0] [:self._sample_size]
            label = pattern.findall(key)[2]
            self._labels = np.append(self._labels, label)
            self._signal_data = np.vstack((self._signal_data, data))
            self._keys = np.append(self._keys, label)       

