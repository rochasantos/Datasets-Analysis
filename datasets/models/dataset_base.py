from abc import ABC, abstractmethod

import numpy as np
import os
import csv


class DatasetBase(ABC):

    def __init__(self):
        self._url: str
        self._name = self.__class__.__name__.lower()
        
        self._dataset_dir = f"datasets/data/{self._name}"
        self._raw_data_dir = os.path.join(self._dataset_dir, f"{self._name}_raw")
        
        self._metadata_path = os.path.join(self._dataset_dir, f"{self._name}_bearings.csv")
        zip_file_path = os.path.join(self._dataset_dir, f"{self._name}_bearings.zip")
        rar_file_path = os.path.join(self._dataset_dir, f"{self._name}_bearings.rar")

        self._sample_size = 4096
        self._signal_data = np.empty((0, self._sample_size))
        self._labels = []
        self._keys = []
        
        self._files_path = None
        

    @property
    def url(self):
        return self._url    

    @property
    def name(self):
        return self._name
    
    @property
    def dataset_dir(self):
        return self._dataset_dir
    
    @property
    def raw_data_dir(self):
        return self._raw_data_dir
    
    @property
    def metadata_path(self):
        return self._metadata_path
      
    
    @abstractmethod
    def download(self):
        pass
    
    @abstractmethod
    def load_acquisitions(self):
        pass


    def get_files_path(self):
        # Files Paths ordered by bearings
        bearing_labels, bearing_names = self.get_bearings()
        files_path = {}
        for key, bearing in zip(bearing_labels, bearing_names):
            dataset_files_dir = self._raw_data_dir
            files_path[key] = os.path.join(dataset_files_dir, bearing)
        return files_path


    def get_bearings(self):
        bearing_label = []
        bearing_file_names = []

        with open(self._metadata_path, 'r') as fd:
            reader = csv.reader(fd)
            next(reader) # skip the first line which is the header
            for row in reader:
                bearing_label = np.append(bearing_label, ','.join(row))
                bearing_file_names = np.append(bearing_file_names, row[-1])
        return bearing_label, bearing_file_names

    
    def get_acquisitions(self):
        if len(self._labels)==0:
            self.load_acquisitions()
        return self._signal_data, self._labels
    
    
    def set_sample_size(self, sample_size):
        self._n_samples_acquisitions = sample_size


    def set_number_of_acquisitions(self, num_acquisitions):
        self._n_samples_acquisitions = num_acquisitions
    