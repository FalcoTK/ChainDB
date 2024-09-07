import json


class WriteJson:
    def __init__(self):
        self

    async def Write(self, data):
        with open("output.json", "w") as outfile:
            json.dump(data, outfile, indent=4)


class ReadJson:
    def __init__(self):
        self

    async def Read(self):
        with open("output.json", "r") as outfile:
            data = json.load(outfile)
        return data


class DeleteJson:
    def __init__(self):
        self

    async def Delete(self):
        pass
