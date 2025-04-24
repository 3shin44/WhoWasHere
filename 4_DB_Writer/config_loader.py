import yaml


def load_config(
    config_path="configs/default_config.yaml",
):
    """加載 YAML 配置文件"""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise Exception(f"Config file not found at {config_path}")
    except yaml.YAMLError as e:
        raise Exception(f"Error parsing YAML file: {e}")


if __name__ == "__main__":
    config = load_config()
    print(f"App Name: {config['app']['name']}")
    print(f"App Version: v{config['app']['version']}")
