import sys
import os

def unescape_brackets_in_file(file_path):
    """
    Replaces escaped square brackets ('\[' and '\]') with their unescaped
    counterparts ('[' and ']') in a given file. A backup of the original
    file is created with a .bak extension.

    Args:
        file_path (str): The path to the file to process.
    """
    try:
        # It's better to read the file in binary mode to avoid encoding issues
        # and then decode it. However, for DEF files, utf-8 is usually safe.
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content = content.replace('\\[', '[').replace('\\]', ']')

        if new_content != content:
            backup_path = file_path + '.bak'
            print(f"Backing up original file to {backup_path}")
            # In case backup file already exists
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(file_path, backup_path)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"File '{file_path}' has been updated.")
        else:
            print(f"No escaped brackets found. File '{file_path}' remains unchanged.")

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python unescape_def_brackets.py <file_path>")
        sys.exit(1)

    target_file = sys.argv[1]
    unescape_brackets_in_file(target_file)    
