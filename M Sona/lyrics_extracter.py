import lyricsgenius
from pathlib import Path
import logging
import sys
import sqlite3
from typing import Any, Optional
logging.basicConfig(level=logging.DEBUG)
 

ACCESS_TOKEN = Path(__file__).parent / "secrets" / ".env"

if not ACCESS_TOKEN.exists():
    logging.debug("File not found")
    sys.exit()


class LyricsDb:
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.conn = sqlite3.connect(self.base_path / "m_sona.db")
        self.conn_cursor = self.conn.cursor()

    def create_db(self):
        """Creates db if doesn't already exist"""
        self.conn_cursor.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL)
            """)
        self.conn_cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER,
                lyrics TEXT,
                FOREIGN KEY (artist_id) REFERENCES artists(id)
                                 )    
        """)
    
    def close_connection(self):
        """Close connection to db"""
        if self.conn:
            self.conn.close()
            logging.debug("Closing connection to database")

    def commit_data(self):
        """Commits data to database"""
        if self.conn:
            self.conn.commit()
            logging.debug("Commiting data to database")
    
    def insert_artist(self, name:str) -> int:
        """Insert artis into the databse, return artist ID"""
        try:
            self.conn_cursor.execute(
                """
                    INSERT OR IGNORE artists (name) VALUES (?)
                """,
                (name,)
            )
            self.commit_data()
            
            #fetch artist id whether it was just inserted or already exists
            self.conn_cursor.execute(
                """
                    SELECT id FROM artists WHERE name = ?
                """,
                (name,)
            )
            artist_id = self.conn_cursor.fetchone()[0]
            logging.debug(f"Artist {name} has ID {artist_id}")
            return artist_id
        except Exception as e:
            logging.error(f"Error inserting artist {name}: {e}")
            return -1
        
    def insert_song(self, title: str, artist_id: int, lyrics: str):
        """Insert song into the database"""
        try:
            self.conn_cursor.execute(
                """
                    INSERT INTO songs (title, artist_id, lyrics) VALUES (?, ?, ?)
                """, (title, artist_id, lyrics),
            )

        except Exception as e:
            logging.error(f"Error inserting song {title}: {e}")

    def get_all_artists(self):
        """Gets all the names of artists present in the database"""
        
        self.conn_cursor.execute("SELECT * FROM artists")
        return self.conn_cursor.fetchall()
    
    def get_all_songs(self):
        """Get all songs present in the database"""

        self.conn_cursor.execute("SELECT * FROM songs")
        return self.conn_cursor.fetchall()

    def gets_songs_by_artist_name(self, artist_name:str):
        """Gets song by specific artist name"""

        self.conn_cursor.execute(
            """
                SELECT songs.title, songs.lyrics FROM songs JOIN artists ON songs.artist = artists.id WHERE artists.name = ?
            """, (artist_name,)
        )
        return self.conn_cursor.fetchall()
    
    def search_songs_by_title(self, keyword: str):
        """Search for songs by title (e.g 'find all songs with the title of  'love'.)"""

        self.conn_cursor.execute(
            """
                SELECT title, lyrics FROM songs WHERE title like ?
            """, (f"%{keyword}%",)
        )
        return self.conn_cursor.fetchall()

    def get_song_by_title_and_artist(self, title: str, artist_name: str) -> Optional[tuple]:
        """
        Get a specific song and its lyrics by title and artist name.
        Returns (title, lyrics) or None if not found.
        """
        try:
            self.conn_cursor.execute("""
                SELECT songs.title, songs.lyrics
                FROM songs
                JOIN artists ON songs.artist_id = artists.id
                WHERE songs.title = ? AND artists.name = ?
            """, (title, artist_name))
            
            result = self.conn_cursor.fetchone()  # Only one song expected
            if result:
                logging.debug(f"Found song: {result[0]} by {artist_name}")
            else:
                logging.debug(f"Song '{title}' by '{artist_name}' not found")
            return result
        except Exception as e:
            logging.error(f"Error retrieving song '{title}' by '{artist_name}': {e}")
            return None
        

class GeniusLyrics:
    def __init__(self, access_token: str):
        self.genius = lyricsgenius.Genius(access_token.read_text().strip())
        self.genius.skip_non_songs = True
        self.genius.excluded_terms = ["(Remix)", "(Live)"]

    def get_lyrics(self, song_title: str, artist_name: str):
        try:
            song = self.genius.search_song(title=song_title, artist=artist_name)
            if song:
                return song.lyrics
            return "Lyrics not found!"
        except Exception as e:
            return f"An error occurred: {e}"
        
if __name__ == "__main__":

    lyrics_client = GeniusLyrics(ACCESS_TOKEN)

    lyrics = lyrics_client.get_lyrics("Ariana Grande", "Into You")
    print(lyrics)
