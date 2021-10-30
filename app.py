
# This code was designed by Kafalis Panagiotis on Oktober 2021.
# It is intended for academic use at the Dept. of Informatics and Telecommunication
# of University of Ioannina.

# This code was designed and compiled at Visual Studio Code
# It was designed for my dissertation with title "RESEARCH ACTIVITY MONITORING APPLICATION"


from tkinter import Grid, ttk, Tk, Toplevel , Label , Text , Button, \
    OptionMenu, Frame , Scrollbar, Entry, Listbox
import tkinter as tk
from tkinter.constants import  END, INSERT
from tkinter.filedialog import askopenfilename
import json , sqlite3, csv 
import numpy as np
import matplotlib.pyplot as plt
import clipboard
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from collections import Counter
import locale
from PIL import ImageTk, Image
import getpass


user = getpass.getuser()


#main window 
root = Tk()
root.title('Research Activity Application')
root.geometry("1855x960+30+20")
root.iconbitmap('icon.ico')
root.configure(bg="#505251")

#root.state('zoomed')

# width= root.winfo_screenwidth()               
# height= root.winfo_screenheight()               
# root.geometry("%dx%d"%(width, height))


Grid.columnconfigure(root, 0,weight=2)
Grid.columnconfigure(root,1,weight=2)
Grid.columnconfigure(root,2,weight=2)
Grid.columnconfigure(root,3,weight=2)
Grid.columnconfigure(root,4,weight=2)
Grid.rowconfigure(root,0,weight=2)
Grid.rowconfigure(root,1,weight=2)
Grid.rowconfigure(root,2,weight=2)


#database
connection = sqlite3.connect('jbase.db')
c = connection.cursor()

#authors
c.execute("""CREATE TABLE IF NOT EXISTS  person(
      id  text  PRIMARY KEY,
      pname text  
        
)""")


#papers
c.execute("""CREATE TABLE IF NOT EXISTS  papers(
      uidd  text  PRIMARY KEY,
      types text,
      title text,
      authors text,
      years integer,
      source text,
      cites integer 
      
)""")

c.execute("""CREATE TABLE IF NOT EXISTS person_paper(
    id integer PRIMARY KEY AUTOINCREMENT,  
    person_id text,  
    paper_id text,  
    UNIQUE (person_id, paper_id)
    FOREIGN KEY (person_id)
    REFERENCES person (id),
    FOREIGN KEY (paper_id)
    REFERENCES papers(uidd)    
)""")

connection.commit()

# ταξινομιση csv αρχειου
def sort_csv(data):
    locale.setlocale(locale.LC_ALL, 'el_GR.UTF-8')
    data.sort(key= lambda x: locale.strxfrm(x[0]))
    print(data)
    
    
    with open('optnames.csv','w',encoding="utf-8 -sig",newline='') as file:
        writer=csv.writer(file)
        for row in data:
            writer.writerow(row) 
            
    
#csv με ονοματα και id καθηγητών    
def csv_open(): 
    File = open('optnames.csv',encoding="utf-8 -sig")
    Reader = csv.reader(File,delimiter=',')
    Data = list(Reader)
    File.close()
    
    sort_csv(Data)
    
    list_of_entries = []
    for x in list(range(0,len(Data))):
     list_of_entries.append(Data[x][0]) 
    
    #print(list_of_entries)
    return Data,list_of_entries

#Data = csv_reader  |  list_of_entries = ονοματα καθηγητων στα ελληνικα 
Data, list_of_entries = csv_open()


    
#mono gia n gemisei i person s test  
def person_csv_to_db():
    for data in Data:
        c.execute("INSERT INTO person(id, pname) VALUES(:id, :pname)",
                {
                    'id' : data[2],
                    'pname' :str(data[1]),
                }        
            )
        connection.commit()
    # gia n do an leitourgei
    c.execute("SELECT * FROM person")
    records = c.fetchall()
    print(records)   
#person_csv_to_db()  

#!!!!!!!!!!!gia dokimes /diagrafi vasis   
def delete_base():
   # c.execute("DELETE FROM person")
    c.execute("DELETE FROM papers")
    c.execute("DELETE FROM person_paper")
      
#τεστ
def persons():
    c.execute("SELECT * FROM person")
    records = c.fetchall()
    print(records)
    
    

#στατιστικες λειτουργειες εφαρμογης    
functions=('Πλήθος δημοσιεύσεων ανα έτος από όλα τα μέλη του τμήματος μαζί (5ετία)', 
           'H-index και I10 κάθε καθηγητή','Αριθμός αναφορών ανά καθηγητή',
           'Αριθμός δημοσιεύσεων ανά καθηγητή', 'Αριθμός δημοσιεύσεων ανά καθηγητή ανά έτος (5ετία)',
           'Τύποι δημοσιεύσεων μελών του τμήματος (5ετία)s')


# επιστρεφει τον id του καθηγητη που επιλεχθηκε 
def return_key(*args):
    for row in Data:
        if clicked.get() == row[0]:
            id_key = row[2]
            print(id_key)
            return id_key


