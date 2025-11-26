from tabulate import tabulate
import sqlite3
import re
import shutil
import textwrap
import datetime

# Database path
from configs.bot_config import BotConfig
config = BotConfig()
DB_PATH = config.DB_FILE

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# show guide
def show_guide() -> str:
    terminal_width = 80
    border_length = terminal_width

    guide_text = f"""
        ╔{"═" * (border_length - 2)}╗
        ║{" " * (border_length - 2)}║
        ║{" " * ((border_length - len("🛠️ SQLite CLI Interface Guide")) // 2)}🛠️ SQLite CLI Interface Guide{" " * ((border_length - len("🛠️ SQLite CLI Interface Guide")) // 2)}║
        ║{" " * (border_length - 2)}║
        ╠{"═" * (border_length - 2)}╣
        ║ You can use the following commands:                      ║
        ║                                                          ║
        ║ >> SHOW TABLES;           # List all tables              ║
        ║ >> DESCRIBE table_name;   # Show structure of a table    ║
        ║ >> SELECT * FROM table;   # Query data from a table      ║
        ║ >> SELECT * FROM users WHERE id=1 INTO OUTFILE  # Export ║
        ║ >> INSERT INTO table (...) VALUES (...);                 ║
        ║ >> UPDATE table SET col=val WHERE condition;             ║
        ║ >> DELETE FROM table WHERE condition;                    ║
        ║ >> EXIT;                  # Quit the application         ║
        ╚{"═" * (border_length - 2)}╝
        """
    return guide_text

# manage functions
def show_tables():
    """Show all the tables in the SQLite database."""
    try:
        # Adjusting for SQLite: SHOW TABLES is not a valid SQLite command.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("⚠️ No tables found in the database.")
            return

        # Proceed with displaying the tables
        paginate_and_display(tables, ['Tables'])

    except Exception as e:
        print(f"ERROR: {e}")

def parse_command(command: str):
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

def insert_update_delete(command):
    try:
        cursor.execute(command)
        conn.commit()
        print("✅ Command executed successfully.")
    except Exception as e:
        print(f"Error: {e}")

# Utils functions
def wrap_text(text, width=40):
    """Wrap text to fit the specified width."""
    if isinstance(text, str):
        return '\n'.join(textwrap.wrap(text, width=width))
    return text

def truncate_columns(rows, headers, max_cols=6):
    """Truncate columns if the number of columns exceeds max_cols."""
    if len(headers) <= max_cols:
        return rows, headers, []

    visible_headers = headers[:max_cols]
    hidden_headers = headers[max_cols:]
    visible_headers.append(f"+{len(hidden_headers)} more")

    new_rows = []
    for row in rows:
        visible_row = list(row[:max_cols])  # Convert to list for appending
        visible_row.append("...")
        new_rows.append(visible_row)

    return new_rows, visible_headers, hidden_headers

def get_terminal_width():
    """Get the current terminal width for better formatting."""
    return shutil.get_terminal_size((80, 20)).columns

def calculate_column_widths(headers, min_width=10, max_width=30):
    """Calculate column widths based on the number of columns and terminal width."""
    term_width = get_terminal_width()
    # If the number of columns is more than 5, reduce the column width
    if len(headers) > 5:
        col_width = max(min_width, min(max_width, term_width // len(headers)))
    else:
        col_width = max(min_width, min(max_width, term_width // len(headers)))
    return [col_width] * len(headers)

def paginate_and_display(rows, headers, rows_per_page=30, maxcolwidths=None):
    """Paginate and display the rows in the terminal with proper formatting."""
    if rows is None or len(rows) == 0:
        print(tabulate([], headers=headers, tablefmt="fancy_grid", stralign="center"))
        print("⚠️ No rows to display.")
        return

    # Wrap all rows
    wrapped_rows = []
    for row in rows:
        wrapped_row = [wrap_text(cell, width=maxcolwidths[i]) if maxcolwidths else wrap_text(cell) for i, cell in enumerate(row)]
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

def handle_large_columns(rows, headers):
    """Handle large columns that may get truncated in the output."""
    max_cols = 7  # Maximum number of columns to display at once
    show_warning = len(headers) > max_cols

    if show_warning:
        print(f"⚠️ Output truncated: Showing {max_cols} columns of {len(headers)}.")
        print("📝 Tip: Use SELECT col1, col2, ... for full column views.")

    # Truncate the columns
    truncated_rows, truncated_headers, hidden_headers = truncate_columns(rows, headers, max_cols=max_cols)
    paginate_and_display(truncated_rows, truncated_headers)

    if hidden_headers:
        print(f"\n⚠️ Hidden columns: {', '.join(hidden_headers)}")
        print("📝 Tip: To view the full content of the hidden columns, try running:")
        print(f"   SELECT {', '.join(hidden_headers)} FROM table_name;")

import re
import datetime

def select_data(command: str, 
                output_file=None, 
                delimiter=',', 
                enclosure='"', 
                line_terminator='\n'):
    """Execute SELECT query and optionally save the output to a file with default parameters."""
    try:
        # DETECTED INTO OUTFILE
        if re.search(r'into\s+outfile', command, flags=re.IGNORECASE):
            if not output_file:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"query_output_{timestamp}.csv"

            # Clean cammand
            command = re.split(r'into\s+outfile.*', command, flags=re.IGNORECASE)[0].strip()

            # Execute SELECT
            cursor.execute(command)
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]

            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(enclosure + delimiter.join(headers) + enclosure + line_terminator)
                for row in rows:
                    wrapped_row = [str(cell) for cell in row]
                    f.write(enclosure + delimiter.join(wrapped_row) + enclosure + line_terminator)

            print(f"✅ Query OK, results saved to {output_file}")

        else:
            # Execute SELECT
            cursor.execute(command)
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]

            if not rows:
                print(tabulate([], headers=headers, tablefmt="fancy_grid", stralign="center"))
                print("\nQuery OK, 0 rows returned.")
                return

            # show in terminal
            term_width = get_terminal_width()
            col_widths = calculate_column_widths(headers)

            wrapped_rows = []
            for row in rows:
                wrapped_row = [wrap_text(cell, width=col_widths[i]) for i, cell in enumerate(row)]
                wrapped_rows.append(wrapped_row)

            handle_large_columns(wrapped_rows, headers)

    except Exception as e:
        print(f"ERROR: {e}")


def read_multiline_sql():
    """Read multi-line SQL commands from the user until ';' is entered."""
    print("📥 Enter SQL command (end with semicolon ';'):")

    lines = []
    while True:
        line = input(">> ").strip()  # Get input and remove surrounding whitespace
        
        # Continue reading the lines until a semicolon is found at the end
        lines.append(line)
        
        # Break when a line ends with ';'
        if line.endswith(';'):
            break

    # Join all the lines into one single string with space separating them
    full_command = ' '.join(lines).strip()
    
    # Remove any space before the final semicolon to ensure the SQL is correctly formatted
    full_command = re.sub(r'\s+;', ';', full_command)
    
    return full_command

def main():
    """Main function to run the SQLite CLI interface."""
    print(show_guide())
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
            select_data(command=cmd)
        elif cmd_upper.startswith(("INSERT", "UPDATE", "DELETE")):
            insert_update_delete(cmd)
        else:
            print("ERROR: Unknown or unsupported command.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
