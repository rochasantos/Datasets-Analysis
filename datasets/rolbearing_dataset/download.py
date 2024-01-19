import csv
import os
import requests
import numpy as np
from tqdm import tqdm


def download(url, file_path, progress_bar=None):

    if progress_bar is None:
        with requests.get(url, stream=True) as response, open(file_path, 'wb') as file:
            file_size = int(response.headers.get('content-length', 0))
            progress_bar = tqdm(total=file_size)

            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                progress_bar.update(size)

                try:
                    progress_bar.refresh()
                except KeyboardInterrupt:
                    print("Download stopped manually.")
                    progress_bar.close()
                    file.close()
                    os.remove(file_path)
                    raise

            progress_bar.close()
    else:
        print("A download is already in progress.")

    print(f'The file has been downloaded to the : {file_path}')


def get_bearings(metadata_path):

        bearing_label = []
        bearing_file_names = []

        with open(metadata_path, 'r') as fd:
            reader = csv.reader(fd)
            next(reader)
            for row in reader:
                bearing_label = np.append(bearing_label, row[0])
                bearing_file_names = np.append(bearing_file_names, row[1])

        return bearing_label, bearing_file_names


def download_dataset(url, dirname, filename=None,  metadata_path=None):

    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    print("Downloading ...")

    if metadata_path:
        _, files = get_bearings(metadata_path)
        for file in files:
            url_file = os.path.join(url, file)
            file_path = os.path.join(dirname, file)
            if not os.path.exists(file_path):
                download(url_file, file_path)
    else:
        file_path = os.path.join(dirname, filename)
        download(url, file_path)


# url = "https://engineering.case.edu/sites/default/files/97.mat"