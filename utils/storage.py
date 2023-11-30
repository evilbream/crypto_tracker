import collections


class Storage(collections.UserDict):
    TELEGRAM = 'tg'
    WEB = 'web'
    MARKET = 'markets'

    def __init__(self):
        super ().__init__ ()

    def __contains__(self, item):
        return item.lower() in self.data

    def __setitem__(self, key, value):
        key = key.lower()
        if (key in [Storage.WEB, Storage.TELEGRAM]) and (self.data.get(key, 1) != 1):
            self.data[key].appendleft(value)
        elif key in [Storage.WEB, Storage.TELEGRAM]:
            que = collections.deque (maxlen=4)
            que.appendleft(value)
            self.data[key] = que
        elif key == Storage.MARKET:
            if self.data.get(key, 1) != 1:
                self.data[key].append(value)
            else:
                self.data[key] = value

        else:
            raise Exception(f'Unable to set {key} for class Storage')

    def pick(self, place):
        place = place.lower()
        if (place == Storage.WEB) or (place == Storage.TELEGRAM):
            if (self.data.get(place, '1') != '1') and (len(self.data.get(place)) > 1):
                return self.data[place].pop()
            return False
        else:
            return False


cross_storage = Storage()








