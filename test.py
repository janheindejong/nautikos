from enum import Enum


class MyEnum(Enum):
    TEST = "test"


stuff = {MyEnum.TEST: "Hello!"}


print(stuff[MyEnum("bla")])
