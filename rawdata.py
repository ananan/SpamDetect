# coding=utf-8

import jieba
import os
from features import *
import re
from matplotlib import pyplot as plt

jieba.enable_parallel()


def convert2utf8(srcf, tarf):
    sf = open(srcf, 'r')
    tf = open(tarf, 'w')
    lines = sf.readlines()
    utf8 = []
    for line in lines:
        try:
            utf8.append(line.decode('gbk').encode('utf-8'))
        except Exception, e:
            print repr(e)
            continue
    tf.writelines(utf8)


def data2utf8(srcdir, tardir):
    paths = os.listdir(srcdir)
    if not os.path.exists(tardir):
        os.mkdir(tardir)
    for path in paths:
        if os.path.isdir(os.path.join(srcdir, path)):
            data2utf8(os.path.join(srcdir, path), os.path.join(tardir, path))
        else:
            convert2utf8(os.path.join(srcdir, path),
                         os.path.join(tardir, path))

# data2utf8('../trec06c/data/', '../trec06c/utf8/')


def readEmail(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    lines = [line.strip().replace(' ', '').replace('\t', '') for line in lines]
    info = [[], []]
    po = 0
    for line in lines:
        if line == '':
            po = 1
            continue
        info[po].append(line)
    return info



def email_special_token(info):
    infostr = ''.join(info[1])
    special = {}

    url = '[a-zA-z]+://[\w\d/\.]*'
    urlnum = len(re.findall(url, infostr))
    if urlnum > 0:
        special['http://'] = urlnum

    phone = '\d{3}-\d{8}|\d{4}-\d{7}|0?1\d{10}\D|\D\d{8}\D'
    # print re.findall(phone, info)
    phonenum = len(re.findall(phone, infostr))
    if phonenum > 0:
        special['xxx-xxxx-xxxx'] = phonenum

    email = '[\w-]*@[\w-]*.[\w-]*'
    # print re.findall(email, info)
    emailnum = len(re.findall(email, infostr))
    if emailnum > 0:
        special['xxx@xxx.xxx'] = emailnum

    # length = len(info)
    # if length > 4000:
    #     special['email_length'] = 1

    priority = -1
    for line in info[0]:
        if line.lower().startswith('x-priority'):
            line = line.split(':')
            priority = int(line[1].strip())
            # print priority
    if priority != -1 and priority != 3:
        special['priority3-1'] = 1
    return special


def email2dict(filename):
    info = readEmail(filename)
    words = jieba.cut(''.join(info[1])
                      .replace('。', '。' + os.linesep)
                      .replace('，', '，' + os.linesep)
                      .replace('；', '；' + os.linesep)
                      .replace('、', '、' + os.linesep)
                      .replace('！', '！' + os.linesep)
                      .replace('？', '？' + os.linesep))
    wordcnt = {}
    for word in words:

        if useless_word(word):
            # print word.encode('utf-8')
            continue

        if word in wordcnt:
            wordcnt[word] = wordcnt[word] + 1
        else:
            wordcnt[word] = 1

    specialToken = email_special_token(info)
    for special in specialToken:
        wordcnt[special] = specialToken[special]
    return wordcnt


def data2vec(indexfile, max=-1):
    f = file(indexfile, 'r')
    lines = f.readlines()
    lines = [line.strip().split(' ') for line in lines]
    if max == -1:
        max = len(lines)

    vectors = [[], []]
    cnt = 0
    for line in lines:
        emailvec = []
        positive = 1 if line[0].lower() == 'spam' else 0
        emailvec.append(positive)

        path = os.path.join('trec06c/utf8/', '/'.join(line[1].split('/')[-2:]))
        worddict = email2dict(path)

        emailvec.append(worddict)
        vectors[positive].append(emailvec)
        cnt += 1
        print cnt
        if cnt >= max:
            break
    return vectors


def email_length(indexfile, max=-1):
    f = file(indexfile, 'r')
    lines = f.readlines()
    lines = [line.strip().split(' ') for line in lines]
    if max == -1:
        max = len(lines)

    per = ['<500', '500-1000', '1000-2000', '2000-3000', '3000-4000', '4000-5000', '>5000']
    vectors = [{}.fromkeys(per, 0), {}.fromkeys(per, 0)]
    cnt = 0
    for line in lines:
        positive = 1 if line[0].lower() == 'spam' else 0

        path = os.path.join('trec06c/utf8/', '/'.join(line[1].split('/')[-2:]))
        info = readEmail(path)
        length = len(''.join(info[1]))
        if length < 500:
            vectors[positive]['<500'] += 1
        elif length < 1000:
            vectors[positive]['500-1000'] += 1
        elif length < 2000:
            vectors[positive]['1000-2000'] += 1
        elif length < 3000:
            vectors[positive]['2000-3000'] += 1
        elif length < 4000:
            vectors[positive]['3000-4000'] += 1
        elif length < 5000:
            vectors[positive]['4000-5000'] += 1
        else:
            vectors[positive]['>5000'] += 1

        cnt += 1
        print cnt
        if cnt >= max:
            break
    return vectors


def email_priority(indexfile, max=-1):
    f = file(indexfile, 'r')
    lines = f.readlines()
    lines = [line.strip().split(' ') for line in lines]
    if max == -1:
        max = len(lines)

    vectors = [{}, {}]
    cnt = 0
    for line in lines:
        positive = 1 if line[0].lower() == 'spam' else 0

        path = os.path.join('trec06c/utf8/', '/'.join(line[1].split('/')[-2:]))
        info = readEmail(path)
        priority = -1

        for line in info[0]:
            if line.lower().startswith('x-priority'):
                line = line.split(':')
                priority = int(line[1].strip())
                # print priority
        if priority in vectors[positive]:
            vectors[positive][priority] += 1
        else:
            vectors[positive][priority] = 1

        cnt += 1
        print cnt
        if cnt >= max:
            break
    return vectors

# vecs = data2vec('trec06c/full/index', 5000)
# print len(vecs[0]), len(vecs[1])
# email2dict('trec06c/utf8/010/130')

# lengthinfo = email_length('trec06c/full/index', 5000)
# print lengthinfo

# plt.hist(lengthinfo[0])
# plt.xscale('symlog')
# plt.yscale('symlog')
# plt.show()

# priorityinfo = email_priority('trec06c/full/index', 7000)
# print priorityinfo
