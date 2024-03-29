import psycopg2
import bcrypt
import os
import configparser


class Connection:
    def __init__(self):
        # Read db credentials from config.ini
        config = configparser.ConfigParser()
        config.read("config.ini")
        config_db_name = config["db_creds"]["DBName"]
        config_login = config["db_creds"]["Login"]
        config_password = config["db_creds"]["Password"]

        # Connect to an existing database
        self.conn = psycopg2.connect(dbname=config_db_name,
                                     user=os.environ[config_login],
                                     password=os.environ[config_password])
        # Open a cursor to perform database operations
        self.cur = self.conn.cursor()

    def check_user(self, auth_username):
        self.cur.execute("SELECT 1 FROM test_users WHERE username=%s", (auth_username,))
        result = self.cur.fetchone()
        return result

    def check_password(self, auth_username, auth_password):
        self.cur.execute(f"SELECT password FROM test_users WHERE username = '{auth_username}';")
        stored_password = self.cur.fetchone()[0]
        auth_password = auth_password.encode('utf-8')
        stored_password = stored_password.encode('utf-8')
        result = bcrypt.checkpw(auth_password, stored_password)
        return result

    def get_all_records(self):
        self.cur.execute("SELECT * FROM test ORDER BY id;")
        all_records = self.cur.fetchall()
        return all_records

    def get_column_names(self):
        self.cur.execute("SELECT * FROM test;")
        column_names = [desc[0] for desc in self.cur.description]
        return column_names

    def insert_record(self, col_n, values):
        columns = ", ".join(col_n[1:])
        values_formatting = ', '.join(["%s"]*len(values))
        query = f"INSERT INTO test ({columns}) VALUES ({values_formatting});"
        self.cur.execute(query, (*values,))
        self.conn.commit()

    def update_record(self, col_n, new_values, rec_id):
        set_l = []
        for i in range(1, len(col_n)):
            set_l.append(col_n[i] + "=" + "%s")
        set_s = ", ".join(set_l)
        query = f"UPDATE test SET {set_s} WHERE id = {rec_id};"
        self.cur.execute(query, (*new_values,))
        self.conn.commit()

    def delete_record(self, row_id):
        self.cur.execute("DELETE FROM TEST WHERE id=" + row_id)
        self.conn.commit()

    def delete_multiple(self, id_list):
        id_list = map(str, id_list)
        id_string = ", ".join(id_list)
        self.cur.execute("DELETE FROM TEST WHERE id IN(" + id_string + ")")
        self.conn.commit()

    def finish_connection(self):
        # Close communication with the database
        self.cur.close()
        self.conn.close()
