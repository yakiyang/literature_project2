import codecs
import json
import operator
import jieba

LOCATION = 0
CHARACTER = 1

sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '\n', '」']
jieba.set_dictionary('data/dict.txt.big')
class Scene:
    def __init__(self, text):
        self.load_dict()
        self.text = text.replace('\n', '').replace('\r\r', '').replace('」「', '」\n「')
        self.tags = self.init_tag()
        self.sentences, self.tags = self.sentences_segment()
        self.tags = self.item_tag('PER', self.nr)
        self.tags = self.item_tag('LOC', self.ns)
        self.locations_dict = {}
        self.scene_character = []
        self.scene_location = ''
        self.scene_content = []

        for sentence, tag in zip(self.sentences, self.tags):
            #print(sentence)
            if 'D' not in tag:
                self.scene_content.append(['action', sentence])

            diag = ''.join([c for c, t in zip(sentence, tag) if t == 'D'])
            characters = self.find_item(sentence, tag, 'PER')
            self.scene_character += characters
            locations = self.find_item(sentence, tag, 'LOC')
            if len(locations) != 0:
                for i in locations:
                    if i not in self.locations_dict:
                        self.locations_dict[i] = 1
                    else:
                        self.locations_dict[i] += 1

            if len(diag) != 0:
                if len(characters) != 0:
                    character = characters[0]
                else:
                    character = "unknown"
                self.scene_content.append([character, diag])

    def load_dict(self):
        # get characters
        text = codecs.open('data/character_dict.txt', 'r', 'utf-8').read()
        nr = text.split('\n')

        # get locations
        text = codecs.open('data/location_dict.txt', 'r', 'utf-8').read()
        ns = text.split('\n')

        self.nr = list(set(nr))
        self.ns = list(set(ns))


    def get_character(self):

        self.scene_character = list(set(self.scene_character))

        return self.scene_character

    def get_location(self):
        self.scene_location = sorted(self.locations_dict.items(), key=lambda d: d[1], reverse=True)
        if len(self.scene_location) != 0:
            self.scene_location = self.scene_location[0][0]
        else:
            locations_distribution_dict = {}
            text = codecs.open('data/location_distribution.txt', 'r', 'utf-8').read().split('\n')
            for line in text:
                value = line.split(' ')
                if len(value[0]) != 0:
                    locations_distribution_dict[value[0]] = value[1]
            scene_location = sorted(locations_distribution_dict.items(), key=lambda d: d[1], reverse=True)
            self.scene_location = scene_location[0][0]

        return self.scene_location

    def get_content(self):
        self.scene_content = self.trace_talk_character(self.scene_content)

        return self.scene_content


    def sentences_segment(self):
        delimiters = set([item for item in sentence_delimiters])

        res = []
        new_tags = []
        res_c = ''
        res_tag = []
        next_tag = ''
        for i, (c, tag) in enumerate(zip(self.text, self.tags)):
            res_c += c
            res_tag += tag
            #print(c, tag)
            for sep in delimiters:
                if c == sep and tag != 'D':
                    #print(res_c)
                    #print(res_tag)
                    #print()
                    for j in range(i+1, len(self.text)):
                        if self.text[j] in delimiters:
                            next_tag = self.text[j]
                            break

                    if sep == '」' and next_tag == '。':
                        break
                    if len(res_c.strip()) > 0:
                        res.append(res_c)
                        new_tags.append(res_tag)
                    res_c = ''
                    res_tag = []

        return res, new_tags


    def init_tag(self):
        tags = []
        dialog_check = 0
        for c in self.text:
            if c == '」':
                dialog_check = 0
            if dialog_check == 0:
                tags.append('O')
            if dialog_check == 1:
                tags.append('D')
            if c == '「':
                dialog_check = 1

        return tags


    def item_tag(self, item_tag, item_dict):
        new_tags = []
        for sentence, tag in zip(self.sentences, self.tags):
            cut_sentence = list(jieba.cut(sentence))
            for item in item_dict:
                if item in cut_sentence:
                    index = sentence.find(item)
                    if tag[index] != 'D':
                        for i in range(index, index + len(item)):
                            tag[i] = item_tag

            new_tags.append(tag)
        return new_tags

    def find_item(self,sentence, tag, item_tag):
        item = ''
        items = []
        check = 0

        for c, t in zip(sentence, tag):
            if check == 1 and t != item_tag:
                check = 0
                items.append(item)
                item = ''
            if t == item_tag:
                check = 1
            if check == 1:
                item += c

        return items

    def trace_talk_character(self,content):
        two_character = []
        new_content = []

        for i, text in enumerate(content):
            if text[0] != 'action' and text[0] != "unknown":
                if len(two_character) == 2:
                    two_character.remove(two_character[0])
                two_character.append(text[0])
                prev_character = text[0]
            if len(two_character) == 2:
                for j in range(i, 0, -1):
                    if content[j][0] == "unknown":
                        for k in two_character:
                            if k != prev_character:
                                content[j][0] = k
                        prev_character = content[j][0]
                    elif content[j][0] != "action":
                        prev_character = content[j][0]

        for text in content:
            if text[0] == 'action':
                new_content.append(text[1])
            else:
                new_content.append(text[0] + ' : ' + text[1])

        return new_content

