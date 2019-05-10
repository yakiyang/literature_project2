# coding=utf8
import codecs
import jieba
import jieba.posseg as pseg
import operator

time_dic = {
    '白天': ['白天', '白晝', '白間', '日間', '白日', '太陽'],
    '晚上': ['晚上', '三更', '半夜', '三更半夜', '子夜', '五更', '午夜', '半夜', '良宵', '夜', '夜分', '夜半', '夜晚',
           '夜間', '夜裡', '後晌', '星夜', '凌晨', '宵', '晚', '晚間', '深夜', '夤夜', '漏夜', '黑夜', '月亮', '星星',
           '睡覺', '就寢'],
    '清晨': ['清晨', '拂曉', '破曉',  '清早', '早晨', '拂曉', '拔白', '破曉', '朝晨', '黎明', '天亮', '平旦', '平明'],
    '黃昏': ['黃昏', '薄暮', '傍晚', '夕陽', '日落']
}

def extract_time(text):
    score = {
        '白天': 0,
        '晚上': 0,
        '清晨': 0,
        '黃昏': 0,
    }
    jieba.suggest_freq('三更', tune=True)
    word = pseg.cut(text)
    for w in word:
        # print(w.word, w.flag)
        for key, value in time_dic.items():
            for sim_word in range(len(time_dic[key])):
                if time_dic[key][sim_word] == w.word:
                    # print(w.word, '----------match')
                    score[key] += 1
    # print(score)
    time = max(score.items(), key=operator.itemgetter(1))[0]
    return time


if __name__ == "__main__":
    # text = codecs.open('格林童話故事/一群二流子.txt', 'r', 'utf-8').read()
    text = '三更晚上半夜子夜五更'
    jieba.set_dictionary('data/dict.txt.big')
    # jieba.add_word('黃昏')
    # jieba.suggest_freq('黃昏', tune=True)
    time_word = extract_time(text)
    print(time_word)