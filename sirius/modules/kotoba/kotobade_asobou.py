from .wordlist import wordlist
from random import choice

class Kotoba:

    def __init__(self):
        self.word = choice(wordlist)
        self.player = {}

    def enter_word(self, player, answer):
        if len(answer) != 4:
            return '４文字の単語を入力してください'
        if answer not in wordlist:
            return 'この答えは単語リストにありません'
        if player not in self.player:
            self.player[player] = {'counter': 0, 'answer': [], 'result': [], 'win': False}
        if self.player[player]['win']:
            return self.render_result(player)
        result = ''
        win = True
        for i in range(0, 4):
            if answer[i] not in self.word:
                result += '⬛'
                win = False
            elif answer[i] != self.word[i]:
                result += '🟨'
                win = False
            else:
                result += '🟩'
        self.player[player]['counter'] += 1
        self.player[player]['answer'].append(answer)
        self.player[player]['result'].append(result)
        self.player[player]['win'] = win
        return self.render_result(player)

    def render_result(self, player):
        message = ''
        counter = self.player[player]['counter']
        for i in range(0, counter):
            answer = self.player[player]['answer'][i]
            result = self.player[player]['result'][i]
            if i == 0:
                message += f'{answer} {result}'
            else:
                message += f'\n{answer} {result}'
        message += f'\n{player}: {counter}/12'
        if self.player[player]['counter'] == 12 and not self.player[player]['win']:
            message += '\n寄！'
        if self.player[player]['win']:
            message += '\nNEWGAMEをNow Loading...'
            self.new_game()
        return message

    def new_game(self):
        self.word = choice(wordlist)
        self.player = {}
