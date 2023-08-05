str_description = """

    The data models/schemas for the PACS QR collection.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime
from    enum                import Enum
from    pathlib             import Path



class sensorSimple(BaseModel):
    """The simplest sensor model POST"""
    sensor                              : str   = ""

class sensorDelete(BaseModel):
    status                              : bool  = False

class sensorBoolReturn(BaseModel):
    status                              : bool  = False

class persairResponse(BaseModel):
    """The model returned internally"""
    status                              : bool  = False
    message                             : str   = ''
    response                            : dict  = {}

class time(BaseModel):
    """A simple model that has a time string field"""
    time                                : str

