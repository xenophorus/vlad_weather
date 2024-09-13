import yaml


def get_settings():
    with open("settings/settings.yml", "r", encoding="utf-8") as settings_file:
        return yaml.safe_load(settings_file.read())


settings = get_settings()


print(settings)
