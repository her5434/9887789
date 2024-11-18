import socket
import tkinter as tk
import json
from tkinter import messagebox

# Программа "Создатель сайтов"
# Данная программа позволяет создавать сайты, вводя название, контент и необязательный Python-код.
# Сайты сохраняются на сервере и могут быть отображены и открыты в отдельном окне.

def create_website():
    title = title_entry.get().strip()  # Получаем название сайта
    content = content_entry.get("1.0", tk.END).strip()  # Получаем текст содержимого
    code = code_entry.get("1.0", tk.END).strip()  # Получаем Python-код
    url = url_entry.get().strip()  # Получаем URL

    # Проверка корректности URL
    if not url.startswith("http://") and not url.startswith("https://"):
        messagebox.showerror("Ошибка", "URL должен начинаться с http:// или https://")
        return

    # Проверка на заполненность необходимых полей (title, content, url)
    if not title or not content or not url:
        messagebox.showerror("Ошибка", "Название, содержание и URL должны быть заполнены.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))

    # Формат: CREATE|title|content|code|url (без Python-кода просто пропустим его)
    code_part = code if code else ""  # Если код не введен, передаем пустую строку
    client_socket.send(f"CREATE|{title}|{content}|{code_part}|{url}".encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')
    status_label.config(text=response)
    client_socket.close()

def get_websites():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    client_socket.send("LIST".encode('utf-8'))

    response = client_socket.recv(2048).decode('utf-8')
    websites = json.loads(response)

    website_list.delete(0, tk.END)  # Очищаем список сайтов
    for website in websites:
        website_list.insert(tk.END, website['title'])  # Указываем только название сайта

    client_socket.close()

def search_websites():
    search_query = search_entry.get().lower()
    for index in range(website_list.size()):
        website_title = website_list.get(index).lower()
        if search_query in website_title:
            website_list.selection_set(index)
            website_list.see(index)
        else:
            website_list.selection_clear(index)

def open_website():
    selected_index = website_list.curselection()
    if not selected_index:
        messagebox.showwarning("Предупреждение", "Выберите сайт для открытия.")
        return

    selected_website = website_list.get(selected_index)
    content, code_output = get_website_content(selected_website)

    content_window = tk.Toplevel(app)
    content_window.title(selected_website)

    tk.Label(content_window, text=content, wraplength=400).pack(padx=10, pady=10)
    tk.Label(content_window, text="Результаты выполнения кода:", wraplength=400).pack(padx=10, pady=5)
    tk.Label(content_window, text=code_output, wraplength=400).pack(padx=10, pady=10)

def get_website_content(title):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    client_socket.send(f"GET|{title}".encode('utf-8'))

    response = client_socket.recv(2048).decode('utf-8')
    client_socket.close()

    # Разделение контента и результата выполнения кода
    content, code_output = response.split("|", 1)
    return content, code_output

def paste_text():
    try:
        content = app.clipboard_get()  # Получаем текст из буфера обмена
        content_entry.insert(tk.END, content)  # Вставляем текст в поле ввода
    except tk.TclError:
        messagebox.showwarning("Ошибка", "Буфер обмена пуст или содержит недопустимый текст.")

# GUI
app = tk.Tk()
app.title('Создатель сайтов')

tk.Label(app, text='Название сайта:').pack()
title_entry = tk.Entry(app)
title_entry.pack()

tk.Label(app, text='Содержимое сайта:').pack()
content_entry = tk.Text(app, height=15, width=50)  # Увеличенная высота текстового поля
content_entry.pack()

tk.Label(app, text='Python код (необязательно):').pack()  # Метка для Python-кода
code_entry = tk.Text(app, height=15, width=50)  # Увеличенная высота текстового поля для Python-кода
code_entry.pack()

tk.Button(app, text='Вставить текст', command=paste_text).pack()  # Кнопка вставки текста
tk.Label(app, text='URL сайта:').pack()
url_entry = tk.Entry(app)
url_entry.pack()

tk.Button(app, text='Создать сайт', command=create_website).pack()
tk.Button(app, text='Показать сайты', command=get_websites).pack()

# Пoиск сайтов
tk.Label(app, text='Поиск сайтов:').pack()
search_entry = tk.Entry(app)
search_entry.pack()
search_button = tk.Button(app, text='Поиск', command=search_websites)
search_button.pack()

# Список сайтов с прокруткой
tk.Label(app, text='Список сайтов:').pack()
website_list_frame = tk.Frame(app)
website_list_frame.pack()

website_list = tk.Listbox(website_list_frame, height=10, width=50)
website_list.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(website_list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

website_list.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=website_list.yview)

tk.Button(app, text='Открыть сайт', command=open_website).pack()
status_label = tk.Label(app, text='')
status_label.pack()

app.mainloop()