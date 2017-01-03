import csv
import re

TSV_FORMAT = '*.txt *.tsv'


class Flashcard:

    def __init__(self, sides):
        self.sides = sides

    def __len__(self):
        return len(self.sides)

    def __iter__(self):
        for side in self.sides:
            yield side

    def __getitem__(self, key):
        return self.sides[key]

    def __setitem__(self, key, value):
        self.sides[key] = value

    def __delitem__(self, key):
        del self.sides[key]

    def set_size(self, size):
        if size > len(self):
            self.sides += ['' for _ in range(size - len(self))]
        else:
            self.sides = self.sides[:size]

    def __str__(self):
        if len(self.sides) > 0:
            return self.sides[0]
        else:
            return ''


class Deck:

    def __init__(self, col=0, file=None):
        self.flashcards = []
        self.col = col
        self.file = file
        self._dirty = False

    def __iter__(self):
        for flashcard in self.flashcards:
            yield flashcard

    def __len__(self):
        return len(self.flashcards)

    def __getitem__(self, key):
        return self.flashcards[key]

    def __setitem__(self, key, value):
        self.flashcards[key] = value
        self._dirty = True

    def __delitem__(self, key):
        del self.flashcards[key]
        self._dirty = True

    def add(self, flashcard):
        self.flashcards.append(flashcard)
        self._dirty = True

    def quick_add(self, key, dictionaries):
        sides = [key, ]
        for dictionary in dictionaries:
            try:
                value = dictionary[key]
            except KeyError as err:
                value = ''
            sides += value
        self.flashcards.append(Flashcard(sides))
        self._dirty = True

    def clear(self, clear_file_name=True):
        self.flashcards = []
        self.col = 0
        if clear_file_name:
            self.file = None
        self._dirty = False

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, file):
        self.__file = file

    @property
    def col(self):
        if len(self) > 0:
            return max([len(flashcard) for flashcard in self.flashcards])
        else:
            return self.__col

    @col.setter
    def col(self, col):
        for flashcard in self.flashcards:
            flashcard.set_size(col)
        self.__col = col
        if len(self) > 0:
            self._dirty = True

    @property
    def header(self):
        if self.col > 0:
            return ['Text {}'.format(i + 1) for i in range(self.col)]
        else:
            return None

    def is_dirty(self):
        return self._dirty

    def load(self, file=None):
        def is_header(flashcard):
            return all(re.match(r'Text \d', side) for side in flashcard)
        if file:
            self.file = file
        with open(self.file, 'r', encoding='utf-8', newline='\n') as tsv_file:
            tsv_reader = csv.reader(tsv_file, delimiter='\t')
            self.clear(False)
            for row in tsv_reader:
                sides = []
                for col in row:
                    sides.append(col)
                flashcard = Flashcard(sides)
                if not is_header(flashcard):
                    self.add(flashcard)
                else:
                    self.col = len(flashcard)
        self._dirty = False
        return True, '{} loaded successfully'.format(self.file)

    def save(self, file=None):
        if file:
            self.file = file
        with open(self.file, 'w', encoding='utf-8', newline='\n') as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t')
            tsv_writer.writerow(self.header)
            for flashcard in self.flashcards:
                tsv_writer.writerow(flashcard)
        self._dirty = False
        return True, '{} saved successfully'.format(self.file)
