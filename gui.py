import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox


def clear(fields):
    for f in fields:
        f.delete(0, END)


def collect_entries(fields):
    s = []
    for f in fields:
        s.append(f.get())
    return s


def display_values(table, entry_widgets):
    clear(entry_widgets)
    row_vals = table.item(table.focus(), 'values')
    for i in range(len(entry_widgets)):
        entry_widgets[i].insert(0, row_vals[i + 1])


def get_selected_id_list(table):
    id_list = []
    for row in table.selection():
        item = table.item(row)
        rec = item['values']
        id_list.append(rec[0])
    return id_list


class Gui:
    def __init__(self, con):
        self.con = con
        root = Tk()
        root.withdraw()  # Hide main window until logged in
        root.title("Postgre_gui")
        search_label = Label(root, text="Поиск")
        self.search_entry = Entry(root)

        # Authentication window
        auth_window = Toplevel()
        auth_button = Button(auth_window, text="Я админ, отвечаю.", command=lambda: self.login(root, auth_window))
        auth_login_label = Label(auth_window, text="Логин: ")
        auth_password_label = Label(auth_window, text="Пароль: ")
        auth_username = StringVar()
        auth_password = StringVar()
        auth_login_entry = Entry(auth_window, textvariable=auth_username)
        auth_password_entry = Entry(auth_window, textvariable=auth_password)
        auth_login_button = Button(auth_window,
                                   text="Войти",
                                   command=lambda:
                                   self.auth_login_button_handler(auth_username.get(), auth_password.get(), root,
                                                                  auth_window)
                                   )
        auth_exit_button = Button(auth_window,
                                  text="Выйти",
                                  command=lambda: self.auth_exit_button_handler(root)
                                  )
        auth_login_label.grid(row=1, column=0)
        auth_password_label.grid(row=2, column=0)
        auth_login_entry.grid(row=1, column=1)
        auth_password_entry.grid(row=2, column=1)
        auth_login_button.grid(row=3, column=0)
        auth_exit_button.grid(row=3, column=1)
        auth_button.grid(row=4)

        # Close main window if auth window is closed by pressing "X"
        auth_window.protocol("WM_DELETE_WINDOW", root.quit)

        # Main window widgets
        show_id_flag = tkinter.IntVar(value=0)
        show_id_checkbox = Checkbutton(root,
                                       text="Показать id",
                                       variable=show_id_flag,
                                       command=lambda: self.show_id(show_id_flag, column_names))
        self.case_search_flag = tkinter.BooleanVar(value=True)
        case_search_checkbox = Checkbutton(root,
                                           text="Учитывать регистр",
                                           variable=self.case_search_flag,
                                           command=lambda: self.col_searcher()
                                           )
        quit_button = Button(root, text="Выйти", command=lambda: self.quit_button_handler(root))
        # delete_button = Button(root,
        #                        text="Удалить запись",
        #                        command=self.delete_record_button_handler
        #                        )
        # delete_selected_button = Button(root,
        #                                 text="Удалить выбранные записи",
        #                                 command=self.delete_selected_button_handler
        #                                 )
        add_record_button = Button(root,
                                   text="Добавить запись",
                                   command=lambda: self.add_record_button_handler(column_names)
                                   )
        # edit_record_button = Button(root,
        #                             text="Изменить запись",
        #                             command=lambda: self.edit_record_button_handler(column_names)
        #                             )
        # search_button = Button(root,
        #                        text="Поиск",
        #                        command=lambda: self.filter_records(self.table, entry_fields, column_names))
        clear_button = Button(root,
                              text="Очистить",
                              command=lambda: self.clear_search_entry()
                              )
        refresh_button = Button(root,
                                text="Обновить",
                                command=lambda: self.refresh(self.table)
                                )
        test_button = Button(root,
                             text="Тест",
                             command=lambda: self.test_button_handler()
                             )
        test_string = Label(root, text="")

        # Right-click dropdown menu
        self.table_dropdown_menu = Menu(root, tearoff=False)
        self.table_dropdown_menu.add_command(label="Удалить", command=self.delete_selected_button_handler)
        self.table_dropdown_menu.add_command(label="Изменить запись",
                                             command=lambda: self.edit_record_button_handler(column_names))

        # Set up the table

        column_names = con.get_column_names()
        self.table = ttk.Treeview(root,
                                  columns=column_names,
                                  displaycolumns=column_names[not (show_id_flag.get()):],
                                  show="headings",
                                  )
        entry_fields = []
        self.table_scroll = ttk.Scrollbar(root, command=self.table.yview)
        self.table.configure(yscrollcommand=self.table_scroll.set)
        # entry_fields_labels = []
        for name in column_names:
            self.table.heading(name, text=name, anchor="center",
                               command=lambda col=name: self.treeview_sort_column(self.table, col, False)
                               )
            self.table.column(name, anchor="center")
            # if name != "id":
            #     entry_fields.append(Entry(root))
            #     entry_fields_labels.append(Label(root, text=name + ":"))
        self.detached = set()
        self.refresh(self.table)

        row_counter = 0
        self.table.grid(row=0, column=0, columnspan=len(column_names))
        self.table_scroll.grid(row=0, column=len(column_names) + 1, sticky='ns')

        # for i in range(len(entry_fields)):
        #     entry_fields_labels[i].grid(row=1, column=i * 2, sticky='')
        #     entry_fields[i].grid(row=1, column=i * 2 + 1, sticky='')

        #  Place other widgets

        row_counter += 1  # Search row
        search_label.grid(row=row_counter, column=0, sticky='e', padx=5)
        self.search_entry.grid(row=row_counter, column=1, columnspan=1, sticky='we', padx=5)
        clear_button.grid(row=row_counter, column=2, columnspan=1, sticky='w')
        case_search_checkbox.grid(row=row_counter, column=3, columnspan=1, sticky='')

        row_counter += 1
        # delete_button.grid()
        # delete_selected_button.grid()
        add_record_button.grid()
        # search_button.grid()
        # edit_record_button.grid()
        refresh_button.grid()
        quit_button.grid()

        show_id_checkbox.grid()

        test_string.grid()
        test_button.grid()

        # Binds
        # self.table.bind("<Double-Button-1>", lambda e: self.table_click(e, entry_fields))
        self.table.bind("<Button-3>", lambda e: self.table_right_click(e))
        self.search_entry.bind("<KeyRelease>", lambda e: self.col_searcher(e))
        # self.table.bind("<Button-1>", lambda e: self.table_click(e))

        # window geometry
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())

        # main loop
        root.mainloop()

    def auth_login_button_handler(self, username, password, root, auth_window):
        if self.con.check_user(username):
            if self.con.check_password(username, password):
                root.deiconify()
                auth_window.destroy()
            else:
                messagebox.showwarning("Внимание!", "Спасибо за внимание")
        else:
            messagebox.showwarning("Внимание!", "Спасибо за внимание")

    @staticmethod
    def auth_exit_button_handler(root):
        root.quit()

    @staticmethod
    def login(root, auth_widow):
        root.deiconify()
        auth_widow.destroy()

    def table_click(self, event, entry_fields):
        region = self.table.identify_region(event.x, event.y)
        if region == "cell":
            display_values(self.table, entry_fields)

    def table_right_click(self, event):
        region = self.table.identify_region(event.x, event.y)
        if region == "cell":
            selected_id = self.table.identify('item', event.x, event.y)
            if selected_id not in self.table.selection():
                self.table.selection_set(self.table.identify_row(event.y))
            self.table.focus(self.table.identify_row(event.y))
            self.table_dropdown_menu.tk_popup(event.x_root, event.y_root)

    def show_id(self, show_id_flag, col_n):
        self.table.configure(displaycolumns=col_n[not show_id_flag.get():])

    def add_record(self, col_n, fields):
        self.con.insert_record(col_n, collect_entries(fields))
        clear(fields)
        self.refresh(self.table)

    def update_record(self, col_n, fields):
        rec_id = self.table.item(self.table.focus(), 'values')[0]
        new_vals = collect_entries(fields)
        self.con.update_record(col_n, new_vals, rec_id)

    def filter_records(self, table, fields, col_n):
        filters = collect_entries(fields)
        [table.delete(row) for row in table.get_children()]
        [table.insert("", tkinter.END, values=row) for row in self.con.get_searched_records(col_n, filters)]

    def delete_record(self, row_id):
        self.con.delete_record(row_id)
        self.refresh(self.table)

    def delete_selected_records(self, table):
        id_list = get_selected_id_list(table)
        self.con.delete_multiple(id_list)
        self.refresh(self.table)

    def refresh(self, table):
        self.detached = set()
        [table.delete(row) for row in table.get_children()]
        [table.insert("", tkinter.END, values=row) for row in self.con.get_all_records()]

    def col_searcher(self, _=None):
        children = list(self.detached) + list(self.table.get_children())
        self.detached = set()
        search_entry_text = self.search_entry.get()
        self.search(children, search_entry_text)

    def search(self, children, search_entry_text):
        search_result_index = -1
        if not self.case_search_flag.get():
            search_entry_text = search_entry_text.lower()
        for item_id in children:
            values = " ".join(map(str, self.table.item(item_id)["values"]))
            if not self.case_search_flag.get():
                values = values.lower()
            if search_entry_text in values:
                search_result_index += 1
                self.table.reattach(item_id, "", search_result_index)
            else:
                self.detached.add(item_id)
                self.table.detach(item_id)

    def clear_search_entry(self):
        self.search_entry.delete(0, END)
        self.col_searcher()

    def treeview_sort_column(self, table, col, reverse):
        item_list = [(table.set(k, col), k) for k in table.get_children('')]
        item_list.sort(reverse=reverse)
        for index, (val, k) in enumerate(item_list):  # rearrange items in sorted positions
            table.move(k, '', index)
        table.heading(col,
                      text=col,
                      command=lambda _col=col: self.treeview_sort_column(table,
                                                                         _col,
                                                                         not reverse))  # reverse sort next time

    # Button handlers
    @staticmethod
    def test_button_handler():
        test_window = Toplevel()
        test_window.grab_set()
        test_close_button = Button(test_window,
                                   text="Закрытб",
                                   command=test_window.destroy
                                   )
        test_close_button.grid()

    def delete_record_button_handler(self):
        if messagebox.askyesno("", "Удалить запись?"):
            self.delete_record(self.table.item(self.table.focus(), 'values')[0])

    def edit_record_button_handler(self, col_n):
        edit_window = Toplevel()
        edit_window.grab_set()
        edit_window.rowconfigure(1, pad=10)
        edit_window.rowconfigure(2, pad=5)
        edit_window.rowconfigure(3, pad=5)
        edit_entry_fields = []
        edit_entry_fields_labels = []
        for name in col_n:
            if name != "id":
                edit_entry_fields.append(Entry(edit_window))
                edit_entry_fields_labels.append(Label(edit_window, text=name + ":"))
        for i in range(len(edit_entry_fields)):
            edit_entry_fields_labels[i].grid(row=1, column=i * 2, sticky='')
            edit_entry_fields[i].grid(row=1, column=i * 2 + 1, sticky='')
        display_values(self.table, edit_entry_fields)
        confirm_edit_button = Button(edit_window,
                                     text="Подтвердить изменения",
                                     command=lambda:
                                     self.confirm_edit_button_handler(col_n, edit_entry_fields, edit_window)
                                     )
        cancel_edit_button = Button(edit_window, text="Отмена", command=edit_window.destroy)
        confirm_edit_button.grid(row=2, column=0, columnspan=len(edit_entry_fields) * 2)
        cancel_edit_button.grid(row=3, column=0, columnspan=len(edit_entry_fields) * 2)

    def confirm_edit_button_handler(self, col_n, entry_fields, window):
        if messagebox.askyesno("", "Изменить запись?"):
            self.update_record(col_n, entry_fields)
            self.refresh(self.table)
            window.destroy()

    def delete_selected_button_handler(self):
        if messagebox.askyesno("", "Удалить выбранные записи?"):
            self.delete_selected_records(self.table)

    # def add_record_button_handler(self, col_n, entry_fields):
    #     if messagebox.askyesno("", "Добавить запись?"):
    #         self.add_record(col_n, entry_fields)

    def add_record_button_handler(self, col_n):
        add_window = Toplevel()
        add_window.grab_set()
        add_window.rowconfigure(1, pad=10)
        add_window.rowconfigure(2, pad=5)
        add_window.rowconfigure(3, pad=5)
        add_entry_fields = []
        add_entry_fields_labels = []
        for name in col_n:
            if name != "id":
                add_entry_fields.append(Entry(add_window))
                add_entry_fields_labels.append(Label(add_window, text=name + ":"))
        for i in range(len(add_entry_fields)):
            add_entry_fields_labels[i].grid(row=1, column=i * 2, sticky='', padx=3)
            add_entry_fields[i].grid(row=1, column=i * 2 + 1, sticky='')
        confirm_add_button = Button(add_window,
                                    text="Добавить запись",
                                    command=lambda:
                                    self.confirm_add_button_handler(col_n, add_entry_fields, add_window)
                                    )

        cancel_add_button = Button(add_window, text="Отмена", command=add_window.destroy)
        confirm_add_button.grid(row=2, column=0, columnspan=len(add_entry_fields) * 2)
        cancel_add_button.grid(row=3, column=0, columnspan=len(add_entry_fields) * 2)

    def confirm_add_button_handler(self, col_n, entry_fields, window):
        if messagebox.askyesno("", "Добавить запись?"):
            self.add_record(col_n, entry_fields)
            window.destroy()

    @staticmethod
    def quit_button_handler(window):
        if messagebox.askyesno("", "Выйти?"):
            window.quit()
