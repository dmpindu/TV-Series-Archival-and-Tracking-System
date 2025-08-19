import mysql.connector
import hashlib
import matplotlib.pyplot as plt

# --------- DATABASE CONFIG --------------

db_config = {
    'host': 'mysql-2ea854e1-tvarchive.b.aivencloud.com',
    'user': 'avnadmin',
    'port': 24192,
    'passwd': 'AVNS_0ycqFP-8ogLpMFf5yCm',
    'database': 'TVArchive'
}


def connect():
    return mysql.connector.connect(**db_config)


def hash_pass(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# ----------- USER MANAGEMENT -------

def reg_user(username, password, permissions="user"):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO UserInformation (Username, Password, Permissions)
            VALUES (%s, %s, %s)
        """, (username, hash_pass(password), permissions))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        conn.close()



def login(username, password):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Username, Permissions FROM UserInformation
        WHERE Username = %s AND Password = %s
    """, (username, hash_pass(password)))
    result = cursor.fetchone()
    conn.close()
    return result if result else None  # (username, permissions)



# ------- SERIES FUNCTIONS ------

def add_series():
    sid = input("Series ID: ")
    name = input("Series Name: ")
    length = input("Length (e.g., '3 Seasons'): ")
    genre = input("Genre: ")
    release = input("Release Date (YYYY-MM-DD): ")

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Series (SeriesID, SeriesName, SeriesLengthEP, SeriesGenre, ReleaseDate)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE SeriesName=VALUES(SeriesName)
    """, (sid, name, length, genre, release))
    conn.commit()
    conn.close()
    print("Series added.")


def find_series():
    conn = connect()
    cursor = conn.cursor()

    # Optional filters
    genre_filter = input("Enter genre to filter by (or press Enter to skip): ").strip()
    print("Sort by:\n1. Release Date\n2. Series Length\n3. No sorting")
    sort_choice = input("Choose sorting option (1/2/3): ").strip()

    query = "SELECT SeriesID, SeriesName, SeriesLengthEP, SeriesGenre, ReleaseDate FROM Series"
    conditions = []
    params = []

    if genre_filter:
        conditions.append("SeriesGenre LIKE %s")
        params.append(f"%{genre_filter}%")



    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_choice == '1':
        query += " ORDER BY ReleaseDate"
    elif sort_choice == '2':
        query += " ORDER BY SeriesLengthEP"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("No series found.")
        return

    print("\n--- Series List ---")
    for row in results:
        sid, name, length, genre, release = row
        print(f"ID: {sid} | Title: {name} | Length: {length} | Genre: {genre} | Release: {release}")

def view_public_ratings():
    conn = connect()
    cursor = conn.cursor()

    print("\nPublic Ratings Options:")
    print("1. View all")
    print("2. Search by Series ID")
    print("3. Sort by IMDB")
    print("4. Sort by Rotten Tomatoes")
    choice = input("Choose an option (1-4): ").strip()

    query = """
        SELECT s.SeriesName, r.IMDB, r.Rotten_Tomatoes
        FROM Rating r
        JOIN Series s ON r.SeriesID = s.SeriesID
    """
    params = []

    if choice == '2':
        sid = input("Enter Series ID: ").strip()
        query += " WHERE r.SeriesID = %s"
        params.append(sid)
    elif choice == '3':
        order = input("Sort IMDB ascending or descending? (asc/desc): ").strip().lower()
        if order not in ['asc', 'desc']:
            order = 'desc'
        query += f" ORDER BY r.IMDB {order.upper()}"
    elif choice == '4':
        order = input("Sort Rotten Tomatoes ascending or descending? (asc/desc): ").strip().lower()
        if order not in ['asc', 'desc']:
            order = 'desc'
        query += f" ORDER BY r.Rotten_Tomatoes {order.upper()}"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("No ratings found.")
        return

    print("\nSeries Ratings:")
    for name, imdb, rt in results:
        rt_display = "N/A" if rt == 101 else f"{rt}%"
        print(f"{name} | IMDB: {imdb} | Rotten Tomatoes: {rt_display}")



# ----------- SERVICE FUNCTIONS ----------------

def add_service():
    sid = input("Service ID: ")
    name = input("Service Name: ")
    price_ads = float(input("Price (with ads): "))
    price_no_ads = float(input("Price (no ads): "))

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Service (ServiceID, ServiceName, PriceWithAds, PriceWithoutAds)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE PriceWithAds=VALUES(PriceWithAds), PriceWithoutAds=VALUES(PriceWithoutAds)
    """, (sid, name, price_ads, price_no_ads))
    conn.commit()
    conn.close()
    print("Service added.")

