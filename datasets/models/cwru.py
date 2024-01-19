import scipy.io
import numpy as np
import re

from .dataset_base import DatasetBase
from ..rolbearing_dataset.download import download_dataset

class CWRU(DatasetBase):
    
    def __init__(self):
        self._url = "https://engineering.case.edu/sites/default/files/"

        super().__init__()
   
    def download(self, dirname, metadata_path=None):
        
        url = self.url
        dirname = self.raw_data_dir
        metadata = self.metadata_path

        download_dataset(url, dirname, metadata_path=metadata)

    def load_acquisitions(self):
        pattern = r'\b([A-Za-z]+).(\d+).(\d+)'

        self._files_path = self.get_files_path()    
        for key in self._files_path[:5]:
            path = self._files_path[key] 
            
            matlab_file = scipy.io.loadmat(path)            
            data = matlab_file["data"].reshape(1, -1)[0] [:self._sample_size]
            k = data.keys()
            # defect = re.search(pattern, key).group(1)
            # self._labels = np.append(self._labels, defect)
            # self._signal_data = np.vstack((self._signal_data, data))
            # self._keys = np.append(self._keys, key)   
