import sqlite3
import pandas as pd

def check_anomaly():
    conn = sqlite3.connect('sales.db')
    
    # FIX: Use 'localtime' otherwise SQLite uses UTC and finds 0 data
    query = """
    SELECT 
        COALESCE(SUM(CASE WHEN timestamp >= datetime('now', 'localtime', '-5 minutes') THEN amount ELSE 0 END),0) as last_5,
        COALESCE(SUM(CASE WHEN timestamp BETWEEN datetime('now', 'localtime', '-35 minutes') AND datetime('now', 'localtime', '-5 minutes') THEN amount ELSE 0 END),0) as prev_30
    FROM orders WHERE payment_status='Success'
    """
    df = pd.read_sql(query, conn)
    last_5 = df['last_5'][0]
    prev_30 = df['prev_30'][0]
    
    prev_avg = prev_30 / 6 if prev_30 > 0 else 0
    
    print(f"DEBUG: Last 5 min sales = Rs.{last_5} | Prev 30 min avg = Rs.{int(prev_avg)}")

    if prev_avg > 0 and last_5 < (prev_avg * 0.7):
        drop_percent = int((1 - last_5/prev_avg)*100)
        root_q = """
        SELECT city, category, COUNT(*) as cnt FROM orders 
        WHERE timestamp >= datetime('now', 'localtime', '-5 minutes') AND payment_status='Failed'
        GROUP BY city, category ORDER BY cnt DESC LIMIT 1
        """
        root_df = pd.read_sql(root_q, conn)
        if not root_df.empty:
            cause = f"{root_df['city'][0]} - {root_df['category'][0]} (Payment Failures)"
        else:
            cause = "General Sales Drop"
        return True, drop_percent, cause, last_5, prev_avg
    
    return False, 0, "No Issue", last_5, prev_avg

# --- THIS PART WAS MISSING, THAT'S WHY NO OUTPUT ---
if __name__ == "__main__":
    print("Checking anomaly...")
    is_anomaly, drop, cause, last_5, prev_avg = check_anomaly()
    
    if is_anomaly:
        print(f"🚨 ALERT: Sales dropped by {drop}%!")
        print(f"🔍 Cause: {cause}")
    else:
        print(f"✅ Normal: {cause}")