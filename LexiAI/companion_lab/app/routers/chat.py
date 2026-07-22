import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest, ChatResponse
from app.services.ollama import chat, OllamaError
from app.services.memory import save_message

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    conversation_id = str(uuid.uuid4())
    user_message = {"role": "user", "content": request.message}
    save_message(conversation_id, "user", request.message)

    try:
        response_lines = list(chat([user_message]))
        reply = "".join(response_lines).strip()
    except OllamaError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    save_message(conversation_id, "assistant", reply)
    return ChatResponse(reply=reply, conversation_id=conversation_id)