def show_services():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * 
        FROM Service
    """)
    services = cursor.fetchall()
    conn.close()

    if not services:
        print("No streaming services found.")
        return

    print("\n--- Streaming Services ---")
    for sid, name, ads_price, noads_price in services:
        print(f"ID: {sid} | Name: {name} | Price with Ads: ${ads_price:.2f} | Price without Ads: ${noads_price:.2f}")

#--link and display--
def link_series_service():
    services = {
        1: "Netflix",
        2: "Hulu",
        3: "MAX",
        4: "Disney+",
        5: "Amazon Prime VIdeo",
        7: "Paramount+",
        8: "CrunchyRoll",
        10: "Discovery+",
        11: "Peacock",
        12: "testing"
    }

    print("\nAvailable Services:")
    print("ID: 5 | Name: Amazon Prime VIdeo | Price with Ads: $8.99 | Price without Ads: $11.98")
    print("ID: 8 | Name: CrunchyRoll | Price with Ads: $0.00 | Price without Ads: $7.99")
    print("ID: 10 | Name: Discovery+ | Price with Ads: $5.99 | Price without Ads: $9.99")
    print("ID: 4 | Name: Disney+ | Price with Ads: $7.99 | Price without Ads: $12.99")
    print("ID: 2 | Name: Hulu | Price with Ads: $7.99 | Price without Ads: $17.99")
    print("ID: 3 | Name: MAX | Price with Ads: $9.99 | Price without Ads: $16.99")
    print("ID: 1 | Name: Netflix | Price with Ads: $7.99 | Price without Ads: $17.99")
    print("ID: 7 | Name: Paramount+ | Price with Ads: $7.99 | Price without Ads: $12.99")
    print("ID: 11 | Name: Peacock | Price with Ads: $7.99 | Price without Ads: $13.99")
    print("ID: 12 | Name: testing | Price with Ads: $1.23 | Price without Ads: $3.45")

    sid = input("\nEnter Series ID: ")
    input_ids = input("Enter Service ID(s) to link (comma-separated): ")
    
    try:
        service_ids = [int(s.strip()) for s in input_ids.split(',')]
    except ValueError:
        print("Invalid input. Please enter only numeric service IDs.")
        return

    conn = connect()
    cursor = conn.cursor()

    for service_id in service_ids:
        service_name = services.get(service_id)
        if service_name:
            cursor.execute("""
                INSERT IGNORE INTO WhereToWatch (SeriesID, ServiceName)
                VALUES (%s, %s)
            """, (sid, service_name))
        else:
            print(f"Service ID {service_id} not recognized. Skipping.")

    conn.commit()
    conn.close()
    print("Series linked to selected services.")

def view_series_services():
    sid = input("Enter Series ID to view its services: ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ServiceName FROM WhereToWatch
        WHERE SeriesID = %s
    """, (sid,))
    results = cursor.fetchall()

    conn.close()

    if results:
        print(f"Services linked to Series ID {sid}:")
        for row in results:
            print(f"- {row[0]}")
    else:
        print("No services linked to this series.")


