def get_dir_size(path):
    total_size = 0
    with os.scandir(path) as directory:
        for entry in directory:
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += Backup.get_dir_size(entry.path)
    return total_size
