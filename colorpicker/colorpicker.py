import colorsys
from PIL import Image
import pyautogui as pyagui
from ast import literal_eval as convToStructure
import wx
import os
import re
import urllib.request
import time
import tomllib



#image path
imgPath = None
xOrig = 0
yOrig = 0
xSize = 1919
ySize = 1079
#pixel to be searched
pixel = [1076,659]
#HSV color
hsv = ()
#number of decimal places for HSV colors








#scan pixels for HSV color
def scanPixelsHSV(imagePath, hsv, XSize,YSize, HSVrounding, isDecimal, config):
    outList = []
    townSetting = config.get("townSetting")
    startX = 0
    startY = 0
    image = Image.open(imagePath)
    pixels = image.load()
    #print(imagePath)
    if townSetting and os.path.basename(imagePath) != ("screenshot.png") and os.path.basename(imagePath) != ("product.png"): return "'townSetting' only works with screenshots!"
    if townSetting:
        startX = 816
        startY = 326
        XSize = 262
        YSize = 251
        if imagePath != "./product.png":
            img = Image.new(image.mode, image.size)
            pixelsNew = img.load()
    if not isDecimal:
        (h,s,v) = hsv
        hsv = (round(h/360,HSVrounding),round(s/100,HSVrounding),round(v/100,HSVrounding))
    for x in range(startX,startX + XSize): # X
        for y in range(startY,startY + YSize): # Y
            (r, g, *b) = pixels[x,y]
            modPixel = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
            modPixel = list(modPixel)

            #print(x,y)
            if townSetting and imagePath != "./product.png":
                img.putpixel((x,y),(round(r/0.78125), round(g/0.78125), round(b[0]/0.78125)))
                #print("doing this")
            for i in range(len(modPixel)):
                modPixel[i] = round(modPixel[i],HSVrounding)
            modPixel = tuple(modPixel)       
            if modPixel == hsv:
                outList.append("Found pixel")
                outList.append(f'X,Y: {[x,y]}')
                outList.append(f'RGB(A): {pixels[x,y]}')
                outList.append(f"HSV: {hsv}")
                if townSetting and imagePath != "./product.png": outList.append("Pixel was found before stage 2")
                pyagui.moveTo(x,y)
                return outList
    if townSetting and imagePath != "./product.png":
        outList.append("Starting stage 2")
        img.save("product.png")
    else:
        outList.append("Pixel not found")
        outList.append(f"HSV used: {hsv}")
    return outList





x = xOrig
y = yOrig