if __name__ == '__main__':

    #小紅帽
    story = ['從前，有一隻胖胖的豬媽媽，她生了三隻小豬。最大的小豬：豬大哥很貪睡，很懶惰。一天到晚都在打瞌睡。第二個小豬：豬二哥很愛吃，他也很懶惰。幸好最小的小豬：豬小弟是個勤勞的好孩子。常常努力的工作。',
             '有一天，豬媽媽告訴他們說：「你們都長大了，應該自己蓋房子，自己住，自己種田，自己生活。我要你們自己照顧自己。」豬大哥噘起嘴，懶洋洋走出家門。「咿咿．．．．．好討厭哦！」豬大哥想一想說：「蓋一棟稻草屋吧，那最簡單了。」稻草屋很快的蓋好了，豬大哥好得意，他馬上去找兩個弟弟來，很驕傲的對他們說：「我的房子蓋好了，很漂亮吧～，你們也快一點蓋吧！」 豬二哥看見說：「哇，果然很漂亮，大哥，你真了不起啊！」可是豬小弟並不以為然，他說：「哥，你不擔心稻草屋會被風吹倒嗎？」豬二哥想了想，說：「稻草屋會被風吹倒，那我就用木頭來蓋好了，木屋較重，不怕風吹。」豬二哥決定以後，「咚咚咚，咚咚咚！」他很認真的工作，一會兒敲敲釘子，一會兒鋸木頭。很快的，一棟木屋蓋好了。豬二哥趕忙把哥哥和弟弟都請來，驕傲的說：「你們看，這麼漂亮的房子！而且釘得很牢固，不會被風吹倒，我真的好棒呀！」豬小弟說：「木屋雖然不會被風吹倒，可是用力打，木頭會被打斷，房子就垮了。」「討厭！」豬二哥罵小弟說：「你以為你最聰明？看你搬磚頭搬一整天了，房子還沒蓋出來。笨蛋～～」豬小弟不慌不忙說：「我蓋房子雖然比你們慢，但是我要蓋的房子不怕風吹，也不怕敲打，紅磚房子最牢固了。」豬小弟不理會哥哥的嘲笑，他搬好了磚塊，又搬水泥，他把水泥和好了，開始堆砌磚塊，一塊一塊將抹上水泥的磚頭堆砌起來。豬小弟心理想：你們不要笑我，等我蓋好了，你們就知道了，我的房子比什麼都堅固，野狼來了我也不怕呢！豬小弟繼續加油工作，他趕呀趕，趕到天黑，月亮掛在天上了，他的紅磚房子才好不容易蓋好了。豬小弟正想休息，卻聽到了大野狼的吼叫聲。豬小弟猛吸一口氣說：「幸好房子蓋好了，我不怕大野狼。」這時兩個豬哥哥也聽到了野狼的吼叫聲，怕得發抖，他們怕野狼來，所以整夜都不敢安心睡覺。',
             '隔天，豬媽媽要三隻小豬到田裡工作，沒想到走到半路的時候，他們被一隻可怕的大野狼發現了，野狼一直跟蹤他們。野狼決定先吃豬大哥。豬大哥剛回到家，就聽到大野狼的聲音：「砰砰砰！小豬朋友，快給我開門！」野狼叫門叫得好兇。豬大哥嚇得臉都白了，他趕緊拿一把大鎖，把門緊緊鎖了起來。可是野狼哈哈大笑說：「你這個大笨蛋，這種稻草屋，我吹一口氣就倒了。」他說完話，用力一吹，果然把稻草屋吹倒了，豬大哥嚇得直跑到豬二哥家。「救命呀！」大哥慌慌張張跑進豬二哥的木屋子，趕忙把大門閂上，怕野狼闖進來。可是野狼吼叫說：「木頭屋子一樣擋不住我，我一定要把你吃掉！」兩隻小豬怕得縮著身子擠在一起，頭上直冒冷汗。因為野狼怕把門打壞了，「砰～～」，門板發出吱吱吱的斷裂聲，兩隻小豬眼看野狼就要衝進來了，他們亂闖亂撞，結果撞倒了木屋子，他們直奔到豬小弟的家。野狼也一直在身後追趕他們。兩隻小豬逃呀逃呀，逃到小弟弟的家中。「弟弟，弟弟，小．．．．弟弟，野狼在我們．．身．．．後．．．」豬大哥上氣不接下氣的說：「快把門鎖緊，不然我們會被吃掉的。」豬小弟卻一點都不擔心，他說：「怕什麼？這麼堅固的磚屋，野狼進不來的。」很快的，野狼就追來了。他生氣的說：「死小豬，看我把你們的房子撞倒，你們就要被我吃掉了。」野狼說著說的開始撞牆了。「呀！～～」他使出全身力氣，向磚牆猛撞過去！「啪啦！」一聲，磚牆沒被撞倒，野狼的骨頭卻斷了，「哎唷，痛死我了，痛死我了！」野狼哭哭啼啼的回家去了。「萬歲！」三隻小豬很高興的叫起來。從此，他們三個兄弟住在一起，每天一起吃飯睡覺，也一起工作，日子過得很快樂，而且野狼一直沒再出現呢！']

    s = Scene(story[1])
    print(s.get_character())
    print(s.get_location())
    print(s.get_content())









