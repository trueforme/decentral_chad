import client
import tkinter
import threading
# def btt_opt(field):
#     text = field.get()
#     me.send_msgH(text)



me = client.Client(20121,'me1')
# th2 = threading.Thread(target=me.accept_connection)
# th2.start()
me.start_session('192.168.0.105',20122)

# root = tkinter.Tk()
# field = tkinter.Entry()
# field.place(x=0,y=0)
# btt = tkinter.Button(command=lambda x=field: btt_opt(x))
# btt.place(x=0,y=20)
# th = threading.Thread(target=me.get_msgH,args=[0])
# th.start()

# root.mainloop()



