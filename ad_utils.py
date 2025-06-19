import sqlite3
from datetime import datetime, timedelta

def query_next_rb_ad(within_minutes=10):
    now = datetime.now()
    later = now + timedelta(minutes=within_minutes)
    conn = sqlite3.connect("./data/ads.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT ad_id, company_name, end_time FROM Structured_Ad_calendar
        WHERE rb_nrb='Rb' AND end_time BETWEEN ? AND ?
        ORDER BY end_time ASC LIMIT 1
    """, (now.isoformat(), later.isoformat()))
    result = cur.fetchone()
    conn.close()
    if result:
        return {
            "ad_id": result[0],
            "company_name": result[1],
            "end_time": result[2]
        }
    return None




def is_ad_table_empty(db_path: str = "./data/ads.db", table: str = "Structured_Ad_calendar") -> bool:
    """Return True if the Structured_Ad_calendar table is missing or has zero rows."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT count(1) FROM {table}")
        count = cur.fetchone()[0]
    except sqlite3.OperationalError:
        # table does not exist
        count = 0
    conn.close()
    return ( count == 0 )


def fetch_upcoming_ads(limit: int = 3, db_path: str = "./data/ads.db", table: str = "Structured_Ad_calendar"):
    """Return next `limit` ads ordered by end_time ascending."""
    from datetime import datetime
    now = datetime.now().isoformat()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        f"SELECT ad_id, company_name, end_time FROM {table} ORDER BY end_time ASC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [{"ad_id": r[0], "company_name": r[1], "end_time": r[2]} for r in rows]






