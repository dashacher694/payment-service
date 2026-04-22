from typing import Any, Callable, Protocol, Self

from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWorkProtocol(Protocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def __call__(self, *, reuse_session: bool = False) -> Self: ...


class UseCaseProtocol(Protocol):
    def __init__(self, uow: UnitOfWorkProtocol) -> None:
        self.uow = uow


def async_transactional(
    uc_for_reuse_session: list[str] | None = None, *, read_only: bool = False
):
    def decorator(func: Callable):
        async def wrapper(use_case: UseCaseProtocol, *args, **kwargs):
            if not use_case.uow.session:
                async with use_case.uow:
                    _set_session_in_use_cases(use_case, uc_for_reuse_session)
                    result = await func(use_case, *args, **kwargs)

                    if not read_only:
                        await _end_write_session(use_case, result)

                    return result

            else:
                async with use_case.uow(reuse_session=True):
                    _set_session_in_use_cases(use_case, uc_for_reuse_session)
                    return await func(use_case, *args, **kwargs)

        return wrapper

    return decorator


def _set_session_in_use_cases(
    use_case: UseCaseProtocol, nested_use_cases: list[str] | None
):
    if nested_use_cases:
        for nested_uc_name in nested_use_cases:
            nested_use_case: UseCaseProtocol = use_case.__dict__[nested_uc_name]
            nested_use_case.uow.session = use_case.uow.session


async def _end_write_session(use_case: UseCaseProtocol, result: Any):
    await use_case.uow.session.commit()
    try:
        inspect(result)
        await use_case.uow.session.refresh(result)
    except NoInspectionAvailable:
        pass
