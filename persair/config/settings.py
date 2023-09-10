import  os
from    pydantic_settings  import BaseSettings

class Keys(BaseSettings):
    ReadKey:str         = ""
    WriteKey:str        = ""

keys                    = Keys()
