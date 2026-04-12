from database.connection import get_connection

def create_tables():
    conn = get_connection() #obtenir une connexion à la base de données
    conn.execute('''
        CREATE TABLE IF NOT EXISTS 
        users ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    conn.execute('''
                CREATE TABLE IF NOT EXISTS
                categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
    ''')

    conn.execute('''
                CREATE TABLE IF NOT EXISTS
                transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER,
                    amount REAL NOT NULL CHECK (amount > 0),
                    date TEXT NOT NULL CHECK (date GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'),
                    description TEXT,
                    type TEXT NOT NULL CHECK (type IN ('revenu', 'depense')),
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
                )
    ''')
    conn.commit()