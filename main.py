import client
import tkinter
import threading
def btt_opt(field):
    text = field.get()
    me.send_msgH(text)



me = client.Client(20122,'me1')
me.start_session("")
root = tkinter.Tk()
field = tkinter.Entry()
field.place(x=0,y=0)
btt = tkinter.Button(command=lambda x=field: btt_opt(x))
btt.place(x=0,y=20)
th = threading.Thread(target=me.get_msgH,args=[0])
th.start()

root.mainloop()



