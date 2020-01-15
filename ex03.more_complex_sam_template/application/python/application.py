import abc
import enum
import json
import os

import requests
from dynamodb_json import json_util as dynamodb_json


class AgeLevel(enum.Enum):
    baby = 'baby'
    young = 'young'
    old = 'old'


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
            return AgeLevel.baby.value
        elif self.age < 8:
            return AgeLevel.young.value
        else:
            return AgeLevel.old.value

    def json(self):
        return json.dumps({
            'species': self.species,
            'name': self.name,
            'age': self.age,
            'level': self.get_age_level()
        })


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
                'age': {'N': str(cat.age)}
            }
        )

    def _get(self, name):
        response = self.session.get_item(
            TableName=self.table_name,
            Key={'name': {'S': name}}
        )
        item = response.get('Item')
        if not item:
            return None
        data = dynamodb_json.loads(item)
        return Cat(**data)


class Message(abc.ABC):

    @abc.abstractmethod
    def generate_message(self, message):
        pass


class NewCatMessage(Message):

    def __init__(self, name, age_level):
        self.name = name
        self.age_level = age_level

    def _get_recommended_food(self):
        food = getattr(RecommendedFood, self.age_level)
        return food.value

    def generate_message(self):
        return f'{self.name} needs {self._get_recommended_food()}!'


class MessageSender(abc.ABC):

    def __init__(self, message):
        self.message = message

    @abc.abstractmethod
    def _send(self, message):
        pass

    def send(self):
        self._send(self.message)


class SlackSender(MessageSender):

    def _send(self, message):
        msg = self.message.generate_message()
        r = requests.post(
                url=os.getenv('SLACK_URL'),
                json={'message': msg}
            )
        if r.status_code == '200':
            return True
        else:
            return False


class FakeSender(MessageSender):

    def _send(self, message):
        msg = self.message.generate_message()
        print(msg)
        return True
