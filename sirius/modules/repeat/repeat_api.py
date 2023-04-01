from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from random import randint

class Repeat:

    def __init__(self, rate):
        self.repeat_rate = rate
        self.cache = {}

    def is_repeat(self, group: Group, member: Member, current_message: MessageChain):
        # if new group
        if group.id not in self.cache:
            self.cache[group.id] = {'lastMember': member.id, 'lastMessage': current_message, 'repeatCount': 0}
            return False
        # if not same message
        if not self.cache[group.id]['lastMessage'] == current_message:
            self.cache[group.id].update({'lastMember': member.id, 'lastMessage': current_message, 'repeatCount': 0})
            if self.random_repeat():
                self.cache[group.id].update({'repeatCount': 3})
                return True
            return False
        # if same message
        else:
            if self.cache[group.id]['lastMember'] == member.id:
                return False
            else:
                count = self.cache[group.id]['repeatCount'] + 1
                self.cache[group.id].update({'lastMember': member.id, 'repeatCount': count})
                return True if count == 3 else False

    def random_repeat(self):
        if randint(1, 1000) <= self.repeat_rate:
            return True
        else:
            return False

    def set_rate(self, rate):
        rate = float(rate)
        if rate > 1 or rate < 0:
            self.repeat_rate = 1000
        else:
            self.repeat_rate = rate * 1000