# fortosi json file -koumpi jsonfile- epistrefei diadromi arxeioy
def import_jsonfile():
    REQUIRED_FIELDS= {"uid", "type", "title", "authors", "year", "source", "cites"}
    id_key = return_key()
    flag=0
    if clicked.get() != "Επιλέξτε Καθηγητή":
        json_name = askopenfilename(initialdir="C:/Users/%s/Documents" % user,
                                filetypes =(("Json File", "*.json"), ("All Files", "*.*")),
                                title = "Choose a file."
                                )
        
        try:   
            with open(json_name ,'r',encoding="utf-8 -sig") as json_file:
                    jdata = json.load(json_file)
               
            # elegxos gia kena pedia sto arxeio json
            ids = c.execute("SELECT uidd FROM papers").fetchall()
            list_ids=[i[0] for i in ids]
            for paper in jdata:
                if REQUIRED_FIELDS.issubset(set(paper.keys())) : # elegxos gia kena pedia sto arxeio json
                    if paper['uid'] in list_ids : # an t ar8ro uparxei idi, enimerose t cites
                        c.execute("UPDATE papers SET cites = ? WHERE uidd= ? ",(paper['cites'],paper['uid']))
                        flag = 1
                        connection.commit()
                        print("enimerose: ", paper['title'])
                        
                        paper_ids =  c.execute("SELECT paper_id FROM person_paper WHERE person_id = ?",(id_key,)).fetchall()
                        list_paper_ids=[i[0] for i in paper_ids]
                        if paper['uid'] not in list_paper_ids: #an to ar8ro uparxei idi alla m  allo ka8igiti
                            c.execute("INSERT INTO person_paper(person_id, paper_id) VALUES(:person_id, :paper_id)",
                                    {
                                        'person_id' : str(id_key),
                                        'paper_id' : str(paper['uid']),
                                        }        
                                    )
                            connection.commit()
                            flag=0
                            print("pros8ese person_paper")
                        
                    else: #den yparxei t ar8ro 
                        c.execute("INSERT INTO papers(uidd, types, title, authors, years, source, cites) VALUES \
                                  (:uidd, :types, :title, :authors, :years, :source, :cites)",
                                {
                                    'uidd' : paper['uid'],
                                    'types' : paper['type'],
                                    'title' : paper['title'],
                                    'authors' : str(paper['authors']),
                                    'years' : int(paper['year']),
                                    'source' : paper['source'],
                                        'cites' : int(paper['cites'])
                                        }        
                                    )
                        connection.commit()
                        print("pros8ese paper")
                            
                        
                        c.execute("INSERT INTO person_paper(person_id, paper_id) VALUES(:person_id, :paper_id)",
                                {
                                    'person_id' : str(id_key),
                                    'paper_id' : str(paper['uid']),
                                    }        
                                )
                        connection.commit()
                        print("pros8ese person_paper")
                else:
                    print( "Eλλειπή στοιχεια")
                    continue
        except FileNotFoundError:
            tk.messagebox.showerror(title="ERROR", message="Δεν βρέθηκε αρχείο!!!")
    else:
        tk.messagebox.showerror(title="ERROR", message="Επιλέξτε καθηγητή!!!") 
    
    if flag ==1:
        tk.messagebox.showinfo(title="Ενημέρωση", message="Οι εγραφές ενημερώθηκαν!!") 
    
                
# provoli data apo base
def data_print():   
    if clicked.get() != "Επιλέξτε Καθηγητή":        
        for i in my_tree.get_children():     # καθαρισμος treeview
            my_tree.delete(i)
        
        c.execute("""SELECT * FROM papers
                    JOIN person_paper ON papers.uidd = person_paper.paper_id     
                    WHERE person_paper.person_id = ?
                    ORDER BY years""",(return_key(),))
        papers = c.fetchall()
                      
        for row in (papers):
            my_tree.insert("", tk.END, values=row)
        connection.commit()   
    else:
        tk.messagebox.showerror(title="ERROR", message="Επιλέξτε καθηγητή!!!")
 

