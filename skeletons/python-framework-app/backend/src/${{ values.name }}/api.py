"""Endpoints of the ${{ values.entities }}. Reading needs a signed-in user with a ${{ values.name }} role; writing, the admin one."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from refresquito_fastapi import ConflictError, NotFoundError, Page, PageParamsDep, User, require_roles
from refresquito_fastapi.db import SessionDep, paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ${{ values.Entity }}, ${{ values.Entity }}Status
from .schemas import ${{ values.Entity }}In, ${{ values.Entity }}Out

VIEWER, ADMIN = "${{ values.name }}-viewer", "${{ values.name }}-admin"
Reader = Annotated[User, Depends(require_roles(VIEWER, ADMIN))]
Writer = Annotated[User, Depends(require_roles(ADMIN))]

router = APIRouter(prefix="/api/${{ values.entities }}", tags=["${{ values.entities }}"])


async def find(session: AsyncSession, ${{ values.entity }}_id: int) -> ${{ values.Entity }}:
    ${{ values.entity }} = await session.get(${{ values.Entity }}, ${{ values.entity }}_id)
    if ${{ values.entity }} is None:
        raise NotFoundError(f"${{ values.Entity }} {${{ values.entity }}_id} does not exist")
    return ${{ values.entity }}


async def check_name_is_free(session: AsyncSession, name: str, except_id: int | None = None) -> None:
    other = await session.scalar(select(${{ values.Entity }}).where(${{ values.Entity }}.name == name))
    if other is not None and other.id != except_id:
        raise ConflictError(f"There is already a ${{ values.entity }} called {name}", code="${{ values.entity }}_name_taken")


@router.get("")
async def list_${{ values.entities }}(
    user: Reader,
    session: SessionDep,
    params: PageParamsDep,
    status: Annotated[${{ values.Entity }}Status | None, Query(description="Only the ${{ values.entities }} in this status")] = None,
    category: Annotated[str | None, Query(description="Only this category")] = None,
) -> Page[${{ values.Entity }}Out]:
    statement = select(${{ values.Entity }}).order_by(${{ values.Entity }}.name)
    if status:
        statement = statement.where(${{ values.Entity }}.status == status)
    if category:
        statement = statement.where(${{ values.Entity }}.category == category.strip())
    return await paginate(session, statement, params)


@router.get("/{${{ values.entity }}_id}")
async def get_${{ values.entity }}(${{ values.entity }}_id: int, user: Reader, session: SessionDep) -> ${{ values.Entity }}Out:
    return ${{ values.Entity }}Out.model_validate(await find(session, ${{ values.entity }}_id))


@router.post("", status_code=201)
async def create_${{ values.entity }}(body: ${{ values.Entity }}In, user: Writer, session: SessionDep) -> ${{ values.Entity }}Out:
    await check_name_is_free(session, body.name)
    ${{ values.entity }} = ${{ values.Entity }}(**body.model_dump(), created_by=user.username)
    session.add(${{ values.entity }})
    await session.flush()
    await session.refresh(${{ values.entity }})
    return ${{ values.Entity }}Out.model_validate(${{ values.entity }})


@router.put("/{${{ values.entity }}_id}")
async def update_${{ values.entity }}(${{ values.entity }}_id: int, body: ${{ values.Entity }}In, user: Writer, session: SessionDep) -> ${{ values.Entity }}Out:
    ${{ values.entity }} = await find(session, ${{ values.entity }}_id)
    await check_name_is_free(session, body.name, except_id=${{ values.entity }}_id)
    for field, value in body.model_dump().items():
        setattr(${{ values.entity }}, field, value)
    await session.flush()
    return ${{ values.Entity }}Out.model_validate(${{ values.entity }})


@router.delete("/{${{ values.entity }}_id}", status_code=204)
async def delete_${{ values.entity }}(${{ values.entity }}_id: int, user: Writer, session: SessionDep) -> None:
    await session.delete(await find(session, ${{ values.entity }}_id))
