# coding=utf-8
import re
import os
import logging
from datetime import datetime
from logging import captureWarnings, Formatter, Logger, Handler, StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Dict, Match, List

from .exceptions.config import InvalidLiteralError


class ConvertedObject:
    pass

def convertDictToObject(x: Dict) -> object:
    y: ConvertedObject = ConvertedObject()

    for k, v in x.items():
        if isinstance(v, dict):
            v: Dict = convertDictToObject(v)

        if not isSafeLiteral(k):
            raise InvalidLiteralError(f"`{k}` is invalid literal.")
        setattr(y, k, v)

    return y

def listAttr(x: object) -> list:
    return [y for y in dir(x) if not y.startswith("__") and not y.endswith("__")]

def isSafeLiteral(x: str) -> bool:
    m: Match = re.match("^\w+$", x)
    m2: Match = re.match("^[^\d]", x)
    return m is not None and m2 is not None

def dumpVar(x: object) -> None:
    width: int = max([len(y) for y in dir(x)])
    [print(y.ljust(width + 10), "=", getattr(x, y)) for y in dir(x)]

def getLogger(name:str, directory: str, logLevel: int) -> Logger:
    logger: Logger = logging.getLogger(name)
    captureWarnings(capture=True)

    handler: Handler = RotatingFileHandler(
            f"{directory}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
            maxBytes=2 ** 20, backupCount=10000, encoding="utf-8"
    )
    handler2: Handler = StreamHandler()
    formatter: Formatter = Formatter(
            "[%(asctime)s][%(threadName)s %(name)s/%(levelname)s]: %(message)s",
            "%H:%M:%S"
    )
    handler.setFormatter(formatter)
    handler2.setFormatter(formatter)

    logger.setLevel(logLevel)
    logger.addHandler(handler)
    logger.addHandler(handler2)
    return logger

def makeDirs(names: List[str]) -> None:
    [
        os.makedirs(x) for x in names if not os.path.isdir(x)
    ]
