from os import walk, system, unlink, listdir, makedirs
from os.path import join, getsize, abspath, basename, dirname, isfile, isdir, exists
import shutil
from typing import Tuple
import customtkinter
from customtkinter import filedialog
from datetime import datetime
import sys
        
class TitleFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.appTitle = customtkinter.CTkLabel(self, text="DUPLICATE FILES FINDER", font=customtkinter.CTkFont(weight="bold", size=20))
        self.appTitle.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

class DirFrame(customtkinter.CTkFrame):
    dirPath = ""

    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)  

        self.browseButton = customtkinter.CTkButton(self, text="Chọn thư mục", width=100, command=self.browseDir)
        self.browseButton.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.dirOutput = customtkinter.CTkEntry(self, width=400, height=28, state="disabled")
        self.dirOutput.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="ew")

    def browseDir(self):
        self.dirOutput.configure(state="normal")
        DirFrame.dirPath = filedialog.askdirectory()
        if self.dirOutput.get():
            self.dirOutput.delete(0, customtkinter.END)
        self.dirOutput.insert(0, f"{DirFrame.dirPath}")
        self.dirOutput.configure(state="disabled")

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.font = customtkinter.CTkFont(family="Inter")

        self.dump_dir = "./dumps"
        self.dupIndexList = [" (1)", " (2)", " (3)", " (4)", " (5)", " (6)", " (7)", " (8)", " (9)", " (10)"]
        self.ogFileNames = []
        self.duplicatesDirRaw = []
        self.duplicatesDir = []
        self.execLog = [] 
        self.dupCount = 0
        self.confirmation = customtkinter.CTk() 

        self.consoleLog = customtkinter.CTkTextbox(self, width=400, wrap="none", font=customtkinter.CTkFont(family="Consolas"))
        self.consoleLog.grid(row=0, column=0, padx=20, pady=20, columnspan=2, sticky="ew")
        self.consoleLog.insert(customtkinter.END, "*Console Log:\n" + "--------------------------------------------\n")
        self.consoleLog.configure(state="disabled")
        
        self.moveToDumpButton = customtkinter.CTkButton(self, text="Chuyển vào Dumps", command=self.moveToDump)
        self.moveToDumpButton.grid(row=0, column=2, padx=20, pady=20, sticky="n")
        
        self.undoButton = customtkinter.CTkButton(self, text="Hoàn tác", command=self.undoDump)
        self.undoButton.grid(row=0, column=2, padx=20, pady=60, sticky="n")

        self.openDumpButton = customtkinter.CTkButton(self, text="Mở file Dumps", command=self.openDump)
        self.openDumpButton.grid(row=0, column=2, padx=20, pady=100, sticky="n")

        self.clearDumpButton = customtkinter.CTkButton(self, text="Xóa dữ liệu Dumps", fg_color="#990000", hover_color="#660000", command=self.clearDumpWindow)
        self.clearDumpButton.grid(row=0, column=2, padx=20, pady=(140,0), sticky="n")
        
        self.submitDirButton = customtkinter.CTkButton(self, text= "Tìm kiếm", font=self.font, fg_color="#4CBB17", hover_color="#228B22", command=self.findDuplicates)
        self.submitDirButton.grid(row=1, column=0, padx=20, pady=(0, 20), columnspan=3, sticky="ew")
    
    def openDump(self):
        self.consoleLog.configure(state="normal")
        system(f"explorer {abspath(self.dump_dir)}")
        self.consoleLog.insert(customtkinter.END, f"Đang mở thư mục dumps tại '{abspath(self.dump_dir)}'...\n")
        self.consoleLog.configure(state="disabled")

    def moveToDump(self):
        self.consoleLog.configure(state="normal")
        if not exists(self.dump_dir):
            self.consoleLog.insert(customtkinter.END, f"Không tồn tại file dumps, đang tạo tại '{abspath(self.dump_dir)}'...\n")
            makedirs(self.dump_dir)
            self.consoleLog.insert(customtkinter.END, f"Đã tạo file dumps tại '{abspath(self.dump_dir)}'...\n")
        for dup in self.duplicatesDir:
            shutil.move(dup, self.dump_dir)
            self.consoleLog.insert(customtkinter.END, f"- Đã di chuyển file {dup} sang dump: {abspath(self.dump_dir)}\n")
        moveTime = datetime.now()
        formattedTime = moveTime.strftime("%Y-%m-%d %H-%M-%S")
        txtLogPath = f'{self.dump_dir}/{basename(DirFrame.dirPath)}-{formattedTime}.txt'
        with open(txtLogPath, 'w') as f:
            f.write("Duplicate Files Paths:\n")
            for path in self.duplicatesDir:
                f.write(f"{path}\n")
        self.consoleLog.insert(customtkinter.END, f"Di chuyển hoàn tất! Đã tạo log file '{basename(txtLogPath)}' tại '{dirname(abspath(txtLogPath))}'\n")
        self.consoleLog.configure(state="disabled")

    def clearDump(self):
        self.consoleLog.configure(state="normal")
        self.confirmation.destroy()
        for filename in listdir(self.dump_dir):
            file_path = join(self.dump_dir, filename)
            try:
                if isfile(file_path):
                    unlink(file_path)
                elif isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                self.consoleLog.insert(customtkinter.END, f"Không thể xóa {file_path}. Lỗi: {e}")
        self.consoleLog.insert(customtkinter.END, f"Đã xóa dữ liệu file Dumps.")             
        self.consoleLog.configure(state="disabled") 

    def clearDumpWindow(self):
        self.confirmation.title("Xác nhận")
        self.confirmation.geometry("400x150")
        self.confirmation.grid_columnconfigure((0, 1), weight=1)
        label = customtkinter.CTkLabel(self.confirmation, text="Bạn có chắc muốn xóa dữ liệu Dumps không?\n(*Lưu ý: Không thể hoàn tác!)")
        label.grid(row=0, column=0, padx=20, pady=20, columnspan=2, sticky="ew")

        confirmButton = customtkinter.CTkButton(self.confirmation, text="Xóa", command=self.clearDump)
        confirmButton.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        cancelButton = customtkinter.CTkButton(self.confirmation, text="Hủy Bỏ", fg_color="#990000", hover_color="#660000", text_color="#FFFFFF", command=self.confirmation.destroy)
        cancelButton.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

        self.confirmation.mainloop()

    def undoDump(self):
        self.consoleLog.configure(state="normal")
        dumpfiles = [join(dirpath,f) for (dirpath, dirnames, filenames) in walk(self.dump_dir) for f in filenames]
        for dupPath in self.duplicatesDir:
            for dumpfile in dumpfiles:
                if basename(dumpfile) in dupPath:
                    shutil.move(dumpfile, dirname(dupPath))
                    self.consoleLog.insert(customtkinter.END, f"- Đã hoàn tác file {basename(dumpfile)} về {dirname(dupPath)}\n")
        self.consoleLog.insert(customtkinter.END, "Đã hoàn tác!\n")
        self.consoleLog.configure(state="disabled")

    def findDuplicates(self):
        self.consoleLog.configure(state="normal")
        self.dupCount = 0
        self.consoleLog.insert(customtkinter.END, f"Đang tìm kiếm trong {DirFrame.dirPath}...\n")
        onlyfiles = [join(dirpath,f) for (dirpath, dirnames, filenames) in walk(DirFrame.dirPath) for f in filenames]
        for filePath in onlyfiles:
            for index in self.dupIndexList:
                if filePath.__contains__(index):
                    self.duplicatesDirRaw.append(filePath)
                    self.ogFileNames.append(filePath.replace(index, ''))
        for filePath in onlyfiles:            
            for ogFile in set(self.ogFileNames):
                if basename(ogFile) in filePath:
                    for dup in self.duplicatesDirRaw:
                        if getsize(dup) == getsize(filePath):
                            self.consoleLog.insert(customtkinter.END, f"- Tìm thấy file lặp ở địa chỉ '{dup}' giống file ở địa chỉ '{filePath}' \n")
                            self.dupCount += 1
                            self.duplicatesDir.append(dup)
        if self.dupCount > 0:
            self.consoleLog.insert(customtkinter.END, f"Đã tìm thấy {self.dupCount} file trùng lặp.\n")
            self.consoleLog.insert(customtkinter.END, "Hãy nhấn vào nút 'Chuyển vào Dump' để chuyển các file lặp và xử lý sau.\n")
        else:
            self.consoleLog.insert(customtkinter.END, f"Không tìm thấy file trùng lặp!\n")
        self.duplicatesDirRaw.clear()
        self.consoleLog.configure(state="disabled")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("DupFinder")
        self.geometry("800x500")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        self.titleFrame = TitleFrame(self)
        self.titleFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=3)

        self.dirFrame = DirFrame(self)
        self.dirFrame.grid(row=1, column=0, padx=20, pady=0, columnspan=4, sticky="nwes")
        
        self.mainFrame = MainFrame(self)
        self.mainFrame.grid(row=2, column=0, padx=20, pady=20, columnspan=4, sticky="nwes")

def onClosing():
    sys.exit()

app = App()
app.protocol("WM_DELETE_WINDOW", onClosing)
app.mainloop()