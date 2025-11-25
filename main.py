import sys
import asyncio
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from panel import Ui_MainWindow
from qasync import QEventLoop, asyncSlot
from code_dialog import CodeDialog, AsyncMessageBox
from pyrogram import (Client,errors,enums)
import os, traceback , time , re


API_ID , API_HASH = 6 , "eb06d4abfb49dc3eeb1aeb98ae0f581e"

os.makedirs('bots', exist_ok=True)


Extract = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.ui.testTokenButton.clicked.connect(self.testbottoken)
        self.ui.stopButton.clicked.connect(self.disable_remove)
        self.ui.startButton.clicked.connect(self.removeing_member)
        self.ui.testChannelButton.clicked.connect(self.testacss)
    
    def is_valid_telegram_link(self,text):
        pattern_username = r"^@[a-zA-Z0-9_]{5,}$"
        pattern_invite = r"^t\.me/\+[\w\-]{10,}$"
        return bool(re.match(pattern_username, text)) or bool(re.match(pattern_invite, text))

    @asyncSlot()
    async def ask_code_dialog(self, title, label):
        dlg = CodeDialog(title, label, self)
        dlg.setModal(True)
        dlg.show()
        while dlg.result() == 0:  # QDialog.DialogCode.Rejected = 0, Accepted = 1
            await asyncio.sleep(0.1)

        if dlg.result() == 1:
            return dlg.get_value(), True
        else:
            return "", False
    
    
    @asyncSlot()
    async def show_async_message(self, title, message, icon=QMessageBox.Icon.Information):
        dlg = AsyncMessageBox(title, message, icon, self)
        dlg.show()

        while dlg.result is None:
            await asyncio.sleep(0.05)

        return dlg

    
    @asyncSlot()
    async def testbottoken(self):
        gettoken = self.ui.botTokenInput.text().strip()
        if gettoken == "":
            await self.show_async_message("Error", "Please enter a token.", icon=QMessageBox.Icon.Critical)
            return
        asyncio.create_task(self.testbot(gettoken))
    
    async def testbot(self, token):
        global Extract
        if Extract:
            await self.show_async_message("Error", "Already Active Process.", icon=QMessageBox.Icon.Critical)
            return
        try:
            name = token.split(":")[0]
            if os.path.exists(f"bots/{name}.session"):
                os.remove(f"bots/{name}.session")
            bot = Client(f"bots/{name}",API_ID , API_HASH,bot_token=token)
            await bot.start()
            me = await bot.get_me()
            await self.show_async_message("Success", "Successfully logged in : @{}".format(me.username), icon=QMessageBox.Icon.Information)
            await bot.stop()
            return True
        except Exception as e:
            await self.show_async_message("Error", str(e), icon=QMessageBox.Icon.Critical)
            print(traceback.format_exc())
            try:await bot.stop()
            except:pass
            try:os.remove(f"bots/{name}.session")
            except:pass
            return False
    
    @asyncSlot()
    async def testacss(self):
        gettoken = self.ui.botTokenInput.text().strip()
        link = self.ui.channelInput.text().strip()
        if gettoken == "":
            await self.show_async_message("Error", "Please enter a token.", icon=QMessageBox.Icon.Critical)
            return
        if self.is_valid_telegram_link(link) or link.startswith("-100") and link.replace("-100","").isdigit():
            if link.startswith("-100"):
                link = int(link)
            asyncio.create_task(self.testacssproc(gettoken,link))
        else:
            await self.show_async_message("Error", "Invalid Telegram link.", icon=QMessageBox.Icon.Critical)
        return
    
    async def testacssproc(self, token, link):
        global Extract
        if Extract:
            await self.show_async_message("Error", "Already Active Process.", icon=QMessageBox.Icon.Critical)
            return
        try:
            name = token.split(":")[0]
            bot = Client(f"bots/{name}",API_ID , API_HASH,bot_token=token)
            await bot.start()
            
            chat = await bot.get_chat(link)
            
            async for user in bot.get_chat_members(chat.id,limit=1, filter=enums.ChatMembersFilter.RECENT):
                pass
            
            self.ui.logDisplay.append("Chat Info: {}".format(chat))
            await self.show_async_message("Success", "Successfully Chat Accessed!", icon=QMessageBox.Icon.Information)
            await bot.stop()
            return True
        
        except errors.ChatAdminRequired:
            await self.show_async_message("Error", "Chat Admin Required.", icon=QMessageBox.Icon.Critical)
            try:await bot.stop()
            except:pass
            return
        
        except Exception as e:
            await self.show_async_message("Error", str(e), icon=QMessageBox.Icon.Critical)
            print(traceback.format_exc())
            try:await bot.stop()
            except:pass
            return False
    
    @asyncSlot()
    async def disable_remove(self):
        global Extract
        if Extract:
            Extract = False
            self.ui.logDisplay.append("Status: Inactive")
            await self.show_async_message("Success", "Removing stopped.", icon=QMessageBox.Icon.Information)
        else:
            await self.show_async_message("Error", "Removing is not active.", icon=QMessageBox.Icon.Critical)
        return
        
    
    @asyncSlot()
    async def removeing_member(self):
        global Extract
        
        self.ui.logDisplay.clear()
        self.ui.logDisplay.setReadOnly(True)
        gettoken = self.ui.botTokenInput.text().strip()
        if gettoken == "":
            await self.show_async_message("Error", "No token found.", icon=QMessageBox.Icon.Critical)
            return
        if Extract:
            await self.show_async_message("Error", "Already Active Process.", icon=QMessageBox.Icon.Critical)
            return
        
        
        link = self.ui.channelInput.text().strip()
        if self.is_valid_telegram_link(link) or link.startswith("-100") and link.replace("-100","").isdigit():
            Extract = True
            self.ui.logDisplay.append("Status: Active")
            if link.startswith("-100"):
                link = int(link)
            asyncio.create_task(self.removeing_proc(gettoken,link))
        else:
            await self.show_async_message("Error", "Invalid Telegram link.", icon=QMessageBox.Icon.Critical)
        return
    
    
    async def removeing_proc(self,token , link):
        global Extract
        try:
            name = token.split(":")[0]

            self.ui.logDisplay.append("Extracting {}...".format(name))
            bot = Client(f"bots/{name}",API_ID , API_HASH,bot_token=token)
            await asyncio.wait_for(bot.connect() , 15)
            self.ui.logDisplay.append("Connected to {}.".format(name))
            chat= await bot.get_chat(link)
            count = chat.members_count
            self.ui.logDisplay.append("Number of chat members: {}".format(count))
            self.ui.lcdTotalMembers.display(count)
            self.ui.lcdRemovedMembers.display(0)
            self.ui.lcdTimer.display(0)
            self.ui.logDisplay.append("Status: Started")
            
            timestart = time.time()
            removed = True
            number = 0
            limitremove = self.ui.memberCountInput.value()
            while removed:
                removed = False
                if Extract == False:break
                if limitremove != 0 and number >= limitremove:break    
                self.ui.lcdTimer.display(int(time.time() - timestart))
                async for user in bot.get_chat_members(chat.id,limit=200, filter=enums.ChatMembersFilter.RECENT):
                    if Extract == False:break
                    if limitremove != 0 and number >= limitremove:break
                    self.ui.lcdTimer.display(int(time.time() - timestart))
                    if user.status == enums.ChatMemberStatus.MEMBER:
                        removed = True
                        try:
                            await bot.ban_chat_member(chat.id,user.user.id)
                            number += 1
                            self.ui.lcdRemovedMembers.display(number)
                            self.ui.lcdTimer.display(int(time.time() - timestart))
                            self.ui.logDisplay.append("[{}] Removed => {}".format(number,user.user.id))
                            await asyncio.sleep(0.1)
                            await bot.unban_chat_member(chat.id,user.user.id)
                        except errors.FloodWait as e:
                            self.ui.logDisplay.append("FloodWait => {}".format(e.value))
                            await asyncio.sleep(e.value)
                        except Exception as e:
                            self.ui.logDisplay.append("Exception => {}".format(e))
                            traceback.print_exc()
                    await asyncio.sleep(0.1)
                    self.ui.lcdTimer.display(int(time.time() - timestart))
                self.ui.logDisplay.append("Sleep 10 sec")
                for _ in range(10):
                    await asyncio.sleep(1)
                    self.ui.lcdTimer.display(int(time.time() - timestart))
                    
            Extract = False
            self.ui.logDisplay.append("Done.")
            self.ui.logDisplay.append("Status: Disactive")
            await bot.disconnect()
            self.ui.logDisplay.append("Disconnected from {}.".format(name))
            self.ui.logDisplay.append("Number of chat members removed: {}".format(number))
            await self.show_async_message("Success", "Removed {} members.".format(number), icon=QMessageBox.Icon.Information)
            self.ui.lcdTimer.display(int(time.time() - timestart))
            return
        except Exception as e:
            Extract = False
            await self.show_async_message("Error", str(e), icon=QMessageBox.Icon.Critical)
            print(traceback.format_exc())
            self.ui.logDisplay.append(traceback.format_exc())
            try:await bot.disconnect()
            except:pass
            return
    
                
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()
