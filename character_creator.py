logFile = open("log.txt","a")
import time
import datetime
logFile.write(f"Execution starting at {datetime.datetime.now()}:\n")

manualSelect = False

import os
import sys

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

try:
  import kivy
except ModuleNotFoundError:
  logFile.write("Kivy not found. Installing with Pip.\n")
  os.system("pip3 install kivy")
  import kivy
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import *
from kivy.graphics import Rectangle
from kivy.graphics import Canvas

import json
import urllib.request
import zipfile
import pypdf

SrcHeaderList = ["Ability-Scores", "Alignments", "Backgrounds", "Classes", "Conditions", "Damage-Types", "Equipment", "Feats", "Features", "Languages", "Magic-Items", "Magic-Schools", "Monsters", "Proficiencies", "Races", "Rule-Sections", "Rules", "Skills", "Spells", "Subclasses", "Subraces", "Traits", "Weapon-Properties"]
srcData = {}

if False in [os.path.isfile(f"./5e-database-3.3.3/src/{itemType}.json") for itemType in SrcHeaderList]: #Switched to if statement as the file not existing is the only possible issue
  logFile.write("Some database files were missing. Attempting to reinstall directory from \"https://github.com/5e-bits/5e-database/archive/refs/tags/v3.3.3.zip\". ")
  if not os.path.isfile("./5e-database-3.3.3.zip"):
    try:
      urllib.request.urlretrieve("https://github.com/5e-bits/5e-database/archive/refs/tags/v3.3.3.zip","5e-database-3.3.3.zip")
    except Exception as e:
      logFile.write(f"\n{str(e)} No source files can be found. Starting in manual select mode.\n ")
      manualSelect=True
  else:
    logFile.write("Zip file already exists, will use that instead of installing. ")
  logFile.write("Unzipping.\n")
  zipfile.ZipFile("./5e-database-3.3.3.zip","r").extractall()

for fileName in SrcHeaderList: #Copied loading here instead
  try:
    baseData = json.load(open(f"./5e-database-3.3.3/src/5e-SRD-{fileName}.json", "r"))
  except MemoryError:
    logFile.write("Out of memory. Quitting to not crash entire computer.\n")
    sys.exit()
  baseDataDict = {}
  for item in baseData:
    item["sourcebook"] = "phb"
    baseDataDict[item["index"]] = item
  srcData[fileName] = baseDataDict
del baseData, baseDataDict

#____________________________________________________________________________________________________________________________________________

def save(data = {}):
  pass

toolBarHeight = 30
pageSize = (2550,3300)
pageSize = (1000,500)

class CharacterCreator(MDApp):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
  def build(self):
    envWidget = BoxLayout(orientation = "vertical")
    envWidget.size_hint = 1,1
    with envWidget.canvas:
      Color(.7,.7,.7)
      Rectangle(pos=(0,0),size=(9999,9999))
    mainWindTB = ToolBar(toolBarButtons = {
  
  "File":{
    "New":{"TestButton":Button()},
    "Open":{"TestButton":Button()},
    "Save":Button(on_select = save),
    "Save As":Button()
  },"Edit":{
    "TestButton":Button()
  },"TestButton":Button()

})#Edit this to change button behaviors.
    envWidget.add_widget(mainWindTB)
    
    self.basePages = [Page(pageName = "Name + Stats"), Page(pageName = "Test"), SpellSheet()]
    self.Pages = GridLayout(cols = 1, spacing = 50, size_hint = (1, None))
    self.Pages.bind(minimum_height = self.Pages.setter( "height"))
    PagesScroll = ScrollView(bar_pos_y = "right", scroll_type = ["bars"], bar_width = 15, pos_hint = {"center_x":.5}, scroll_wheel_distance = 50)
    for page in self.basePages:
      self.Pages.add_widget(page)
    PagesScroll.add_widget(self.Pages)
    envWidget.add_widget(PagesScroll)
    
    return envWidget
  #def rebuildPages(self):
    self.Pages.clear_widgets()
    for page in self.basePages():
      self.Pages.add_widget(page)

class Page(BoxLayout):
  def __init__(self, pageName = None, **kwargs):
    super().__init__(**kwargs)
    self.size_hint = None, None
    self.size = pageSize
    self.add_widget(Button(size_hint = (1,1)))
    self.pageName = pageName

class SpellSheet(Page):
  def __init__(self, pageName = None, **kwargs):
    super().__init__(pageName, **kwargs)
    with self.canvas:
      Color(1.,1.,0)
      Line(rounded_rectangle=(0,0,self.width,self.height,20),width=50)
    self.clear_widgets()
  

class ToolBar(BoxLayout):
  def __init__(self, toolBarButtons={},**kwargs):
    self.toolBarButtons = toolBarButtons
    self.orientation = "horizontal"
    self.height = toolBarHeight
    self.size_hint_y = None
    self.pos_hint = {"y":1,"x":0}
    super().__init__(**kwargs)
    
    for btn in toolBarButtons.keys():
      match toolBarButtons[btn]:
        
        case dict():
          dropButton = Button(text = btn,height = toolBarHeight,size_hint_y = None, size_hint_x = None)
          buttonDrop = DropDown()
          self.add_widget(dropButton)
          for chldBtn in toolBarButtons[btn].keys():
            match toolBarButtons[btn][chldBtn]:
              
              case dict():
                horizButton = Button(text = chldBtn, height = toolBarHeight, size_hint_y = None, size_hint_x = None)
                horizDrop = DropDown()
                buttonDrop.add_widget(horizButton)
                for horizChldBtn in toolBarButtons[btn][chldBtn].keys():
                  toolBarButtons[btn][chldBtn][horizChldBtn].height = toolBarHeight; toolBarButtons[btn][chldBtn][horizChldBtn].size_hint_y = None
                  toolBarButtons[btn][chldBtn][horizChldBtn].text = horizChldBtn
                  horizDrop.add_widget(toolBarButtons[btn][chldBtn][horizChldBtn])
                horizButton.bind(on_release = horizDrop.open)
              
              case Button():
                toolBarButtons[btn][chldBtn].height = toolBarHeight; toolBarButtons[btn][chldBtn].size_hint_y = None
                toolBarButtons[btn][chldBtn].text = chldBtn
                buttonDrop.add_widget(toolBarButtons[btn][chldBtn])
          dropButton.bind(on_release = buttonDrop.open)
       
        case Button():
          toolBarButtons[btn].text = btn
          toolBarButtons[btn].size_hint_y = None; toolBarButtons[btn].height = toolBarHeight
          toolBarButtons[btn].size_hint_x = None
          self.add_widget(toolBarButtons[btn])

CharacterCreator().run()


#Use this code whenever accessing json data in case some of it goes missing or a file is deleted accidentally.
"""
try:
  the actual code
except KeyError as k:
  logFile.write(f"{k}. Key read failed so software shutting down.")
  sys.exit()
"""
