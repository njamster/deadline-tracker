import sqlite3
import argparse
import datetime

import itertools

class Tracker():
    def __init__(self, name, group_by_category):
        self.db_conn = sqlite3.connect(name)
        self.db_conn.row_factory = sqlite3.Row
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS tasks (date TEXT, time TEXT, category TEXT, description TEXT)')
        self.db_conn.commit()

        # delete all records with dates that already passed
        self.cursor.execute("DELETE FROM tasks WHERE date <= datetime('now')");
        self.db_conn.commit()

        self.group_by_category = group_by_category
        self.now = datetime.datetime.now()


    def add_task(self, description, date, time=None, category=None):
        new_task = (date, time, category, description)
        self.cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?)', new_task)
        self.db_conn.commit()


    def edit_task(self):
        # TODO
        pass


    def delete_task(self):
        # TODO
        pass


    def compute_time_left(self, row):
        if row['time']:
            deadline = datetime.datetime.strptime(row['date'] + ' ' + row['time'], '%Y-%m-%d %H:%M')
        else:
            deadline = datetime.datetime.strptime(row['date'], '%Y-%m-%d')

        time_left = deadline - self.now

        days    = time_left.days
        hours   = time_left.seconds // 3600
        minutes = (time_left.seconds // 60) % 60

        if days < 0:
            return '  missed' 
        if days > 0:
            return (str(days) + 'd left').rjust(8, ' ')
        elif hours > 0:
            return (str(hours) + 'h left').rjust(8, ' ')
        else:
            return (str(minutes) + 'm left').rjust(8, ' ')


    def print_row(self, row, print_category=True):
        time_left = self.compute_time_left(row)

        if print_category and row['category']:
            dot_number = 60 - len(row['description']) - len(row['category']) - 3
            print('[%s] %s %s %s' % (row['category'], row['description'], '.' * dot_number, time_left))
        else:
            dot_number = 60 - len(row['description'])
            print('%s %s %s' % (row['description'], '.' * dot_number, time_left))


    def list_tasks(self, categories=None):
        # TODO: how to list only tasks _without_ a category?

        if categories:
            query = 'SELECT * FROM tasks WHERE category IN ('
            query += ','.join('?' for _ in categories)

            if self.group_by_category:
                query += ') ORDER BY category, date, time'
            else:
                query += ') ORDER BY date, time'

            results = self.cursor.execute(query, categories)

            if self.group_by_category:
                for category, rows in itertools.groupby(results, key=lambda r: r[2]):
                    print('\n%s:' % category)
                    for row in rows:
                        self.print_row(row, False)
            else:
                for row in results:
                    self.print_row(row)
        else:
            if self.group_by_category:
                query = 'SELECT * FROM tasks ORDER BY category, date, time'
            else:
                query = 'SELECT * FROM tasks ORDER BY date, time'

            results = self.cursor.execute(query)

            if self.group_by_category:
                for category, rows in itertools.groupby(results, key=lambda r: r[2]):
                    print('\n%s:' % category)
                    for row in rows:
                        self.print_row(row, False)
            else:
                for row in results:
                    self.print_row(row)


if __name__ == "__main__":
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

    parser.add_argument('-G', '--group-by-category', dest='group', action='store_true')

    args = parser.parse_args()

    tracker = Tracker('example.db', args.group)

    if args.operation == 'add':
        tracker.add_task(args.description, args.date, args.time, args.category)
    elif args.operation == 'listonly':
        tracker.list_tasks(args.category)
    else:
        tracker.list_tasks()
