import mysql.connector

def db_available():
    try:
        import mysql.connector
        return True
    except ModuleNotFoundError:
        return False



def reset_login_attempts(email):
    try:
        import mysql.connector
    except ModuleNotFoundError:
        print("MySQL not installed → skipping DB reset.")
        return

    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="opencart_db",
            connection_timeout=3
        )
    except Exception:
        print("MySQL not running → skipping DB reset.")
        return

    cursor = connection.cursor()
    query = "DELETE FROM oc_customer_login WHERE email = %s"
    cursor.execute(query, (email,))
    connection.commit()
    cursor.close()
    connection.close()