#koympi leitourgeion
def results(*args):
    current_year = datetime.now().year
    function_number =functions.index(clicked2.get()) 
    zipped_data=list(zip(*Data))
    if function_number == 0:
        #πληθος αρθρων ανα ετος απο ολους τς καθηγητες μαζι
        c.execute("""SELECT years FROM papers
                 WHERE years >= ?
                 ORDER BY years""",(current_year-4,)) 

        paper_year = c.fetchall()
        
        papers_per_year=dict(Counter(elem[0] for elem in paper_year))
        #print(papers_per_year)
        
        pop1 = Toplevel(root)
        pop1.title("Πλήθος δημοσιεύσεων ανα έτος από όλα τα μέλη του τμήματος μαζί (5ετία)")
        pop1.geometry("970x550+400+300")
        
        text = Text(pop1, height =" 20", width = "35")
        for key in papers_per_year.keys():
            text.insert(tk.INSERT, str(key) + ": " + str(papers_per_year[key]) + '\n')
         
        text.grid(row=0, column=1, padx=10,pady=10)
        
        ok = Button(pop1, text="OK",height =" 2", width = "8" ,bg="#3bdb51", command=lambda: pop1.destroy())
        ok.grid(row=1, column=1, padx=10, pady=10)
    
        #matplotlib
        exp_vals = papers_per_year.values()
        exp_labels = papers_per_year.keys()
        figure1 = plt.figure()
        ax = figure1.subplots()
        ax.set_title('Πλήθος δημοσιεύσεων ανα έτος από όλα τα μέλη του τμήματος μαζί (5ετία)')
        ax.pie(exp_vals,labels=exp_labels, shadow=True,autopct='%1.1f%%')
        pie = FigureCanvasTkAgg(figure1, pop1)
        pie.get_tk_widget().grid(row=0 , column= 2)
 
    elif function_number ==1 :
        #h-index και το i-10
        authors_names=list()
        h_index_per_author=list()
        i10_per_author=list()
        for id in zipped_data[2]: # pairno cites gia ka8e ka8igiti xorista
            c.execute("""SELECT cites FROM papers
                        JOIN person_paper ON papers.uidd = person_paper.paper_id     
                        WHERE person_paper.person_id = ? """,(id,))
            citations= c.fetchall()
            for i in range(0,len(citations)):
                citations[i]=citations[i][0] # t kano aplo list apo tuple            
            h_index_per_author.append(h_index(citations))
            i10_per_author.append(i_10(citations))
        for i in range(0,len(zipped_data[0])):
            if h_index_per_author[i] is None: #entopizo k allazo oti einai None se 0 giati vgazei error sto 307
                h_index_per_author[i]=0
            authors_names.append(zipped_data[0][i])
            print(zipped_data[0][i] ," H-index:" ,h_index_per_author[i], ", I-10:", i10_per_author[i])
            
        pop = Toplevel(root)
        pop.title("H-index και I10 κάθε καθηγητή")
        pop.geometry("1750x850+100+100")
           
        text = Text(pop, height =" 40", width = "45")
        text.grid(row=0, column=1, padx=10,pady=10)
        
        for i, item in enumerate(zipped_data[0]):
            text.insert(tk.INSERT, zipped_data[0][i] + ":" + " H-index: " + str(h_index_per_author[i]) + " | I-10:" + str(i10_per_author[i]) +"\n"+"\n") 
                        
        ok = Button(pop, text="OK",height =" 2",width = "8" ,bg="#3bdb51", command=lambda: pop.destroy())
        ok.grid(row=1, column=1, padx=10, pady=10)  
        
        labels =authors_names
        data1 = h_index_per_author
        data2 = i10_per_author
        
        x = np.arange(len(labels))  # the label locations
        width = 0.35 # the width of the bars
        
        figure1, ax = plt.subplots(figsize=(15,7.5))

        rects1=ax.barh(x + 0.2+width/2, data1, width, label="H_index")
        rects2=ax.barh(x - 0.2+width/2, data2, width, label="I_10")
        
        ax.set_title('H-index και I10 κάθε καθηγητή')
        ax.set_yticks(x)
        ax.set_yticklabels(labels)
        ax.legend()
        
        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)
        
        plot = FigureCanvasTkAgg(figure1, pop)
        plot.get_tk_widget().grid(row=0 , column= 4, padx=5)
                 
    elif function_number ==2 :
        #αριθμος αναφορων ανα καθηγητη
        authors_names = list()
        cite=list()
        for i,id in enumerate(zipped_data[2]): # pairno cites gia ka8e ka8igiti xorista
            authors_names.append(zipped_data[0][i])
            c.execute("""SELECT cites FROM papers
                        JOIN person_paper ON papers.uidd = person_paper.paper_id     
                        WHERE person_paper.person_id = ? """,(id,))
            citations= c.fetchall()
            for y in range(0,len(citations)):
                citations[y]=citations[y][0] # t kano aplo list apo tuple
            cite.append(sum(citations)) 
            #print(authors_names[i] , ':', cite[i])  # na all3o to id sto onoma tou ka8igiti
            
        pop = Toplevel(root)
        pop.title("Aριθμός αναφορών ανά καθηγητή")
        pop.geometry("1750x800+100+100")
           
        text = Text(pop, height =" 40", width = "35")
        text.grid(row=0, column=1, padx=10,pady=10)
        
        for i, item in enumerate(cite):
            text.insert(tk.INSERT, authors_names[i] + ":" +" "+ str(cite[i]) + "\n"+"\n")  
                    
        ok = Button(pop, text="OK",height =" 2",width = "8" ,bg="#3bdb51", command=lambda: pop.destroy())
        ok.grid(row=1, column=1, padx=10, pady=10)
        
        exp_vals = cite
        exp_labels = authors_names
        
        figure1, ax = plt.subplots(figsize=(15,7))
        ax.set_title('Aριθμός αναφορών ανά καθηγητή')
        ax.barh(authors_names,exp_vals)
        
        for Y, X in enumerate(exp_vals):
            ax.annotate(X, xy=(X,Y), va='center')
   
        plot = FigureCanvasTkAgg(figure1, pop)
        plot.get_tk_widget().grid(row=0 , column= 4, padx=10)

    elif function_number ==3 :
        #Αριθμός δημοσιεύσεων ανά καθηγητή
        authors_names = list()
        count_papers = list()
        for i,id in enumerate(zipped_data[2]): 
            authors_names.append(zipped_data[0][i])
            c.execute("""SELECT COUNT(person_id) FROM person_paper     
                        WHERE person_id = ? """,(id,))
            count_papers.append(c.fetchone())
        for i in range(0,len(count_papers)):
            count_papers[i]=count_papers[i][0]
            #print(authors_names[i] ,":", count_papers[i])
            
        pop = Toplevel(root)
        pop.title("Αριθμός δημοσιεύσεων ανά καθηγητή")
        pop.geometry("1750x800+100+100")
           
        text = Text(pop, height =" 40", width = "35")
        text.grid(row=0, column=1, padx=10,pady=10)
        
        for i, item in enumerate(count_papers):
            text.insert(tk.INSERT, authors_names[i] + ":" + " " + str(count_papers[i]) + "\n"+"\n") 
                    
        ok = Button(pop, text="OK",height =" 2", width = "8" ,bg="#3bdb51", command=lambda: pop.destroy())
        ok.grid(row=1, column=1, padx=10, pady=10)
        
        exp_vals = count_papers
        exp_labels = authors_names
        
        figure1, ax = plt.subplots(figsize=(15,7))
        ax.set_title('Αριθμός δημοσιεύσεων ανά καθηγητή')
        ax.barh(authors_names,exp_vals)
        
        for Y, X in enumerate(exp_vals):
            ax.annotate(X, xy=(X,Y), va='center')
            
        plot = FigureCanvasTkAgg(figure1, pop)
        plot.get_tk_widget().grid(row=0 , column= 4, padx=10)
    
    elif function_number ==4 :
        #Αριθμός δημοσιεύσεων ανά καθηγητή ανά έτος (5ετία)
        authors_names = list()
        items_list = list()
        for i,id in enumerate(zipped_data[2]): 
            authors_names.append(zipped_data[0][i])
            c.execute("""SELECT years FROM papers
                        JOIN person_paper ON papers.uidd = person_paper.paper_id     
                        WHERE person_paper.person_id = ? AND years >= ? 
                        ORDER BY years""",(id,current_year-4))         
            years= c.fetchall()
            papers_per_year_per_author=dict(Counter(elem[0] for elem in years))
            items_list.append(papers_per_year_per_author)
            #print(authors_names[i] , items_list[i])
            
        pop = Toplevel(root)
        pop.title("Αριθμός δημοσιεύσεων ανά καθηγητή ανά έτος (5ετία)")
        pop.geometry("1900x1000+5+5")
           
        text = Text(pop, height =" 45", width = "30")
        text.grid(row=0, column=1, padx=10,pady=10)
        
        for i, item in enumerate(items_list):
            text.insert(tk.INSERT, authors_names[i] + ":" + "\n") 
            for key in item.keys():
                text.insert(tk.INSERT, "       "+ str(key) + " "+ str(item[key]) + "\n") 
                    
        ok = Button(pop, text="OK",height =" 2", width = "8" ,bg="#3bdb51", command=lambda: pop.destroy())
        ok.grid(row=1, column=1, padx=10, pady=10)
        
        bar_data=[len(authors_names)*[0] for x in range(5)]
         
        for i,year in enumerate(range(current_year-4, current_year+1)):
            for item in range(0,len(items_list)):
                if year in items_list[item]:
                    temp = items_list[item]      # ta keys einai integers k anagnorizontai os indexes st pinaka 
                    bar_data[i][item]= temp[year]      
        
        labels =authors_names
        data1 = bar_data[0]
        data2 = bar_data[1]
        data3 = bar_data[2]
        data4 = bar_data[3]
        data5 = bar_data[4]

        x = np.arange(len(labels))  # the label locations
        width = 0.12  # the width of the bars

        figure1, ax = plt.subplots(figsize=(18, 9))
       
        ax.barh(x + 1.1*width, data1, width, label=current_year-4)
        ax.barh(x + 1.1*width*2, data2, width, label=current_year-3)
        ax.barh(x + 1.1*width*3, data3, width, label=current_year-2)
        ax.barh(x + 1.1*width*4, data4, width, label=current_year-1)
        ax.barh(x + 1.1*width*5, data5, width, label=current_year)

        ax.set_title('Αριθμός δημοσιεύσεων ανά καθηγητή ανά έτος (5ετία)')
        ax.set_yticks(x+ 2.5*width+width/2)
        ax.set_yticklabels(labels)
        ax.legend()
        
        plot = FigureCanvasTkAgg(figure1, pop)
        plot.get_tk_widget().grid(row=0 , column= 4, padx=5)     
        
    elif function_number ==5 :
        #Τύποι δημοσιεύσεων μελών του τμήματος (5ετία)
        authors_names = list()
        items_list = list()
        
        c.execute("""SELECT types FROM papers
                   WHERE years >= ?""",(current_year-4,))
                   
        types= c.fetchall()
        
        for i in range(0,len(types)):
            types[i]=types[i][0] # t kano aplo list apo tuple  
        items_list.append(types)
        print(items_list)

        counts = Counter(items_list[0])
        print(counts)
        
        pop1 = Toplevel(root)
        pop1.title("Τύποι δημοσιεύσεων μελών του τμήματος (5ετία)")
        pop1.geometry("970x550+400+300")
        
        text = Text(pop1, height =" 20", width = "35")
        for key in counts.keys():
            text.insert(tk.INSERT, str(key) + ": " + str(counts[key]) + '\n')
         
        text.grid(row=0, column=1, padx=10,pady=10)
        
        ok = Button(pop1, text="OK",height =" 2", width = "8" ,bg="#3bdb51", command=lambda: pop1.destroy())
        ok.grid(row=1, column=1, padx=10, pady=10)
        
        exp_vals = counts.values()
        exp_labels = counts.keys()
        
        figure1 = plt.figure()
        ax = figure1.subplots()
        ax.set_title('Τύποι δημοσιεύσεων μελών του τμήματος (5ετία)')
        ax.pie(exp_vals,labels=exp_labels, shadow=True,autopct='%1.1f%%')
        pie = FigureCanvasTkAgg(figure1, pop1)
        pie.get_tk_widget().grid(row=0 , column= 2)
   
   

