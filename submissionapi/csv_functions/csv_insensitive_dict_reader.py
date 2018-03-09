import csv


class DictReaderInsensitive(csv.DictReader):
    # This class overrides the csv.fieldnames property.
    # All fieldnames are without white space and in lower case

    @property
    def fieldnames(self):
        return [field.strip().lower() for field in super(DictReaderInsensitive, self).fieldnames]

    def __next__(self):
        # get the result from the original __next__, but store it in DictInsensitive

        dInsensitive = DictInsensitive()
        dOriginal = super(DictReaderInsensitive, self).__next__()

        # store all pairs from the old dict in the new, custom one
        for key, value in dOriginal.items():
            dInsensitive[key] = value.strip()

        return dInsensitive

class DictInsensitive(dict):
    # This class overrides the __getitem__ method to automatically strip() and lower() the input key

    def __getitem__(self, key):
        return dict.__getitem__(self, key.strip().lower())