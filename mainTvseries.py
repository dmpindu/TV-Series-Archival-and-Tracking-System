import sqlite3
import hashlib
from datetime import datetime
import matplotlib.pyplot as plt


db_path = "./series_tracker.db"


def connect():
    return sqlite3.connect(db_path)


def hash_pass(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def reg_user(username, pw):
    with connect() as c:
        try:
            c.execute("INSERT INTO UserInformation (Username, Password) VALUES (?, ?)",
                      (username, hash_pass(pw)))
            c.commit()
            return True
        except:
            return False


def login(username, pw):
    with connect() as c:
        res = c.execute("SELECT Username FROM UserInformation WHERE Username=? AND Password=?",
                        (username, hash_pass(pw))).fetchone()
        return res[0] if res else None


def add_series(sid, name, length, genre, release):
    with connect() as c:
        c.execute("INSERT OR IGNORE INTO Series VALUES (?, ?, ?, ?, ?)", (sid, name, length, genre, release))
        c.commit()


def find_series(name):
    with connect() as c:
        return c.execute("SELECT * FROM Series WHERE Series_Name LIKE ?", (f"%{name}%",)).fetchall()


def add_service(sid, name, ads, no_ads):
    with connect() as c:
        c.execute("INSERT OR IGNORE INTO Service VALUES (?, ?, ?, ?)", (sid, name, ads, no_ads))
        c.commit()


def link_series_service(sid, service):
    with connect() as c:
        c.execute("INSERT INTO WhereToWatch VALUES (?, ?)", (sid, service))
        c.commit()


def compare_prices(series_name):
    with connect() as c:
        q = """
        SELECT s.Service_Name, s.Price_ADs, s.Price_NoADS
        FROM Service s
        JOIN WhereToWatch wtw ON s.Service_ID = wtw.Service_Name
        JOIN Series se ON wtw.Series_ID = se.Series_ID
        WHERE se.Series_Name = ?
        """
        return c.execute(q, (series_name,)).fetchall()


def mark_status(user, sid, stat, liked):
    with connect() as c:
        c.execute("INSERT INTO UserHistory (Username, Series_ID, Watch_Status, Like_Dislike) VALUES (?, ?, ?, ?)",
                  (user, sid, stat, liked))
        c.commit()


def add_rating(sid, imdb, rt):
    with connect() as c:
        c.execute("INSERT OR REPLACE INTO Ratings VALUES (?, ?, ?)", (sid, imdb, rt))
        c.commit()


def add_creator(cid, name, tw, insta):
    with connect() as c:
        c.execute("INSERT OR IGNORE INTO Creator VALUES (?, ?, ?, ?)", (cid, name, tw, insta))
        c.commit()


def link_creator(sid, cname):
    with connect() as c:
        c.execute("INSERT INTO SeriesCreators VALUES (?, ?)", (sid, cname))
        c.commit()


def get_creators(series):
    with connect() as c:
        q = """
        SELECT c.Creator_Name, c.Twitter, c.Instagram
        FROM Creator c
        JOIN SeriesCreators sc ON c.Creator_Name = sc.Creator_Name
        JOIN Series s ON s.Series_ID = sc.Series_ID
        WHERE s.Series_Name = ?
        """
        return c.execute(q, (series,)).fetchall()


def plot_genres(username):
    with connect() as c:
        rows = c.execute("""
            SELECT s.Genre, COUNT(*) FROM UserHistory u
            JOIN Series s ON u.Series_ID = s.Series_ID
            WHERE u.Username = ? GROUP BY s.Genre
        """, (username,)).fetchall()
    if rows:
        g, cnt = zip(*rows)
        plt.bar(g, cnt)
        plt.title('Genres Watched')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def plot_likes(username):
    with connect() as c:
        rows = c.execute("SELECT Like_Dislike, COUNT(*) FROM UserHistory WHERE Username = ? GROUP BY Like_Dislike", (username,)).fetchall()
    if rows:
        labs = ['Dislike', 'Like'] if len(rows) == 2 else ['Like' if rows[0][0] else 'Dislike']
        vals = [x[1] for x in rows]
        plt.pie(vals, labels=labs, autopct='%1.1ff%%')
        plt.title('Like vs Dislike')
        plt.show()


def spending(username, ad_type='both'):
    with connect() as c:
        rows = c.execute("""
            SELECT DISTINCT s.Price_ADs, s.Price_NoADS
            FROM Service s
            JOIN WhereToWatch wtw ON s.Service_ID = wtw.Service_Name
            JOIN UserHistory u ON wtw.Series_ID = u.Series_ID
            WHERE u.Username = ?
        """, (username,)).fetchall()
    total = 0
    for ads, noads in rows:
        if ad_type == 'with':
            total += ads
        elif ad_type == 'without':
            total += noads
        else:
            total += (ads + noads) / 2
    return total


if __name__ == '__main__':
    uname = login("alice", "testpass") or reg_user("alice", "testpass")
    print("user:", uname)
    print("found:", find_series("Gilmore"))


    add_service(1, "Netflix", 6.99, 15.49)
    add_service(2, "Hulu", 7.99, 14.99)
    print("compare:", compare_prices("Gilmore Girls"))


    print("spending:", spending(uname))
    plot_genres(uname)
    plot_likes(uname)

