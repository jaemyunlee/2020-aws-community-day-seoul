# driver쪽의 port는 command
import abc
import enum
import os
from typing import NamedTuple

# import requests


RegisterCat = NamedTuple('RegisterCat', [('species', str),('name', str), ('age', int)])
FindCat = NamedTuple('FindCat', [('name', str)])

# model

class AgeLevel(enum.Enum):
    baby = 'BABY'
    young = 'YOUNG'
    old = 'OLD'


class RecommendedFood(enum.Enum):
    baby = 'KITTEN DELICIOUS FOOD'
    young = 'ACTIVE POWER FOOD'
    old = 'ANTI-AGING FOOD'

class Cat:
    
    def __init__(self, species, name, age):
        self.species = species
        self.name = name
        self.age = age

    def get_age_level(self):
        if self.age < 1:
            return AgeLevel.baby
        elif self.age < 8:
            return AgeLevel.young
        else:
            return AgeLevel.old

# use case

def register_cat(session, cmd):
    cat = Cat(cmd.species, cmd.name, cmd.age)
    session.add(cat)


def find_cat(session, cmd):
    cat = session.get(cmd.name)
    return cat


def get_cat(something, cmd):
    pass

# driven쪽의 port는


class CatNotRegisteredException(Exception):
    pass


class NewCat(abc.ABC):
    
    @abc.abstractmethod
    def add(self, cat):
        pass

    @abc.abstractmethod
    def _get(self, name):
        pass

    def get(self, name):
        cat = self._get(name)
        if cat is None:
            raise CatNotRegisteredException()
        return cat

# 이제 driven쪽 adaptor는 짝퉁일수도 있고, 이제 Database에 직접 연결 할 수도 있겠지!

class FakeCatRepository(NewCat):

    def __init__(self):
        self.cats = []
    
    def add(self, cat):
        self.cats.append(cat)

    def _get(self, name):
        for cat in self.cats:
            if cat.name == name:
                return cat
        
        return None


class DynamoDBCatRepository(NewCat):
    
    def __init__(self, session, table_name):
        self.session = session
        self.table_name = table_name
    
    def add(self, cat):
        self.session.put_item(
            TableName=self.table_name,
            Item={
                'species': {'S': cat.species},
                'name': {'S': cat.name},
                'age': {'N': cat.age}
            }
        )

    def _get(self, name):
        self.session.get_item(
            TableName=self.table_name,
            Key={'name': {'S': name}}
        )


class Message:

    def __init__(self, cat_name, cat_age_level):
        self.cat_name = cat_name
        self.cat_age_level = cat_age_level

    def _get_recommended_food(self):
        food = getattr(RecommendedFood, self.cat_age_level)
        return food.value

    def generate_message(self):
        return f'{self.cat_name} needs {self._get_recommended_food()}!'


class MessageSender(abc.ABC):

    @abc.abstractmethod
    def _send(self, message):
        pass

    def send(self, message):
        self._send(message)


# class SlackSender(MessageSender):

#     def _send(self, message):
#         r = requests.post(url=os.getenv('SLACK_URL'), json={'message': message})
#         if r.status_code == '200':
#             return True
#         else:
#             return False
