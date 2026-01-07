import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sidoine@2006",
        database="First_taf_IA"
    )


