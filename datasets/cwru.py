"""
Class definition of CWRU Bearing dataset download and acquisitions extraction.
"""

import urllib.request
import scipy.io
import numpy as np
import os
import csv
import urllib
import sys

# Code to avoid incomplete array results
np.set_printoptions(threshold=sys.maxsize)


def download_file(url, dirname, bearing):
    print("Downloading Bearing Data:", bearing)
    file_name = bearing

    try:
        req = urllib.request.Request(url + file_name, method='HEAD')
        f = urllib.request.urlopen(req)
        file_size = int(f.headers['Content-Length'])

        dir_path = os.path.join(dirname, file_name)
        if not os.path.exists(dir_path):
            urllib.request.urlretrieve(url + file_name, dir_path)
            downloaded_file_size = os.stat(dir_path).st_size
        else:
            downloaded_file_size = os.stat(dir_path).st_size

        if file_size != downloaded_file_size:
            os.remove(dir_path)
            print("File Size Incorrect. Downloading Again.")
            download_file(url, dirname, bearing)
    except Exception as e:
        print("Error occurs when downloading file: " + str(e))
        print("Trying do download again")
        download_file(url, dirname, bearing)


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

    def get_bearings(self):
        # Get bearings to be considered

        bearing_file = os.path.join("datasets", self.bearing_names_file)

        bearing_label = []
        bearing_file_names = []

        with open(bearing_file, 'r') as fd:
            reader = csv.reader(fd)
            for row in reader:
                bearing_label = np.append(bearing_label, row[0])
                bearing_file_names = np.append(bearing_file_names, row[1])

        return bearing_label, bearing_file_names

    def __init__(self, bearing_names_file="cwru_bearings.csv"):
        self.rawfilesdir = "cwru_raw"
        #self.url = "http://csegroups.case.edu/sites/default/files/bearingdatacenter/files/Datafiles/"
        self.url = "https://engineering.case.edu/sites/default/files/"
        self.sample_size = 4096
        self.bearing_names_file = bearing_names_file
        self.bearing_labels, self.bearing_names = self.get_bearings()

        self.n_channels = 2
        self.signal_data = np.empty((0, self.sample_size, self.n_channels))
        self.labels = []
        self.keys = []

        """
        Associate each file name to a bearing condition in a Python dictionary. 
        The dictionary keys identify the conditions.

        There are only four normal conditions, with loads of 0, 1, 2 and 3 hp. 
        All conditions end with an underscore character followed by an algarism 
        representing the load applied during the acquisitions. 
        The remaining conditions follow the pattern:
        
        First two characters represent the bearing location, 
        .e. drive end (DE) and fan end (FE). 
        The following two characters represent the failure location in the bearing, 
        i.e. ball (BA), Inner Race (IR) and Outer Race (OR). 
        The next three algarisms indicate the severity of the failure, 
        where 007 stands for 0.007 inches and 0021 for 0.021 inches. 
        For Outer Race failures, the character @ is followed by a number 
        that indicates different load zones.
        """

        # Files Paths ordered by bearings
        files_path = {}

        for key, bearing in zip(self.bearing_labels, self.bearing_names):
            files_path[key] = os.path.join(self.rawfilesdir, bearing)

        self.files = files_path

    def download(self):
        """
        Download and extract compressed files from CWRU website.
        """

        # Download MAT Files
        url = self.url
        dirname = self.rawfilesdir

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        print("Downloading MAT files:")

        for bearing in self.bearing_names:
            download_file(url, dirname, bearing)

        print("Dataset Loaded.")

    def load_acquisitions(self):
        """
        Extracts the acquisitions of each file in the dictionary files_names.
        """
        cwd = os.getcwd()

        for key in self.files:
            matlab_file = scipy.io.loadmat(os.path.join(cwd, self.files[key]))
            acquisition = []
            positions = ['DE', 'FE', 'BA']
            for position in positions[:self.n_channels]:
                keys = [k for k in matlab_file if k.endswith(position + "_time")]
                if len(keys) > 0:
                    array_key = keys[0]
                    acquisition.append(matlab_file[array_key].reshape(1, -1)[0])
            if len(acquisition) < self.n_channels:
                # print('escaping', key, len(acquisition))
                continue
            acquisition = np.array(acquisition).T
            for i in range(acquisition.shape[0]//self.sample_size):
                sample = acquisition[(i * self.sample_size):((i + 1) * self.sample_size),:]
                self.signal_data = np.append(self.signal_data, np.array([sample]), axis=0)
                self.labels = np.append(self.labels, key[0])
                self.keys = np.append(self.keys, key)
     
    
    def get_acquisitions(self):
        if len(self.labels)==0:
            self.load_acquisitions()
        return self.signal_data, self.labels