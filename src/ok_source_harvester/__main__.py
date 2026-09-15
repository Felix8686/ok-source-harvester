from .config import get_settings


def main() -> None:
    settings = get_settings()
    print(f"ok-source-harvester environment={settings.environment}")


if __name__ == "__main__":
    main()
