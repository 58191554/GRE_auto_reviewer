import os
import datetime
import random

class HistoryBook:
    def __init__(self, path = "history.md"):
        self.path = path
        self.today = None
        self.load_today()
    
    def load_today(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            today_raw = lines[-1]
            if(today_raw == "\n"):
                lines.pop()
                today_raw = lines[-1]
        self.today = DateData(today_raw)
        print(self.today.date, self.today.new_num, self.today.review_num)
        if(self.today.date != datetime.datetime.now().date()):
            self.today.date = datetime.datetime.now().date()
            self.today.new_num = 0
            self.today.review_num = 0

            with open(self.path, "w", encoding='utf-8') as file_overwrite:
                new_date_str = str(self.today.date.year)+","+str(self.today.date.month)+","+str(self.today.date.day)
                lines.append("|" + new_date_str + "|"+str(self.today.new_num)+"|"+str(self.today.review_num)+"|")
                file_overwrite.writelines(lines)

    def store_today(self):
        
        with open(self.path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            with open(self.path, "w", encoding='utf-8') as file_overwrite:
                new_date_str = str(self.today.date.year)+","+str(self.today.date.month)+","+str(self.today.date.day)
                lines[-1] = "|" + new_date_str + "|"+str(self.today.new_num)+"|"+str(self.today.review_num)+"|"
                file_overwrite.writelines(lines)

class DateData:
    def __init__(self, raw:str):
        data = raw.split("|")
        date_str = data[1].strip()
        self.new_num = int(data[2].strip())
        self.review_num = int(data[3].strip())
        date_arr = date_str.split(",")
        self.date = datetime.date(year = int(date_arr[0]), month = int(date_arr[1]), day = int(date_arr[2]))
        print("fuck",self.date)

class WordBook:
    def __init__(self, path:str, history:HistoryBook, word_dict:dict = None):
        self.path = path
        self.word_dict = word_dict
        if word_dict != None:
            self.word_dict = word_dict
        else:
            self.word_dict = {}
            self.load_dict()
        self.history = history

    '''
    Load the markdown file from the give path
    '''
    def load_dict(self):
        # empty the dict first
        self.word_dict = {}
        with open(self.path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if len(lines) == 0:
                print("the file is empty")
                return

            if len(lines) < 3:
                print("the file table is empty")
                return
            
            for i in range(2, len(lines)):
                if lines[i] == "\n":
                    break
                word = Word(lines[i])
                self.word_dict[word.name] = word

    def add_word(self):
        name = input("input the name of the word:")
        if name == "q":
            print("~QUIT~")
            return
        if name in self.word_dict:
            print("the word exist")
        else:
            new_meaning = input("input the meaning of the word:")
            more = input("input more information:")
            new_date = datetime.datetime.now()
            new_date_str = str(new_date.year)+","+str(new_date.month)+","+str(new_date.day)
            new_word = Word(raw="", name=name, meaning=new_meaning, more=more, last_visit_date=new_date, accuracy=0, visit_times=0)                
            self.word_dict[name] = new_word
            # write in the markdown file
            with open(self.path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines[-1] == "\n":
                    lines.pop()
                with open(self.path, 'w', encoding='utf-8') as file:
                    lines.append("| "+name+" | "+new_meaning+" | "+more+" | "+new_date_str+" | "+ "0"+" | "+"0"+" |\n")
                    file.writelines(lines)
        
        self.history.today.new_num+=1
        self.history.store_today()

    '''
    review by the importance
    '''
    def review(self):
        self.load_dict()
        # calculate the importance
        review_ls =  self.get_review_ls()
        input("start review~~~")
        for word in review_ls:
            shuffle_meanings = self.get_shuffle_meanings(word.name, count=3)
            os.system('cls')
            print(word.name)
            shuffle_meanings.append(word.meaning)
            shuffle_meanings = random.sample(shuffle_meanings, 4)
            answer = shuffle_meanings.index(word.meaning)+1

            print("1)", shuffle_meanings[0])            
            print("2)", shuffle_meanings[1])            
            print("3)", shuffle_meanings[2])
            print("4)", shuffle_meanings[3])
            print("5)", "不會")
            # print("answer: ", answer)

            keyin = input()
            if keyin == "Q":
                again = input("Exit? [y/n]")
                if again == "y":
                    self.store()
                    self.history.store_today()
                    break
            if keyin==str(answer):
                print("Correct!")
                # update the word
                word.update(1)
            else:
                print("Wrong🤦‍♂️")
                print("More Information:", word.more)
                # update the word 
                word.update(0)
            print("More Info: ", word.more)
            self.word_dict[word.name] = word
            input("Enter to continue~")
            self.history.today.review_num += 1


    '''
    Get get_review_ls by importance formular
    Importance formular: normalized date value + (1-accuracy)
    '''
    def get_review_ls(self):
        dates = []
        words = []
        accuracies = []
        min_date = datetime.date(2099, 6, 28)
        max_date = datetime.date(2023, 6, 28)
        for key, value in self.word_dict.items():
            tmp_date = value.last_visit_date
            if min_date>tmp_date:
                min_date = tmp_date
            if max_date<tmp_date:
                max_date = tmp_date
            words.append(value)
            dates.append(tmp_date)
            accuracies.append(value.accuracy)

        # normalize dates
        date_range = max_date-min_date
        if date_range != max_date-max_date:
            normalized_dates = [(max_date - tmp_date)/date_range for tmp_date in dates]
            importance_arr = [normalized_dates[i] + (1-accuracies[i]) for i in range(len(words))]
        else: 
            print("fuck")
            importance_arr = [(1-accuracies[i]) for i in range(len(words))]
        sorted_indexes = sorted(range(len(importance_arr)), key=lambda i: importance_arr[i], reverse=True)
        importnace_words = [words[i] for i in sorted_indexes]
        return importnace_words
        
    '''
    Generate selections in a question
    '''    

    def get_shuffle_meanings(self, name, count):
        shuffle_meanings = [value.meaning for k, value in self.word_dict.items() if k != name]
        print("shuffle_meanings", shuffle_meanings)
        random_values = random.sample(shuffle_meanings, count)
        return random_values

    '''
    Store the wordbook image to a markdown file
    '''
    def store(self, new_path = None):
        lines = ["| Word      | Meaning       | More | last_visit_date | accuracy | visit_times |\n| --------- | ------------- | ---- | --------------- | -------- | ----------- |\n"]        
        for word in self.word_dict.values():
            date_str = str(word.last_visit_date.year)+","+str(word.last_visit_date.month)+","+str(word.last_visit_date.day)
            lines.append("| "+word.name+" | "+word.meaning+" | "+word.more+" | "+date_str+" | "+ str(word.accuracy)+" | "+str(word.visit_times)+" |\n")

        if new_path != None:
            with open(new_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
        else:
            with open(self.path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

    '''
    Reset the history of words
    '''
    def reset(self):
        for word in self.word_dict.values():
            word.last_visit_date = datetime.datetime.now()
            word.accuracy = 0
            word.visit_times = 0
        self.store()
    


class Word:
    def __init__(self, raw:str, name:str = None, meaning:str = None, more:str = None, last_visit_date:datetime.date = None, accuracy:float = None, visit_times:int = None):
        self.name = name
        self.meaning = meaning
        self.more = more
        self.last_visit_date = last_visit_date
        self.accuracy = accuracy
        self.visit_times = visit_times
        self.importance = None
        if self.meaning == None:
            self.load_word(raw)

    '''
    Load the word with given line
    '''
    def load_word(self, raw:str):
        arr = raw.split("|")
        self.name = arr[1].strip()
        self.meaning = arr[2].strip()
        self.more = arr[3].strip()
        date = arr[4].split(",")
        self.last_visit_date = datetime.date(eval(date[0]), eval(date[1]), eval(date[2]))
        self.accuracy = float(arr[5])
        self.visit_times = int(arr[6])            
        
    
    def update(self, correctness:int):
        self.last_visit_date = datetime.datetime.now()
        right_num = self.accuracy*self.visit_times
        self.visit_times += 1
        self.accuracy = (right_num+correctness)/self.visit_times
   

BULLETIN  = "\
    Press:\n\
    A: to add~🙌\n\
    R: to review~😎\n\
    S: to save the dictionary now~👌\n\
    Q: to quit~😅\n\
    rst: to reset the wordbook~😈\n\
    "       

if __name__ == "__main__":
    historybook = HistoryBook()
    wordbook = WordBook(path = "words.md", history=historybook)
    wordbook.load_dict()
    os.system('cls')
    tmp_key = input(BULLETIN)
    while tmp_key != "Q":
        if tmp_key == "A":
            wordbook.add_word()
        if tmp_key == "R":
            wordbook.review()
        if tmp_key == "S":
            new_path = input("New path (enter o to overwrite on original):")
            if new_path == "o":
                wordbook.store()
    #         else:
                wordbook.store(new_path)
        if tmp_key == "rst":
            auth = input("Input 'I want to reset'")
            if auth == "I want to reset":
                wordbook.reset()
        os.system("cls")
        tmp_key = input(BULLETIN)  
    wordbook.store()                                                                                              
