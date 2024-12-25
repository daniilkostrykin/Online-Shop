import os
import subprocess

def start_docker_and_container():
    try:
        # Запуск Docker Desktop
        print("Запуск Docker Desktop...")
        if os.name == "nt":  # Windows
            docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
            subprocess.Popen([docker_desktop_path], shell=True)
        else:
            raise OSError("Автоматический запуск Docker Desktop поддерживается только на Windows.")

        # Проверяем, запущен ли Docker
        print("Ожидание запуска Docker...")
        subprocess.run(["docker", "info"], check=True)

        # Запуск контейнера online-shop
        print("Запуск контейнера online-shop...")
        container_name = "online-shop"
        image_name = "online-shop:latest"
        
        # Проверяем, существует ли контейнер
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            text=True,
        )
        existing_container = result.stdout.strip()

        if existing_container:
            print(f"Контейнер {container_name} уже существует. Запуск...")
            subprocess.run(["docker", "start", container_name], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды Docker: {e}")
    except FileNotFoundError:
        print("Путь к Docker Desktop указан неверно или Docker не установлен.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Вызов метода
start_docker_and_container()
