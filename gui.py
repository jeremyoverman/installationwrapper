import wx, re, threading, subprocess
import time

class Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, None, *args, **kwargs)

class TitleLabel(wx.StaticText):
    def __init__(self, parent, text):
        wx.StaticText.__init__(self, parent, label=text)
        font = wx.Font(18, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        self.SetFont(font)
        
class DoubleList(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.right_is_empty = True
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_title = wx.StaticText(self, label="Listbox1")
        self.left_listbox = wx.ListBox(self)
        self.left_sizer.Add(self.left_title, 0, wx.BOTTOM, 5)
        self.left_sizer.Add(self.left_listbox, 1, wx.EXPAND|wx.BOTH)
        
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_title = wx.StaticText(self, label="Listbox2")
        self.right_listbox = wx.ListBox(self)
        self.right_sizer.Add(self.right_title, 0, wx.BOTTOM, 5)
        self.right_sizer.Add(self.right_listbox, 1, wx.EXPAND|wx.BOTH)
        
        self.buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.move_right = wx.Button(self, label=">", size=(25,25))
        self.move_left = wx.Button(self, label="<", size=(25,25))
        
        self.buttons_sizer.Add((25,25), wx.EXPAND|wx.VERTICAL)
        self.buttons_sizer.Add(self.move_right, 0)
        self.buttons_sizer.Add(self.move_left, 0)
        self.buttons_sizer.Add((25,25), wx.EXPAND|wx.VERTICAL)
        
        self.main_sizer.Add(self.left_sizer, 1, wx.EXPAND|wx.BOTH)
        self.main_sizer.Add(self.buttons_sizer, 0, wx.EXPAND|wx.VERTICAL)
        self.main_sizer.Add(self.right_sizer, 1, wx.EXPAND|wx.BOTH)
        
        self.__init__bindings__()
        
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()
        
    def __init__bindings__(self):
        self.move_right.Bind(wx.EVT_BUTTON, lambda x: self.moveItem("right"))
        self.move_left.Bind(wx.EVT_BUTTON, lambda x: self.moveItem("left"))
        
    def setListboxTitles(self, left, right):
        self.left_title.SetLabel(left)
        self.right_title.SetLabel(right)
        
    def populateList(self, items):
        self.left_listbox.AppendItems(items)
        self.left_listbox.Select(0)
    
    def rightListCheck(self):
        if self.right_listbox.GetCount() == 0:
            self.right_is_empty = True
        else:
            self.right_is_empty = False
        
    def moveItem(self, direction):
        if direction == "right":
            src = self.left_listbox
            dst = self.right_listbox
        else:
            src = self.right_listbox
            dst = self.left_listbox
            
        item = src.GetSelection()
        
        if item >= 0:
            name = src.GetString(item)
            src.Delete(item)
            dst.Append(name)
            
            if item < src.GetCount():
                src.Select(item)
            else:
                src.Select(item - 1)
            dst.Select(dst.GetCount() - 1)
            
        self.rightListCheck()

class PackageChooserPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.current_action_label = wx.StaticText(self,
                                                  label="Select the installations to be run. Note that packages are installed "+
                                                        "in a pre-determined order so the order\nin which you add the packages to "+
                                                        "the list will not affect the order in which they are installed."
                                                  )
        
        self.chooser = DoubleList(self)
        self.chooser.setListboxTitles("Available software", "To be installed")
        
        self.main_sizer.Add(self.current_action_label, 0, wx.BOTTOM, 15)
        self.main_sizer.Add(self.chooser, 1, wx.EXPAND|wx.ALL)
        
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()
        
class NavButtonPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.back_button = wx.Button(self, label="Back")
        self.next_button = wx.Button(self, label="Next")
        self.cancel_button = wx.Button(self, label="Cancel")
        
        self.main_sizer.Add((0,0), 1, wx.EXPAND|wx.HORIZONTAL)
        self.main_sizer.Add(self.back_button, 0, wx.RIGHT, 15)
        self.main_sizer.Add(self.next_button, 0, wx.RIGHT, 15)
        self.main_sizer.Add(self.cancel_button, 0, wx.RIGHT, 15)
        
        self.__init__bindings__()
        
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()
        
    def __init__bindings__(self):
        self.cancel_button.Bind(wx.EVT_BUTTON, self.exitInstaller)
    
    def exitInstaller(self, e=None):
        gui.Close()
            
class InstallerPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.installing_label = wx.StaticText(self, label="Installing...")
        self.progress_bar = wx.Gauge(self)
        
        self.buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.details_button = wx.Button(self, label="Show Details")
        self.save_button = wx.Button(self, label="Save Log")
        self.buttons_sizer.Add(self.details_button)
        self.buttons_sizer.Add((15,0))
        self.buttons_sizer.Add(self.save_button)
        
        self.details_box = wx.ListBox(self)
        self.log_box = wx.ListBox(self)
        
        self.main_sizer.Add(self.installing_label, 0)
        self.main_sizer.Add(self.progress_bar, 0, wx.EXPAND|wx.HORIZONTAL|wx.BOTTOM, 15)
        self.main_sizer.Add(self.buttons_sizer, 0, wx.BOTTOM, 5)
        self.main_sizer.Add(self.details_box, 1, wx.EXPAND|wx.BOTH)
        self.main_sizer.Add(self.log_box, 1, wx.EXPAND|wx.BOTH)
        
        self.__init__bindings__()
        
        self.details_box.Hide()
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()
    
    def __init__bindings__(self):
        self.details_button.Bind(wx.EVT_BUTTON, lambda x: self.toggleLog())
        self.save_button.Bind(wx.EVT_BUTTON, lambda x: self.saveLog())
    
    def saveLog(self):
        current_time = time.asctime().replace(":", "-")
        file_types =  "All Files|*.*|"
        file_types += "Text File (.txt)|*.txt|"
        file_types += "Log File (.log)|*.log"
        file_dialog = wx.FileDialog(self, "Save Log File", "", current_time, file_types, wx.FD_SAVE)
        if file_dialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            savefile = file_dialog.GetPath()
            buff = ""
            for line in self.details_box.GetItems():
                buff += line + "\n"
            try:
                f = open(savefile, 'w')
                f.write(buff)
                f.close()
            except IOError, e:
                wx.MessageBox("Error saving the log file.\n\n%s" % e, "File Error", wx.ICON_ERROR)
                return 1
            subprocess.Popen('notepad "%s"' % (savefile))
        
    
    def toggleLog(self):
        if self.details_button.GetLabel() == "Show Details":
            self.log_box.Hide()
            self.details_box.Show()
            self.details_button.SetLabel("Hide Details")
            self.Layout()
        else:
            self.details_box.Hide()
            self.log_box.Show()
            self.details_button.SetLabel("Show Details")
            self.Layout()
    
    def runInstaller(self, packages):
        plist = []
        self.install_errors = False
        
        self.package_index = 0
        for package in package_list.list: 
            if package in packages:
                plist.append(package)
                
                
        self.progress_bar.SetRange(len(plist))
        
        for package in plist:
            self.package_index += 1
            name = package_list.package_properties[package]["name"]
            path = package_list.package_properties[package]["path"]
            path = path.replace("/", "\\")
            
            wx.CallAfter(self.installing_label.SetLabel, "Installing %s... (%d/%d)" % (name, self.package_index, len(plist)))
            self.log("Installing %s..." % name)
            
            if package_list.package_properties[package]["type"] == "bat":
                result = self.installBatch(path)
            elif package_list.package_properties[package]["type"] == "msi":
                result = self.installMSI(path)
            if result == 0:
                self.log("%s successfully installed." % name)
            else:
                self.log("%s installation failed. Returned error code %d." % (name, result))
                self.install_errors = True
            gui.nav_button_panel.cancel_button.SetLabel("Finish")
            
            wx.CallAfter(self.progress_bar.SetValue, self.package_index)
        
        if not self.install_errors:
            self.installing_label.SetLabel("All packages installed successfully.")
        else:
            self.installing_label.SetLabel("Some packages failed to install. See details for more information.")
    
    def installMSI(self, path):
        cmd = 'msiexec.exe /i "%s" /quiet /passive' % path
        if gui.menu_bar.msi_log_options:
            cmd += " /l%s msi.log" % gui.menu_bar.msi_log_options
            result = self.runProcess(cmd)
            if result > 0:
                return result
            else:
                f = open("msi.log", 'r')
                for line in f.readlines():
                    line = line.decode("windows-1252").encode("ascii", "ignore")
                    print line
                    self.log(line, detailed=True)
                f.close()
                return result
        else:
            return self.runProcess(cmd)
    
    def installBatch(self, path):
        cmd = 'cmd /C "%s"' % path
        return self.runProcess(cmd)

    def runProcess(self, cmd):
        print cmd
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=info)
        last_line = ""
        
        while True and gui.running:
            retcode = proc.poll()
            line = proc.stdout.readline().strip()
            if len(line) > 0:
                self.log(line, detailed=True)
            elif len(line) == 0 and len(last_line) > 0:
                self.log(line, detailed=True)
            if retcode is not None:
                return retcode
            last_line = line
        
    def log(self, line, detailed=False):
        if not detailed:
            wx.CallAfter(self.log_box.Append, line)
        wx.CallAfter(self.details_box.Append, line)
        detail_count = self.details_box.GetCount()
        log_count = self.log_box.GetCount()
        if detail_count != 0: detail_count -= 1
        if log_count != 0: log_count -= 1
        wx.CallAfter(self.details_box.SetFirstItem, detail_count)
        wx.CallAfter(self.log_box.SetFirstItem, log_count)

class MenuBar(wx.MenuBar):
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        
        self.msi_log_options = None
        
        #File Menu
        self.file_menu = wx.Menu()
        self.package_button = self.file_menu.Append(wx.ID_EXIT, '&Load Package List', 'Load a different package list')
        self.exit_button = self.file_menu.Append(wx.ID_EXIT, '&Exit', 'Exit The Installation')
        
        #Options Menu
        self.options_menu = wx.Menu()
        self.msi_logging = self.options_menu.Append(wx.ID_ANY, "&MSI Logging...", "Set MSI logging options") 
        
        #Menu
        self.Append(self.file_menu, "&File")
        self.Append(self.options_menu, "&Options")
        
        self.__init__bindings__()
        
    def __init__bindings__(self):
        self.Bind(wx.EVT_MENU, lambda x: self.msiOptionsDialog(), self.msi_logging)
        
    def msiOptionsDialog(self):
        msi_logging_desc = "i\tStatus messages\n" 
        msi_logging_desc += "w\tNonfatal warnings\n"
        msi_logging_desc += "e\tAll error messages\n"
        msi_logging_desc += "a\tStart up of actions\n"
        msi_logging_desc += "r\tAction-specific records\n"
        msi_logging_desc += "u\tUser requests\n"
        msi_logging_desc += "c\tInitial UI parameters\n"
        msi_logging_desc += "m\tOut-of-memory or fatal exit information\n"
        msi_logging_desc += "o\tOut-of-disk-space messages\n"
        msi_logging_desc += "p\tTerminal properties\n"
        msi_logging_desc += "v\tVerbose output\n"
        msi_logging_desc += "x\tExtra debugging information\n"
        msi_logging_desc += "*\tLog all information, except for v and x options\n"

        input_dialog = TextInputDialog(self,
                                       size=(350,350),
                                       title="MSI Logging Options",
                                       inputlabel="Logging Options",
                                       desclabel=msi_logging_desc)
        input_dialog.ShowModal()
        
        if input_dialog.getText():
            self.msi_log_options = input_dialog.getText()
        
class TextInputDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        inputlabel = kwargs.pop("inputlabel")
        desclabel = kwargs.pop("desclabel")
        
        self.saved = False
        
        wx.Dialog.__init__(self, *args, **kwargs)
        
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_label = wx.StaticText(self.panel, label=inputlabel)
        self.text_entry = wx.TextCtrl(self.panel)
        self.input_sizer.Add(self.input_label, 0, wx.RIGHT|wx.CENTER, 10)
        self.input_sizer.Add(self.text_entry, 1, wx.EXPAND|wx.HORIZONTAL)
        
        self.description_label = wx.StaticText(self.panel, label=desclabel)
        
        self.buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(self.panel, label="Save")
        self.buttons_sizer.Add((0,0), 1, wx.EXPAND|wx.HORIZONTAL)
        self.buttons_sizer.Add(self.save_button, 0)
        
        self.main_sizer.Add(self.input_sizer, 0, wx.EXPAND|wx.HORIZONTAL|wx.LEFT|wx.RIGHT|wx.TOP, 15)
        self.main_sizer.Add(self.description_label, 1, wx.EXPAND|wx.BOTH|wx.ALL, 15)
        self.main_sizer.Add(self.buttons_sizer, 0, wx.EXPAND|wx.HORIZONTAL|wx.ALL, 15)
        
        self.__init__bindings__()
        
        self.panel.SetSizerAndFit(self.main_sizer)
        self.panel.Layout()
    
    def __init__bindings__(self):
        self.save_button.Bind(wx.EVT_BUTTON, lambda x: self.save())
    
    def save(self):
        self.saved = True
        self.Destroy()
        
    def getText(self):
        if self.saved:
            return self.text_entry.GetValue()
        else:
            return None
         

class GUI(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        
        self.running = True
        self.current_screen = 0
        
        self.menu_bar = MenuBar()
        self.SetMenuBar(self.menu_bar)
        
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.title_label = TitleLabel(self.main_panel, self.GetTitle())
        
        self.package_chooser_panel = PackageChooserPanel(self.main_panel)
        self.installer_panel = InstallerPanel(self.main_panel)
        
        self.nav_button_panel = NavButtonPanel(self.main_panel)

        self.main_sizer.Add(self.title_label, 0, wx.LEFT|wx.TOP, 15)
        
        self.main_sizer.Add(self.package_chooser_panel, 1, wx.EXPAND|wx.BOTH|wx.ALL, 15)
        self.main_sizer.Add(self.installer_panel, 1, wx.EXPAND|wx.BOTH|wx.ALL, 15)
        
        self.main_sizer.Add(self.nav_button_panel, 0, wx.EXPAND|wx.HORIZONTAL|wx.BOTTOM, 15)
        
        self.nav_button_panel.back_button.Disable()
        self.nav_button_panel.next_button.Disable()
        
        self.main_panel.SetSizerAndFit(self.main_sizer)
        self.main_panel.Layout()
        
        self.screens = {0: [self.showPackageChooser, self.package_chooser_panel], 1: [self.showInstaller, self.installer_panel]}
        
        for screen in self.screens:
            self.screens[screen][1].Hide()
        self.screens[0][1].Show()
        
        self.__init__bindings__()
        
        self.Show()
    
    def __init__bindings__(self):
        dlistbox = self.package_chooser_panel.chooser
        dlistbox.move_right.Bind(wx.EVT_BUTTON, lambda x: self.handleListboxButtons("right"))
        dlistbox.move_left.Bind(wx.EVT_BUTTON, lambda x: self.handleListboxButtons("left"))
        
        self.nav_button_panel.next_button.Bind(wx.EVT_BUTTON, lambda x: self.nextScreen())
        self.Bind(wx.EVT_CLOSE, lambda x: self.onClose())
        
    def onClose(self):
        if self.current_screen == 1 and self.nav_button_panel.cancel_button.GetLabel() != "Finish":
            messagebox = wx.MessageBox("Are you sure you want to exit the installer?\n\n" +
                               "Note that if you are currently installing any packages, installation " + 
                               "may be abruptly ended resulting in an inconsitent state. It is not "+ 
                               "recommended to end the installer during package installation.",
                               "Exit the installer?",
                               wx.YES_NO|wx.ICON_QUESTION)
            if messagebox != wx.YES:
                return
        self.running = False
        self.Destroy()
        #exit(0)
        
    def nextScreen(self):
        print self.current_screen, len(self.screens)
        if self.current_screen == 0:
            self.screens[self.current_screen][1].Hide()
            self.current_screen += 1
            self.nav_button_panel.next_button.Disable()
        elif self.current_screen == 1:
            print "HELLO"
        self.screens[self.current_screen][0]()
        
    def showPackageChooser(self):
        pass

    def getPackagesToInstall(self):
        installer_names = self.package_chooser_panel.chooser.right_listbox.GetStrings()
        plist = package_list.package_properties
        packages = []
        for package in plist:
            if plist[package]["name"] in installer_names:
                packages.append(package)
        return packages

    def showInstaller(self):
        self.installer_panel.Show()
        self.main_panel.Layout()
        
        packages = self.getPackagesToInstall()
        t = threading.Thread(target=self.installer_panel.runInstaller, args=(packages,))
        t.setDaemon(True)
        t.start()
        
    def handleListboxButtons(self, button):
        self.package_chooser_panel.chooser.moveItem(button)
        if self.package_chooser_panel.chooser.right_is_empty:
            self.nav_button_panel.next_button.Disable()
        else:
            self.nav_button_panel.next_button.Enable()
    
    def populateAvailablePackages(self, packages):
        names = []
        for package in packages:
            name = packages[package]["name"]
            names.append(name)
        self.package_chooser_panel.chooser.populateList(sorted(names))

class PackageList:
    def __init__(self, packfile):
        self.package_properties = {}
        self.window_properties = {}
        self.list = []
        
        f = open(packfile, 'r')
        contents = f.read()
        sections = contents.split("[end]")
        for section in sections:
            self.parseSection(section)
    
    def parseSection(self, section):
        lines = section.split("\n")
        is_header = re.compile(r'\[[a-zA-Z0-9]+\]')
        is_options = re.compile(r'([a-z]+)=(.*)')
        
        current_section = None
        for line in lines:
            if line[0:1] == "#":
                continue
            line = line.strip().lstrip()
            if is_header.match(line):
                current_section = line[1:-1]
                self.package_properties[current_section] = {}
                self.list.append(current_section)
            elif is_options.match(line):
                key, value = is_options.match(line).groups()
                self.package_properties[current_section][key] = value
        
        if "windowparams" in self.package_properties:
            self.window_properties = self.package_properties.pop("windowparams")

if __name__ == "__main__":
    app = wx.App()
    
    package_list = PackageList("packages.list")
    window_params = package_list.window_properties
    gui = GUI(title=window_params["title"], size=(640,480))
    gui.populateAvailablePackages(package_list.package_properties)
    
    app.MainLoop()
    
    