#Logo τμήματος         
img = ImageTk.PhotoImage(Image.open("photo_1.png"))
panel = Label(root, image = img)
panel.pack(fill=None, expand=False)  
panel.place(relx=.15, rely=.1, anchor="c")

#Πλαισιο κουμπιων
button_frame = Frame(root)
button_frame.configure(width = 205,height= 2, bg="#2f929c" )
button_frame.pack(fill=None, expand=False)
button_frame.place(relx=.63, rely=.1, anchor="c")

    

#λιστα καθηγητων 
clicked = tk.StringVar()
clicked.set("Επιλέξτε Καθηγητή")
drop = OptionMenu(button_frame, clicked , *list_of_entries, command= return_key)
drop.config(bg="WHITE", fg="BLACK")
drop.config(width = 35, height= 2)
drop["menu"].config(bg="WHITE")

#λιστα αποτελεσματων 
clicked2 = tk.StringVar()
clicked2.set("Αποτελέσματα")
drop2 = OptionMenu(button_frame, clicked2 , *functions, command=results)
drop2.config(bg="WHITE", fg="BLACK")
drop2.config(width = 35, height= 2)
drop2["menu"].config(bg="WHITE")

  

# παραθυρο προσθηκης νεου καθηγητη
def add_person_creation():
    pop = Toplevel(root)
    pop.title("Προσθήκη νέου καθηγητή")
    pop.geometry("650x150+400+300")
    
    pop_label = Label(pop, text="Όνομα με Ελληνικούς χαρακτήρες :",  font=("helvetica", 12))
    pop_label.grid(row=0, column=0, padx=10 ,pady=10)
    
    pop_label2 = Label(pop, text="Όνομα με Λατινικούς χαρακτήρες :",  font=("helvetica", 12))
    pop_label2.grid(row=1, column=0, padx=10,pady=10)
 
    pop_label3 = Label(pop, text="Κωδικός Google Scholar ID :",  font=("helvetica", 12))
    pop_label3.grid(row=2, column=0, padx=10,pady=10)
    
    elperson = Text(pop, height =" 1", width = "30" )
    elperson.grid(row=0, column=1, padx=10)

    enperson = Text(pop, height =" 1", width = "30" )
    enperson.grid(row=1, column=1, padx=10)

    scholar_id = Text(pop, height =" 1", width = "30" )
    scholar_id.grid(row=2, column=1, padx=10)

    ok = Button(pop, text="OK",height =" 3", width = "8",bg='#268c35', 
                command=lambda: add_person(elperson.get("1.0",tk.END), enperson.get("1.0",tk.END) , scholar_id.get("1.0",tk.END) , pop))
    ok.grid(row=1, column=4, padx=10)
    

