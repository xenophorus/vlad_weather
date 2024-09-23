from dataclasses import fields
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
                lines = csv.DictReader(f)
                return list(lines)
                # for line in csv.DictReader(f):
                #     yield line
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
    def write_csv(data: tuple, destination_folder: str) -> None:
        destination = Path(destination_folder)
        file_name, data_dict = data
        destination.mkdir(parents=True, exist_ok=True)

        file = destination / f"{file_name}.csv"

        with file.open("w", encoding="utf-8") as csv_file:
            regions = list(data_dict.values())
            field_names = list(regions[0].keys())
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
            csv_writer.writeheader()
            for region in regions:
                csv_writer.writerow(region)

    @staticmethod
    def move_file(file, source, destination) -> None:
        file_src = Path(source) / file
        file_dest = Path(destination)
        shutil.move(file_src, file_dest)
