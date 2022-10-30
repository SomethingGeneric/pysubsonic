import requests

import hashlib,string,random
import urllib.parse
from bs4 import BeautifulSoup
# hashlib.md5(b'string')

class pysubsonic:
    def __init__(self, url, username, cleartext_password):
        self.ver = "1.16.1"
        self.client = "pysubsonic"
        self.url = url
        self.username = username
        self.cleartext_password = cleartext_password
        return
    def get_bad_salt(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
    def make_bad_auth_params(self):
        salt = self.get_bad_salt()
        bytestr=self.cleartext_password+salt
        hashed = hashlib.md5(bytestr.encode()).hexdigest()
        return f"u={self.username}&t={hashed}&s={salt}"
    def do_request(self, endpoint, extra=""):
        full_url = f"{self.url}/rest/{endpoint}?{self.make_bad_auth_params()}&c={self.client}&v={self.ver}"
        if extra != "":
            full_url += "&" + extra
        r = requests.get(full_url)
        return r.text
    def do_search3(self, query):
        return self.do_request("search3", "query="+urllib.parse.quote_plus(query))
    def parse_search3(self, query, tag):
        xml = self.do_search3(query)
        soup = BeautifulSoup(xml, 'xml')
        return soup.find_all(tag)
    def get_song_ids(self, query):
        song_elements = self.parse_search3(query, 'song')
        ids = []
        for elem in song_elements:
            ids.append(elem['id'])
        return ids
    def create_playlist(self, id=None, name=None, songid=None):
        params = f"playlistId={id}" if id is not None else ""
        params += f"&name={name}" if name is not None else ""
        params += f"&songId={songid}" if songid is not None else ""
        return self.do_request("createPlaylist", params)
    def parse_playlist_id(self, response_data):
        soup = BeautifulSoup(response_data, 'xml')
        pl = soup.find_all('playlist')[0]
        return pl['id']
if __name__ == "__main__":
    import getpass
    passw = getpass.getpass(prompt="Password: ")
    p = pysubsonic("https://music.xhec.dev", "matt", passw)
    song_id = p.get_song_ids("Such Great Heights")[0]

    xml = p.create_playlist(name="Test Playlist")
    pl_id = p.parse_playlist_id(xml)
    print(f"Created Test Playlist: {pl_id}")