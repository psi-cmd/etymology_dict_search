#!python.exe
'''
search for the source of word(s) ( Chinese and English planned to be mutually searched. )
search(word) : one word searching, and will recursively search according to the sources of words.
search_in() : for consecutive and interactive searching, welcome to directly paste columns from excel.

output.txt is generated for your search history, \
    "l" for list history this time, 
    "r" to remove last search,
    "rm" to choose which to move,
    "s" to save.

    well, it's useful only when you want to memorize what you search.

Directly hit enter will quit, automatically save the history.

This is version for search use.

by psi-cmd 2019.8
'''
import codecs, re
import os
import sys

os.chdir("C:\\Users\\longbang-cmd\\cmd_line_tools\\bin")
doc = './ciyuan_dict.txt'

outputstrs = []
output = './output.txt'

class Dictionary(object):
    def __init__(self, doc):
        self.doc = doc
    def __enter__(self):
        with codecs.open(self.doc, 'r', 'utf-8') as f:
            t = eval(f.read())
            self.dict = t if t else {}
            self.r_dict = {b: a for a, (b, c) in self.dict.items()}
        with codecs.open(self.doc + '_unsolved', 'r', 'utf-8') as f:
            t = eval(f.read())
            self.unsolved = t if t else []
        return self
    def __exit__(self, type, value, trace):
        with codecs.open(self.doc, 'w', 'utf-8') as f:
            f.write(str(self.dict))
        with codecs.open(self.doc + '_unsolved', 'w', 'utf-8') as f:
            f.write(str(self.unsolved))



def search(string, resist_repeat, split='\n'):
    for word in string.split(split):
        if word:
            try:
                a, b = ciyuan.dict[word.strip()]
                print('\n'+word+' '+a+'\n'+b+'\n')
                resist_repeat.append(word)
                x = re.findall('来自([a-z\s]*),', b)
                if x and x[0].strip() not in resist_repeat:
                    search(x[0].strip(), resist_repeat)
                y = re.findall('词源同([a-z\s]*)', b)
                if y and y[0].strip() not in resist_repeat:
                    search(y[0].strip(), resist_repeat)
            except KeyError:
                print(word+'?')
                vague_search(ciyuan, word)
                
def search_in(reverse=None, split='\n'): # main search func
    dict = ciyuan.r_dict if reverse else ciyuan.dict
    print(len(dict))
    resist_repeat = []
    global outputstrs
    while True:
        resist_repeat.clear()
        try:
            string = input('word(s):')
        except EOFError:
            exit()
        if string == '':
            break
        elif string == 'r':
            try:
                outputstrs.pop()
                print("Done.")
            except IndexError:
                pass
            continue
        elif string == 'c':
            with codecs.open(output, "r", encoding="utf-8") as f:
                setText(f.read())
            continue
        elif string == 's':
            with codecs.open(output, "a", encoding="utf-8") as f:
                f.write("".join(set(outputstrs)))
                outputstrs.clear()
            continue
        elif string == 'rm' or string == 'l':
            for i in range(len(outputstrs)):
                print(i+1, ' ', outputstrs[i])
            num = input("delete which? ")
            if string == 'rm':
                try:
                    print("line ", end='')
                    for i in num.split(' '):
                        del outputstrs[int(i)-1]
                        print(i+' ', end='')
                except (ValueError, IndexError):
                    print("... value/index error",end='')
                print('')
            continue
        elif string[:2] == '\V' and not '\n' in string:
            vague_search(ciyuan, string[2:], cut=False)
            break
        for word in string.split(split):
            word = word.strip()
            try:
                if not reverse:
                    a, b = dict[word]
                    print('\n'+word+' '+a+'\n'+b+'\n')
                    if word not in resist_repeat:
                        outputstrs.append(word + "\t" + a + "\n" + b + "\n\n")
                    resist_repeat.append(word)
                    x = re.findall('来自([a-z\s]*),', b)
                    if x and x[0].strip() not in resist_repeat:
                        print('<**************')
                        search(x[0].strip(), resist_repeat)
                        print('**************>')
                    y = re.findall('词源同([a-z\s]+)', b)
                    if y and y[0].strip() not in resist_repeat:
                        print('<**************')
                        search(y[0].strip(), resist_repeat)
                        print('**************>')
            except KeyError:
                print(word+'?')
                if not reverse:
                    vague_search(ciyuan, word)
                
        
def vague_search(diction, word, cut=True):   # a primitive fuzzy search, try to omit the perfix and suffix.
    def show(f):
        a, b = diction.dict[key]
        print('\t'+key+' '+a+'\n\t'+b+'\n')
        if not f:
            outputstrs.append(word + "\t" + a + "\n" + b + "\n\n")
        return 1
    f = 0
    for key in diction.dict:
        if cut:
            if len(word) > 8:
                if re.match(word[:-4], key) or re.search(word[2:], key):
                    f = show(f)
            elif len(word) > 5:
                if re.match(word[:-2], key):
                    f = show(f)
        else:
            if re.search(word.strip(), key):
                f = show(f)
    if f == 0:
        print('vague failed.')

if __name__ == '__main__':
    with Dictionary('ciyuan_pydict') as ciyuan:
        try:
            search_in()
        except KeyboardInterrupt:
            pass
        finally:
            with codecs.open(output, "a", encoding="utf-8") as f:
                f.write("".join(set(outputstrs)))