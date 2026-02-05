"""Chat API endpoints - 전문가와 대화."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from clora.api.deps import AI, DB, CurrentUser, Knowledge, Memory
from clora.models.conversation import Conversation, Message, MessageRole
from clora.models.expert import Expert
from clora.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: DB,
    current_user: CurrentUser,
    ai_service: AI,
    knowledge_service: Knowledge,
    memory_service: Memory,
) -> ChatResponse:
    """Send a message to an expert and get a response.

    This is the main chat endpoint that:
    1. Retrieves relevant knowledge from the expert's knowledge base (RAG)
    2. Retrieves relevant memories from user's memory
    3. Generates a response using the AI service
    4. Optionally saves important information to memory
    """
    # Get expert
    result = await db.execute(
        select(Expert).where(Expert.id == chat_request.expert_id, Expert.is_active == True)
    )
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    # Get or create conversation
    conversation: Conversation
    if chat_request.conversation_id:
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == chat_request.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            expert_id=chat_request.expert_id,
            title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
        )
        db.add(conversation)
        await db.flush()
        conversation.messages = []

    # Get conversation history
    conversation_history = []
    for msg in conversation.messages[-10:]:  # Last 10 messages for context
        conversation_history.append({
            "role": msg.role.value,
            "content": msg.content,
        })

    # Get knowledge context (RAG)
    knowledge_context = await knowledge_service.get_context_for_chat(
        expert_id=expert.id,
        query=chat_request.message,
        n_results=3,
    )

    # Get memory context
    memory_context = None
    if chat_request.include_memory:
        memory_context = await memory_service.get_context_for_chat(
            user_id=current_user.id,
            query=chat_request.message,
            expert_id=expert.id,
            n_results=3,
        )

    # Generate AI response
    ai_response = await ai_service.chat(
        message=chat_request.message,
        expert=expert,
        conversation_history=conversation_history,
        knowledge_context=knowledge_context,
        memory_context=memory_context,
        thinking_mode=chat_request.thinking_mode,
    )

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=chat_request.message,
    )
    db.add(user_message)

    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=ai_response.content,
        reasoning_content=ai_response.reasoning_content,
        input_tokens=ai_response.input_tokens,
        output_tokens=ai_response.output_tokens,
    )
    db.add(assistant_message)
    await db.flush()

    # Analyze conversation for memory
    memory_saved = False
    try:
        conversation_text = f"사용자: {chat_request.message}\n{expert.name}: {ai_response.content}"
        memory_data = await ai_service.analyze_for_memory(conversation_text)

        if memory_data:
            await memory_service.save_memory(
                db=db,
                user_id=current_user.id,
                title=memory_data["title"],
                content=memory_data["content"],
                category=memory_data.get("category"),
                expert_id=expert.id,
                conversation_id=conversation.id,
                importance=memory_data.get("importance", 5),
            )
            memory_saved = True
    except Exception:
        pass  # Don't fail chat if memory save fails

    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageResponse(
            id=assistant_message.id,
            role=assistant_message.role,
            content=assistant_message.content,
            reasoning_content=assistant_message.reasoning_content,
            created_at=assistant_message.created_at,
        ),
        expert_name=expert.name,
        memory_saved=memory_saved,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: DB,
    current_user: CurrentUser,
    expert_id: int | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
) -> list[Conversation]:
    """List user's conversations."""
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.user_id == current_user.id)
    )

    if expert_id:
        query = query.where(Conversation.expert_id == expert_id)

    query = query.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: DB,
    current_user: CurrentUser,
) -> Conversation:
    """Get a specific conversation with messages."""
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """Delete a conversation."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await db.delete(conversation)
