import os
import sqlite3
import re
import shutil
import textwrap
from tabulate import tabulate

# database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# utils functions
def wrap_text(text, width=40):
    if isinstance(text, str):
        return '\n'.join(textwrap.wrap(text, width=width))
    return text

def truncate_columns(rows, headers, max_cols=6):
    if len(headers) <= max_cols:
        return rows, headers, []

    visible_headers = headers[:max_cols]
    hidden_headers = headers[max_cols:]
    visible_headers.append(f"+{len(hidden_headers)} more")

    new_rows = []
    for row in rows:
        visible_row = list(row[:max_cols])  # تبدیل به لیست برای append
        visible_row.append("...")
        new_rows.append(visible_row)

    return new_rows, visible_headers, hidden_headers

def get_terminal_width():
    return shutil.get_terminal_size((80, 20)).columns

def calculate_column_widths(headers, min_width=15, max_width=50):
    term_width = get_terminal_width()
    padding = 6 * len(headers)
    available_width = max(min_width * len(headers), term_width - padding)
    col_width = max(min_width, min(max_width, available_width // len(headers)))
    return [col_width] * len(headers)

def paginate_and_display(rows, headers, rows_per_page=30, maxcolwidths=None):
    if not rows:
        print(tabulate([], headers=headers, tablefmt="fancy_grid", stralign="center"))
        print("⚠️ No rows to display.")
        return

    # wrap on all row
    wrapped_rows = []
    for row in rows:
        wrapped_row = [wrap_text(cell) for cell in row]
        wrapped_rows.append(wrapped_row)

    total = len(wrapped_rows)
    start = 0
    while start < total:
        end = min(start + rows_per_page, total)
        chunk = wrapped_rows[start:end]
        print(tabulate(chunk, headers=headers, tablefmt="fancy_grid", stralign="center"))
        print(f"\nShowing rows {start+1} to {end} of {total}")
        if end < total:
            input("Press Enter to continue...")
        start += rows_per_page


def parse_command(command):
    return command.strip().strip(';').split()

def describe_table(table_name):
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        exists = cursor.fetchone()
        if not exists:
            print(f"❌ Table '{table_name}' does not exist.")
            return

        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        if columns is None or len(columns) == 0:
            print(f"⚠️ Table '{table_name}' exists but has no columns defined.")
            return

        headers = ['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
        widths = calculate_column_widths(headers)
        paginate_and_display(columns, headers, maxcolwidths=widths)
    except Exception as e:
        print(f"ERROR: {e}")

def show_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    paginate_and_display(tables, ['Tables'])

def select_data(command):
    try:
        cursor.execute(command)
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]

        if not rows:
            print(tabulate([], headers=headers, tablefmt="fancy_grid", stralign="center"))
            print("\nQuery OK, 0 rows returned.")
            return

        # check columns
        max_cols = 7
        show_warning = len(headers) > max_cols
        truncated_rows, truncated_headers, hidden_headers = truncate_columns(rows, headers, max_cols=max_cols)
        paginate_and_display(truncated_rows, truncated_headers)

        if hidden_headers:
            print(f"\n⚠️ Hidden columns: {', '.join(hidden_headers)}")
            print("📝 Tip: Use SELECT col1, col2, ... to display them.")

        # Wrning
        if show_warning:
            print(f"⚠️ Output truncated: Showing {max_cols} columns of {len(headers)}.")
            print("📝 Tip: Use SELECT col1, col2, ... for full column view.")

    except Exception as e:
        print(f"ERROR: {e}")


def insert_update_delete(command):
    try:
        cursor.execute(command)
        conn.commit()
        print("✅ Command executed successfully.")
    except Exception as e:
        print(f"Error: {e}")

def read_multiline_sql():
    print("📥 Enter SQL command (end with semicolon ';'):")
    lines = []
    while True:
        line = input(">> ")
        lines.append(line)
        if ';' in line:
            break
    return '\n'.join(lines)

def main():
    print("""
╔════════════════════════════════════════════════════════╗
║             🛠️ SQLite CLI Interface Guide              ║
╠════════════════════════════════════════════════════════╣
║ You can use the following commands:                    ║
║                                                        ║
║ >> SHOW TABLES;           List all tables              ║
║ >> DESCRIBE table_name;   Show structure of a table    ║
║ >> SELECT * FROM table;   Query data from a table      ║
║ >> INSERT INTO table (...) VALUES (...);               ║
║ >> UPDATE table SET col=val WHERE condition;           ║
║ >> DELETE FROM table WHERE condition;                  ║
║ >> EXIT;                  Quit the application         ║
╚════════════════════════════════════════════════════════╝
""")
    print("📡 SQLite CLI ready. Type your command.")
    while True:

        cmd = read_multiline_sql()

        if not cmd:
            continue
        cmd_upper = cmd.upper()

        if cmd_upper == 'EXIT;':
            break
        elif cmd_upper == 'SHOW TABLES;':
            show_tables()
        elif cmd_upper.startswith("DESCRIBE"):
            parts = parse_command(cmd)
            if len(parts) >= 2:
                describe_table(parts[1])
            else:
                print("ERROR: Usage: DESCRIBE table_name;")
        elif cmd_upper.startswith("SELECT"):
            select_data(cmd)
        elif cmd_upper.startswith(("INSERT", "UPDATE", "DELETE")):
            insert_update_delete(cmd)
        else:
            print("ERROR: Unknown or unsupported command.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
