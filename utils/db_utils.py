import mysql.connector

def reset_login_attempts(email):
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        database="opencart_db"
    )
    cursor = connection.cursor()
    query = "DELETE FROM oc_customer_login WHERE email = %s"
    cursor.execute(query, (email,))
    connection.commit()
    cursor.close()
    connection.close()
