from pathlib import Path
import shutil
import csv
from Settings import settings

class DiskIO:

    @staticmethod
    def get_regions() -> dict[str: str]:
        try:
            file = Path(settings.urls_file)
            with file.open("r", encoding="utf-8") as f:
                for line in csv.DictReader(f):
                    yield line
        except FileNotFoundError as fnf:
            return ["Error", fnf.strerror]
        except Exception as e:
            return ["Error", f"{e.__class__}"]

    @staticmethod
    def write_file(data, destination, file_name) -> None:
        file = Path(destination) / file_name + ".csv"
        with file.open("w", encoding="utf-8") as f:
            f.write(data)

    @staticmethod
    def move_file(file, source, destination) -> None:
        file_src = Path(source) / file + ".csv"
        file_dest = Path(destination) / file + ".csv"
        shutil.move(file_src, file_dest)
