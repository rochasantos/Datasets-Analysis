from abc import ABC, abstractmethod

import numpy as np
import os
import csv


class DatasetBase(ABC):

    def __init__(self):
        self._url: str
        self._dataset_name = self.__class__.__name__.lower()
        self._rawfilesdir = f"{self.dataset_name}_raw"
        self._metadata_file = f"{self._dataset_name}_bearings.csv"
        self._metadata_dir = f'datasets/dataset_metadata'
        self._dataset_dir = f'datasets/data/{self.__class__.__name__.lower()}_raw'

        self._sample_size = 4096
        self._signal_data = np.empty((0, self._sample_size))
        self._labels = []
        self._keys = []
        
        self._files_path = None
        

    @property
    def dataset_name(self):
        return self._dataset_name

    @property
    def url(self):
        return self._url
    
    @property
    def bearing_names_file(self):
        return self._bearing_names_file
    
    
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
            dataset_files_dir = os.path.join(self._dataset_dir, f"{self.dataset_name}_bearing")
            files_path[key] = os.path.join(dataset_files_dir, bearing)
        return files_path


    def get_bearings(self):
        metadata_file_path = os.path.join(self._metadata_dir, self._metadata_file)
        bearing_label = []
        bearing_file_names = []

        with open(metadata_file_path, 'r') as fd:
            reader = csv.reader(fd)
            next(reader) # skip the first line which is the header
            for row in reader:
                bearing_label = np.append(bearing_label, row[0])
                bearing_file_names = np.append(bearing_file_names, row[1])

        return bearing_label, bearing_file_names

    
    def get_acquisitions(self):
        if len(self._labels)==0:
            self.load_acquisitions()
        return self._signal_data, self._labels
    
    
    def set_sample_size(self, sample_size):
        self._n_samples_acquisitions = sample_size


    def set_number_of_acquisitions(self, num_acquisitions):
        self._n_samples_acquisitions = num_acquisitions
    