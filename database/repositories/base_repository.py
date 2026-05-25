from __future__ import annotations
from typing import Any, Type, TypeVar, Generic
from core.exceptions import AlreadyExistsError, DeletionError
from peewee import IntegrityError
from database.errors import is_unique_violation

from peewee import Model, DoesNotExist, ModelSelect

T = TypeVar("T", bound=Model)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, model_id: int) -> T:
        try:
            return self.model.get_by_id(model_id)
        except DoesNotExist:
            raise DoesNotExist(f"{self.model.__name__} не найден.")

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
