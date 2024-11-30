
from utils import class_utils


class FakeSingletonClass(class_utils.Singleton):
    pass


class NonSingletonClass:
    pass


def test_singleton_class() -> None:
    singleton_instance_1 = FakeSingletonClass()
    singleton_instance_2 = FakeSingletonClass()

    assert singleton_instance_1 is singleton_instance_2

    unique_instance_1 = NonSingletonClass()
    unique_instance_2 = NonSingletonClass()

    assert unique_instance_1 is not unique_instance_2
