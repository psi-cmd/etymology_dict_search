#!python.exe
'''

文档内容来自《童哥说单词：牛津词源全解》，由于从 pdf 版转换过来，无法被格式化脚本所统一（比如不时少回车之类，难以处理）。已尽量根据已有规则修订。
如果有更好的文档源，欢迎使用或改进处理脚本并录入数据。

本脚本为最初筛选词条时所用，原始 pdf 转换的文本放在 ciyuan_dict.txt 中，转换成功的词条位于 ciyuan_pydict，无法处理的词条放在 unsolved 文件，\
    并且搜索时可能出现诸如释义被构成词组的另一个单词替代的情况。

本文件亦残留一些原始的功能，可能已弃之不用。
'''
import codecs, re
import os

os.chdir("C:\\Users\\longbang-cmd\\cmd_line_tools\\bin")
doc = './ciyuan_dict.txt'


class Dictionary(object):
    def __init__(self, doc):
        self.doc = doc
    def __enter__(self):
        with codecs.open(self.doc, 'r', 'utf-8') as f:
            t = eval(f.read())
            self.dict = t if t else {}
            self.r_dict = {b: a for a, b in self.dict.items()}
        with codecs.open(self.doc + '_unsolved', 'r', 'utf-8') as f:
            t = eval(f.read())
            self.unsolved = t if t else []
        return self
    def __exit__(self, type, value, trace):
        with codecs.open(self.doc, 'w', 'utf-8') as f:
            f.write(str(self.dict))
        with codecs.open(self.doc + '_unsolved', 'w', 'utf-8') as f:
            f.write(str(self.unsolved))
        

def pre_import(doc):   #废弃
    with codecs.open(doc, 'r', 'utf-8') as f:
        text = f.read()
    text = re.sub(r'(?<=[\w.。])\n(?=[一-龥])', '', text)
    text = re.sub(r'(?<=[一-龥])\n(?=[\w.。])', '', text)
    with codecs.open(doc, 'w', 'utf-8') as f:
        f.write(text)

def import_dict():
    ciyuan_dict = {}
    unsolved = []
    flag = 0
    with codecs.open('ciyuan_dict.txt', 'r', 'utf-8') as f:
        for line in f:
            line = line.strip('\n')
            if not re.search(r'[一-龥]', line):
                continue
            elif not re.search(r'[.。]', line):
                t = re.split(r'(?<=[a-zA-Z])\W+?(?=[一-龥])', line)
                flag = 1
                #print(t)
            elif re.search(r'[.。]$', line):
                if flag == 1:
                    try:
                        ciyuan_dict[t[0]] = (t[1], line)
                    except :
                        print(t)
                        unsolved.append(line)    #str
                    flag = 0
                else:
                    print(line)
                    unsolved.append(line)     #str
                #取整句话加入子列表，开始下一个获取
            else:
                q = re.split(r'[.。]', line)
                t = re.split(r'(?<=[a-zA-Z])\W+?(?=[一-龥])', q.pop().strip())
                if len(t) != 2:
                    print(t)
                    unsolved.append(t)       #list
                else:
                    print(str(t) + '!!!')
                    ciyuan_dict[t[-2]] = (t[-1], ''.join(q))
                #最后一个英文单词之前加入子列表，之后放入临时变量
    with codecs.open('ciyuan_pydict', 'w', 'utf-8') as f:
        f.write(str(ciyuan_dict))
    with codecs.open('ciyuan_pydict_unsolved', 'w', 'utf-8') as f:
        f.write(str(unsolved))
    #return ciyuan_dict, unsolved

def revise():
    with Dictionary('ciyuan_pydict') as ciyuan:
        target = ['来自', '比喻', '拟声', '词源', '词义', '感叹']
        failed = []
        for r in target:
            for i in ciyuan.unsolved:
                if type(i) == str and r in i:
                    p = re.split(f'({r})', i, 1)
                    t = re.split(r'(?<=[a-zA-Z])\W+?(?=[一-龥])', p[0])
                    print(t, p)
                    if len(t) == 2:
                        ciyuan.dict[t[0]] = (t[1], ''.join(p[1:]))
                        ciyuan.unsolved.remove(i)
                        print('ok')
                    else:
                        print(t)
                        failed.append(i)
    
    print('fin')
    return failed


def search(string, split='\n'):
    with Dictionary('ciyuan_pydict') as ciyuan:
        for word in string.split(split):
            if word:
                try:
                    a, b = ciyuan.dict[word.strip()]
                    print('\n'+word+' '+a+'\n'+b+'\n')
                    x = re.findall('来自([a-z\s]*),', b)
                    if x:
                        search(x[0].strip())
                    y = re.findall('词源同([a-z\s]*)', b)
                    if y:
                        search(y[0].strip())
                except KeyError:
                    print(word+'?')
                    vague_search(ciyuan, word)
                
def search_in(reverse=None, split='\n'):
    with Dictionary('ciyuan_pydict') as ciyuan:
        dict = ciyuan.r_dict if reverse else ciyuan.dict
        print(len(dict))
        while True:
            string = input('word(s):')
            if string == ':q':
                break
            elif string[:2] == '\V' and not '\n' in string:
                vague_search(ciyuan, string[2:], cut=False)
                break
            for word in string.split(split):
                word = word.strip()
                try:
                    a, b = dict[word]
                    print('\n'+word+' '+a+'\n'+b+'\n')
                    x = re.findall('来自([a-z\s]*),', b)
                    if x:
                        print('<**************')
                        search(x[0].strip())
                        print('**************>')
                    y = re.findall('词源同([a-z\s]+)', b)
                    if y:
                        print('<**************')
                        search(y[0].strip())
                        print('**************>')
                except KeyError:
                    print(word+'?')
                    if not reverse:
                        vague_search(ciyuan, word)
                
        
def vague_search(diction, word, cut=True):
    def show():
        a, b = diction.dict[key]
        print('\t'+key+' '+a+'\n\t'+b+'\n')
        return 1
    f = 0
    for key in diction.dict:
        if cut:
            if len(word) > 8:
                if re.match(word[:-4], key) or re.search(word[2:], key):
                    f = show()
            elif len(word) > 5:
                if re.match(word[:-2], key):
                    f = show()
        else:
            if re.search(word.strip(), key):
                f = show()
    if f == 0:
        print('vague failed.')
            
def origin(root):
    with Dictionary('ciyuan_pydict') as ciyuan:
        for key in ciyuan.dict:
            _, explan = ciyuan.dict[key]
            if root in explan:
                print(key+'\n')
            
            
def part(part):
    with Dictionary('ciyuan_pydict') as ciyuan:
        for key in ciyuan.dict:
            _, explan = ciyuan.dict[key]
            if part in key:
                print(key + '  '+ _ + '\n')

if __name__ == '__main__':
    search_in()