#lambda προσθηκη νεου καθηγητη
def add_person(elperson, enperson, scholar_id, pop):    
    global Data, list_of_entries
    el = elperson.strip()
    en = enperson.strip()
    sid = scholar_id.strip()
       
    sid_list=list(zip(*Data))[2]
    
    if el != "" and en != "" and sid != "":
            if sid not in sid_list:
                try:  
                    print("uparxei t id")     
                    error=c.execute("INSERT INTO person(id, pname) VALUES(:id, :pname )", #  t error epistrefei t sql string i an uparxei error, t error
                            {
                                'pname' : str(en),
                                'id' : str(sid)
                                }        
                        )
                    connection.commit()
                    with open(r'optnames.csv', 'a', encoding="utf-8 -sig") as f:
                        f.write("{},{},{}\n".format(el, en, sid)) 
                    
                except: 
                    connection.rollback()
                    tk.messagebox.showerror(title="ERROR", message="Αποτυχία προσθήκης")
                    print(error)
            else:
                tk.messagebox.showerror(title="ERROR", message="Ο καθηγητής υπάρχει ήδη")
           
    else:
        tk.messagebox.showerror(title="ERROR", message="Κενά πεδία")
    
    Data, list_of_entries = csv_open() 
    
    menu = drop["menu"]
    menu.delete(0, "end")
    for string in list_of_entries:
        menu.add_command(label=string, 
                            command=lambda value=string: clicked.set(value))     
          
    pop.destroy()
 
 
