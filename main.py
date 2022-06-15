# coding=utf-8
from pprint import pprint
import psycopg2
from prettytable import PrettyTable

conn = psycopg2.connect(database='Clients', user='postgres', password='posParol12380')
with conn.cursor() as cur:
    def drop_table():
        cur.execute("""
        DROP TABLE phone_number;
        DROP TABLE client;        
        """)
        conn.commit()

    def create_table():
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
        clientid SERIAL PRIMARY KEY,
        firstname VARCHAR(60),
        lastname VARCHAR(60),
        email VARCHAR(60)
        );
        """)

    def create_phone_number():
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone_number(
        id SERIAL PRIMARY KEY,
        client_id INTEGER NOT NULL REFERENCES client(clientid),
        phone_number VARCHAR(15)
        );
        """)


    def add_client(cursor):
        firstname = input('Введите имя: ')
        lastname = input('Введите фамилию: ')
        email = input('Введите e-mail: ')
        phone_number = input('Введите номер телефона(опционально): ')
        cursor.execute("""
            INSERT INTO client(firstname, lastname, email) VALUES(%s, %s, %s);
        """, (firstname, lastname, email))
        conn.commit()
        cursor.execute("""
            SELECT clientid FROM client WHERE firstname=%s AND lastname=%s AND email=%s LIMIT 1;
        """, (firstname, lastname, email))
        client_id = cursor.fetchone()[0]
        if phone_number != '':
            cursor.execute("""
                    INSERT INTO phone_number(client_id, phone_number) VALUES(%s, %s);
                    """, (client_id, phone_number))
            conn.commit()
        return print('Запись успешно добавлена')

    def add_phone_number(cursor):
        id = int(input('Введите id клиента: '))
        add_phone_number = input('Введите номер телефона: ')
        cursor.execute("""
            INSERT INTO phone_number(client_id, phone_number) VALUES(%s, %s);
            """, (id, add_phone_number))
        conn.commit()

    def select_info(cursor):
        cursor.execute("""
        SELECT * FROM client;
        """)
        print('fetchall', cursor.fetchall())
        cursor.execute("""
                SELECT * FROM phone_number;
                """)
        return print('fetchall', cursor.fetchall())

    def delete_client(cursor):
        client_id = int(input('Введите id клиента: '))
        cursor.execute("""
            DELETE FROM phone_number WHERE client_id=%s;
            """, (client_id, ))
        conn.commit()
        cursor.execute("""
            DELETE FROM client WHERE clientid=%s;
            """, (client_id, ))
        print(f'Клиент с id {client_id} удалён')
        conn.commit()

    def change_client_info(client_id=None):
        client_id = int(input('Введите id клиента: '))
        try:
            cur.execute("""
            SELECT clientid FROM client WHERE clientid=%s LIMIT 1;
            """, (client_id, ))
            if cur.fetchone()[0] == client_id:
                print('Что нужно изменить? \n'
                      '1: Имя\n'
                      '2: Фамилию\n'
                      '3: E-mail\n'
                      '4: Номер телефона'
                      )
                action = int(input())
                if action == 1:
                    firstname = input('Введите новое имя: ')
                    cur.execute("""
                        UPDATE client SET firstname=%s WHERE clientid=%s
                        """, (firstname, client_id))
                    conn.commit()
                elif action == 2:
                    lastname = input('Введите новую фамилию: ')
                    cur.execute("""
                        UPDATE client SET lastname=%s WHERE clientid=%s
                        """, (lastname, client_id))
                    conn.commit()
                elif action == 3:
                    email = input('Введите новый e-mail: ')
                    cur.execute("""
                        UPDATE client SET email=%s WHERE clientid=%s
                        """, (email, client_id))
                    conn.commit()
                elif action == 4:
                    cur.execute("""
                        SELECT phone_number FROM phone_number WHERE client_id=%s;
                        """, (client_id,))
                    print('Номера телефона, доступные для данного клиента:',
                          cur.fetchall())
                    old_phone_number = input('Введите номер, который необходимо изменить: ')
                    phone_number = input('Введите новый номер: ')
                    cur.execute("""
                        UPDATE phone_number SET phone_number=%s WHERE client_id=%s AND phone_number=%s
                        """, (phone_number, client_id, old_phone_number))
                    conn.commit()
                else:
                    print('Таких данных у нас нет')
        except (Exception):
            print('Клиента с таким id нет в базе')

    def delete_phone_number():
        client_id = int(input('Введите id клиента: '))
        try:
            cur.execute("""
                    SELECT clientid FROM client WHERE clientid=%s LIMIT 1;
                    """, (client_id,))
            if cur.fetchone()[0] == client_id:
                print('Сколько номеров нужно удалить? \n'
                      '1: Один\n'
                      '2: Несколько\n'
                      '3: Все'
                      )
                action = int(input())
                if action == 1:
                    cur.execute("""
                        SELECT phone_number FROM phone_number WHERE client_id=%s;
                        """, (client_id,))
                    print('Номера телефона, доступные для данного клиента:',
                          cur.fetchall())
                    phone_number = input('Введите номер, который необходимо удалить: ')
                    cur.execute("""
                        DELETE FROM phone_number WHERE phone_number=%s
                        """, (phone_number, ))
                    conn.commit()
                elif action == 2:
                    key = input('Для продолжения нажмите любую клавишу...\nВыход: q ')
                    while key != 'q':
                        cur.execute("""
                            SELECT phone_number FROM phone_number WHERE client_id=%s;
                            """, (client_id,))
                        print('Номера телефона, доступные для данного клиента:',
                              cur.fetchall())
                        phone_number = input('Введите номер, который необходимо удалить: ')
                        key = phone_number
                        cur.execute("""
                            DELETE FROM phone_number WHERE phone_number=%s
                            """, (phone_number,))
                        conn.commit()
                    if key == 'q':
                        exit()
                elif action == 3:
                    cur.execute("""
                        DELETE FROM phone_number WHERE client_id=%s;
                        """, (client_id,))
                    conn.commit()
                else:
                    print('Таких данных у нас нет')
        except (Exception):
            print('Клиента с таким id нет в базе')

    def find_client():
        data = input('Введите Имя, Фамилию, Номер телефона или e-mail: ')
        cur.execute("""
        SELECT clientid, firstname, lastname, email, phone_number FROM client c 
        LEFT JOIN phone_number pn ON c.clientid = pn.client_id 
        WHERE firstname = %s OR lastname = %s OR email = %s OR phone_number = %s;
        """, (data, data, data, data))
        th = ['id', 'Имя', 'Фамилия', 'e-mail', 'Телефон']
        td = cur.fetchall()
        columns = len(th)
        rows = len(td)
        table = PrettyTable(th)
        for i in range(0, rows):
            td_data = td[:][i]
            while td_data:
                table.add_row(td_data[:columns])
                td_data = td_data[columns:]
        print(table)

    def terminal_choice():
        print('Выберите действие: \n'
              '1: Добавить нового клиента\n'
              '2: Добавить телефон для существующего клиента\n'
              '3: Изменить данные о клиенте\n'
              '4: Удалить телефон для существующего клиента\n'
              '5: Удалить существующего клиента\n'
              '6: Найти клиента по его данным\n'
              '7: Выход'
              )
        try:
            action = int(input())
            if action == 1:
                add_client(cur)
            elif action == 2:
                add_phone_number(cur)
            elif action == 3:
                change_client_info()
            elif action == 4:
                delete_phone_number()
            elif action == 5:
                delete_client(cur)
            elif action == 6:
                find_client()
            elif action == 7:
                exit()
            else:
                print('Такого действия нет')
                terminal_choice()
        except (Exception):
            print('Введите число')
            terminal_choice()


    create_table()
    create_phone_number()
    terminal_choice()
    # select_info(cur)
    # drop_table()

conn.close()