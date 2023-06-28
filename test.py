import os
import datetime
import random

class WordBook:
    def __init__(self, path:str, word_dict:dict = None):
        self.path = path
        self.word_dict = word_dict
        if word_dict != None:
            self.word_dict = word_dict
        else:
            self.word_dict = {}
            self.load_dict()

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
                print(lines[i])
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
            new_word = Word(raw="", name=name, meaning=new_meaning, more=more, last_visit_date=new_date_str, accuracy=0, visit_times=0)                
            self.word_dict[name] = new_word
            # write in the markdown file
            with open(self.path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines[-1] == "\n":
                    lines.pop()
                with open(self.path, 'w', encoding='utf-8') as file:
                    lines.append("| "+name+" | "+new_meaning+" | "+more+" | "+new_date_str+" | "+ "0"+" | "+"0"+" |\n")
                    file.writelines(lines)

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
            # os.system('cls')
            print(word.name)
            shuffle_meanings.append(word.meaning)
            shuffle_meanings = random.sample(shuffle_meanings, 4)
            answer = shuffle_meanings.index(word.meaning)+1

            print("1)", shuffle_meanings[0])            
            print("2)", shuffle_meanings[1])            
            print("3)", shuffle_meanings[2])
            print("4)", shuffle_meanings[3])
            print("5)", "不會")
            print("answer: ", answer)

            keyin = input()
            if keyin==str(answer):
                print("Correct!")
                # update the word
                word.update(1)
            else:
                print("Wrong🤦‍♂️")
                # update the word 
                word.update(0)
            self.word_dict[word.name] = word

            

                
                          




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
            normalized_dates = [(tmp_date-min_date)/date_range for tmp_date in dates]
            importance_arr = [normalized_dates[i] + (1-accuracies[i]) for i in range(len(words))]
        else: 
            print(accuracies[0])
            importance_arr = [(1-accuracies[i]) for i in range(len(words))]
        sorted_indexes = sorted(range(len(importance_arr)), key=lambda i: importance_arr[i], reverse=True)
        importnace_words = [words[i] for i in sorted_indexes]
        return importnace_words
        

    def get_shuffle_meanings(self, name, count):
        shuffle_meanings = [value.meaning for k, value in self.word_dict.items() if k != name]
        print("shuffle_meanings", shuffle_meanings)
        random_values = random.sample(shuffle_meanings, count)
        return random_values

    def store(self):
        lines = []        
        for word in self.word_dict.values():
            lines.append("| "+word.name+" | "+word.meaning+" | "+word.more+" | "+word.last_visit_date+" | "+ word.accuracy+" | "+word.visit_times+" |\n")
        with open(self.path, 'w', encoding='utf-8') as file:
            file.writelines(lines)


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
        self.meaning = arr[2]
        self.more = arr[3]
        date = arr[4].split(",")
        self.last_visit_date = datetime.date(eval(date[0]), eval(date[1]), eval(date[2]))
        self.accuracy = float(arr[5])
        self.visit_times = int(arr[6])
        print(self.name)
            
        
    
    def update(self, correctness:int):
        self.last_visit_date = datetime.datetime.now()
        right_num = self.accuracy*self.visit_times
        self.visit_times += 1
        self.accuracy = (right_num+correctness)/self.visit_times
   



if __name__ == "__main__":
    wordbook = WordBook(path = "words.md")
    wordbook.load_dict()
    tmp_key = input("Press:\n\
                    A: to add~\n\
                    R: to review~\n\
                    S: to save the dictionary now~\n\
                    Q: to quit~\n")
    while tmp_key != "Q":
        if tmp_key == "A":
            wordbook.add_word()
        if tmp_key == "R":
            wordbook.review()
        if tmp_key == "S":
            wordbook.store()
        tmp_key = input("Press:\nA: to add~\nR: to review~\nQ: to quit~\n")

