import sqlite3
import argparse
import datetime


class Tracker():
    def __init__(self, name):
        self.db_conn = sqlite3.connect(name)
        self.db_conn.row_factory = sqlite3.Row
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS tasks (date TEXT, time TEXT, category TEXT, description TEXT)')
        self.db_conn.commit()

        self.now = datetime.datetime.now()


    def add_task(self, description, date, time=None, category=None):
        new_task = (date, time, category, description)
        self.cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?)', new_task)
        self.db_conn.commit()


    def compute_time_left(self, row):
        if row['time']:
            deadline = datetime.datetime.strptime(row['date'] + ' ' + row['time'], '%Y-%m-%d %H:%M')
        else:
            deadline = datetime.datetime.strptime(row['date'], '%Y-%m-%d')

        time_left = deadline - self.now

        if time_left.days < 0:
            # TODO: remove row from db (can this be done automatically?)
            return -1
        else:
            days    = time_left.days
            hours   = time_left.seconds // 3600
            minutes = (time_left.seconds // 60) % 60

            if days > 0:
                return '%02.dd' % days
            elif hours > 0:
                return '%02.dh' % hours
            else:
                return '%02.dm' % minutes


    def print_row(self, row):
        time_left = self.compute_time_left(row)
        if time_left == -1:
            return

        if row['category']:
            print('%s left: [%s] %s' % (time_left, row['category'], row['description']))
        else:
            print('%s left: %s' % (time_left, row['description']))


    def list_tasks(self, categories=None):
        if categories:
            # TODO: how to list only tasks _without_ a category?
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
    # TODO: it's not possible to only pass the category but not the time as an argument
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
