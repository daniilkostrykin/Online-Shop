import json
import time
import subprocess
import tkinter as tk
from tkinter import messagebox
import psycopg2
import os
import sys
import threading

current_user = None
current_role = None
current_username = None
cart = {}


import psycopg2
import logging
from tkinter import messagebox

# Set up logging (optional but useful)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def get_db_connection():
    try:
        conn = psycopg2.connect(
        dbname="shop",
        user="postgres",
        password="postgres",
        host="localhost",
        port="55432"
    )
        conn.autocommit = False #Отключаем авто коммит для последующей логики в скрипте.
        return conn

    except psycopg2.Error as e:
         error_msg = f"Ошибка при подключении к базе данных: {e}"
         logging.error(error_msg) # log with datetime stamp
         messagebox.showerror("Ошибка",error_msg)
         return None # Если вызвалась ошибка - возращаем None.
    except Exception as e:
        error_msg = f"Неизвестная ошибка при подключении к базе данных: {e}"
        logging.error(error_msg) #log other unexpected errors
        messagebox.showerror("Ошибка",error_msg)
        return None

def show_login_window():
    for widget in content_frame.winfo_children():
        widget.destroy()

    tk.Label(content_frame, text="Введите логин:").pack(pady=5)
    login_entry = tk.Entry(content_frame)
    login_entry.pack(pady=5)

    tk.Label(content_frame, text="Введите пароль:").pack(pady=5)
    password_entry = tk.Entry(content_frame, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(content_frame, text="Войти",
                             command=lambda: check_login(login_entry.get(), password_entry.get()))
    login_button.pack(pady=10)


def check_login(login, password):
    global current_user, current_role, current_username

    conn = get_db_connection()
    cur = conn.cursor()

    # Выполняем запрос для проверки логина и пароля
    cur.execute(
        "SELECT role FROM users WHERE login=%s AND password=%s", (login, password))
    result = cur.fetchone()

    conn.close()

    if result:
        # Если логин и пароль совпадают, сохраняем данные текущего пользователя
        current_user = login
        current_username = login
        current_role = result[0]

        # Переходим в соответствующее окно в зависимости от роли
        if current_role == 'admin':
            show_admin_window()
        elif current_role == 'rab':
            show_rab_window()
        elif current_role == 'user':
            show_user_window()
    else:
        # Если логин или пароль неверные, выводим окно с ошибкой
        messagebox.showerror("Ошибка входа", "Неверный логин или пароль.")


def show_admin_window():
    for widget in content_frame.winfo_children():
        widget.destroy()

    label = tk.Label(
        content_frame, text=f"Добро пожаловать, администратор {current_username}!")
    label.pack(pady=20)

    button_frame = tk.Frame(content_frame)
    button_frame.pack(pady=10)

    users_button = tk.Button(
        button_frame, text="Пользователи", command=show_users)
    users_button.pack(side=tk.LEFT, padx=5)

    assortment_button = tk.Button(
        button_frame, text="Ассортимент", command=show_assortment_window)
    assortment_button.pack(side=tk.RIGHT, padx=5)

    back_button = tk.Button(content_frame, text="Выход",
                            command=show_login_window)
    back_button.pack(pady=5)


def show_users():
    global new_role_variable
    new_role_variable = None

    for widget in content_frame.winfo_children():
        widget.destroy()

    back_button = tk.Button(content_frame, text="Назад",
                            command=show_admin_window)
    back_button.pack(pady=10)

    scrollable_frame = tk.Frame(content_frame)

    scrollable_frame.pack(fill=tk.BOTH, expand=True)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT login, role FROM users ORDER BY id ASC")
    users = cur.fetchall()

    for user in users:
        frame = tk.Frame(scrollable_frame)
        frame.pack(pady=5)

        label = tk.Label(
            frame, text=f"Пользователь: {user[0]}, Роль: {user[1]}")
        label.pack(side=tk.LEFT)

        role_var = tk.StringVar(value=user[1])
        role_dropdown = tk.OptionMenu(frame, role_var, 'admin', 'rab', 'user')
        role_dropdown.pack(side=tk.LEFT)

        change_role_button = tk.Button(frame, text="Изменить роль",
                                       command=lambda login=user[0], role=role_var: change_user_role(login, role.get()))
        change_role_button.pack(side=tk.LEFT)

    conn.close()


def change_user_role(login, new_role):
    global new_role_variable
    new_role_variable = new_role

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE users SET role=%s WHERE login=%s ", (new_role, login))
    conn.commit()

    new_role_variable = None

    conn.close()

    show_users()


def show_assortment_window():
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Кнопка "Назад" в верхней части
    back_button = tk.Button(content_frame, text="Назад",
                            command=show_admin_window)
    back_button.pack(pady=5, anchor="w")  # Прижать кнопку "Назад" влево

    # Кнопка "Добавить товар" также слева
    add_button = tk.Button(
        content_frame, text="Добавить товар", command=add_item)
    add_button.pack(pady=5, anchor="w")

    # Создание фрейма для списка ассортимента
    assortment_frame = tk.Frame(content_frame)
    assortment_frame.pack(fill=tk.BOTH, expand=True)

    # Подключение к базе данных и вывод товаров
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM list ORDER BY id ASC")
    items = cur.fetchall()

    for item in items:
        frame = tk.Frame(assortment_frame)
        frame.pack(pady=5, anchor="w")  # Прижать элементы к левой стороне

        label = tk.Label(frame,
                         text=f"ID: {item[0]}, Наличие: {item[1]} штук, Название: {item[2]}, Цена: {item[3]} руб",
                         anchor="w")
        label.pack(side=tk.LEFT)

        edit_button = tk.Button(frame, text="Редактировать",
                                command=lambda item_id=item[0], item_name=item[2]: edit_item(item_id, item_name))
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(frame, text="Удалить",
                                  command=lambda item_id=item[0]: delete_item(item_id))
        delete_button.pack(side=tk.LEFT, padx=5)

    conn.close()


def add_item():
    add_window = tk.Toplevel(root)
    add_window.title("Добавить товар")
    add_window.geometry("300x330")

    tk.Label(add_window, text="ID товара:").pack(pady=5)
    id_entry = tk.Entry(add_window)
    id_entry.pack(pady=5)

    tk.Label(add_window, text="Количество:").pack(pady=5)
    count_entry = tk.Entry(add_window)
    count_entry.pack(pady=5)

    tk.Label(add_window, text="Название:").pack(pady=5)
    name_entry = tk.Entry(add_window)
    name_entry.pack(pady=5)

    tk.Label(add_window, text="Цена:").pack(pady=5)
    price_entry = tk.Entry(add_window)
    price_entry.pack(pady=5)

    def save_new_item():
        item_id = id_entry.get()
        quantity = count_entry.get()
        name = name_entry.get()
        price = price_entry.get()

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO list (id, count, name, price) VALUES (%s, %s, %s, %s)",
                    (item_id, quantity, name, price))
        conn.commit()
        conn.close()

        add_window.destroy()
        show_assortment_window()

    save_button = tk.Button(
        add_window, text="Сохранить", command=save_new_item)
    save_button.pack(pady=10)

    cancel_button = tk.Button(
        add_window, text="Отмена", command=add_window.destroy)
    cancel_button.pack(pady=5)


