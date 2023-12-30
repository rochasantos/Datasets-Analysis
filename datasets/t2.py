from tqdm import tqdm
import os
import sys
from pathlib import Path
import requests

# This example script downloads python program for mac.

# Home directory of Mac, pathlib.Path module make this easy.
home_path = Path.home()
# This is the sub directory under home directory.
sub_path = "tmp"
# The download link of python.
url = "https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/cbv7jyx4p9-2.zip"

# The header of the dl link has a Content-Length which is in bytes.
# The bytes is in string hence has to convert to integer.
filesize = int(requests.head(url).headers["Content-Length"])

# os.path.basename returns python-3.8.5-macosx10.9.pkg,
# without this module I will have to manually split the url by "/"
# then get the last index with -1.
# Example:
# url.split("/")[-1]
filename = os.path.basename(url)

# make the sub directory, exists_ok=True will not have exception if the sub dir does not exists.
# the dir will be created if not exists.
os.makedirs(os.path.join(home_path, sub_path), exist_ok=True)

# The absolute path to download the python program to.
dl_path = os.path.join(home_path, sub_path, filename)
chunk_size = 1024

# Use the requests.get with stream enable, with iter_content by chunk size,
# the contents will be written to the dl_path.
# tqdm tracks the progress by progress.update(datasize)
with requests.get(url, stream=True) as r, open(dl_path, "wb") as f, tqdm(
        unit="B",  # unit string to be displayed.
        unit_scale=True,  # let tqdm to determine the scale in kilo, mega..etc.
        unit_divisor=1024,  # is used when unit_scale is true
        total=filesize,  # the total iteration.
        file=sys.stdout,  # default goes to stderr, this is the display on console.
        desc=filename  # prefix to be displayed on progress bar.
) as progress:
    for chunk in r.iter_content(chunk_size=chunk_size):
        # download the file chunk by chunk
        datasize = f.write(chunk)
        # on each chunk update the progress bar.
        progress.update(datasize)