import yaml
from pathlib import Path


class Settings:
    def __init__(self):
        self._from_today = True
        self.urls_file = "input/towns.csv"
        self._target_folder: str = "~"
        self._days: int = 0
        self._nights: bool = False
        self.settings_file = Path.cwd() / "settings/settings.yml"
        self.check_settings_file()
        self._get_settings()

    def check_settings_file(self, bind=True, create=True):
        if not self.settings_file.exists():
            self.settings_file.parent.mkdir(exist_ok=True, parents=True)
            if bind:
                self.urls_file = "input/towns.csv"
                self._target_folder = str(Path.cwd())
                self._days = 3
                self._nights = True
                self._from_today = True
            if create:
                self.write_settings()

    def _get_settings(self) -> None:
        with open(self.settings_file, "r", encoding="utf-8") as settings_file:
            _settings = yaml.safe_load(settings_file.read())
            self.urls_file = _settings.get("urls_file")
            self._target_folder = _settings.get("last_path")
            if not _settings.get("days"):
                self._days = 2
            else:
                self._days = _settings.get("days")
            self._nights = bool(_settings.get("nights"))
            self._from_today = _settings.get("from_today")

    def write_settings(self) -> None:
        self.check_settings_file(bind=False, create=False)
        data = (f"urls_file: '{self.urls_file}'\n"
                f"last_path: '{self._target_folder}'\n"
                f"days: {self._days}\n"
                f"nights: {bool(self._nights)}\n"
                f"from_today: {self._from_today}\n")
        with open(self.settings_file, "w", encoding="utf-8") as settings_file:
            settings_file.write(data)

    def get_target_folder(self) -> str:
        return self._target_folder

    def set_target_folder(self, path) -> None:
        self._target_folder = path

    def get_days(self) -> int:
        return self._days

    def set_days(self, days) -> None:
        self._days = days

    def get_nights(self) -> bool:
        return self._nights

    def set_nights(self, nights):
        self._nights = nights

    def get_from_today(self):
        return self._from_today

    def set_from_today(self, from_today):
        self._from_today = from_today


settings = Settings()