#Application
class App(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Color Picker and Finder")

        # vars
        self.HSVcolor = None
        self.chosenFile = None
        self.X = None
        self.Y = None
        self.HSVroundingFactor = 2
        self.isDecimal = False

        self.XSize = None
        self.YSize = None
        self.defaultWindowStyle = None

        self.outputList = []

        # config loading
        if not os.path.exists("./config.toml"):
            urllib.request.urlretrieve("https://raw.githubusercontent.com/stabbyfork/stuff/main/colorpicker/config.toml", "./config.toml")
        self.config = tomllib.loads(open("./config.toml", "r").read())

        self.panel = wx.Panel(self)
        

        # sizers
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.gridSizer = wx.FlexGridSizer(4,4,1,1)

        # widgets/windows
        self.HSVdesc = wx.StaticText(self.panel,label="HSV color:")
        self.HSV = wx.TextCtrl(self.panel, value="180, 50, 50",style=wx.TE_PROCESS_ENTER)
        self.HSVroundDesc = wx.StaticText(self.panel,label="HSV rounding factor:")
        self.HSVround = wx.TextCtrl(self.panel, value=str(self.HSVroundingFactor))

        self.mousePositionText = wx.TextCtrl(self.panel, value="Mouse Position",style=wx.TE_PROCESS_ENTER,size=(175,25))
        self.ImageSelect = wx.Button(self.panel, label="Choose a file")
        self.screenshotButton = wx.Button(self.panel, label="Take screenshot")
        self.ColorPickerButton = wx.Button(self.panel, label=f"Pick color at mouse position (F1)")

        self.scanButton = wx.Button(self.panel, label=f"Scan image")
        self.isDecimalCheckbox = wx.CheckBox(self.panel, label="Decimal HSV")
        self.output = wx.TextCtrl(self.panel, value="Output:\n", style=wx.TE_READONLY | wx.TE_MULTILINE, size=(-1,250))
        self.windowTypeCheckbox = wx.CheckBox(self.panel, label='Window type: normal')

        self.manualButton = wx.Button(self.panel, label="Manual")
        self.settingsButton = wx.Button(self.panel, label="Settings")
        self.saveDataButton = wx.Button(self.panel, label="Save pixel data")

        # hotkeys
        self.RegisterHotKey(1, wx.MOD_CONTROL, wx.WXK_F1)
        self.RegisterHotKey(2, wx.MOD_CONTROL, wx.WXK_F2)
        self.RegisterHotKey(3, wx.MOD_CONTROL, wx.WXK_F3)

        # F<n> binds
        self.Bind(wx.EVT_CHAR_HOOK, self.on_F1_key_pressed)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_F2_key_pressed)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_F3_key_pressed)

        # other binds
        self.windowTypeCheckbox.Bind(wx.EVT_CHECKBOX, self.on_window_checkbox_pressed)
        self.ImageSelect.Bind(wx.EVT_BUTTON, self.on_image_select_pressed)
        self.ColorPickerButton.Bind(wx.EVT_BUTTON, self.on_color_picker_pressed)
        self.screenshotButton.Bind(wx.EVT_BUTTON, self.on_screenshot_button)
        self.mousePositionText.Bind(wx.EVT_TEXT_ENTER, self.on_coords_entered)
        self.scanButton.Bind(wx.EVT_BUTTON, self.on_scan)
        self.isDecimalCheckbox.Bind(wx.EVT_CHECKBOX, self.on_decimal_toggle)
        self.HSV.Bind(wx.EVT_TEXT_ENTER, self.on_HSV_entered)
        self.manualButton.Bind(wx.EVT_BUTTON, self.on_manual_press)
        self.saveDataButton.Bind(wx.EVT_BUTTON, self.on_save_pixel_press)
        self.settingsButton.Bind(wx.EVT_BUTTON, self.on_settings_press)

        # hotkey binds
        self.Bind(wx.EVT_HOTKEY,self.ctrl_F1_hotkey, id=1)
        self.Bind(wx.EVT_HOTKEY,self.ctrl_F2_hotkey, id=2)
        self.Bind(wx.EVT_HOTKEY,self.ctrl_F3_hotkey, id=3)

        # grid sizer add
        self.gridSizer.AddMany([
            (self.HSVdesc, 0, wx.ALL , 5),
            (self.HSV, 0, wx.ALL , 5),
            (self.HSVroundDesc, 0, wx.ALL , 5),
            (self.HSVround, 0, wx.ALL , 5),

            (self.screenshotButton, 0, wx.ALL , 5),
            (self.ColorPickerButton, 0, wx.ALL , 5),
            (self.mousePositionText, 0, wx.ALL, 5),
            (self.scanButton, 0, wx.ALL, 5),

            (self.windowTypeCheckbox, 0, wx.ALL , 5),
            (self.isDecimalCheckbox, 0, wx.ALL , 5),
            (self.ImageSelect, 0, wx.ALL , 5),
            (self.output, 0, wx.ALL , 5),

            (self.manualButton, 0, wx.ALL , 5),
            (self.saveDataButton, 0, wx.ALL , 5),
            (self.settingsButton, 0, wx.ALL , 5),
        ])
        
        sizer.Add(self.gridSizer)
        self.gridSizer.Layout()
        self.gridSizer.Fit(self)
        self.panel.SetSizer(sizer)

        self.Show()

    def ctrl_F1_hotkey(self,event):
        self.confUpd()
        self.X, self.Y = pyagui.position()
        self.mousePositionText.SetValue(f"Mouse X: {self.X} Y: {self.Y}")
        self.ColorPickerButton.Label = f"Pick color at X {self.X}, Y {self.Y}"
        self.outputUpdate("Mouse (position) captured")

        self.gridSizer.Fit(self)
        self.gridSizer.Layout()

    def ctrl_F2_hotkey(self,event):
        self.confUpd()
        if self.X != None and self.Y != None:
                pyagui.moveTo(self.X, self.Y)
                if self.config.get("townSetting"):
                    for i in range(5):
                        pyagui.dragRel(-10,0,1)
                        time.sleep(0.2)
                        pyagui.dragRel(10,0,1)
                self.outputUpdate(f"Mouse moved to ({self.X}, {self.Y})")
        else:
            self.outputUpdate("No position captured")
            event.Skip()

        self.gridSizer.Fit(self)
        self.gridSizer.Layout()

    def ctrl_F3_hotkey(self,event):
        self.confUpd()
        pyagui.screenshot("./screenshot.png")
        self.chosenFile = "screenshot.png"
        self.XSize = Image.open(self.chosenFile).size[0]
        self.YSize = Image.open(self.chosenFile).size[1]
        self.scanButton.SetLabel(f"Scan {self.chosenFile}")
        self.ImageSelect.SetLabel(f"Chosen: {self.chosenFile}")
        self.outputUpdate("Screenshot taken")
    
    def on_window_checkbox_pressed(self, event):
        self.confUpd()
        if self.defaultWindowStyle == None: self.defaultWindowStyle = self.GetWindowStyle()
        if self.windowTypeCheckbox.IsChecked():
            self.windowTypeCheckbox.Label = "Window type: top"
            self.outputUpdate("Window type set to top")
            self.SetWindowStyle(wx.STAY_ON_TOP)
            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
        else:
            self.windowTypeCheckbox.Label = "Window type: normal"
            self.outputUpdate("Window type set to normal")
            self.SetWindowStyle(self.defaultWindowStyle)
            self.gridSizer.Fit(self)
            self.gridSizer.Layout()


    def on_F1_key_pressed(self, event):
        self.confUpd()
        if event.GetKeyCode() == wx.WXK_F1:
            (self.X, self.Y) = pyagui.position()
            self.mousePositionText.SetValue(f"Mouse X: {self.X} Y: {self.Y}")
            self.ColorPickerButton.Label = f"Pick color at X {self.X}, Y {self.Y}"
            self.outputUpdate(f"Mouse ({self.X}, {self.Y}) captured")

            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
        else:
            event.Skip()
    
    def on_F2_key_pressed(self, event):
        self.confUpd()
        if event.GetKeyCode() == wx.WXK_F2:
            if self.X != None and self.Y != None:
                pyagui.moveTo(self.X, self.Y)
                pyagui.moveRel(-10,0)
                time.sleep(0.2)
                pyagui.moveRel(10,0)
                self.outputUpdate(f"Mouse moved to ({self.X}, {self.Y})")
            else:
                self.outputUpdate("No position captured")
                event.Skip()
        else:
            event.Skip()
    
    def on_F3_key_pressed(self, event):
        self.confUpd()
        if event.GetKeyCode() == wx.WXK_F3:
            pyagui.screenshot("./screenshot.png")
            self.chosenFile = "screenshot.png"
            self.XSize = Image.open(self.chosenFile).size[0]
            self.YSize = Image.open(self.chosenFile).size[1]
            self.scanButton.SetLabel(f"Scan {self.chosenFile}")
            self.ImageSelect.SetLabel(f"Chosen: {self.chosenFile}")
            self.outputUpdate("Screenshot taken")
        else:
            event.Skip()
    
    def on_image_select_pressed(self,event):
        self.confUpd()
        with wx.FileDialog(self,"Open image file",wildcard="Image files (*.png; *.jpeg)|*.png;*.jpeg", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileBrowser:
            if fileBrowser.ShowModal() == wx.ID_CANCEL:
                self.outputUpdate("Cancelled file selection")
                return
            path = fileBrowser.GetPath()
            if os.path.isfile(path):
                self.chosenFile = path
                self.outputUpdate("Image chosen")
            self.ImageSelect.Label = f"Chosen: {os.path.basename(path)}"
            self.scanButton.SetLabel(f"Scan {os.path.basename(self.chosenFile)}")
            self.XSize = Image.open(self.chosenFile).size[0]
            self.YSize = Image.open(self.chosenFile).size[1]

            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
    
    def on_color_picker_pressed(self,event):
        self.confUpd()
        try: self.HSVroundingFactor = int(self.HSVround.GetValue())
        except: self.outputUpdate("Invalid rounding factor"); return
        if self.chosenFile != None: image = Image.open(self.chosenFile)
        else: self.outputUpdate("No file chosen"); return
        pixels = image.load()
        outList = []
        if self.X != None and self.Y != None:
            if image.size[0] >= self.X and image.size[1] >= self.Y:
                (r, g, *b) = pixels[self.X, self.Y]
                pix = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
                pix = list(pix)
                for i in range(len(pix)):
                    pix[i] = round(pix[i],self.HSVroundingFactor)
                pix = tuple(pix)
                outList.append(f"Pixel at X,Y: {self.X}, {self.Y}")
                outList.append(f"RGB(A): {pixels[self.X,self.Y]}")
                outList.append(f"HSV: {pix}")
                self.outputUpdate(outList)
            else:
                self.outputUpdate("Coordinates out of bounds"); return
        else:
            self.outputUpdate("Empty coordinates, use F1")
    
    def on_screenshot_button(self,event):
        self.confUpd()
        pyagui.screenshot("./screenshot.png")
        self.chosenFile = "./screenshot.png"
        self.outputUpdate("Screenshot taken")
        self.ImageSelect.Label = f"Chosen: {os.path.basename(self.chosenFile)}"
        self.scanButton.SetLabel(f"Scan {os.path.basename(self.chosenFile)}")
        self.XSize = Image.open(self.chosenFile).size[0]
        self.YSize = Image.open(self.chosenFile).size[1]
        
        self.gridSizer.Fit(self)
        self.gridSizer.Layout()
    
    def on_coords_entered(self,event):
        self.confUpd()
        pattern = re.findall(r"\d+", self.mousePositionText.GetValue())
        if pattern:
            if len(pattern) > 0: self.X = int(pattern[0]); self.outputUpdate("X value updated") 
            if len(pattern) > 1: self.Y = int(pattern[1]); self.outputUpdate("Y value updated")
            try: pyagui.moveTo(self.X, self.Y)
            except: self.mousePositionText.SetValue("Mouse movement exception"); self.outputUpdate("Mouse movement exception")
            self.ColorPickerButton.SetLabel(f"Pick color at X {self.X}, Y {self.Y}")
            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
        else:
            self.mousePositionText.SetValue("Invalid coordinate")
            self.outputUpdate("Invalid coordinate")
            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
    
    def on_scan(self,event):
        self.confUpd()
        if self.chosenFile == None: self.outputUpdate("No file chosen"); return
        try: self.HSVcolor = convToStructure(f"({self.HSV.GetValue()})")
        except: self.outputUpdate("Invalid color"); return
        try: self.HSVroundingFactor = int(self.HSVround.GetValue())
        except: self.outputUpdate("Invalid rounding factor"); return
        label = self.scanButton.GetLabel()
        self.scanButton.SetLabel("Scanning")
        #try: 
        self.outputUpdate(scanPixelsHSV(self.chosenFile, self.HSVcolor, self.XSize, self.YSize, self.HSVroundingFactor, self.isDecimal, self.config))
        if self.config.get("townSetting"):
            self.outputUpdate(scanPixelsHSV("./product.png", self.HSVcolor, self.XSize, self.YSize, self.HSVroundingFactor, self.isDecimal, self.config))
        #except Exception as e: self.outputUpdate("Error during scan"); print(e)
        #finally:
        self.scanButton.SetLabel(label)

        self.gridSizer.Fit(self)
        self.gridSizer.Layout()

    def on_HSV_entered(self,event):
        try: self.HSVcolor = convToStructure(f"({self.HSV.GetValue()})")
        except: self.outputUpdate("Invalid color")

    def on_decimal_toggle(self,event):
        if self.isDecimalCheckbox.IsChecked():
            self.isDecimal = True
        else: self.isDecimal = False

    def outputUpdate(self, output):
        self.confUpd()
        if isinstance(output, list):
            if self.config.get("showTime"):
                output[0] = time.strftime("%H:%M:%S: ") + output[0]
            output[0] = "\n" + output[0]
            for out in output:
                out += ";\n"
                self.outputList.append(str(out))
        else:
            if self.config.get("showTime"):
                output = time.strftime("%H:%M:%S: ") + output
            output += ";\n"
            self.outputList.append(str(output))
        while len(self.outputList) > 5:
            self.outputList.pop(0)
        self.output.Value = "Output:\n"
        for out in self.outputList:
            self.output.Value = self.output.Value + out
        
        self.gridSizer.Fit(self)
        self.gridSizer.Layout()

    def on_manual_press(self,event):
        textDisplayWindow(self,"Manual","https://raw.githubusercontent.com/stabbyfork/stuff/main/colorpicker/manual.txt", True, True)

    def on_save_pixel_press(self,event):
        self.confUpd()
        try: self.HSVroundingFactor = int(self.HSVround.GetValue())
        except: self.outputUpdate("Invalid rounding factor"); return
        if self.chosenFile != None: image = Image.open(self.chosenFile)
        else: self.outputUpdate("No file chosen"); return
        self.saveDataButton.SetLabel("Saving")
        pixelsSet = image.getdata()
        file = open("pixels.txt", "w")
        for pix in pixelsSet:
            (r, g, *b) = pix
            pix = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
            pix = list(pix)
            pix = [pix[0]*360,pix[1]*100,pix[2]*100]
            for i in range(len(pix)):
                pix[i] = round(pix[i],self.HSVroundingFactor - 2)
            pix = tuple(pix)
            file.write(str(pix) + "\n")

        file.close()
        image.close()
        self.saveDataButton.SetLabel("Save pixel data")
        self.outputUpdate(f"Saved pixel data to {os.path.abspath('./pixels.txt')}")
    
    def on_settings_press(self,event):
        textDisplayWindow(self,"Configuration","./config.toml", False, False)

    def confUpd(self):
        self.config = tomllib.loads(open("./config.toml","r").read())



class textDisplayWindow(wx.Frame):
    def __init__(self, parent=None, title="Window", path="./config.toml", isURL=False, isReadOnly=True, id=wx.ID_ANY):
        super().__init__(parent=parent, title=title, id=id)
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer()

        self.path = path
        
        if isReadOnly:
            self.fullDisplayText = wx.TextCtrl(self.panel, size=(self.Size[0],self.Size[1]), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH | wx.TE_AUTO_URL)
        else:
            self.fullDisplayText = wx.TextCtrl(self.panel, size=(self.Size[0],self.Size[1]), style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_AUTO_URL)
            self.saveButton = wx.Button(self.panel, label=f"Save to {os.path.basename(path)}")

            self.saveButton.Bind(wx.EVT_BUTTON, self.on_save)

        if isReadOnly:
            self.sizer.Add(self.fullDisplayText, 0, wx.SHAPED, 0)
        else:
            self.sizer.Add(self.fullDisplayText, 0, wx.TOP , 25)

        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        if isURL:
            self.fullDisplayText.SetValue(urllib.request.urlopen(path).read())
        else:
            self.fullDisplayText.SetValue(open(path).read())

        self.Show()

    def on_resize(self,event):
        self.sizer.Layout()
        self.fullDisplayText.SetSize(self.Size[0], self.Size[1])
        event.Skip()
    
    def on_save(self,event):
        self.saveButton.SetLabel("Saving")
        time.sleep(0.2)
        open(self.path, "w").write(self.fullDisplayText.GetValue())
        self.saveButton.SetLabel(f"Save to {os.path.basename(self.path)}")

    def on_close(self,event):
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = App()
    app.MainLoop()
# https://github.com/stabbyfork/stuff/tree/main/colorpicker