from __future__ import annotations
from typing import Any, Type, TypeVar, Optional, Generic
from core.exceptions import AlreadyExistsError, DeletionError
from peewee import IntegrityError
from database.errors import is_unique_violation

from peewee import Model, DoesNotExist, ModelSelect, Node

T = TypeVar("T", bound=Model)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, filters: dict[str, Any]) -> T:
        try:
            return self.model.get(
                *(getattr(self.model, key) == value for key, value in filters.items())
            )
        except DoesNotExist:
            raise DoesNotExist(f"{self.model.__name__} не найден.")

    def get_by_id(self, model_id: int) -> T:
        try:
            return self.model.get_by_id(model_id)
        except DoesNotExist:
            raise DoesNotExist(f"{self.model.__name__} не найден.")

    def get_or_none(self, **filters) -> Optional[T]:
        try:
            return self.model.get(**filters)
        except DoesNotExist:
            return None

    def filter(self, where_clause: Node) -> ModelSelect:
        return (
            self.model.
            select().
            where(where_clause)
        )

    def get_all(self) -> ModelSelect:
        query = self.model.select()
        return query

    def create(self, data: dict[str, Any]) -> T:
        """
        Создаёт и возвращает объект модели с указанными данными.

        :raises AlreadyExistsError: Если объект с такими данными уже существует (уникальные поля).
        """
        try:
            return self.model.create(**data)
        except IntegrityError as error:
            if is_unique_violation(error):
                fields = ", ".join(data.keys())
                raise AlreadyExistsError(f"{self.model.__name__} с такими данными уже существует "
                                         f"\n(поля: {fields}).") from error

    def update(
            self,
            where_clause: Node,
            values: dict[str, Any]
    ) -> int:
        """
        Обновляет объекты модели по указанному условию.

        :param where_clause: Условие фильтрации для выбора обновляемых записей (например, User.id == 1).
        :param values: Словарь {"параметр": значение} с параметрами, соответствующими полям модели.
        :return: Количество обновлённых строк.
        """
        return (
            self.model
            .update(values)
            .where(where_clause)
            .execute()
        )

    def update_by_id(
            self,
            model_id: int,
            **fields: Any
    ) -> int:
        if not fields:
            raise ValueError("Не переданы поля для обновления.")

        pk_field = self.model._meta.primary_key

        return (
            self.model
            .update(**fields)
            .where(pk_field == model_id)
            .execute()
        )

    def update_by_ids(
            self,
            ids: list[int],
            values: dict[str, Any]
    ) -> int:
        return (
            self.model
            .update(values)
            .where(self.model._meta.primary_key.in_(ids))
            .execute()
        )

    def delete(self, where_clause: Node) -> int:
        """
        Удаляет объект(ы) модели, удовлетворяющие указанному условию.

        :param where_clause: Условия фильтрации
        :return: Количество удалённых строк.
        :raises DoesNotExist: Если объект не найден.
        :raises DeletionError: Любая другая ошибка.
        """
        try:
            deleted = self.model.delete().where(where_clause).execute()
            if deleted == 0:
                raise DoesNotExist(f"{self.model.__name__} не найден для удаления.")
            return deleted
        except Exception as error:
            raise DeletionError(f"{self.model.__name__} ошибка при удалении."
                                f"\n{error}")

    def delete_by_id(self, model_id: int) -> int:
        """
        Удаляет объект модели по ID.

        :param model_id: ID модели.
        :return: Количество удалённых строк.
        :raises DoesNotExist: Если объект не найден.
        :raises DeletionError: Любая другая ошибка
        """
        try:
            deleted = (
                self.model
                .delete()
                .where(self.model.id == model_id)
                .execute()
            )
        except Exception as error:
            raise DeletionError(f"{self.model.__name__} ошибка при удалении."
                                f"\n{error}")
        if deleted == 0:
            raise DoesNotExist(f"{self.model.__name__} с id={model_id} не найден для удаления.")

        return deleted



    def update_if_key_absent(  # TODO: разобраться как работает
        self,
        obj_id: int,
        field: str,
        key: str,
        value: Any,
    ) -> bool:
        obj = self.get_by_id(obj_id)

        data = dict(getattr(obj, field) or {})

        if key in data:
            return False

        data[key] = value

        updated = (
            self.model
            .update(**{field: data})
            .where(
                (self.model.id == obj_id) &
                (getattr(self.model, field) == getattr(obj, field))
            )
            .execute()
        )

        return bool(updated)
