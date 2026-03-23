"""
CRM Corven — Documents module (upload + RAG).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

import boto3
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import CurrentUser
from app.models.document import Document

settings = get_settings()


# ── Schemas ──────────────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: str
    filename: str
    original_name: str
    content_type: str | None = None
    file_size: int | None = None
    embedding_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── S3 Client ────────────────────────────────────────────────────────────────

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


# ── Service ──────────────────────────────────────────────────────────────────

async def upload_document(
    db: AsyncSession, tenant_id: UUID, user_id: UUID, file: UploadFile
) -> Document:
    file_id = str(uuid.uuid4())
    s3_key = f"tenants/{tenant_id}/documents/{file_id}/{file.filename}"

    # Upload to S3
    s3 = get_s3_client()
    content = await file.read()

    try:
        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
    except Exception:
        pass  # Bucket already exists

    s3.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key,
        Body=content,
        ContentType=file.content_type or "application/octet-stream",
    )

    doc = Document(
        tenant_id=tenant_id,
        filename=file_id,
        original_name=file.filename or "unknown",
        s3_key=s3_key,
        content_type=file.content_type,
        file_size=len(content),
        embedding_status="pending",
        uploaded_by=user_id,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    # TODO: Dispatch Celery task for text extraction + embedding
    return doc


async def list_documents(
    db: AsyncSession, tenant_id: UUID, skip: int = 0, limit: int = 50
) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def delete_document(db: AsyncSession, tenant_id: UUID, doc_id: UUID) -> None:
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.tenant_id == tenant_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise NotFoundError("Document", str(doc_id))

    # Delete from S3
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=doc.s3_key)
    except Exception:
        pass

    await db.delete(doc)
    await db.flush()


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/documents", tags=["Documents / RAG"])


def _out(d: Document) -> DocumentOut:
    return DocumentOut(
        id=str(d.id), filename=d.filename, original_name=d.original_name,
        content_type=d.content_type, file_size=d.file_size,
        embedding_status=d.embedding_status, created_at=d.created_at,
    )


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document_endpoint(
    current_user: CurrentUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document for RAG indexation."""
    doc = await upload_document(db, current_user.tenant_id, current_user.id, file)
    return _out(doc)


@router.get("/", response_model=list[DocumentOut])
async def list_documents_endpoint(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    docs = await list_documents(db, current_user.tenant_id)
    return [_out(d) for d in docs]


@router.delete("/{doc_id}", status_code=204)
async def delete_document_endpoint(
    doc_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await delete_document(db, current_user.tenant_id, doc_id)
