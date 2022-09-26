import aiorequests

class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError

async def GetUidInfo(uid):
    res = await aiorequests.get(
        url="https://enka.microgg.cn/u/" + uid + "/__data.json"
    )
    data = await res.json(object_hook=Dict)
    return data