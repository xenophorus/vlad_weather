import yaml


class Settings:
    def __init__(self):
        self._target_folder: str = "~"
        self._get_settings()

    def _get_settings(self) -> None:
        with open("settings/settings.yml", "r", encoding="utf-8") as settings_file:
            _settings = yaml.safe_load(settings_file.read())
            self._target_folder = _settings.get("last_path")

    def write_settings(self) -> None:
        data = f"last_path: '{self._target_folder}'\n"
        with open("settings/settings.yml", "w", encoding="utf-8") as settings_file:
            settings_file.write(data)

    def get_target_folder(self) -> str:
        return self._target_folder

    def set_target_folder(self, path) -> None:
        self._target_folder = path

settings = Settings()