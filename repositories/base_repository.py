from peewee import Model, DoesNotExist, ModelSelect
from typing import Type
from utils.misc.exceptions import CreationError, AlreadyExistsError
from peewee import IntegrityError
from utils.misc.exceptions import DeletionError


class BaseRepository:
    """
    Базовый репозиторий для работы с моделями Peewee.
    Все дочерние классы должны указать конкретную модель в
    атрибуте `model`.
    """
    model: Type[Model] = None  # Дочерние классы должны указать модель

    @classmethod
    def get(cls, **filters) -> Model:
        """
        Получает один объект модели по указанным фильтрам.

        :param filters: Именованные параметры фильтрации (например, id=1, username="test").
        :return: Один объект модели.
        :raises DoesNotExist: Если объект не найден.
        """
        query = cls.model.select().where(*(getattr(cls.model, key) == value for key, value in filters.items()))
        if not query.exists():
            raise DoesNotExist(f"{cls.model.__name__} не найден.")
        return query.get()

    @classmethod
    def filter(cls, **filters) -> ModelSelect:
        """
        Возвращает выборку объектов модели, удовлетворяющих указанным фильтрам.

        :param filters: Именованные параметры фильтрации (например, status="active").
        :return: ModelSelect — выборка объектов модели.
        """
        return cls.model.select().where(*(getattr(cls.model, key) == value for key, value in filters.items()))

    @classmethod
    def get_all(cls) -> ModelSelect:
        """
        Возвращает все объекты модели.

        :return: ModelSelect — выборка всех объектов модели.
        :raises DoesNotExist: Если в базе нет ни одного объекта модели.
        """
        query = cls.model.select()
        if not query.exists():
            raise DoesNotExist(f"Объекты {cls.model.__name__} не найдены.")
        return query

    @classmethod
    def create(cls, **data) -> Model:
        """
        Создаёт объект модели с указанными данными.

        :param data: Именованные аргументы, соответствующие полям модели.
        :return: Созданный объект модели.
        :raises AlreadyExistsError: Если объект с такими данными уже существует (уникальные поля).
        :raises CreationError: Если произошла другая ошибка при создании.
        """
        try:
            return cls.model.create(**data)
        except IntegrityError as error:
            msg = str(error).lower()
            if "unique constraint" in msg or "unique violation" in msg:
                raise AlreadyExistsError(f"{cls.model.__name__} уже существует.") from error
            raise CreationError(f"Ошибка создания {cls.model.__name__}: {error}") from error
        except Exception as error:
            raise CreationError(f"Ошибка создания {cls.model.__name__}: {error}") from error

    @classmethod
    def update(cls, where_clause, **data) -> int:
        """
        Обновляет объекты модели по указанному условию.

        :param where_clause: Условие фильтрации для выбора обновляемых записей (например, User.id == 1).
        :param data: Поля и значения, которые нужно обновить (например, status="finished").
        :return: Количество обновлённых строк.
        :raises ValueError: Если переданы пустые данные.
        """
        if not data:
            raise ValueError("Нет данных для обновления.")

        query = cls.model.update(data).where(where_clause)
        return query.execute()

    @classmethod
    def update_instance(cls, instance: Model, **data) -> int:
        """
        Обновляет переданный экземпляр модели с новыми данными.

        :param instance: Экземпляр модели, который нужно обновить.
        :param data: Пары ключ-значение для обновления.
        :return: Количество обновлённых строк (всегда 1, если всё прошло корректно).
        :raises ValueError: Если не переданы данные или объект другого класса.
        """
        if not data:
            raise ValueError("Нет данных для обновления.")
        if not isinstance(instance, cls.model):
            raise ValueError(f"Ожидался объект {cls.model.__name__}, получен {type(instance).__name__}.")

        return cls.model.update(data).where(cls.model._meta.primary_key == instance.get_id()).execute()

    @classmethod
    def delete(cls, where_clause=None):
        """
        Удаляет объект(ы) модели, удовлетворяющие указанному условию.

        :param where_clause: Условие фильтрации (например, User.id == 1).
        :return: Количество удалённых строк.
        :raises DoesNotExist: Если ни один объект не найден по условию.
        :raises DeletionError: Если произошла ошибка при удалении.
        """
        try:
            query = cls.model.delete()
            if where_clause:
                query = query.where(where_clause)
            deleted = query.execute()
            if deleted == 0:
                raise DoesNotExist(f"{cls.model.__name__} не найден для удаления.")
            return deleted
        except Exception as error:
            raise DeletionError(f"Ошибка при удалении {cls.model.__name__}: {error}") from error

    @classmethod
    def delete_instance(cls, instance: Model, recursive: bool = True):
        """
        Удаляет конкретный экземпляр модели.

        :param instance: Экземпляр модели, который нужно удалить.
        :param recursive: Удалять ли связанные объекты (если настроено on_delete='CASCADE').
        :return: None
        :raises DeletionError: Если возникла ошибка при удалении.
        """
        try:
            instance.delete_instance(recursive=recursive)
        except Exception as error:
            raise DeletionError(f"Ошибка при удалении {cls.model.__name__}: {error}") from error

    @classmethod
    def is_instance(cls, obj) -> bool:
        """
        Проверяет, является ли переданный объект экземпляром модели репозитория.

        :param obj: Объект для проверки.
        :return: True, если объект принадлежит cls.model, иначе False.
        """
        return isinstance(obj, cls.model)
