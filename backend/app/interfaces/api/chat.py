import logging
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent
from collections.abc import AsyncIterable
from app.interfaces.schemas import ChatRequest, DeliveryEventData, SourcesEventData, DoneEventData, ErrorEventData
from app.interfaces.dependencies import ContainerDep
from app.application.dto import AnswerQuestionInput, AnswerQuestionOutput, SourceInfo
from app.domain.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()

@router.post("/chats", response_class=EventSourceResponse, response_model=None)
async def chat(
    body: ChatRequest,
    container: ContainerDep
 ) -> AsyncIterable[ServerSentEvent]:

    try: 
        usecase_input: AnswerQuestionInput = AnswerQuestionInput(question=body.message)
        result: AnswerQuestionOutput = await container.answer_question_usecase().execute(input=usecase_input)

        source_info: list[SourceInfo] = result.sources

        async for token in result.token_stream:
            yield ServerSentEvent(data=DeliveryEventData(content=token), retry=5000)

        yield ServerSentEvent(data=SourcesEventData(sources=source_info))

        yield ServerSentEvent(data=DoneEventData(conversation_id=body.conversation_id), event="done")
    
    except ExternalServiceError as e:
        # Known service error — message is safe to expose
        yield ServerSentEvent(data=ErrorEventData(message=str(e)), event="error")
    except Exception as e:
        # Unexpected error — log details, send generic message
        logger.exception("Unexpected error in chat SSE")
        yield ServerSentEvent(data=ErrorEventData(message="Internal server error"), event="error")
