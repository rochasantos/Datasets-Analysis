import os
import requests
from tqdm import tqdm

def download(url, file_path, progress_bar=None):

    # file_path = os.path.join('datasets/data/hust_bearing.zip')
    if progress_bar is None:
        with requests.get(url, stream=True) as response, open(file_path, 'wb') as file:
            file_size = int(response.headers.get('content-length', 0))
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

            print("Downloading ...")
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


def download_dataset(url, dirname, file_name,  url_mapper=None):

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    file_path = os.path.join(dirname, file_name)

    if url_mapper:
        for file in url_mapper:
            url = os.path.join(url, file)
            file_path = os.path.join(dirname, file)
            download(url, file_path)
    else:
        download(url, file_path)