def compare_prices():
    conn = connect()
    cursor = conn.cursor()

    # Display available series for user to choose
    cursor.execute("SELECT SeriesID, SeriesName FROM Series")
    series_list = cursor.fetchall()

    if not series_list:
        print("No series available.")
        conn.close()
        return

    print("\nAvailable Series:")
    for sid, name in series_list:
        print(f"{sid}: {name}")

    selected_id = input("Enter the Series ID to compare prices for: ")

    # Fetch and display services linked to selected series
    cursor.execute("""
        SELECT s.ServiceName, s.PriceWithAds, s.PriceWithoutAds
        FROM Service s
        JOIN WhereToWatch wtw ON s.ServiceName = wtw.ServiceName
        WHERE wtw.SeriesID = %s
    """, (selected_id,))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("No services linked to this series.")
        return

    print(f"\nServices linked to Series ID {selected_id}:")
    for service in results:
        print(f"{service[0]} | Ads: ${service[1]} | No Ads: ${service[2]}")



# ---- HISTORY AND RATING ---------

def mark_status(username):
    try:
        series_id = int(input("Enter the Series ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    conn = connect()
    cursor = conn.cursor()

    # Get the series name from ID
    cursor.execute("SELECT SeriesName FROM Series WHERE SeriesID = %s", (series_id,))
    result = cursor.fetchone()

    if not result:
        print("Series not found.")
        conn.close()
        return

    series_name = result[0]

    watch_status = input("Enter your watch status (e.g., Watching, Completed, Dropped): ").strip()

    enjoy_input = input("Did you enjoy the show? (Yes or No, leave blank to skip): ").strip().lower()
    if enjoy_input in ("yes", "y", "liked", "like"):
        like_dislike = "Liked"
    elif enjoy_input in ("no", "n", "disliked", "dislike"):
        like_dislike = "Disliked"
    else:
        like_dislike = None

    cursor.execute("""
        INSERT INTO UserHistory (Username, SeriesID, WatchStatus, Like_Dislike)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE WatchStatus = VALUES(WatchStatus), Like_Dislike = VALUES(Like_Dislike)
    """, (username.strip(), series_id, watch_status, like_dislike))

    conn.commit()
    conn.close()
    print(f"Status updated for '{series_name}'.")


def show_watch_history(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.SeriesName, uh.WatchStatus, uh.Like_Dislike
        FROM UserHistory uh
        JOIN Series s ON uh.SeriesID = s.SeriesID
        WHERE uh.Username = %s
    """, (username.strip(),))

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("No watch history found.")
        return

    print("\nYour Watch History:")
    for series_name, status, like_dislike in results:
        line = f"{series_name} | Status: {status.capitalize()}"
        if like_dislike:
            line += f" | {like_dislike}"
        print(line)
 

def add_rating():
    sid = input("Series ID: ")
    imdb = float(input("IMDB Rating: "))
    rt = float(input("Rotten Tomatoes Rating: "))
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        REPLACE INTO Rating (SeriesID, IMDB, Rotten_Tomatoes)
        VALUES (%s, %s, %s)
    """, (sid, imdb, rt))
    conn.commit()
    conn.close()
    print("Rating added.")


# ------------ CREATOR FUNCTIONS ---------------

def add_creator():
    cid = input("Creator ID: ")
    name = input("Creator Name: ")
    twitter = input("Twitter Handle: ")
    insta = input("Instagram Handle: ")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT IGNORE INTO Creator (CreatorID, CreatorName, Twitter, Instagram)
        VALUES (%s, %s, %s, %s)
    """, (cid, name, twitter, insta))
    conn.commit()
    conn.close()
    print("Creator added.")


def link_creator():
    sid = input("Series ID: ")
    cname = input("Creator Name: ")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO SeriesCreators (SeriesID, CreatorName) VALUES (%s, %s)", (sid, cname))
    conn.commit()
    conn.close()
    print("Creator linked to series.")


def get_creators():
    seriesname = input("Enter series name to get creators: ")
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.CreatorName, c.Twitter, c.Instagram
        FROM Creator c
        JOIN SeriesCreators sc ON c.CreatorID = sc.CreatorID
        JOIN Series s ON sc.SeriesID = s.SeriesID
        WHERE s.SeriesName = %s
    """, (seriesname,))
    
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("No creators found for this series.")
    else:
        print(f"\nCreators for '{seriesname}':")
        for i, c in enumerate(results, start=1):
            print(f"\nCreator {i}:")
            print(f"  Name     : {c[0]}")
            print(f"  Twitter  : {c[1] if c[1] else 'N/A'}")
            print(f"  Instagram: {c[2] if c[2] else 'N/A'}")


        

# ---------- ANALYTICS ----------------

def plot_genres(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.SeriesGenre, COUNT(*)
        FROM UserHistory u
        JOIN Series s ON u.SeriesID = s.SeriesID
        WHERE u.Username = %s
        GROUP BY s.SeriesGenre
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        genres, counts = zip(*rows)
        plt.bar(genres, counts)
        plt.xticks(rotation=45)
        plt.title("Genres Watched")
        plt.tight_layout()
        plt.show()
    else:
        print("No genre data available.")


def plot_likes(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Like_Dislike, COUNT(*) FROM UserHistory
        WHERE Username = %s
        GROUP BY Like_Dislike
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        labels = ['Dislike', 'Like'] if len(rows) == 2 else ['Like' if rows[0][0] else 'Dislike']
        sizes = [x[1] for x in rows]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Likes vs Dislikes")
        plt.show()
    else:
        print("No like/dislike data available.")


def spending(username):
    ad_type = input("Ad preference (with/without/both): ")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT s.Price_ADs, s.Price_NoADS
        FROM Service s
        JOIN WhereToWatch wtw ON s.Service_Name = wtw.Service_Name
        JOIN UserHistory uh ON wtw.SeriesID = uh.SeriesID
        WHERE uh.Username = %s
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    total = 0
    for ads, noads in rows:
        if ad_type == 'with':
            total += ads
        elif ad_type == 'without':
            total += noads
        else:
            total += (ads + noads) / 2
    print(f"Estimated monthly spending: ${total:.2f}")
  #-- User Rating ---
def add_personal_rating(username):
    sid = input("Series ID: ")
    rating = float(input("Your personal rating (0–10): "))
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO UserRatings (Username, SeriesID, Personal_Rating)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE Personal_Rating = VALUES(Personal_Rating)
    """, (username, sid, rating))
    conn.commit()
    conn.close()
    print("Your personal rating was saved.")
def get_personal_rating(username):
    sid = input("Series ID: ")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Personal_Rating FROM UserRatings
        WHERE Username = %s AND SeriesID = %s
    """, (username, sid))
    row = cursor.fetchone()
    conn.close()
    if row:
        print(f"Your rating for series {sid}: {row[0]}")
    else:
        print("You haven't rated this series yet.")

# --------- MAIN CLI LOOP ------------

def main():
    print("Welcome to TV Show Tracker")

    choice = input("Login or Register? (l/r): ").strip().lower()
    uname = None
    permissions = "user"

    if choice == 'r':
        uname = input("New username: ")
        pw = input("New password: ")
        if reg_user(uname, pw):
            print("User registered.")
        else:
            print("Username already exists.")
    elif choice == 'l':
        uname = input("Username: ")
        pw = input("Password: ")
        login_result = login(uname, pw)
        if not login_result:
            print("Invalid login.")
            return
        uname, permissions = login_result
        print(f"Welcome back, {uname} ({permissions})!")

    while True:
        print("\nOptions:")

        # Display options with consistent numbering
        option_map = {}
        option_number = 1

        print(f"{option_number}. Find Series")
        option_map[str(option_number)] = 'find_series'
        option_number += 1
        
        print(f"{option_number}. Show Services")
        option_map[str(option_number)] = 'show_services'
        option_number += 1
        
        print(f"{option_number}. View Services for Series")
        option_map[str(option_number)] = 'view_series_services'
        option_number += 1

        print(f"{option_number}. Compare Prices")
        option_map[str(option_number)] = 'compare_prices'
        option_number += 1

        print(f"{option_number}. Mark Watch Status")
        option_map[str(option_number)] = 'mark_status'
        option_number += 1
        
        print(f"{option_number}. Show Watch History")
        option_map[str(option_number)] = 'show_watch_history'
        option_number += 1

        print(f"{option_number}. Get Creators")
        option_map[str(option_number)] = 'get_creators'
        option_number += 1

        print(f"{option_number}. Plot Genres Watched")
        option_map[str(option_number)] = 'plot_genres'
        option_number += 1

        print(f"{option_number}. Plot Likes/Dislikes")
        option_map[str(option_number)] = 'plot_likes'
        option_number += 1

        print(f"{option_number}. Spending Summary")
        option_map[str(option_number)] = 'spending'
        option_number += 1

        print(f"{option_number}. Add Personal Rating")
        option_map[str(option_number)] = 'add_personal_rating'
        option_number += 1

        print(f"{option_number}. View Your Rating")
        option_map[str(option_number)] = 'get_personal_rating'
        option_number += 1
      
        print(f"{option_number}. View Public Ratings")
        option_map[str(option_number)] = 'view_public_ratings'
        option_number += 1

        print(f"{option_number}. Enter Admin Passcode")
        option_map[str(option_number)] = 'become_admin'
        option_number += 1

        if permissions == 'admin':
            print(f"{option_number}. Add Series [ADMIN]")
            option_map[str(option_number)] = 'add_series'
            option_number += 1

            print(f"{option_number}. Add Service [ADMIN]")
            option_map[str(option_number)] = 'add_service'
            option_number += 1

            print(f"{option_number}. Link Series to Service [ADMIN]")
            option_map[str(option_number)] = 'link_seriesservice'
            option_number += 1

            print(f"{option_number}. Add Rating (Public) [ADMIN]")
            option_map[str(option_number)] = 'add_rating'
            option_number += 1

            print(f"{option_number}. Add Creator [ADMIN]")
            option_map[str(option_number)] = 'add_creator'
            option_number += 1

            print(f"{option_number}. Link Creator to Series [ADMIN]")
            option_map[str(option_number)] = 'link_creator'
            option_number += 1

        print("0. Exit")

        opt = input("Choose: ").strip()

        if opt == '0':
            print("Goodbye!")
            break

        elif opt not in option_map:
            print("Invalid option.")
            continue

        selected = option_map[opt]

        if selected == 'find_series':
            find_series()
        elif selected == 'show_services':
            show_services()
        elif selected == 'view_series_services':
            view_series_services()
        elif selected == 'compare_prices':
            compare_prices()
        elif selected == 'mark_status':
            mark_status(uname)
        elif selected == 'show_watch_history':
            show_watch_history(uname)
        elif selected == 'view_public_ratings':
            view_public_ratings()
        elif selected == 'get_creators':
            get_creators()
        elif selected == 'plot_genres':
            plot_genres(uname)
        elif selected == 'plot_likes':
            plot_likes(uname)
        elif selected == 'spending':
            print("Spending:", spending(uname))
        elif selected == 'add_personal_rating':
            add_personal_rating(uname)
        elif selected == 'get_personal_rating':
            get_personal_rating(uname)
        elif selected == 'become_admin':
            code = input("Enter admin passcode: ")
            if code == "BecomeAdmin":
                conn = connect()
                cursor = conn.cursor()
                cursor.execute("UPDATE UserInformation SET Permissions = 'admin' WHERE Username = %s", (uname,))
                conn.commit()
                conn.close()
                permissions = 'admin'
                print("You are now an admin!")
            else:
                print("Incorrect passcode.")
        elif selected == 'add_series':
            add_series()
        elif selected == 'add_service':
            add_service()
        elif selected == 'link_seriesservice':
            link_series_service()
        elif selected == 'add_rating':
            add_rating()
        elif selected == 'add_creator':
            add_creator()
        elif selected == 'link_creator':
            link_creator()





if __name__ == '__main__':
    main()
