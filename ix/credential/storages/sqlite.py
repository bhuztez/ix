import sqlite3
from .. import BaseCredentialStorage, lazy_property


class SqliteCredentialStorage(BaseCredentialStorage):

    def __init__(self, filename):
        self.filename = filename

    @lazy_property
    def cursor(self):
        self.conn = sqlite3.connect(self.filename)
        cursor = self.conn.cursor()
        cursor.execute(
'''
CREATE TABLE IF NOT EXISTS credentials(
  oj TEXT,
  key TEXT,
  value TEXT,
  UNIQUE(oj, key))
''')
        return cursor

    def load(self, name):
        self.cursor.execute("SELECT key, value FROM credentials WHERE oj = ?", (name,))
        return dict(self.cursor.fetchall())

    def save(self, name, credential):
        keys = list(credential.keys())
        self.cursor.execute(
            "DELETE FROM credentials WHERE oj=? AND key NOT IN (%s)"%(','.join('?'*len(keys))),
            (name,) + tuple(keys))
        self.cursor.executemany(
            "INSERT OR REPLACE INTO credentials VALUES (?,?,?)",
            [(name,k,v) for k,v in credential.items()])
        self.conn.commit()