def edit_item(item_id, item_name):
    edit_window = tk.Toplevel(root)
    edit_window.title("Редактировать товар")
    edit_window.geometry("300x250")

    tk.Label(edit_window, text=f"Редактирование товара: {item_name}").pack(
        pady=5)

    tk.Label(edit_window, text="Введите новое количество:").pack(pady=5)
    quantity_entry = tk.Entry(edit_window)
    quantity_entry.pack(pady=5)

    tk.Label(edit_window, text="Введите новую цену:").pack(pady=5)
    price_entry = tk.Entry(edit_window)
    price_entry.pack(pady=5)

    def save_changes():
        new_quantity = quantity_entry.get()
        new_price = price_entry.get()

        conn = get_db_connection()
        cur = conn.cursor()

        if new_quantity:
            cur.execute("UPDATE list SET count=%s WHERE id=%s",
                        (new_quantity, item_id))
        if new_price:
            cur.execute("UPDATE list SET price=%s WHERE id=%s",
                        (new_price, item_id))

        conn.commit()
        conn.close()

        edit_window.destroy()
        show_assortment_window()

    save_button = tk.Button(
        edit_window, text="Сохранить", command=save_changes)
    save_button.pack(pady=10)

    cancel_button = tk.Button(
        edit_window, text="Отмена", command=edit_window.destroy)
    cancel_button.pack(pady=5)

    save_button = tk.Button(
        edit_window, text="Сохранить", command=save_changes)
    save_button.pack(pady=10)

    cancel_button = tk.Button(
        edit_window, text="Отмена", command=edit_window.destroy)
    cancel_button.pack(pady=5)


