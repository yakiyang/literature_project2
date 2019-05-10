# coding=utf8
import codecs
import re

def cuttest(text):
    cut_word_loc = []
    cut_word = []

    with open('data/scene_dic.txt', 'r') as f:
        for line in f:
            if line.strip('\n') in text:
                cut_word.append(line.strip('\n'))

    # save location of the cut word
    for i in range(len(cut_word)):
        pos = text.index(cut_word[i])
        cut_word_loc.append(pos)

    # sorting by article
    cut_word_loc, cut_word = zip(*sorted(zip(cut_word_loc, cut_word)))
    print(cut_word_loc, cut_word)

    return cut_word

def split_scene(cut_word, text):
    scene = []
    scene_num = len(cut_word)
    minus_scene = ''

    # sce: 0,1,2,3...
    for sce in range(scene_num):
        if sce == 0:
            pass
        elif sce == 1:
            regex = cut_word[sce]
            scene_temp = re.split(re.escape(regex), text)
            scene_temp = scene_temp[0]
            scene.append(scene_temp)
        else:
            regex = cut_word[sce]
            scene_temp = re.split(re.escape(regex), text)
            minus_scene += scene[sce-2]
            scene_temp = scene_temp[0].replace(minus_scene, '')
            scene.append(scene_temp)

    # last scene
    last_scene = text.replace(minus_scene+scene[-1], '')
    scene.append(last_scene)

    return scene, scene_num

def check_whether_merge(scene, scene_num):
    for i in range(scene_num-1):
        print(len(scene[i].encode('utf-8')))
        # chinese word contains 2 characters
        if len(scene[i].encode('utf-8')) < 12:
            scene[i:i+2] = [''.join(scene[i:i+2])]
            scene_num -= 1
    return scene, scene_num

if __name__ == "__main__":
    text = codecs.open('格林童話故事/一群二流子.txt', 'r', 'utf-8').read()
    cut_word = cuttest(text)
    temp_scene, temp_scene_num = split_scene(cut_word, text)
    scene, scene_num = check_whether_merge(temp_scene, temp_scene_num)
    # for i in range(scene_num):
    #     print(scene[i], '\n')