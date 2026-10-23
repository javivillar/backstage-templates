"""Endpoints of the ${{ values.entities }}. Reading needs a signed-in user with a ${{ values.name }} role; writing, the admin one."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from refresquito_fastapi import ConflictError, NotFoundError, Page, PageParamsDep, User, lineage, require_roles
from refresquito_fastapi.db import SessionDep, paginate
{%- if values.flows %}
from refresquito_fastapi.platform.flows import FlowsDep  # block flows
{%- endif %}
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ${{ values.entityTitle }}, ${{ values.entityTitle }}Status
from .schemas import ${{ values.entityTitle }}In, ${{ values.entityTitle }}Out

VIEWER, ADMIN = "${{ values.name }}-viewer", "${{ values.name }}-admin"
Reader = Annotated[User, Depends(require_roles(VIEWER, ADMIN))]
Writer = Annotated[User, Depends(require_roles(ADMIN))]

router = APIRouter(prefix="/api/${{ values.entities }}", tags=["${{ values.entities }}"])


async def find(session: AsyncSession, ${{ values.entity }}_id: int) -> ${{ values.entityTitle }}:
    ${{ values.entity }} = await session.get(${{ values.entityTitle }}, ${{ values.entity }}_id)
    if ${{ values.entity }} is None:
        raise NotFoundError(f"${{ values.entityTitle }} {${{ values.entity }}_id} does not exist")
    return ${{ values.entity }}


async def check_name_is_free(session: AsyncSession, name: str, except_id: int | None = None) -> None:
    other = await session.scalar(select(${{ values.entityTitle }}).where(${{ values.entityTitle }}.name == name))
    if other is not None and other.id != except_id:
        raise ConflictError(f"There is already a ${{ values.entity }} called {name}", code="${{ values.entity }}_name_taken")


@router.get("", openapi_extra=lineage.source("table:${{ values.entity }}"))
async def list_${{ values.entities }}(
    user: Reader,
    session: SessionDep,
    params: PageParamsDep,
    status: Annotated[${{ values.entityTitle }}Status | None, Query(description="Only the ${{ values.entities }} in this status")] = None,
    category: Annotated[str | None, Query(description="Only this category")] = None,
) -> Page[${{ values.entityTitle }}Out]:
    statement = select(${{ values.entityTitle }}).order_by(${{ values.entityTitle }}.name)
    if status:
        statement = statement.where(${{ values.entityTitle }}.status == status)
    if category:
        statement = statement.where(${{ values.entityTitle }}.category == category.strip())
    return await paginate(session, statement, params)


@router.get("/{${{ values.entity }}_id}", openapi_extra=lineage.source("table:${{ values.entity }}"))
async def get_${{ values.entity }}(${{ values.entity }}_id: int, user: Reader, session: SessionDep) -> ${{ values.entityTitle }}Out:
    return ${{ values.entityTitle }}Out.model_validate(await find(session, ${{ values.entity }}_id))


@router.post("", status_code=201, openapi_extra=lineage.target("table:${{ values.entity }}"))
async def create_${{ values.entity }}(body: ${{ values.entityTitle }}In, user: Writer, session: SessionDep{% if values.flows %}, flows: FlowsDep{% endif %}) -> ${{ values.entityTitle }}Out:
    await check_name_is_free(session, body.name)
    ${{ values.entity }} = ${{ values.entityTitle }}(**body.model_dump(), created_by=user.username)
    session.add(${{ values.entity }})
    await session.flush()
    await session.refresh(${{ values.entity }})
{%- if values.flows %}
    await flows.publish("${{ values.entity }}.created", {"id": ${{ values.entity }}.id, "name": ${{ values.entity }}.name, "category": ${{ values.entity }}.category})  # block flows
{%- endif %}
    return ${{ values.entityTitle }}Out.model_validate(${{ values.entity }})


@router.put("/{${{ values.entity }}_id}", openapi_extra=lineage.target("table:${{ values.entity }}"))
async def update_${{ values.entity }}(${{ values.entity }}_id: int, body: ${{ values.entityTitle }}In, user: Writer, session: SessionDep) -> ${{ values.entityTitle }}Out:
    ${{ values.entity }} = await find(session, ${{ values.entity }}_id)
    await check_name_is_free(session, body.name, except_id=${{ values.entity }}_id)
    for field, value in body.model_dump().items():
        setattr(${{ values.entity }}, field, value)
    await session.flush()
    return ${{ values.entityTitle }}Out.model_validate(${{ values.entity }})


@router.delete("/{${{ values.entity }}_id}", status_code=204, openapi_extra=lineage.target("table:${{ values.entity }}"))
async def delete_${{ values.entity }}(${{ values.entity }}_id: int, user: Writer, session: SessionDep) -> None:
    await session.delete(await find(session, ${{ values.entity }}_id))
