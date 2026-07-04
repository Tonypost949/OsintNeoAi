
import os
import zipfile
import datetime

def create_backup(source_dir, backup_dir):
    """
    Creates a zip backup of the specified source directory in the backup directory.

    Args:
        source_dir (str): The path to the directory to back up.
        backup_dir (str): The path to the directory where the backup file will be stored.
    """
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.zip"
        backup_filepath = os.path.join(backup_dir, backup_filename)

        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # Exclude the backup directory from the backup
                if root == backup_dir:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    print(f"Adding {arcname} to backup...")
                    zipf.write(file_path, arcname)

        print(f"Backup created successfully: {backup_filepath}")

    except Exception as e:
        print(f"Error creating backup: {e}")

if __name__ == "__main__":
    source_directory = "c:\\Users\\HP\\.gemini\\antigravity-ide\\scratch\\osint-agent"
    backup_directory = "c:\\Users\\HP\\.gemini\\antigravity-ide\\scratch\\osint-agent\\backups"
    create_backup(source_directory, backup_directory)
