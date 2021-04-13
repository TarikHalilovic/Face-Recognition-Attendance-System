import sqlite3 as sq

class LocalDb:
    def __init__(self):
        self.conn = sq.connect('local.db', check_same_thread=False)
        self.c = self.conn.cursor()
        self._initialize_db()
    
    def __del__(self):
        self.conn.close()
    
    def _initialize_db(self):
        self.c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='action' ''')
        if self.c.fetchone()[0]==0:
            self.c.execute('''CREATE TABLE action
                (id INTEGER NOT NULL PRIMARY KEY,
                event_id INTEGER not null,
                personnel_id INTEGER not null,
                date_time INT NOT NULL)''')
                # FOREIGN KEY (personnel_id) REFERENCES personnel (id))''')
            #self.c.execute('''CREATE TABLE personnel
            #    (id integer not null primary key,
            #    first_name text not null,
            #    last_name text not null)''')
        self.conn.commit()
            
    #def add_user(self, user_id, first_name, last_name):
    #    self.c.execute("INSERT INTO personnel VALUES (?, ?, ?)", user_id, first_name, last_name)
    #    self.conn.commit()
        
    def add_action(self, event_id, personnel_id, date_time):
        self.c.execute('''INSERT INTO action (event_id, personnel_id, date_time) VALUES (?, ?, ?)''', (event_id, personnel_id, date_time))
        self.conn.commit()
        
    def get_last_n_actions(self, n, personnel_id, offset = 0):
        self.c.execute('''SELECT * FROM action WHERE personnel_id = ? ORDER BY date_time DESC LIMIT ? OFFSET ?''', (personnel_id, n, offset))
        return self.c.fetchall()
        
    def delete_last_action(self):
        self.c.execute('''DELETE FROM action WHERE id = (SELECT MAX(id) FROM action)''')
        self.conn.commit()