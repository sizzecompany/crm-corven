# Documents

## Telas necessárias
1. **Biblioteca de documentos**
2. **Upload de documento**

## Componentes necessários
- Lista/tabela de documentos
- Drag-and-drop uploader
- Indicador de progresso de upload
- Ações por item (excluir)

## Dados necessários por tela
### 1) Biblioteca de documentos
- **API:** `GET /api/v1/documents`
- **Dados:** `DocumentOut[]`
- **Ação de remoção:** `DELETE /api/v1/documents/{doc_id}`

### 2) Upload de documento
- **API:** `POST /api/v1/documents/upload` (`multipart/form-data`)
- **Campo:** `file`
- **Resposta:** `DocumentOut`
