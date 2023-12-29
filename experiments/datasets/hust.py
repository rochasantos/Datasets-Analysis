"""
Class definition of HUST Bearing dataset download and acquisitions extraction.
"""

import scipy.io
import numpy as np
import os
import zipfile
import sys
import requests
from tqdm import tqdm
import os
import sys
from pathlib import Path
import requests
import csv
import re
import pandas as pd


# Code to avoid incomplete array results
np.set_printoptions(threshold=sys.maxsize)


def download_file(url, dirname, file_name):    
     
    full_path = os.path.join(dirname, file_name)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # doing download of file
    with requests.get(url, stream=True) as response, open(full_path, 'wb') as file:
        file_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

        print("Downloading MAT files.")
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


# extract the data from zip file
def extract_zip(zip_name, target_dir, relative_path=""):
    print("Extracting Bearings Data...")
    
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



# creates a metadata file from bearing data files containing the 
# failure location, bearing type, working condition, and file name.
def create_metadata_file(data_dir, target_dir):
    file_names = os.listdir(data_dir)
    data = [['types of defects ', 'types of bearing', 'working conditions', 'file']]
    for filename in file_names:
        match = re.match(r'^([a-zA-Z]+)(\d+)', filename)
        label = f"{match.group(1)}.620{match.group(2)[0]}.{match.group(2)[-1]}00_W"
        data.append([label, filename])
    
    with open(target_dir, mode='w', newline='') as csv_file:
        print("Creating Matadata File...")

        csv_writer = csv.writer(csv_file)

        for line in data:
            csv_writer.writerow(line)
    
    print('Metadata file created successfully.')
    

class HUST():
    """
    CWRU class wrapper for database download and acquisition.

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

    def __init__(self, bearing_names_file="hust_bearings.csv"):
        self.rawfilesdir = "hust_raw/HUST bearing/HUST bearing dataset"
        self.url = "https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/cbv7jyx4p9-2.zip"
        # Files Paths ordered by bearings

        self.bearing_names_file = bearing_names_file
        self.bearing_labels, self.bearing_names = self.get_hust_bearings()      

        self.sample_size = pow(2, 16)
        self.signal_data = np.empty((0, self.sample_size))
        self.labels = []
        self.keys = []
        self.df = pd.DataFrame()
        
        files_path = {}
        for key, bearing in zip(self.bearing_labels, self.bearing_names):
            files_path[key] = os.path.join(self.rawfilesdir, bearing)
        self.files = files_path

        """
        Associate each file name to a bearing condition in a Python dictionary. 
        The dictionary keys identify the conditions.

        This dataset contains 99 raw vibration data with 6 types of fault and 5 types
        of bearing at 3 working conditions. The sample rate is 51,200 samples per second.
        """


    def get_hust_bearings(self):
        bearing_file = os.path.join("hust_raw", self.bearing_names_file)
        bearing_label = []
        bearing_file_names = []

        with open(bearing_file, 'r') as fd:
            reader = csv.reader(fd)
            next(reader) # skip the first line which is the header
            for row in reader:
                bearing_label = np.append(bearing_label, row[0])
                bearing_file_names = np.append(bearing_file_names, row[1])

        return bearing_label, bearing_file_names
   

    def download(self):
        """
        Download and extract compressed files from CWRU website.
        """

        # Download MAT Files
        url = self.url
        dirname = "hust_raw"
        zip_file = "hust_bearing.zip"
        csv_file = os.path.join(dirname, "hust_bearings.csv")

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        download_file(url, dirname, zip_file)
        extract_zip(zip_file, dirname)
        create_metadata_file(self.rawfilesdir, csv_file)

    def load_acquisitions(self):
        """
        Extracts the acquisitions of each file in the dictionary files_names.
        """
      
        cwd = os.getcwd()

        # get the types of defects
        pattern = r'\b([A-Za-z]+)\.(\d+)\.(\d+)'
        defects = []
        for defect in list(self.files.keys()):
            match = re.search(pattern, defect)
            defects.append(match.group(1))

        defects = list(set(defects))
        print("defects: ", defects)

        
        for key in self.files:
            matlab_file = scipy.io.loadmat(os.path.join(cwd, self.files[key]))
            
            data = matlab_file["data"].reshape(1, -1)[0] [:self.sample_size]
            defect = re.search(pattern, key).group(1)
            
            self.labels = np.append(self.labels, defect)
            self.signal_data = np.vstack((self.signal_data, data))
            self.keys = np.append(self.keys, key)       


    def get_acquisitions (self, n_samples_acquisitions=None):

        if len(self.signal_data) == 0:
            self.load_acquisitions()

        if not n_samples_acquisitions:
            return self.signal_data, self.labels

        # get the first index of each feature
        label_names = list(set(self.labels))        
        n_samples_per_label = n_samples_acquisitions // len(label_names)

        index_list = tuple()
        for label in label_names:
            index_list = index_list + (np.where(self.labels == label)[0][:n_samples_per_label],)
        
        indexes = np.concatenate(index_list, axis=0)

        return self.signal_data[indexes], self.labels[indexes]
