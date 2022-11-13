from tkinter import *
from tkinter import ttk
from ByClient import ByClient
import pickle
import os

class ByWindow():
    def __init__(self):
        # window
        self.root = Tk()
        self.root.title('ByClient')
        self.massage = {
            'fromAddress':'',
            'passkey':'',
            'toAddress':'',
            'subject':'',
            'body':''
        }
        self.fromAddress = StringVar()
        self.passkey = StringVar()
        self.toAddress = StringVar()
        self.subject = StringVar()
        self.body = StringVar()
        self.msgbody = None

        # client server
        self.client = ByClient()

    # run
    def run(self):
        # contacts and history
        try:
            with open('contacts.pkl', 'rb') as fp:
                self.contacts = pickle.load(fp)
        except:
            self.contacts = []

        try:
            with open('history.pkl', 'rb') as fp:
                self.history = pickle.load(fp)
        except:
            self.history = []

        # draft
        try:
            with open('draft.pkl', 'rb') as fp:
                info = pickle.load(fp)
                self.massage['fromAddress'] = info[0]
                self.massage['passkey'] = info[1]
                self.massage['toAddress'] = info[2]
                self.massage['subject'] = info[3]
                self.massage['body'] = info[4]
        except:
            pass
        
        self.massage_out()

        # main window
        self.mainWindow = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainWindow.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainWindow.columnconfigure(0, weight=1)
        self.mainWindow.rowconfigure(0, weight=1)

        # input email
        ttk.Label(self.mainWindow, text="Your Email: ").grid(column=0, row=1, sticky=W)
        account_entry = ttk.Entry(self.mainWindow, width=30, textvariable=self.fromAddress)
        account_entry.grid(column=4, row=1, sticky=(W, E))

        # passkey
        ttk.Label(self.mainWindow, text="Your Password: ").grid(column=0, row=2, sticky=W)
        passkey_entry = ttk.Entry(self.mainWindow, show="*", width=30, textvariable=self.passkey)
        passkey_entry.grid(column=4, row=2, sticky=(W, E))

        # contact
        ttk.Label(self.mainWindow, text="Recepient's Email: ").grid(column=0, row=3, sticky=W)
        receiver_entry = ttk.Button(self.mainWindow, width=30, textvariable=self.toAddress, command=self.func_contact)
        receiver_entry.grid(column=4, row=3, sticky=(W, E))

        # subject
        ttk.Label(self.mainWindow, text="Subject: ").grid(column=0, row=6, sticky=W)
        subject_entry = ttk.Entry(self.mainWindow, width=30, textvariable=self.subject)
        subject_entry.grid(column=4, row=6, sticky=(W, E))

        # body
        ttk.Label(self.mainWindow, text="Message Body: ").grid(column=0, row=7, sticky=W)
        self.msgbody = Text(self.mainWindow, width=30, height=10)
        self.msgbody.insert("end", self.massage['body'])
        self.msgbody.grid(column=4, row=7, sticky=(W, E))

        # history
        ttk.Button(self.mainWindow, text="History", command=self.func_history).grid(column=0,row=8,sticky=W)

        # draft
        ttk.Button(self.mainWindow, text="Save Draft", command=self.func_draft).grid(column=2,row=8,sticky=E)

        # send email
        ttk.Button(self.mainWindow, text="Send Email", command=self.func_sendEmail).grid(column=4,row=8,sticky=E)

        for child in self.mainWindow.winfo_children(): child.grid_configure(padx=5, pady=5)

        account_entry.focus()

        self.root.mainloop()

    # contact
    def func_contact(self):
        self.massage_in()

        # window
        new_window = Toplevel()

        Buttons = {}
        for k in self.contacts:
            Buttons[k] = IntVar()
            Checkbutton(new_window, text = k, variable = Buttons[k]).pack(anchor=W)

        # new contact
        Label(new_window, text="New Contact: ").pack(anchor=W)
        new_contacts = StringVar()
        Entry(new_window, textvariable=new_contacts).pack(anchor=W)

        # input contact
        toaddress_list = [x.strip() for x in self.massage['toAddress'].strip().split(';')]
        toaddress_remain = []
        for k in toaddress_list:
            if k in Buttons:
                Buttons[k].set(1)
            else:
                toaddress_remain.append(k)
        new_contacts.set('; '.join(toaddress_remain))
        
        # close frame
        def func_close_contact():
            toaddress_list = []
            for k, v in Buttons.items():
                if v.get() == 1:
                    toaddress_list.append(k)

            for t in new_contacts.get().strip().split(";"):
                if t.strip() != "":
                    toaddress_list.append(t.strip())

            self.massage['toAddress'] = ';\n'.join(toaddress_list)
            self.toAddress.set(self.massage['toAddress'])

            new_window.destroy()

        Button(new_window, text="Accept", command=func_close_contact).pack(anchor=E)

        new_window.mainloop()

    # history
    def func_history(self):
        new_window = Toplevel()
        name_length = 0
        for info in self.history:
            name_length = max(name_length, len(info[0]))

        for info in self.history:
            toEmail = info[0]
            if len(toEmail) > name_length:
                toEmail = toEmail[:name_length - 3] + '...'
            if len(toEmail) < name_length:
                toEmail = toEmail + ' ' * (name_length - len(toEmail))

            subject = info[3]
            if len(subject) > name_length:
                subject = subject[:name_length - 3] + '...'

            # select history
            def func_select():
                s_info = info
                def f():
                    self.massage['fromAddress'] = s_info[0]
                    self.massage['passkey'] = s_info[1]
                    self.massage['toAddress'] = s_info[2]
                    self.massage['subject'] = s_info[3]
                    self.massage['body'] = s_info[4]

                    self.massage_out()
                    new_window.destroy()
                return f

            # botton to set
            Button(new_window, width=30, height=1, text = "{}: {}".format(toEmail, subject), command=func_select(), anchor=W, justify=LEFT).pack(anchor=W)

        new_window.mainloop()

    # draft
    def func_draft(self):
        self.massage_in()
        info = [self.massage['fromAddress'],
            self.massage['passkey'],
            self.massage['toAddress'],
            self.massage['subject'],
            self.massage['body']]
        with open('draft.pkl', 'wb') as fp:
            pickle.dump(info, fp)

        ttk.Label(self.mainWindow, text="Draft has saved successfully").grid(column=4,row=9,sticky=W)

    # send email
    def func_sendEmail(self):

        self.massage_in()
        self.client.get_massage(self.massage)
        err = self.client.send_an_email(serverPort=465)

        if err!=0:
            print('end from err:{}\n'.format(err))
            ttk.Label(self.mainWindow, text=str(err)).grid(column=4,row=9,sticky=W)
            return
        
        # update contacts
        for to in self.massage['toAddress'].split(';'):
            if to != "" and to not in self.contacts:
                self.contacts.append(to)
        with open('contacts.pkl', 'wb') as fp:
            pickle.dump(self.contacts, fp)

        # update history
        self.history.append([
            self.massage['fromAddress'],
            self.massage['passkey'],
            self.massage['toAddress'],
            self.massage['subject'],
            self.massage['body']])
        with open('history.pkl', 'wb') as fp:
            pickle.dump(self.history, fp)

        # 如果当前邮件存在草稿，则将其删除
        if os.path.exists('draft.pkl'):
            os.remove('draft.pkl')

    # update massage
    def massage_out(self):
        self.fromAddress.set(self.massage['fromAddress'])
        self.toAddress.set(self.massage['toAddress'])
        self.passkey.set(self.massage['passkey'])
        self.body.set(self.massage['body'])
        self.subject.set(self.massage['subject'])

        if self.msgbody!=None:
            self.msgbody.delete('0.0',END)
            self.msgbody.insert('end',self.massage['body'])

    # update self
    def massage_in(self):
        self.massage['fromAddress'] = self.fromAddress.get()
        self.massage['toAddress'] = self.toAddress.get()
        self.massage['passkey'] = self.passkey.get()
        self.body.set(self.msgbody.get('1.0','end'))
        self.massage['body'] = self.body.get()
        self.massage['subject'] = self.subject.get()


