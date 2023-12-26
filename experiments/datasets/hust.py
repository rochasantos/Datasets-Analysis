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
import csv
import re

# Unpack Tools
from pyunpack import Archive

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
    



# DATA FOR TEST
        
# url = "https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/cbv7jyx4p9-2.zip"
# dirname = "hust_raw"
# zip_name = "hust_bearing.zip"
# relative_path = os.path.join("HUST bearing", "HUST bearing dataset")
# zip_file_path = os.path.join(dirname, zip_name)

# download_file(url, "hust_raw", "hust_bearing.zip")
# extract_zip(zip_file_path, "hust_raw", relative_path)
# create_metadata_file( "hust_raw/HUST bearing/HUST bearing dataset", 
#                                  "hust_raw/hust_bearings.csv" )
        

class CWRU():
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
        self.sample_size = 4096
        self.bearing_names_file = bearing_names_file
        self.bearing_labels, self.bearing_names = self.get_hust_bearings()

        self.signal_data = np.empty((0, self.sample_size))
        self.labels = []
        self.keys = []

        """
        Associate each file name to a bearing condition in a Python dictionary. 
        The dictionary keys identify the conditions.

        This dataset contains 99 raw vibration data with 6 types of fault and 5 types
        of bearing at 3 working conditions. The sample rate is 51,200 samples per second.
        """

        # Files Paths ordered by bearings
        files_path = {}

        for key, bearing in zip(self.bearing_labels, self.bearing_names):
            files_path[key] = os.path.join(self.rawfilesdir, bearing)

        self.files = files_path

    def get_hust_bearings(self):
        # Get bearings to be considered

        bearing_file = os.path.join("hust_raw", self.bearing_names_file)
        print('bearing file:', bearing_file)

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

    # def load_acquisitions(self):
    #     """
    #     Extracts the acquisitions of each file in the dictionary files_names.
    #     """
    #     cwd = os.getcwd()

    #     for key in self.files:
    #         matlab_file = scipy.io.loadmat(os.path.join(cwd, self.files[key]))            
    #         acquisition = []
    #         for position in ['DE', 'FE', 'BA']:
    #             keys = [key for key in matlab_file if key.endswith(position + "_time")]
    #             if len(keys) > 0:
    #                 array_key = keys[0]
    #                 acquisition = matlab_file[array_key].reshape(1, -1)[0]
    #         for i in range(len(acquisition)//self.sample_size):
    #             sample = acquisition[(i * self.sample_size):((i + 1) * self.sample_size)]
    #             self.signal_data = np.append(self.signal_data, np.array([sample]), axis=0)
    #             self.labels = np.append(self.labels, key[0])
    #             self.keys = np.append(self.keys, key)


#     def get_acquisitions (self, n_samples_acquisitions=None):

#         if len(self.signal_data) == 0:
#             self.load_acquisitions()

#         if not n_samples_acquisitions:
#             return self.signal_data, self.labels

#         # get the first index of each feature
#         label_names = list(set(self.labels))        
#         n_samples_per_label = n_samples_acquisitions // len(label_names)

#         index_list = tuple()
#         for label in label_names:
#             index_list = index_list + (np.where(self.labels == label)[0][:n_samples_per_label],)
        
#         indexes = np.concatenate(index_list, axis=0)

#         # print('CWRU')
#         # print('labels ----', self.labels[indexes].shape)
#         # print('signal ----', self.signal_data[indexes].shape)

#         return self.signal_data[indexes], self.labels[indexes]

