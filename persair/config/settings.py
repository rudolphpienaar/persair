import  os
from    pydantic_settings  import BaseSettings

class Keys(BaseSettings):
    DBauthPath:str      = '/db/init.json'
    ReadWriteKey:str    = "local"

class Mongo(BaseSettings):
    URI:str             = "localhost:27017"
    DB:str              = "default"

keys            = Keys()
mongosettings   = Mongo()
