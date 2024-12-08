import tkinter as tk
from tkinter import ttk, simpledialog, font, filedialog, messagebox

class DatabaseView:
    def __init__(self, root):
        self.root = root
        self._build_main_frame()
        self._build_treeview()
        self._build_input_frame()
        self._build_buttons()

    def _build_main_frame(self):
        self.db_frame = tk.Frame(self.root)
        self.db_frame.pack(fill=tk.BOTH, expand=True)

    def _build_treeview(self):
        self.columns = ("nickname", "value", "another_value")
        self.tree = ttk.Treeview(self.db_frame, columns=self.columns, show="headings")
        self.tree.column("another_value", width=75)
        self.tree.column("value", width=100)
        self.tree.column("nickname", width=150)
        self.tree.heading("nickname", text="Nickname", anchor='w')
        self.tree.heading("value", text="ip", anchor='w')
        self.tree.heading("another_value", text="port", anchor='w')
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tree.tag_configure('evenrow', background='lightgrey')
        self.tree.tag_configure('oddrow', background='white')

        # Stretching
        self.db_frame.columnconfigure(0, weight=1)
        self.db_frame.rowconfigure(0, weight=1)

    def _build_input_frame(self):
        self.input_frame = tk.Frame(self.db_frame)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.nickname_label = tk.Label(self.input_frame, text="Ник: ")
        self.nickname_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")

        self.ip_label = tk.Label(self.input_frame, text="Ip: ")
        self.ip_label.grid(row=1, column=0, padx=0, pady=0, sticky="w")

        self.port_label = tk.Label(self.input_frame, text="Port: ")
        self.port_label.grid(row=2, column=0, padx=0, pady=0, sticky="w")

        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=1)

    def _build_buttons(self):
        self.buttons_frame = tk.Frame(self.db_frame)
        self.buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.add_user_button = tk.Button(self.buttons_frame, text="Add user")
        self.add_user_button.grid(row=0, column=1, padx=10, pady=0, sticky="e")

        self.change_nickname_button = tk.Button(self.buttons_frame, text="Изменить ник")
        self.change_nickname_button.grid(row=0, column=0, padx=10, pady=0, sticky="w")

    def set_nickname_info(self, nickname, ip, port):
        self.nickname_label.config(text=f"Ник: {nickname}")
        self.ip_label.config(text=f"Ip: {ip}")
        self.port_label.config(text=f"Port: {port}")

    def show_records(self, records):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in enumerate(records):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert('', tk.END, values=row, tags=(tag,))

    def get_selected_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            return self.tree.item(selected_item[0], "values")
        return None

    def show_error(self, message, parent=None):
        # Можно сделать отдельный класс окна ошибки, но для простоты:
        if parent is None:
            parent = self.root
        messagebox.showerror("Error", message, parent=parent)

    def prompt_nickname(self):
        return simpledialog.askstring("", "new nickname:", parent=self.root)

    def prompt_add_user(self, on_confirm, on_cancel):
        # Окно добавления пользователя
        add_user_window = tk.Toplevel(self.db_frame)
        add_user_window.title("Add User")

        tk.Label(add_user_window, text="Nickname:").grid(row=0, column=0, padx=5, pady=5)
        nickname_entry = tk.Entry(add_user_window)
        nickname_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_user_window, text="Ip:").grid(row=1, column=0, padx=5, pady=5)
        ip_entry = tk.Entry(add_user_window)
        ip_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_user_window, text="Port").grid(row=2, column=0, padx=5, pady=5)
        port_entry = tk.Entry(add_user_window)
        port_entry.grid(row=2, column=1, padx=5, pady=5)

        def confirm():
            on_confirm(nickname_entry.get(), ip_entry.get(), port_entry.get(), add_user_window)

        def cancel():
            on_cancel(add_user_window)

        ok_button = tk.Button(add_user_window, text="OK", command=confirm)
        ok_button.grid(row=3, column=0, padx=5, pady=0)

        cancel_button = tk.Button(add_user_window, text="Cancel", command=cancel)
        cancel_button.grid(row=3, column=1, padx=5, pady=5)

        # Центрирование окна относительно родителя
        add_user_window.transient(self.root)
        add_user_window.grab_set()
        self.root.wait_window(add_user_window)

    def bind_tree_context_menu(self, menu):
        self.tree.bind("<Button-3>", lambda event: self._show_context_menu(event, menu))

    def _show_context_menu(self, event, menu):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            menu.post(event.x_root, event.y_root)
        else:
            region = self.tree.identify_region(event.x, event.y)
            if region == "nothing":
                menu.post(event.x_root, event.y_root)

    def create_context_menu(self, on_connect, on_delete, on_refresh):
        context_menu = tk.Menu(self.db_frame, tearoff=0)
        context_menu.add_command(label="Connect", command=on_connect)
        context_menu.add_command(label="Delete", command=on_delete)
        context_menu.add_command(label="Refresh", command=on_refresh)
        return context_menu
