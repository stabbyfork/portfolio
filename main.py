import discord

from queue import Queue
import asyncio
import threading
import wx

# globals
hasMessage = False

class Client(discord.Client):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        print("init started")
        self.guildName = 'KäseKorp'
        #self.p1 = threading.Thread(target=self.frameStart)
        #self.p1.start()

    # better init
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        await self.sendMessage()
        #await channel.send("nuh uh")

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


    async def sendMessage(self):
        while True:
            #print("queue before")
            #sendQueue.join()
            #print("queue found")
            if sendQueue.qsize != 0:
                try: message = sendQueue.get(block=False)
                except: continue#print("Nothing in queue"); continue
                channel = "general-en"
                if discord.utils.get(client.get_all_channels(), guild__name='KäseKorp', name=channel) == None:
                    return f"Could not find channel {channel}"
                channel = discord.utils.get(client.get_all_channels(), guild__name='KäseKorp', name=channel)
                #channelID = channel.id
                await channel.send(message)
            else:
                await asyncio.sleep(0.1)


        




class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)
        
        self.receiveLog = wx.TextCtrl

        
        

        self.panel = wx.Panel(self)

        self.sendMessageButton = wx.Button(self,label="Send a message")

        self.Bind(wx.EVT_BUTTON, self.sendMessage, self.sendMessageButton)
        
    def sendMessage(self,event):
        dialog = wx.TextEntryDialog(self, message="Enter the message to send")
        ret = dialog.ShowModal()
        if ret == wx.ID_CANCEL:
            dialog.Destroy()
        try: sendQueue.put(dialog.GetValue(), block=False)
        except Exception as e: return f"Queue full: {e}"

    async def updateLog(self):
        while True:
            try: message = receiveQueue.get()
            except: continue





intents = discord.Intents.default()
intents.message_content = True


if __name__ == '__main__':
    print("here")
    client = Client(intents=intents)



#Queue for sending messages
sendQueue = Queue()

#Queue for receiving messages
receiveQueue = Queue()

loop = asyncio.new_event_loop()
loop.create_task(client.start(open("./TOKEN.txt").read()))
t = threading.Thread(target=loop.run_forever)
t.start()
t.join

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, title="Discord Bot")
    frame.Show()
    app.MainLoop()

