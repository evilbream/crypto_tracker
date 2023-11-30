import json
from dataclasses import dataclass, field
from collections.abc import Sequence
from socket_request.data import currency_pairs
from socket_request.data import *
from typing import NamedTuple, Optional

# сделать декоратор для оберкти ответов от сервера
#print(markets)

# берем 1 маркет передаем его и он форматирвуется и возвращает маркет

class Market:
    def __init__(self, name: str, uri: str, command: tuple[dict]|list[dict]|dict):
        self.name = name
        self.uri = uri
        if isinstance(command, dict):
            self.command = [json.dumps(command)]
        elif isinstance(command, tuple|list):
            self.command = [json.dumps(com) for com in command]

    def __repr__(self):
        return f'name: {self.name}\nuri: {self.uri}\ncommands: {self.command}'


# сообщения хранятся в листе потому что вдруг оно не одно
@dataclass()
class Format:
    def __init__(self):
        self.handlers = dict()

    def on(self, command):
        def deco(func):
            self.handlers[command] = func
            return func
        return deco

    def handle(self, name):
        if name in self.handlers.keys():
            return self.handlers[name](name)
        else:
            return f'Formatting for {name} is not defined'

    def get(self, markets: tuple[str]|list[str]|str):
        if isinstance(markets, str):
            return self.handle(markets)
        elif isinstance(markets, tuple|list):
            return [self.handle (market) for market in markets]
        else:
            raise TypeError






















