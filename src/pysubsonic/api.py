import requests

import hashlib,string,random
import urllib.parse
from bs4 import BeautifulSoup
# hashlib.md5(b'string')

class pysubsonic:
    def __init__(self, url, username, cleartext_password):
        """Instantiate the API. Needs instance URL, username, and password"""
        self.ver = "1.16.1"
        self.client = "pysubsonic"
        self.url = url
        self.username = username
        self.cleartext_password = cleartext_password
        return
    def get_bad_salt(self):
        """Create the god-awful random salt for password-auth"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
    def make_bad_auth_params(self):
        """Combine the bad salt with the md5 hash of the password, and return them both in URL param format"""
        salt = self.get_bad_salt()
        bytestr=self.cleartext_password+salt
        hashed = hashlib.md5(bytestr.encode()).hexdigest()
        return f"u={self.username}&t={hashed}&s={salt}"
    def do_request(self, endpoint, extra=""):
        """Perform the actual GET request, with endpoint param, auth params, and any extra args"""
        full_url = f"{self.url}/rest/{endpoint}?{self.make_bad_auth_params()}&c={self.client}&v={self.ver}"
        if extra != "":
            full_url += "&" + extra
        r = requests.get(full_url)
        return r.text
    def do_search3(self, query):
        """Perform a 'search3' query with the given input"""
        return self.do_request("search3", "query="+urllib.parse.quote_plus(query))
    def parse_search3(self, query, tag):
        """Return all of <tag> from a given query, thru Search3"""
        xml = self.do_search3(query)
        soup = BeautifulSoup(xml, 'xml')
        return soup.find_all(tag)
    def get_song_ids(self, query):
        """Uses Search3 to find all songs matching <query>"""
        song_elements = self.parse_search3(query, 'song')
        ids = []
        for elem in song_elements:
            ids.append(elem['id'])
        return ids
    def get_playlists(self, username=None):
        """List all visible playlists, optionally only of a given username"""
        extra = f"username={username}" if username is not None else ""
        return self.do_request("getPlaylists", extra)
    def create_playlist(self, id=None, name=None, songid=None):
        """Create playlist, or update playlist (this appears to overwrite!) Args: id, name, songid"""
        params = f"playlistId={id}" if id is not None else ""
        params += f"&name={name}" if name is not None else ""
        params += f"&songId={songid}" if songid is not None else ""
        return self.do_request("createPlaylist", params)
    def update_playlist(self, playlistId, songIdToAdd):
        """Add given songid to playlist by id"""
        params = f"playlistId={playlistId}&songIdToAdd={songIdToAdd}"
        return self.do_request("updatePlaylist", params)
    def get_playlist_id_by_name(self, name, username=None):
        """Return the playlist id matching given name, optionally add username to shorten the list of elements to check"""
        data = self.get_playlists(username=username)
        soup = BeautifulSoup(data, 'xml')
        playlists = soup.find_all('playlist')
        for playlist in playlists:
            if playlist['name'] == name:
                return playlist['id']
        return None
    def get_playlist(self, id):
        """Return raw XML of playlist by ID"""
        return self.do_request("getPlaylist", f"id={id}")
    def get_songs_from_playlist(self, id=None, name=None):
        """Return all song elements from playlist by either name or id"""
        if id is None and name is not None:
            id = self.get_playlist_id_by_name(name)
        elif id is None and name is None:
            return "Huh?"
        # we should have an id no matter what now
        pl_data = self.get_playlist(id)
        soup = BeautifulSoup(pl_data, 'xml')
        return soup.find_all('entry')
    def check_song_in_playlist(self, playlist_name, song_name):
        """Returns true if 'song_name' is in 'playlist_name', false otherwise"""
        entries = self.get_songs_from_playlist(name=playlist_name)
        for entry in entries:
            if entry['title'] == song_name:
                return True
        return False
    def parse_playlist_id(self, response_data):
        """Extract playlist id from response XML"""
        soup = BeautifulSoup(response_data, 'xml')
        pl = soup.find_all('playlist')[0]
        return pl['id']
if __name__ == "__main__":
    import getpass
    passw = getpass.getpass(prompt="Password: ")
    p = pysubsonic("https://music.xhec.dev", "matt", passw)
    if p.check_song_in_playlist('Burn', 'Burned Out'):
        print("yay!")
    else:
        print(":(")