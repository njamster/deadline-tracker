import sqlite3
import argparse

from dateutil.relativedelta import relativedelta
import datetime


class Tracker():
    def __init__(self, name):
        self.db_conn = sqlite3.connect(name)
        self.db_conn.row_factory = sqlite3.Row
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS tasks (date TEXT, time TEXT, category TEXT, description TEXT)')
        self.db_conn.commit()


    def add_task(self, description, date, time=None, category=None):
        new_task = (date, time, category, description)
        self.cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?)', new_task)
        self.db_conn.commit()


    def print_row(self, row):
        today = datetime.date.today()

        if row['time']:
            deadline = datetime.datetime.strptime(row['date'] + ' ' + row['time'], '%Y-%m-%d %H:%M')
            time_left = relativedelta(deadline, today)
            print(time_left)
            
            if row['category']:
                print('%s, %s: [%s] %s' % (row['date'], row['time'], row['category'], row['description']))
            else:
                print('%s, %s: %s' % (row['date'], row['time'], row['description']))
        else:
            deadline = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
            time_left = relativedelta(deadline, today)
            print(time_left)

            if row['category']:
                print('%s: [%s] %s' % (row['date'], row['category'], row['description']))
            else:
                print('%s: %s' % (row['date'], row['description']))


    def list_tasks(self, categories=None):
        if categories:
            query = 'SELECT * FROM tasks WHERE category IN ('
            query += ','.join('?' for _ in categories)
            query += ') ORDER BY date, time'

            for row in self.cursor.execute(query, categories):
                self.print_row(row)
        else:
            for row in self.cursor.execute('SELECT * FROM tasks ORDER BY date, time'):
                self.print_row(row)


if __name__ == "__main__":
    tracker = Tracker('example.db')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='operation')

    parser_op_add = subparsers.add_parser('add', help='add a new task')
    parser_op_add.add_argument('description', action='store')
    parser_op_add.add_argument('date', action='store')
    parser_op_add.add_argument('time', action='store', nargs='?')
    parser_op_add.add_argument('category', action='store', nargs='?')

    parser_op_add = subparsers.add_parser('listonly', help='list a category')
    parser_op_add.add_argument('category', nargs='+', action='store')

    args = parser.parse_args()

    if args.operation == 'add':
        tracker.add_task(args.description, args.date, args.time, args.category)
    elif args.operation == 'listonly':
        tracker.list_tasks(args.category)
    else:
        tracker.list_tasks()
