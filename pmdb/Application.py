import tkinter as tk
import tkinter.ttk as ttk
import api
import config as cfg
import webbrowser
import filesave
from tkinter import filedialog
from globals import endl, sortoptions

class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master=master
        self.pack()

        #runtime settings vars
        self.lastsearch = ""
        self.searchindex = 0
        self.searchsettingsopen = False
        #ini settings vars
        self.initsettings()

        self.create_resultsbox()
        self.create_searchbar()
        self.create_menu()

    def initsettings(self, d=False):
        if (d):
            cfg.resetsettings()
            print("reset called")
        settings = cfg.loadsettings()
        self.database = tk.StringVar(self, settings["database"])
        self.maxresults = tk.IntVar(self, int(settings["maxresults"]))
        self.links = tk.IntVar(self, settings.getint("links"))
        self.authors = tk.IntVar(self, settings.getint("authors"))
        self.date = tk.IntVar(self, settings.getint("date"))
        self.source = tk.IntVar(self, settings.getint("source"))
        self.title = tk.IntVar(self, settings.getint("title"))
        self.journal = tk.IntVar(self, settings.getint("journal"))
        self.displayorder = list(settings["displayorder"].split(","))

    def create_menu(self):
        menubar = tk.Menu(self.master)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label="Change Displayed Info", command= self.opensearchsettings)
        settings.add_command(label="Change Order", command= self.openordersettings)

        save = tk.Menu(menubar, tearoff=0)
        #save.add_command(label="Save Results to Spreadsheet", command= lambda: filesave.saveas(self.lastsearch, self.resultbox.get(1.0, tk.END)))
        save.add_command(label="Save Results As...", command= lambda: filesave.saveas(filedialog.asksaveasfilename(initialdir = "/",title = "Save File",filetypes = (("csv files","*.csv"),("all files","*.*"))), self.resultbox.get(1.0, tk.END)))

        menubar.add_cascade(label="File", menu=save)
        menubar.add_cascade(label="Search Options", menu=settings)
        self.master.config(menu=menubar)

    def create_searchbar(self):
        tk.Label(self, text="Search").grid(row=1, column=1, sticky="e")
        self.searchEntry = tk.Entry(self)
        self.searchEntry.grid(row=1, column=2, sticky="w")
        self.searchEntry.bind("<Return>", lambda e: self.search())

        tk.Label(self, text="Database").grid(row=2, column=1, sticky="e")
        self.dbEntry = tk.OptionMenu(self, self.database, *api.getdblist())
        self.dbEntry.grid(row=2, column=2, sticky="w")

        tk.Label(self, text="Sort By").grid(row=2, column=3)
        self.sort = tk.StringVar(self)
        self.sort.set("Default")
        self.sortmenu = tk.OptionMenu(self, self.sort, *sortoptions)
        self.sortmenu.grid(row=2, column = 4, sticky="w")

        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def create_resultsbox(self):
        self.resultbox = tk.Text(self.master, background="#EFEFEF")
        self.resultbox.pack(fill=tk.BOTH, expand=1, pady=20, padx = 60)
        self.resultbox.config(state=tk.DISABLED)
        self.resultbox.tag_config("link", foreground="blue", underline=1)
        self.resultbox.tag_bind("link","<Button-1>", lambda e: webbrowser.open_new_tab(self.resultbox.get("@%d,%d" % (e.x, e.y)+"linestart+6chars", "@%d,%d" % (e.x, e.y)+"lineend")))
        self.resultbox.bind("<Motion>", self.linkevent)
        self.resultbox.config(cursor="arrow")

    def displayresults(self, results):
        self.resultbox.config(state=tk.NORMAL)
        self.resultbox.delete(1.0, "end")
        for id in results["uids"]:
            for dsp in self.displayorder:
                if (getattr(self, dsp).get()):
                    if (dsp == "links"):
                        try:
                            tempstr ="Link: https://www.ncbi.nlm.nih.gov/"+self.database.get()+"/"+id+endl
                        except:
                            tempstr = "Link: Error Generating Link"+endl
                        self.resultbox.insert(tk.INSERT, tempstr, "link")

                    elif (getattr(self, dsp).get()):
                        self.resultbox.insert(tk.INSERT, api.getresultline(results[id], dsp, self.database.get()))

            #end dsp in self.displayorder
            #insert break between results
            self.resultbox.insert(tk.INSERT, "-"*20+endl)
        #disable at end
        self.resultbox.config(state=tk.DISABLED)

    def linkevent(self, e):
        if ("link" in self.resultbox.tag_names("@%d,%d" % (e.x, e.y))):
            self.resultbox.config(cursor="hand2")
        else:
            self.resultbox.config(cursor="arrow")

    def search(self):
        try:
            WebEnv, Key, count = api.searchdb(self.searchEntry.get(), self.database.get().lower())
        except ValueError:
            print("Invalid Database")
            self.alert("'"+self.dbEntry.get()+"' is not recognized as a valid Entrez data base, please check spelling or try again later.")
            return None
        results = api.getsummary(WebEnv, Key, start=self.searchindex, count=self.maxresults.get())
        self.lastsearch = self.searchEntry.get()
        self.searchEntry.delete(0, 'end')

        self.displayresults(results)
        #return results

    def alert(self, msg):
        popup = tk.Tk()
        popup.wm_title("Error")
        tk.Label(popup, text=msg).pack(side="top", fill="x", pady=10)
        tk.Button(popup, text="Okay", command = popup.destroy).pack()
        popup.mainloop()

    def opensearchsettings(self):
        self.top = tk.Toplevel()

        for dsp in self.displayorder:
            if (dsp=="links"):
                tk.Checkbutton(self.top, text="Show Links", variable= self.links).pack()
            elif (dsp=="authors"):
                tk.Checkbutton(self.top, text="Show Authors", variable= self.authors).pack()
            elif (dsp=="date"):
                tk.Checkbutton(self.top, text="Show Date", variable= self.date).pack()
            elif (dsp=="source"):
                tk.Checkbutton(self.top, text="Show Source", variable= self.source).pack()
            elif (dsp=="title"):
                tk.Checkbutton(self.top, text="Show Title", variable= self.title).pack()
            elif (dsp=="journal"):
                tk.Checkbutton(self.top, text="Show Journal", variable= self.journal).pack()


        self.top.saveBtn = tk.Button(self.top, text="Save")
        self.top.resetBtn = tk.Button(self.top, text="Reset to Default")
        self.top.saveBtn.pack()
        self.top.resetBtn.pack()
        self.top.saveBtn.bind("<1>", lambda e: cfg.changesettings([("links",self.links.get()),("authors",self.authors.get()),("date",self.date.get()),("source",self.source.get()),("title",self.title.get()),("journal",self.journal.get())]))
        self.top.saveBtn.bind("<ButtonRelease-1>", lambda e: self.top.destroy())
        self.top.resetBtn.bind("<1>", lambda e: self.initsettings(d=True))
        self.top.resetBtn.bind("<ButtonRelease-1>", lambda e: self.top.destroy())

    def openordersettings(self):
        self.top = tk.Toplevel()
        self.top.comboboxes = []
        for dsp in self.displayorder:
            self.top.comboboxes.append(ttk.Combobox(self.top, values=self.displayorder, state="readonly")) #switch to tkoption menu
            self.top.comboboxes[-1].pack()
            self.top.comboboxes[-1].set(dsp)
        self.top.save = tk.Button(self.top, text="Save")
        self.top.cancel = tk.Button(self.top, text="Cancel")
        self.top.save.pack()
        self.top.cancel.pack()
        self.top.save.bind("<1>", lambda e: self.updateorder(self.top.comboboxes))
        self.top.save.bind("<ButtonRelease-1>", lambda e: self.top.destroy())
        self.top.cancel.bind("<ButtonRelease-1>", lambda e: self.top.destroy())

    def updateorder(self, comboboxes):
        self.displayorder = [self.displayorder[cb.current()] for cb in comboboxes]
