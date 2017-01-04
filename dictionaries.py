import os
import pystardict

STARDICT_EXTENSIONS = ['.idx', '.ifo', '.dict', '.dz', '.gz']


class DictionaryContainer:

    def __init__(self):
        self.dictionaries = []

    def __iter__(self):
        for dictionary in self.dictionaries:
            yield dictionary

    def __len__(self):
        return len(self.dictionaries)

    def __getitem__(self, key):
        return self.dictionaries[key]

    def __setitem__(self, key, value):
        self.dictionaries[key] = value

    def __delitem__(self, key):
        del self.dictionaries[key]

    def sort(self):
        self.dictionaries = sorted(self.dictionaries, key=str)

    def add(self, dictionary):
        self.dictionaries.append(dictionary)

    def remove(self, dictionary):
        self.dictionaries.remove(dictionary)

    def load(self, path, recursive=False):
        def get_strong_candidates(dict_candidates):
            return filter(lambda dict_candidate:
                          os.path.exists(''.join((dict_candidate, '.ifo')))
                          and (os.path.exists(''.join((dict_candidate, '.idx'))) or
                               os.path.exists(''.join((dict_candidate, '.idx.gz'))))
                          and (os.path.exists(''.join((dict_candidate, '.dict'))) or
                               os.path.exists(''.join((dict_candidate, '.dict.dz')))), dict_candidates)
        if recursive:
            loose_candidates = set()
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    name, ext = os.path.splitext(filename)
                    if ext in STARDICT_EXTENSIONS:
                        loose_candidates.add(os.path.join(dirpath, name))
            for strong_candidate in get_strong_candidates(loose_candidates):
                try:
                    dictionary = pystardict.Dictionary(strong_candidate)
                    if dictionary not in self.dictionaries:
                        self.add(dictionary)
                except ValueError as err:
                    # TODO need some better way to handle this
                    print(str(err))
        else:
            loose_candidates = set()
            for filename in os.listdir(path):
                name, ext = os.path.splitext(filename)
                if ext in STARDICT_EXTENSIONS:
                    loose_candidates.add(os.path.join(path, name))
            for strong_candidate in get_strong_candidates(loose_candidates):
                try:
                    dictionary = pystardict.Dictionary(strong_candidate)
                    if dictionary not in self.dictionaries:
                        self.add(dictionary)
                except ValueError as err:
                    # TODO need some better way to handle this
                    print(str(err))