#παραθυρο διαγραφή καθηγητη      
def delete_person_creation():
    pop = Toplevel(root)
    pop.title("Διαγραφή καθηγητή")
    pop.geometry("400x450+250+170")   
    global mylist
    mylist = Listbox(pop, height =" 20", width = "35", selectmode = "multiple")
    mylist.grid(row=0, column=0, padx=20,pady=20)
    for item in list_of_entries:
        mylist.insert(END,item)
        
    dbutton = Button(pop, text="Διαγραφή",height =" 3", width = "10",bg="#d13636",fg='white',
                     command=lambda: delete_person(mylist.curselection() , pop))
    dbutton.grid(row=0, column=1, padx=10)
  
    
#lambda διαγραφη καθηγητη    
def delete_person(indices_to_delete, pop):
    global Data, list_of_entries
    ids_to_delete =[]
    names_to_delete=[]
        
    try:
        connection.commit()     
        for row in enumerate(Data):
            if row[0] in indices_to_delete:
                ids_to_delete.append(row[1][2])
                names_to_delete.append(row[1][0])   
        
        print(ids_to_delete)        
        sqlquery1 =c.execute("""SELECT papers.uidd FROM papers
                            JOIN person_paper ON papers.uidd = person_paper.paper_id 
                            WHERE person_paper.person_id IN (""" + ", ".join(["?"] * len(ids_to_delete)) + ")",ids_to_delete).fetchall()
        
        for i in range(0,len(sqlquery1)):
                sqlquery1[i]=sqlquery1[i][0]       
        print(sqlquery1,"sql1") 
                        
        sqlquery2 =c.execute("""SELECT person_paper.paper_id FROM person_paper 
                            WHERE person_paper.paper_id  IN ("""+ ", ".join(["?"] * len(sqlquery1))+ 
                            ") AND person_paper.person_id NOT IN ("+ ", ".join(["?"] * len(ids_to_delete))+ ")",sqlquery1+ids_to_delete).fetchall()
        
        for i in range(0,len(sqlquery2)):
                sqlquery2[i]=sqlquery2[i][0]  
        print(sqlquery2,"sql2") # elegxos gia keno sqlquery output
        
        paper_set  = set(sqlquery1)           
        person_paper_set = set(sqlquery2)  # ta kano set gia n afero t duplicates
        
        not_duplicates = list(paper_set-person_paper_set)

        c.execute("""DELETE FROM papers 
                  WHERE  papers.uidd IN (""" + ", ".join(["?"] * len(not_duplicates)) + ")",not_duplicates)             
                
        c.execute("""DELETE FROM person_paper
                WHERE person_id IN (""" + ", ".join(["?"] * len(ids_to_delete)) + ")",ids_to_delete)
                
        c.execute("""DELETE FROM person
                WHERE id IN (""" + ", ".join(["?"] * len(ids_to_delete)) + ")",ids_to_delete)
        
        with open('optnames.csv','w',encoding="utf-8 -sig",newline='') as file:
           writer=csv.writer(file)
           for row in enumerate(Data):
               if row[0] not in indices_to_delete: 
                   writer.writerow(row[1])   
                   
        connection.commit()
         
        for x in names_to_delete:
            list_of_entries.remove(x)
        menu = drop["menu"]
        menu.delete(0, "end")
        for string in list_of_entries:
            menu.add_command(label=string, 
                            command=lambda value=string: clicked.set(value))
    
    except:
        connection.rollback()
        tk.messagebox.showerror(title="ERROR", message="Αποτυχία Διαγραφής")      
        
    connection.commit()
    Data, list_of_entries = csv_open()        
    pop.destroy()
   
# συναρτησεις για κουμπι αντιγραφης στ συναρτηση scholar_info    
def el_copy():
    for x in range(0,len(Data)):
    	    if Data[x][0] == clicked.get():
                text = Data[x]
    clipboard.copy(text[0])

def en_copy():
    for x in range(0,len(Data)):
    	    if Data[x][0] == clicked.get():
                text = Data[x]
    clipboard.copy(text[1])
    
def id_copy():
    for x in range(0,len(Data)):
    	    if Data[x][0] == clicked.get():
                text = Data[x]
    clipboard.copy(text[2])


#ονομα κ id καθηγητη    
def scholar_info():
    
    if clicked.get() != "Επιλέξτε Καθηγητή":
        pop = Toplevel(root)
        pop.title("Στοιχεία Google scholar")
        pop.geometry("640x140+400+300")
    
        for x in range(0,len(Data)):
    	    if Data[x][0] == clicked.get():
                row = Data[x]
         
        #print(row[0] + row[1] + row[2])
        text = Text(pop, height =" 2", width = "65")
        text.insert(tk.INSERT, row[0] +" | "+ row[1] +" | "+ row[2]) 
        text.grid(row=0, column=1, padx=10,pady=10)

        el = Button(pop, text="Ελληνικά",height =" 2", width = "8" , bg='#d8dbd7', command=el_copy)
        el.grid(row=1, column=1, sticky=tk.W ,padx=10, pady=10)
        
        en = Button(pop, text="Λατινικά",height =" 2", width = "8" , bg='#d8dbd7', command=en_copy)
        en.grid(row=1, column=1, padx=10, pady=10)
        
        id = Button(pop, text="Scholar ID",height =" 2", width = "8" , bg='#d8dbd7', command=id_copy)
        id.grid(row=1, column=1, sticky=tk.E , padx=10, pady=10)
        
        ok = Button(pop, text="OK",height =" 3", width = "7",bg='#268c35', command=lambda: pop.destroy())
        ok.grid(row=0,rowspan= 10, column=2,  padx=10, pady=10)
    else:
        tk.messagebox.showerror(title="ERROR", message="Επιλέξτε καθηγητή!!!")



