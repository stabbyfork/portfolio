import colorsys
from PIL import Image
import pyautogui as pyagui
from ast import literal_eval as convToStructure
import wx
import os
import re
import urllib.request

# thank you https://stackoverflow.com/questions/24852345/hsv-to-rgb-color-conversion!!
def HSVtoRGB(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

# input values here
#choice = input("Find a pixel by HSV, or find a pixel by location (enter 'color/location') \n")
#if "color" == str.lower(choice) or "location" == str.lower(choice):
   # choice == str.lower(choice)
   # print("valid task")
#else:
    #exit(f"invalid task '{choice}'")

#image path
imgPath = None
#imgPath = "colorguionly.png"
#xOrig = 811 #for colorguifull.png
xOrig = 0
#yOrig = 322 #for colorguifull.png
yOrig = 0
#xSize = 270 #for colorguifull.png
xSize = 1919
#ySize = 259 #for colorguifull.png

ySize = 1079
#pixel to be searched
pixel = [1076,659]
#HSV color
hsv = ()
#number of decimal places for HSV colors
hsvRoundingFactor = 2

#hsv = (0.09, 0.52, 0.51)

#inputs
#if hsv == ():
   # hsv = convToStructure(input("Enter HSV color:\n"))

#if pixel == [] and choice == "location":
    #pixel = convToStructure("[" + input("Input pixel x and y values separated by a comma.\n") + "]")

#if imgPath == None:
    #inp = input("Image path (enter 'screenshot' for screenshot)\n")
    #if inp != "screenshot":
        #imgPath = inp
    #else:
        #pyagui.screenshot("D:\VSCode\Python\colorpicker\screenshot.png")
        #print("screenshot taken")
        #imgPath = "D:\VSCode\Python\colorpicker\screenshot.png"




#scan pixels for HSV color
def scanPixelsHSV(imagePath, hsv, XSize,YSize, HSVrounding, isDecimal):
    outList = []
    image = Image.open(imagePath)
    pixels = image.load()
    if not isDecimal:
        (h,s,v) = hsv
        hsv = (round(h/360,HSVrounding),round(s/100,HSVrounding),round(v/100,HSVrounding))
    for x in range(XSize): # X
        for y in range(YSize): # Y
            (r, g, *b) = pixels[x,y]
            modPixel = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
            modPixel = list(modPixel)
            for i in range(len(modPixel)):
                modPixel[i] = round(modPixel[i],HSVrounding)
            modPixel = tuple(modPixel)
            if modPixel == hsv:
                outList.append("Found pixel")
                outList.append(f'X,Y: {[x,y]}')
                outList.append(f'RGB(A): {pixels[x,y]}')
                outList.append(f"HSV: {hsv}")
                pyagui.moveTo(x,y)
                return outList
    outList.append("Pixel not found")
    outList.append(f"HSV used: {hsv}")
    return outList



#update this
if 1 > 2: #str.lower(input("Update pixels.txt?\n")) == "y":
    image = Image.open(imgPath)
    pixels = image.load()
    pixelsSet = set(image.getdata())
    file = open("pixels.txt", "w")
    for pix in pixelsSet:
        (r, g, *b) = pix
        pix = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
        pix = list(pix)
        for i in range(len(pix)):
            pix[i] = round(pix[i],hsvRoundingFactor)
        pix = tuple(pix)
        file.write(str(pix)+"\n")
    file.close()
    image.close()
    xSize = image.size[0]
    ySize = image.size[1]

x = xOrig
y = yOrig






#update this
if 2 < 1:
    if len(pixel) > 0:
        if pixel[0] < xSize and pixel[1] < ySize:
            print(f"RGBA: {pixels[pixel[0], pixel[1]]}")
            (r, g, *b) = pixels[pixel[0], pixel[1]]
            #del(a)
            pix = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
            pix = list(pix)
            for i in range(len(pix)):
                pix[i] = round(pix[i],hsvRoundingFactor)
            pix = tuple(pix)
            print(f"HSV: {pix}")
            print(f"x,y: {pixel}")
        else:
            print(f"pixel out of bounds: {pixel}")
    else:
        print("pixel has not been entered")
#else:
    #scanPixelsHSV(x,y)
    #print("supposed to scan but commented")


#Application
class App(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Color Picker and Finder")

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

        self.panel = wx.Panel(self)
        

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.gridSizer = wx.FlexGridSizer(4,4,1,1)

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
        self.output = wx.TextCtrl(self.panel, value="Output:\n", style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.windowTypeCheckbox = wx.CheckBox(self.panel, label='Window type: normal')

        self.manualButton = wx.Button(self.panel, label="Manual")
        self.saveDataButton = wx.Button(self.panel, label="Save pixel data")


        self.windowTypeCheckbox.Bind(wx.EVT_CHECKBOX, self.on_window_checkbox_pressed)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_F1_key_pressed)
        self.ImageSelect.Bind(wx.EVT_BUTTON, self.on_image_select_pressed)
        self.ColorPickerButton.Bind(wx.EVT_BUTTON, self.on_color_picker_pressed)
        self.screenshotButton.Bind(wx.EVT_BUTTON, self.on_screenshot_button)
        self.mousePositionText.Bind(wx.EVT_TEXT_ENTER, self.on_coords_entered)
        self.scanButton.Bind(wx.EVT_BUTTON, self.on_scan)
        self.isDecimalCheckbox.Bind(wx.EVT_CHECKBOX, self.on_decimal_toggle)
        self.HSV.Bind(wx.EVT_TEXT_ENTER, self.on_HSV_entered)
        self.manualButton.Bind(wx.EVT_BUTTON, self.on_manual_press)
        self.saveDataButton.Bind(wx.EVT_BUTTON, self.on_save_pixel_press)

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
        ])
        
        sizer.Add(self.gridSizer)
        self.gridSizer.Layout()
        self.gridSizer.Fit(self)
        self.panel.SetSizer(sizer)

        self.Show()
    
    def on_window_checkbox_pressed(self, event):
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
        if event.GetKeyCode() == wx.WXK_F1:
            (self.X, self.Y) = pyagui.position()
            self.mousePositionText.SetValue(f"Mouse X: {self.X} Y: {self.Y}")
            self.ColorPickerButton.Label = f"Pick color at X {self.X}, Y {self.Y}"
            self.outputUpdate("Mouse (position) captured")

            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
        else:
            event.Skip()
    
    def on_image_select_pressed(self,event):
        with wx.FileDialog(self,"Open image file",wildcard="Image files (*.png; *.jpeg)|*.png;*.jpeg", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileBrowser:
            if fileBrowser.ShowModal() == wx.ID_CANCEL:
                self.outputUpdate("Cancelled file selection")
                return
            path = fileBrowser.GetPath()
            if os.path.isfile(path):
                self.chosenFile = path
            self.ImageSelect.Label = f"Chosen: {os.path.basename(path)}"
            self.scanButton.SetLabel(f"Scan {os.path.basename(self.chosenFile)}")
            self.XSize = Image.open(self.chosenFile).size[0]
            self.YSize = Image.open(self.chosenFile).size[1]

            self.gridSizer.Fit(self)
            self.gridSizer.Layout()
    
    def on_color_picker_pressed(self,event):
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
        if self.chosenFile == None: self.outputUpdate("No file chosen"); return
        try: self.HSVcolor = convToStructure(f"({self.HSV.GetValue()})")
        except: self.outputUpdate("Invalid color"); return
        try: self.HSVroundingFactor = int(self.HSVround.GetValue())
        except: self.outputUpdate("Invalid rounding factor"); return
        label = self.scanButton.GetLabel()
        self.scanButton.SetLabel("Scanning")
        try: self.outputUpdate(scanPixelsHSV(self.chosenFile, self.HSVcolor, self.XSize, self.YSize, self.HSVroundingFactor, self.isDecimal))
        except: self.outputUpdate("Error during scan")
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
        if isinstance(output, list):
            output[0] = "\n" + output[0]
            for out in output:
                self.outputList.append(str(out))
        else:
            self.outputList.append(str(output))
        while len(self.outputList) > 5:
            self.outputList.pop(0)
        self.output.Value = "Output:\n"
        for out in self.outputList:
            self.output.Value = self.output.Value + out + ";\n"
        
        self.gridSizer.Fit(self)
        self.gridSizer.Layout()

    def on_manual_press(self,event):
        textDisplayWindow(self,"Manual","https://raw.githubusercontent.com/stabbyfork/stuff/main/colorpicker/manual.txt", True)

    def on_save_pixel_press(self,event):
        try: self.HSVroundingFactor = int(self.HSVround.GetValue())
        except: self.outputUpdate("Invalid rounding factor"); return
        if self.chosenFile != None: image = Image.open(self.chosenFile)
        else: self.outputUpdate("No file chosen"); return
        pixelsSet = set(image.getdata())
        file = open("pixels.txt", "w")
        for pix in pixelsSet:
            (r, g, *b) = pix
            pix = (colorsys.rgb_to_hsv(r/256, g/256, b[0]/256))
            pix = list(pix)
            for i in range(len(pix)):
                pix[i] = round(pix[i],self.HSVroundingFactor)
            pix = tuple(pix)
            file.write(str(pix)+"\n")
        file.close()
        image.close()
        self.outputUpdate(f"Saved pixel data to {os.path.abspath('./pixels.txt')}")


class textDisplayWindow(wx.Frame):
    def __init__(self, parent, title, path, isURL):
        super().__init__(parent=parent, title=title)
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer()
        
        self.fullDisplayText = wx.TextCtrl(self.panel, size=(self.Size[0],self.Size[1]), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH | wx.TE_AUTO_URL)

        self.sizer.Add(self.fullDisplayText, 0, wx.SHAPED , 0)

        self.Bind(wx.EVT_SIZE, self.on_resize)

        if isURL:
            website = urllib.request.urlopen(path)
            self.fullDisplayText.SetValue(website.read())
            website.close()
        else:
            self.fullDisplayText.SetValue(open(path).read())

        self.Show()

    def on_resize(self,event):
        self.sizer.Layout()
        self.fullDisplayText.SetSize(self.Size[0], self.Size[1])
        event.Skip()

if __name__ == "__main__":
    app = wx.App()
    frame = App()
    app.MainLoop()
