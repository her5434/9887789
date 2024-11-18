import socket
import json
import subprocess

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)
    print("Сервер запущен на порту 8080...")
    
    websites = []  # Список всех сайтов

    while True:
        client_socket, address = server_socket.accept()
        print(f"Подключение от {address} получено.")

        try:
            data = client_socket.recv(4096).decode('utf-8')
            if data.startswith("CREATE"):
                parts = data.split('|', 4)  # Используем 4 разделителя
                if len(parts) < 5:
                    client_socket.send("Ошибка: недостаточно данных для создания сайта.".encode('utf-8'))
                    return
                _, title, content, code, url = parts
                # Убедитесь, что код может быть пустым
                websites.append({"title": title, "content": content, "code": code, "url": url})
                print(f"Сайт '{title}' создан с URL: {url}.")
                client_socket.send("Сайт создан.".encode('utf-8'))
            elif data.startswith("LIST"):
                client_socket.send(json.dumps(websites).encode('utf-8'))
            elif data.startswith("GET"):
                _, title = data.split('|')
                website = next((w for w in websites if w['title'] == title), None)
                content = website['content'] if website else "Сайт не найден."
                code_output = execute_code(website['code']) if website else "Ошибка выполнения кода."
                client_socket.send(f"{content}|{code_output}".encode('utf-8'))
            else:
                client_socket.send("Команда не распознана.".encode('utf-8'))
        except Exception as e:
            print(f"Ошибка: {e}")
            client_socket.send("Ошибка при обработке запроса.".encode('utf-8'))
        finally:
            client_socket.close()

def execute_code(code):
    try:
        # Выполняйте код Python и возвращайте результаты
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    run_server()