def h_index(citations: list[int]) -> int:
    citations.sort(reverse = True)
    for indx , citation in enumerate(citations):
        if indx + 1 >= citation:
            return citation
        

def i_10(citations: list[int]):   
    citations.sort(reverse = True)
    count=0
    for indx  in citations:
        if indx >= 10:
            count= count + 1
    return count
                    
#συναρτηση χρησης διπλου κλικ στο μενουν των αρθρων                    
def on_double_click(event):
    item = my_tree.selection() 
    values= my_tree.item(my_tree.selection())['values']
    
    pop = Toplevel(root)
    pop.title("Επεξεργασία δεδομένων")
    pop.geometry("770x440+400+100")
    
    #Labels
    id = Label(pop, text="ID" )
    type = Label(pop, text="Type")  
    title = Label(pop, text="Title")
    author = Label(pop, text="Authors")
    year = Label(pop, text="Year")
    source = Label(pop, text="Source")
    cites = Label(pop, text="Cites")

    id.grid(row=0, column=0, pady=5)
    type.grid(row=2, column=0, pady=5)
    title.grid(row=4, column=0, pady=5)
    author.grid(row=6, column=0, pady=5)
    year.grid(row=8, column=0, pady=5)
    source.grid(row=10, column=0, pady=5)
    cites.grid(row=12, column=0, pady=5)


    #Entry boxes  
    id_box = Entry(pop,width=120)
    type_box = Entry(pop, width=120)
    title_box = Entry(pop, width=120)
    authors_box = Entry(pop, width=120)
    year_box = Entry(pop, width=120)
    source_box = Entry(pop, width=120)
    cites_box = Entry(pop, width=120 )
    
    id_box.insert(tk.INSERT,values[0])
    type_box.insert(tk.INSERT,values[1])
    title_box.insert(tk.INSERT,values[2])
    authors_box.insert(tk.INSERT,values[3])
    year_box.insert(tk.INSERT,values[4])
    source_box.insert(tk.INSERT,values[5])
    cites_box.insert(tk.INSERT,values[6])
    
    id_box.grid(row=1, column=0, padx=20)
    type_box.grid(row=3, column=0)
    title_box.grid(row=5, column=0)
    authors_box.grid(row=7, column=0)
    year_box.grid(row=9, column=0)
    source_box.grid(row=11, column=0)
    cites_box.grid(row=13, column=0)
    
    
    update_button = Button(pop, text="Update",  font="Helvetica", bg='#268c35', height =" 2", width = "10",
                           command=lambda :update_record(values[0],id_box.get(), type_box.get(), title_box.get(), 
                                                         authors_box.get(), year_box.get(), 
                                                         source_box.get(), cites_box.get(), pop))
    
    update_button.grid(row=14,sticky="W", padx=150,pady= 15)
    
    delete_button = Button(pop, text="Delete",  font="Helvetica", bg="#d13636",fg='white', height =" 2", width = "10",
                           command=lambda :delete_record(values[0],pop))

    delete_button.grid(row=14, sticky="E",padx=150, pady= 15)
    
    ok = Button(pop, text="OK",font="Helvetica",fg='blue',  height =" 2", width = "10", bg='#d8dbd7', command=lambda: pop.destroy())
    ok.grid(row=14,  padx=150, pady= 15)
    
                                                         
    return item
    
# on_double_click update
def update_record(old_id, id_box, type_box, title_box, authors_box, year_box,source_box, cites_box,pop):    
    c.execute("""UPDATE papers SET
              uidd = :uidd,
              types = :types,
              title = :title,
              authors = :authors,
              years = :years,
              source = :source,
              cites = :cites
              WHERE uidd= :old_id """,
              {
                'old_id' : old_id,
                'uidd' : id_box,
                'types' : type_box,
                'title' : title_box,
                'authors' : str(authors_box),
                'years' : int(year_box),
                'source' : source_box,
                'cites' : int(cites_box)
                })
                      
    c.execute("""UPDATE person_paper SET paper_id = ? WHERE paper_id= ?""",  
            (id_box, old_id,))
    connection.commit()       
        
    data_print()      
    pop.destroy()
  
# on_double_click  delete       
def delete_record(id,pop):
    c.execute("""DELETE FROM papers
              WHERE papers.uidd = ? """,(id,))
    
    c.execute("""DELETE FROM person_paper
              WHERE person_paper.paper_id = ?
              AND person_paper.person_id = ? """,(id, return_key()) )
    
    x=c.execute("""SELECT person_paper.paper_id FROM person_paper
              WHERE person_paper.person_id = "YB4p5_8AAAAJ" """).fetchall()
    
    connection.commit()       
        
    print(x)
    data_print()      
    pop.destroy()
    
    
#καθαρισμος treeview
def clear_data():
    for i in my_tree.get_children():
        my_tree.delete(i)
    

