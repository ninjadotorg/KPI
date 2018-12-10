import os
import tarfile
import requests

import base58
import sys


class IPFS(object):
    def __init__(self, app=None):
        super(IPFS, self).__init__()
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.host = app.config['IPFS_REST_HOST']
        self.port = app.config['IPFS_REST_PORT']
        self.base_url = ''.join(['http://', self.host, ':', str(self.port), '/api/v0/'])

    def upload(self, data):
        """Upload content of a file to IPFS."""
        files = {'path': data}
        # Add file
        res = requests.post(self.base_url + 'add', files=files).json()
        h = res['Hash']
        # Pin file
        requests.post(self.base_url + 'pin/add', params={'arg': h})
        # get hash
        # short_hash = base58.b58decode(h)[2:]
        return h

    def upload_file(self, file_path):
        """Upload a local file to IPFS."""
        f = open(file_path, 'rb')
        short_hash = self.upload(f)
        f.close()
        return short_hash

    def get_file_streaming(self, short_hash):
        """Download a file with a hash from IPFS."""
        # h = base58.b58encode("\x12\x20" + short_hash)
        params = {'arg': short_hash}
        res = requests.post(self.base_url + 'cat', params=params, stream=True)
        for chunk in res.iter_content(chunk_size=1024):
            yield chunk

if __name__ == '__main__':
    command = sys.argv[1]
    ipfs = IPFS()
    if command == 'upload':
        file_path = sys.argv[2]
        h = ipfs.upload_file(file_path)
        print h
    else:
        hash = sys.argv[2]
        ipfs.download_file(hash)


