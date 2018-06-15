import json

class Utils(object):
    def saveDict(dict, file):
        with open(file, 'w') as fp:
            json.dump(dict, fp, sort_keys=True, indent=4)

    def loadDict(file):
        with open(file, 'r') as fp:
            return json.load(fp)