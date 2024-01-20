import scipy.io
import numpy as np
import re

from .dataset_base import DatasetBase
from ..rolbearing_dataset.download import download_dataset

from utils.regex_util import extract_groups_from_words

class CWRU(DatasetBase):
    
    def __init__(self):
        self._url = "https://engineering.case.edu/sites/default/files/"

        super().__init__()

   
    def download(self, dirname, metadata_path=None):
        
        url = self.url
        dirname = self.raw_data_dir
        metadata = self.metadata_path

        download_dataset(url, dirname, metadata_path=metadata)

    
    def load_acquisitions(self, fault_type=None, sensor_position=None, bearing_type=None):

        pattern = re.compile(r'([A-Z0-9]+_([A-Z]+)_time)')
               
        self._files_path = self.get_files_path()
        
        for key in self._files_path:
            path = self._files_path[key] 
            
            matlab_file = scipy.io.loadmat(path)           
            k = matlab_file.keys()
            
            cols = [word[0] for word in extract_groups_from_words(k, pattern)]
            # sensor_position = [word[1] for word in extract_groups_from_words(k, pattern)]
            
            for col in cols:
                data = matlab_file[col].reshape(1, -1)[0][:self._sample_size]
                self._labels = np.append(self._labels, key[0])
                self._signal_data = np.vstack((self._signal_data, data))
                self._keys = np.append(self._keys, key)  
           