def delete_item(item_id):
    confirmation = messagebox.askyesno(
        "Подтверждение", "Вы уверены, что хотите удалить этот товар?")
    if confirmation:
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            pass  # Add your code here
        except Exception as e:
            print(f"Unexpected error: {e}")
            cur.execute("DELETE FROM list WHERE id = %s", (item_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Товар успешно удалён.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить товар: {e}")
        finally:
            conn.close()

        # Обновляем окно ассортимента после удаления
        show_assortment_window()


def show_rab_window():
    for widget in content_frame.winfo_children():
        widget.destroy()

    label = tk.Label(
        content_frame, text=f"Добро пожаловать, работник {current_username}!")
    label.pack(pady=20)

    back_button = tk.Button(content_frame, text="Выход",
                            command=show_login_window)
    back_button.pack(pady=5)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, username, status, info FROM orders ORDER BY id ASC")
    orders = cur.fetchall()

    if not orders:
        no_orders_label = tk.Label(content_frame, text="Нет заказов.")
        no_orders_label.pack(pady=20)
    else:
        orders_frame = tk.Frame(content_frame)
        orders_frame.pack(fill=tk.BOTH, expand=True)

        for order in orders:
            order_id, username, status, info = order
            order_frame = tk.Frame(orders_frame)
            order_frame.pack(anchor="w", pady=5)

            status_var = tk.StringVar(value=status)
            status_menu = tk.OptionMenu(
                order_frame, status_var, "создан", "собран", "отправлен", "доставлен")
            status_menu.pack(side=tk.LEFT, padx=5)

            save_button = tk.Button(order_frame, text="Сохранить статус",
                                    command=lambda id=order_id, var=status_var: update_order_status(id, var.get()))
            save_button.pack(side=tk.LEFT, padx=5)

            order_label = tk.Label(order_frame,
                                   text=f"Заказ ID: {order_id}, Пользователь: {username}, Статус: {status}, Информация: {info}",
                                   anchor="w")
            order_label.pack(side=tk.LEFT)

    conn.close()


def update_order_status(order_id, new_status):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE orders SET status = %s WHERE id = %s",
                (new_status, order_id))
    conn.commit()

    conn.close()


def show_user_window():
    for widget in content_frame.winfo_children():
        widget.destroy()

    label = tk.Label(
        content_frame, text=f"Добро пожаловать, пользователь {current_username}!")
    label.pack(pady=20)

    assortment_button = tk.Button(
        content_frame, text="Ассортимент", command=show_assortment, width=20, height=1)
    assortment_button.pack(pady=5)

    cart_button = tk.Button(content_frame, text="Корзина",
                            command=show_cart, width=20, height=1)
    cart_button.pack(pady=5)

    orders_button = tk.Button(
        content_frame, text="Заказы", command=show_orders, width=20, height=1)
    orders_button.pack(pady=5)

    back_button = tk.Button(content_frame, text="Выход",
                            command=show_login_window)
    back_button.pack(pady=5)


def show_cart():
    for widget in content_frame.winfo_children():
        widget.destroy()

    label = tk.Label(content_frame, text="Ваша корзина")
    label.pack(pady=20)

    if cart:
        for item, quantity in cart.items():
            frame = tk.Frame(content_frame)
            frame.pack(pady=5)

            label = tk.Label(frame, text=f"{item} - {quantity} шт.")
            label.pack(side=tk.LEFT, padx=5)

            # Кнопка "Удалить"
            delete_button = tk.Button(frame, text="Удалить",
                                       command=lambda item_name=item: remove_from_cart(item_name))
            delete_button.pack(side=tk.LEFT, padx=5)

        clear_cart_button = tk.Button(
            content_frame, text="Очистить корзину", command=clear_cart)
        clear_cart_button.pack(pady=5)

        order_button = tk.Button(
            content_frame, text="Сделать заказ", command=make_order)
        order_button.pack(pady=10)
    else:
        label = tk.Label(content_frame, text="Корзина пуста")
        label.pack(pady=5)

    back_button = tk.Button(content_frame, text="Назад",
                            command=show_user_window)
    back_button.pack(pady=5)


def remove_from_cart(item_name):
    if item_name in cart:
        cart[item_name] -= 1
        if cart[item_name] <= 0:
            del cart[item_name]
    show_cart()


def clear_cart():
    global cart
    cart.clear()
    show_cart()


def make_order():
    global current_username

    conn = get_db_connection()
    cur = conn.cursor()

    for item, quantity in cart.items():
        cur.execute(
            "SELECT count FROM list WHERE name=%s ORDER BY id ASC", (item,))
        result = cur.fetchone()
        if not result or result[0] < quantity:
            tk.messagebox.showerror(
                "Ошибка", f"Недостаточно товара '{item}' в наличии.")
            conn.close()
            return

    cur.execute("SELECT MAX(id) FROM orders")
    max_id = cur.fetchone()[0]
    new_order_id = 1 if max_id is None else max_id + 1

    order_info = ", ".join(
        [f"{item}: {quantity}" for item, quantity in cart.items()])

    for item, quantity in cart.items():
        cur.execute(
            "UPDATE list SET count = count - %s WHERE name = %s", (quantity, item))

    # Вставляем новый заказ в таблицу orders
    cur.execute("INSERT INTO orders (username, id, status, info) VALUES (%s, %s, %s, %s)",
                (current_username, new_order_id, 'создан', order_info))
    conn.commit()

    cart.clear()

    tk.messagebox.showinfo("Успех", "Заказ успешно создан!")
    conn.close()

    show_cart()


def show_orders():
    for widget in content_frame.winfo_children():
        widget.destroy()

    back_button = tk.Button(content_frame, text="Назад",
                            command=show_user_window)
    back_button.pack(pady=5)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, status, info FROM orders WHERE username=%s ORDER BY id ASC", (current_user,))
    orders = cur.fetchall()

    if not orders:
        no_orders_label = tk.Label(content_frame, text="У вас нет заказов.")
        no_orders_label.pack(pady=20)
    else:
        orders_frame = tk.Frame(content_frame)
        orders_frame.pack(fill=tk.BOTH, expand=True)

        for order in orders:
            order_id, status, info = order
            order_label = tk.Label(orders_frame, text=f"Заказ ID: {order_id}, Статус: {status}, Информация: {info}",
                                   anchor="w")
            order_label.pack(anchor="w", pady=5)

    conn.close()


def show_assortment():
    for widget in content_frame.winfo_children():
        widget.destroy()

    back_button = tk.Button(content_frame, text="Назад",
                            command=show_user_window)
    back_button.pack(pady=5)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT name, price FROM list ORDER BY id ASC")
    items = cur.fetchall()

    items_frame = tk.Frame(content_frame)
    items_frame.pack(fill=tk.BOTH, expand=True)

    for item in items:
        frame = tk.Frame(items_frame)
        frame.pack(pady=5)

        label = tk.Label(
            frame, text=f"Товар: {item[0]}, Цена: {item[1]} руб", anchor="w")
        label.pack(side=tk.LEFT, anchor="w")

        select_button = tk.Button(
            frame, text="Выбрать", command=lambda item_name=item[0]: add_to_cart(item_name))
        select_button.pack(side=tk.LEFT, padx=5)

    conn.close()


def add_to_cart(item_name):
    if item_name in cart:
        cart[item_name] += 1
    else:
        cart[item_name] = 1


def show_registration_window():
    for widget in content_frame.winfo_children():
        widget.destroy()

    tk.Label(content_frame, text="Введите логин:").pack(pady=5)
    username_entry = tk.Entry(content_frame)
    username_entry.pack(pady=5)

    tk.Label(content_frame, text="Введите пароль:").pack(pady=5)
    password_entry = tk.Entry(content_frame, show="*")
    password_entry.pack(pady=5)

    register_button = tk.Button(content_frame, text="Зарегистрироваться",
                                command=lambda: register_user(username_entry.get(), password_entry.get()))
    register_button.pack(pady=10)

    back_button = tk.Button(content_frame, text="Назад",
                            command=show_login_window)
    back_button.pack(pady=5)


def register_user(username, password):
    if username and password:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (login, password, role) VALUES (%s, %s, 'user')", (username, password))
        conn.commit()

        # Закрываем соединение с базой данных
        conn.close()

        tk.messagebox.showinfo("Успешная регистрация",
                               "Вы успешно зарегистрировались!")
    else:
        tk.messagebox.showerror("Ошибка", "Введите логин и пароль")

def create_auth_buttons(frame):
   
    login_button = tk.Button(frame, text="Войти", command=show_login_window)
    login_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    register_button = tk.Button(frame, text="Зарегистрироваться", command=show_registration_window)
    register_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)


def center_window(window, width, height):
    """
    Центрирует окно на экране.
    
    :param window: Ссылка на окно Tkinter.
    :param width: Ширина окна.
    :param height: Высота окна.
    """
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Вычисляем координаты для центра
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # Устанавливаем размеры и положение окна
    window.geometry(f"{width}x{height}+{x}+{y}")
root = tk.Tk()
root.title("Cool Store")

content_frame = tk.Frame(root)
content_frame.pack(pady=10)


create_auth_buttons(content_frame)

window_width =900
window_height = 500
center_window(root, window_width, window_height)
root.focus_set() 

root.mainloop()
