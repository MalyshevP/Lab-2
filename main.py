import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from myemail import SMTPClient, IMAPClient
from tkinter import messagebox
from ecp import ecp_verify

# окно ввода кредов для SMTP
class SMTPAutorizationWindow(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        self.top.title("Авторизация SMTP")

        self.l_server = tk.Label(top, text="SMTP сервер")
        self.l_server.pack()
        self.e_server = tk.Entry(top)
        self.e_server.insert(0, "smtp.gmail.com")
        self.e_server.pack()

        self.l_port = tk.Label(top, text="Порт SMTP сервера")
        self.l_port.pack()
        self.e_port = tk.Entry(top)
        self.e_port.insert(0, "465")
        self.e_port.pack()

        self.l_login = tk.Label(top, text="Логин")
        self.l_login.pack()
        self.e_login = tk.Entry(top)
        self.e_login.insert(0, "test@gmail.com")
        self.e_login.pack()

        self.l_pswrd = tk.Label(top, text="Пароль")
        self.l_pswrd.pack()
        self.e_pswrd = tk.Entry(top, show="*")
        self.e_pswrd.insert(0, "pass#")
        self.e_pswrd.pack()

        self.b = tk.Button(self.top, text='OK', command=self.ok)
        self.b.pack()

    # сохранение значений полей и закрытие окна
    def ok(self):
        self.server = self.e_server.get()
        self.port = int(self.e_port.get())
        self.login = self.e_login.get()
        self.pswrd = self.e_pswrd.get()
        self.top.destroy()

# окно ввода кредов для IMAP
class IMAPAutorizationWindow(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        self.top.title("Авторизация IMAP")

        self.l_server = tk.Label(top, text="IMAP сервер")
        self.l_server.pack()
        self.e_server = tk.Entry(top)
        self.e_server.insert(0, "imap.gmail.com")
        self.e_server.pack()

        self.l_port = tk.Label(top, text="Порт IMAP сервера")
        self.l_port.pack()
        self.e_port = tk.Entry(top)
        self.e_port.insert(0, "993")
        self.e_port.pack()

        self.l_login = tk.Label(top, text="Логин")
        self.l_login.pack()
        self.e_login = tk.Entry(top)
        self.e_login.insert(0, "test@gmail.com")
        self.e_login.pack()

        self.l_pswrd = tk.Label(top, text="Пароль")
        self.l_pswrd.pack()
        self.e_pswrd = tk.Entry(top, show="*")
        self.e_pswrd.insert(0, "pass#")
        self.e_pswrd.pack()

        self.b = tk.Button(self.top, text='OK', command=self.ok)
        self.b.pack()

    # сохранение значений полей и закрытие окна
    def ok(self):
        self.server = self.e_server.get()
        self.port = int(self.e_port.get())
        self.login = self.e_login.get()
        self.pswrd = self.e_pswrd.get()
        self.top.destroy()

# окно ошибки авторизации
class AutorizationErrorWindow(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        self.top.title("Ошибка авторизации")

        self.l_server = tk.Label(top, text="Не удалось совершить авторизацию")
        self.l_server.pack()

        self.b = tk.Button(self.top, text='OK', command=self.top.destroy)
        self.b.pack()

# главное окно
class App(object):
    def __init__(self, master):
        self.window = master
        self.window.title("ЭЦП почта")

        # контроллер вкладок
        self.tabControl = ttk.Notebook(self.window)

        # объекты вкладок
        self.tab_send = ttk.Frame(self.tabControl)
        self.tab_recieve = ttk.Frame(self.tabControl)

        # добавление вкладок и их названия
        self.tabControl.add(self.tab_send, text='Отправить')
        self.tabControl.add(self.tab_recieve, text='Получить')
        self.tabControl.pack(expand=1, fill="both")

        self.setup_send()
        self.setup_recieve()

        # Клиенты почты
        self.smtp_client = None
        self.imap_client = None

        # Сертификаты
        self.smtp_cert = None
        self.imap_cert = None

        # Вложения
        self.smtp_attachment_path = None
        self.imap_attachment_path = None


    def setup_send(self):
        # настройка вкладки Отправления письма
        # ------------------------------------
        self.tab_send.rowconfigure(0, minsize=500, weight=1)
        self.tab_send.columnconfigure(0, minsize=500, weight=1)

        self.fr_smtp_text = tk.Frame(self.tab_send)
        self.fr_smtp_buttons = tk.Frame(self.tab_send)

        self.fr_smtp_text.grid(row=0, column=0, sticky="nsew")
        self.fr_smtp_buttons.grid(row=0, column=1, sticky="ns")

        # Кнопки
        self.btn_smtp_auth = tk.Button(self.fr_smtp_buttons, text="Выполнить вход", command=self.smtp_auth)
        self.btn_smtp_select = tk.Button(self.fr_smtp_buttons, text="Выбрать сертификат", command=self.smtp_select_certificate)
        self.btn_smtp_attach = tk.Button(self.fr_smtp_buttons, text="Выбрать вложение", command=self.smtp_select_attach)
        self.btn_smtp_send = tk.Button(self.fr_smtp_buttons, text="Отправить", command=self.smtp_send)

        # Индикаторы
        self.lb_smtp_auth = tk.Label(self.fr_smtp_buttons, text="Авторизация")
        self.lb_smtp_auth.config(fg="#FF0000")

        self.lb_smtp_cert = tk.Label(self.fr_smtp_buttons, text="Сертификат")
        self.lb_smtp_cert.config(fg="#FF0000")

        self.lb_smtp_attach = tk.Label(self.fr_smtp_buttons, text="Файл")
        self.lb_smtp_attach.config(fg="#FF0000")

        # Порядок виджетов
        self.btn_smtp_auth.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_smtp_select.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.btn_smtp_attach.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.btn_smtp_send.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        self.lb_smtp_auth.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        self.lb_smtp_cert.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.lb_smtp_attach.grid(row=6, column=0, sticky="ew", padx=5, pady=5)

        # Поле сообщения
        self.lb_smtp_to = tk.Label(self.fr_smtp_text, text="Получатели")
        self.txt_smtp_to = tk.Text(self.fr_smtp_text, height=1, width=80)
        
        self.lb_smtp_subject = tk.Label(self.fr_smtp_text, text="Тема")
        self.txt_smtp_subject = tk.Text(self.fr_smtp_text, height=1, width=80)

        self.lb_smtp_body = tk.Label(self.fr_smtp_text, text="Текст сообщения")
        self.txt_smtp_body = tk.Text(self.fr_smtp_text, height=30, width=80)

        # Порядок виджетов
        self.lb_smtp_to.grid(row=0, column=0, sticky="ew")
        self.txt_smtp_to.grid(row=1, column=0, sticky="ew")
        self.lb_smtp_subject.grid(row=2, column=0, sticky="ew")
        self.txt_smtp_subject.grid(row=3, column=0, sticky="ew")
        self.lb_smtp_body.grid(row=4, column=0, sticky="ew")
        self.txt_smtp_body.grid(row=5, column=0, sticky="ew")

        # ------------------------------------
    
    def setup_recieve(self):
        # Настройка вкладки Получения письма
        # ----------------------------------
        self.tab_recieve.rowconfigure(0, minsize=500, weight=1)
        self.tab_recieve.columnconfigure(0, minsize=500, weight=1)

        self.fr_imap_text = tk.Frame(self.tab_recieve)
        self.fr_imap_buttons = tk.Frame(self.tab_recieve)

        self.fr_imap_text.grid(row=0, column=0, sticky="nsew")
        self.fr_imap_buttons.grid(row=0, column=1, sticky="ns")

        # Кнопки
        self.btn_imap_auth = tk.Button(self.fr_imap_buttons, text="Выполнить вход", command=self.imap_auth)
        self.btn_imap_select = tk.Button(self.fr_imap_buttons, text="Выбрать сертификат", command=self.imap_select_certificate)
        self.btn_imap_recieve = tk.Button(self.fr_imap_buttons, text="Получить", command=self.imap_recieve)
        self.btn_imap_verify_text = tk.Button(self.fr_imap_buttons, text="Проверить сообщение", command=self.imap_verify_text)
        self.btn_imap_verify_file = tk.Button(self.fr_imap_buttons, text="Проверить файл", command=self.imap_verify_file)

        # Индикаторы
        self.lb_imap_auth = tk.Label(self.fr_imap_buttons, text="Авторизация")
        self.lb_imap_auth.config(fg="#FF0000")

        self.lb_imap_cert = tk.Label(self.fr_imap_buttons, text="Сертификат")
        self.lb_imap_cert.config(fg="#FF0000")

        # Порядок виджетов
        self.btn_imap_auth.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_imap_select.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.btn_imap_recieve.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.btn_imap_verify_text.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.btn_imap_verify_file.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        self.lb_imap_auth.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.lb_imap_cert.grid(row=6, column=0, sticky="ew", padx=5, pady=5)

        # Поле сообщения
        self.lb_imap_from = tk.Label(self.fr_imap_text, text="Отправитель")
        self.txt_imap_from = tk.Text(self.fr_imap_text, height=1, width=80)
        self.txt_imap_from.configure(state='disabled')
        
        self.lb_imap_subject = tk.Label(self.fr_imap_text, text="Тема")
        self.txt_imap_subject = tk.Text(self.fr_imap_text, height=1, width=80)
        self.txt_imap_subject.configure(state='disabled')

        self.lb_imap_body = tk.Label(self.fr_imap_text, text="Текст сообщения")
        self.txt_imap_body = tk.Text(self.fr_imap_text, height=30, width=80)
        self.txt_imap_body.configure(state='disabled')

        # Порядок виджетов
        self.lb_imap_from.grid(row=0, column=0, sticky="ew")
        self.txt_imap_from.grid(row=1, column=0, sticky="ew")
        self.lb_imap_subject.grid(row=2, column=0, sticky="ew")
        self.txt_imap_subject.grid(row=3, column=0, sticky="ew")
        self.lb_imap_body.grid(row=4, column=0, sticky="ew")
        self.txt_imap_body.grid(row=5, column=0, sticky="ew")
        # ----------------------------------
        pass

    def imap_auth(self):
        self.btn_imap_auth["state"] = "disabled" 
        imap_auth_window = IMAPAutorizationWindow(self.window)
        try:
            self.window.wait_window(imap_auth_window.top)
            if imap_auth_window.login == "" or imap_auth_window.pswrd == "" or imap_auth_window.server == "":
                raise Exception()
            self.imap_client = IMAPClient(imap_auth_window.server, imap_auth_window.port, imap_auth_window.login, imap_auth_window.pswrd)
            self.lb_imap_auth.config(fg="#00FF00")
        except Exception as er:
            print(er)
            er_window = AutorizationErrorWindow(self.window)
            self.window.wait_window(er_window.top)
            self.lb_imap_auth.config(fg="#FF0000")
        self.btn_imap_auth["state"] = "normal"

    def smtp_auth(self):
        self.btn_smtp_auth["state"] = "disabled" 
        smtp_auth_window = SMTPAutorizationWindow(self.window)
        try:
            self.window.wait_window(smtp_auth_window.top)
            if smtp_auth_window.login == "" or smtp_auth_window.pswrd == "" or smtp_auth_window.server == "":
                raise Exception()
            self.smtp_client = SMTPClient(smtp_auth_window.server, smtp_auth_window.port, smtp_auth_window.login, smtp_auth_window.pswrd)
            self.lb_smtp_auth.config(fg="#00FF00")
        except Exception as er:
            print(er)
            er_window = AutorizationErrorWindow(self.window)
            self.window.wait_window(er_window.top)
            self.lb_smtp_auth.config(fg="#FF0000")
        self.btn_smtp_auth["state"] = "normal"

    def smtp_select_certificate(self):
        smtp_cert_file = fd.askopenfilename(filetypes=(('Private key', '*.pem'),('All files', '*.*')))
        if smtp_cert_file:
            with open(smtp_cert_file, 'rb') as f:
                self.smtp_cert = f.read()
                self.lb_smtp_cert.config(fg="#00FF00")
                return    
        self.smtp_cert = None
        self.lb_smtp_cert.config(fg="#FF0000")

    def smtp_select_attach(self):
        self.smtp_attachment_path = fd.askopenfilename()
        if self.smtp_attachment_path:
            self.lb_smtp_attach.config(fg="#00FF00") 
            return
        self.smtp_attachment_path  = None
        self.lb_smtp_attach.config(fg="#FF0000")

    def imap_select_certificate(self):
        imap_cert_file = fd.askopenfilename(filetypes=(('Public key', '*.pub'),('All files', '*.*')))
        if imap_cert_file:
            with open(imap_cert_file, 'rb') as f:
                self.imap_cert = f.read()
                self.lb_imap_cert.config(fg="#00FF00")
                return    
        self.imap_cert = None
        self.lb_imap_cert.config(fg="#FF0000")

    def smtp_send(self):
        self.btn_smtp_send["state"] = "disabled" 
        try:
            to_list = self.txt_smtp_to.get("1.0",'end-1c').strip().split(',')
            to = [el.strip() for el in to_list]
            self.smtp_client.send(to, self.txt_smtp_subject.get("1.0",'end-1c'), 
                                  self.txt_smtp_body.get("1.0",'end-1c'), 
                                  self.smtp_cert, self.smtp_attachment_path)
            messagebox.showinfo("Отправлено", "Сообщение отправлено")
        except Exception as er:
            print(er)
            messagebox.showerror("Ошибка", "Сообщение не отправлено")
        self.btn_smtp_send["state"] = "normal" 

    def imap_recieve(self):
        message_from, subject, message, attachment = self.imap_client.get()
        
        self.imap_attachment_path = attachment
        
        self.txt_imap_from.configure(state='normal')
        self.txt_imap_subject.configure(state='normal')
        self.txt_imap_body.configure(state='normal')


        self.txt_imap_from.delete('1.0', 'end')
        self.txt_imap_subject.delete('1.0', 'end')
        self.txt_imap_body.delete('1.0', 'end')

        self.txt_imap_from.insert("1.0", message_from)
        self.txt_imap_subject.insert("1.0", subject)
        self.txt_imap_body.insert("1.0", message)

        self.txt_imap_from.configure(state='disabled')
        self.txt_imap_subject.configure(state='disabled')
        self.txt_imap_body.configure(state='disabled')

    def imap_verify_text(self):
        message = self.txt_imap_body.get("1.0",'end-1c')
        message, signature = message.rsplit('Text signature: ', 1)
        message, _ = message.rsplit('File signature: ', 1)
        message = message.strip()
        signature = signature.strip()

        verification = ecp_verify(message.encode(), int(signature, 0), self.imap_cert)
        if verification['valid']:
            messagebox.showinfo("Результат верификации сообщения", 
                                f"Подпись подлена.\nХеш сообщения: {verification['hash']}\nХеш из подписи: {verification['shash']}")
        else:
            messagebox.showerror("Результат верификации сообщения", 
                                 f"Подпись не прошла проверку подлинности.\nХеш сообщения: {verification['hash']}\nХеш из подписи: {verification['shash']}")

    def imap_verify_file(self):
        if not self.imap_attachment_path:
            messagebox.showerror("Файла нет", "В сообщении не было файла")
            return

        message = self.txt_imap_body.get("1.0",'end-1c')
        message, _ = message.rsplit('Text signature: ', 1)
        message, signature = message.rsplit('File signature: ', 1)
        signature = signature.strip()
        message = open(self.imap_attachment_path, 'rb').read()

        verification = ecp_verify(message, int(signature, 0), self.imap_cert)
        if verification['valid']:
            messagebox.showinfo("Результат верификации файла", 
                                f"Подпись подлена.\nХеш файла: {verification['hash']}\nХеш из подписи: {verification['shash']}")
        else:
            messagebox.showerror("Результат верификации файла", 
                                 f"Подпись не прошла проверку подлинности.\nХеш файла: {verification['hash']}\nХеш из подписи: {verification['shash']}")



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
