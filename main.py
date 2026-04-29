import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import webbrowser

FAVORITES_FILE = 'favorites.json'

def load_favorites():
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_favorites(data):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def search_user():
    username = entry_search.get().strip()
    if not username:
        messagebox.showwarning("Ошибка", "Поле поиска не может быть пустым!")
        return

    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_data = response.json()
            display_user(user_data)
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Проблема с сетью: {e}")

def display_user(data):
    # Очистка предыдущего результата
    for widget in frame_result.winfo_children():
        widget.destroy()

    name = data.get('name') or data.get('login')
    bio = data.get('bio') or "Биография отсутствует"
    
    ttk.Label(frame_result, text=f"Логин: {data['login']}", font=('Arial', 10, 'bold')).pack()
    ttk.Label(frame_result, text=f"Имя: {name}").pack()
    ttk.Label(frame_result, text=bio, wraplength=300).pack()

    btn_fav = ttk.Button(frame_result, text="⭐ В избранное", 
                         command=lambda: add_to_favorites(data['login'], data['html_url']))
    btn_fav.pack(pady=5)

    link = ttk.Label(frame_result, text="Открыть профиль", foreground="blue", cursor="hand2")
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open(data['html_url']))

def add_to_favorites(login, url):
    favs = load_favorites()
    if any(f['login'] == login for f in favs):
        messagebox.showinfo("Инфо", "Пользователь уже в избранном")
        return
    
    favs.append({"login": login, "url": url})
    save_favorites(favs)
    refresh_favorites_list()
    messagebox.showinfo("Успех", f"{login} добавлен в избранное")

def refresh_favorites_list():
    list_favs.delete(0, tk.END)
    for f in load_favorites():
        list_favs.insert(tk.END, f['login'])

# Настройка GUI
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("400x600")

# Поиск
frame_search = ttk.Frame(root, padding=10)
frame_search.pack(fill='x')

entry_search = ttk.Entry(frame_search)
entry_search.pack(side='left', fill='x', expand=True, padx=5)
btn_search = ttk.Button(frame_search, text="Найти", command=search_user)
btn_search.pack(side='right')

# Результат
frame_result = ttk.LabelFrame(root, text="Результат поиска", padding=10)
frame_result.pack(fill='x', padx=10, pady=5)

# Избранное
frame_favs = ttk.LabelFrame(root, text="Избранные пользователи", padding=10)
frame_favs.pack(fill='both', expand=True, padx=10, pady=5)

list_favs = tk.Listbox(frame_favs)
list_favs.pack(fill='both', expand=True)

refresh_favorites_list()
root.mainloop()