#hover buttons
def on_enter(e):
    e.widget['background'] = '#32667d'
    e.widget['foreground'] = 'white'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'
    e.widget['foreground'] = 'black'

#Δημιουργια κουμπιων
    
# κουμπι εμφανισης αρθρων
data_print_button = Button(button_frame, text="Εμφάνιση Δημοσιεύσεων Καθηγητή", font=("Helvetica", 16), command=data_print)

# κουμπι εισαγωγης δεδομενων
import_jsonfile_button = Button(button_frame, text="Προσθήκη αρχείου JSON", width=20 , font=("Helvetica", 16), command=import_jsonfile)

# κουμπι καθαρισμου πινακα
clear_text_button = Button(button_frame, text="Καθαρισμός", font=("Helvetica", 16),  command=clear_data)

# κουμπι εισαγωγης καθηγητη
add_person_button = Button(button_frame, text="Προσθηκη νεου καθηγητη", width=28 , font=("Helvetica", 16), command= add_person_creation)

# κουμπι διαγραφης καθηγητη
del_person_button = Button(button_frame, text="Διαγραφη Καθηγητή",width=20 , font=("Helvetica", 16), command=delete_person_creation)

# κουμπι πληροφοριων καθηγητη
scholar_info_button = Button(button_frame, text="Scholar Info", font=("Helvetica", 16), command=scholar_info)

# κουμπι εξοδου εφαρμογης
quit_button = Button(button_frame, text=" Έξοδος", font=("Helvetica", 24), bg="#d13636", command= root.quit)


#Treeview
style = ttk.Style()

style.theme_use('default')

# Treeview Colors
style.configure("Treeview",
	background="#D3D3D3",
	foreground="black",
	fieldbackground="#D3D3D3")

# Change Selected Color
style.map('Treeview',
	background=[('selected', "#32667d")])

# create tree frame
tree_frame = Frame(root, width = 900, height = 970)

# Create Vertical Scrollbar
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set,height = 36, selectmode="extended")
my_tree.pack()

# Configure Scrollbars
tree_scroll.config(command=my_tree.yview)
#hor_scroll.config(command=my_tree.xview)

my_tree['columns'] = ("ID", "TYPE", "TITLE", "AUTHORS", "YEAR", "SOURCE", "CITES")

# Format Our Columns
my_tree.column("#0", width=0, stretch=tk.NO)
my_tree.column("ID", anchor=tk.W, width=170)
my_tree.column("TYPE", anchor=tk.CENTER, width=140)
my_tree.column("TITLE", anchor=tk.W, width=760)
my_tree.column("AUTHORS", anchor=tk.W, width=400)
my_tree.column("YEAR", anchor=tk.CENTER, width=40)
my_tree.column("SOURCE", anchor=tk.W, width=220)
my_tree.column("CITES", anchor=tk.CENTER, width=40)

# Create Headings
my_tree.heading("#0", text="", anchor=tk.W)
my_tree.heading("ID", text="ID", anchor=tk.CENTER)
my_tree.heading("TYPE", text="TYPE", anchor=tk.CENTER)
my_tree.heading("TITLE", text="TITLE", anchor=tk.CENTER)
my_tree.heading("AUTHORS", text="AUTHORS", anchor=tk.CENTER)
my_tree.heading("YEAR", text="YEAR", anchor=tk.CENTER)
my_tree.heading("SOURCE", text="SOURCE", anchor=tk.CENTER)
my_tree.heading("CITES", text="CITES", anchor=tk.CENTER)

my_tree.bind("<Double-1>",on_double_click)


#grid widgets
drop.grid(row=0, column=0, padx=20,pady=20) #lista ka8igiton  
drop2.grid(row=0, column=2, padx=20,pady=20) #lista apotelesmaton 
import_jsonfile_button.grid(row=1, column=0) # json file
data_print_button.grid(row=0, column=1 ) # emfanisi
clear_text_button.grid(row=0, column=3,padx=15) #ka8arismo
add_person_button.grid(row=1, column=1,padx=15, sticky=tk.W) # pros8iki neoy
del_person_button.grid(row=1, column=2,padx=15) # diagrafi
scholar_info_button.grid(row=1, column=3,padx=15, pady=10 ) # info
quit_button.grid(columnspan=3, rowspan=2, row=0, column=4 , padx=15) # exodos
tree_frame.grid(row=3, rowspan=4,columnspan=5, pady=15) # tree frame


#hover
drop.bind("<Enter>", on_enter)
drop.bind("<Leave>", on_leave)

drop2.bind("<Enter>", on_enter)
drop2.bind("<Leave>", on_leave)

import_jsonfile_button.bind("<Enter>", on_enter)
import_jsonfile_button.bind("<Leave>", on_leave)

data_print_button.bind("<Enter>", on_enter)
data_print_button.bind("<Leave>", on_leave)

clear_text_button.bind("<Enter>", on_enter)
clear_text_button.bind("<Leave>", on_leave)

scholar_info_button.bind("<Enter>", on_enter)
scholar_info_button.bind("<Leave>", on_leave)

add_person_button.bind("<Enter>", on_enter)
add_person_button.bind("<Leave>", on_leave)

del_person_button.bind("<Enter>", on_enter)
del_person_button.bind("<Leave>", on_leave)





root.mainloop()