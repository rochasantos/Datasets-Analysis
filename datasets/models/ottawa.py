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

            print("Downloading OTTAWA dataset...")
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
def extract_zip(zip_file_path, target_dir, pattern=r'[A-Z]_\d+_\d+\.mat'):
    print("Extracting Bearings Data...")
    
    if not os.path.exists(zip_file_path):
        print(f"Zip file {zip_file_path} not found.")
        return
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    
    regex = re.compile(pattern)

    counter = 0
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            filename = file_info.filename
            match = regex.search(filename)

            if match:
                matched_part = match.group()
                output_path = os.path.join(target_dir, matched_part)
                with open(output_path, 'wb') as output_file:
                    output_file.write(zip_ref.read(filename))
                    counter += 1        

    print(f'{counter} files were extracted into {target_dir} directory.')



# creates a metadata file from bearing data files containing the 
# failure location, bearing type, working condition, and file name.
def create_metadata_file(data_dir, target_dir, pattern=r'([A-Z])_(\d+)_(\d+)\.mat'):
    file_names = os.listdir(data_dir)
    data = [["final condition of the bearing", "specific bearing", "condition of the bearing's healthy", "file name"]]
    for filename in file_names:
        match = re.match(pattern, filename)
        label = [match.group(1), match.group(2), match.group(3)]
        data.append([*label, filename])
    
    with open(target_dir, mode='w', newline='') as csv_file:
        print("Creating Matadata File...")

        csv_writer = csv.writer(csv_file)

        for line in data:
            csv_writer.writerow(line)
    
    print('Metadata file created successfully.')
    

class OTTAWA(DatasetBase):
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
        self._url = "https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/y2px5tg92h-4.zip"        
        self._rawfilesdir = "ottawa_raw"             

        super().__init__()
   

    def download(self, target_dir=None):
        """
        Download and extract compressed files from CWRU website.
        """

        if not target_dir:
            target_dir = self._dataset_dir
            print(f"target_dir value is: {target_dir}")
       
        zip_file_name = "ottawa_bearing.zip"
        dataset_files_dir = "dataset_files"

        zip_file_path = os.path.join(target_dir, zip_file_name)
        dataset_files_path = os.path.join(target_dir, dataset_files_dir)
        metadata_file_path = os.path.join(self._metadata_dir, self._metadata_file)

        if not os.path.isfile(zip_file_path):
            download_file(self._url, target_dir, zip_file_name)
            extract_zip(zip_file_path, dataset_files_path)
            create_metadata_file(dataset_files_path, metadata_file_path)
        else:
            # extract_zip(zip_file_path, dataset_files_path)
            create_metadata_file(dataset_files_path, metadata_file_path)


    def load_acquisitions(self):
        """
        Extracts the acquisitions of each file in the dictionary files_names.
        """      
        cwd = os.getcwd()

        pattern = r'\b([A-Za-z]+)\.(\d+)\.(\d+)'

        self._files_path = self.get_files_path()    
        for key in self._files_path:
            path = os.path.join("datasets/data", self._files_path[key])
            matlab_file = scipy.io.loadmat(path)
            data = matlab_file["data"].reshape(1, -1)[0] [:self._sample_size]
            defect = re.search(pattern, key).group(1)
            
            self._labels = np.append(self._labels, defect)
            self._signal_data = np.vstack((self._signal_data, data))
            self._keys = np.append(self._keys, key)       

