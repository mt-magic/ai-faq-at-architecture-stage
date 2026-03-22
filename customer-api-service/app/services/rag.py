"""
Vertex AI RAG Engine 連携サービス（顧客コーパス）
WordPressサイト情報を基にした顧客向けFAQ回答を生成する
"""
import logging
from dataclasses import dataclass

import vertexai
from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool

from app.config import settings

logger = logging.getLogger(__name__)

vertexai.init(project=settings.gcp_project_id, location=settings.gcp_location)

_rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_corpora=[settings.rag_corpus_name],
            similarity_top_k=settings.rag_top_k,
            vector_distance_threshold=settings.rag_distance_threshold,
        )
    )
)

_model = GenerativeModel(
    model_name=settings.gemini_model,
    tools=[_rag_retrieval_tool],
    system_instruction=(
        "あなたはWebサイトのサポートAIです。"
        "提供されたWebサイトの情報のみを根拠として質問に回答してください。"
        "情報がない場合は「ご不明な点はお問い合わせフォームよりご連絡ください。」と案内してください。"
        "回答は日本語で、丁寧かつ簡潔に行ってください。"
    ),
)


@dataclass
class RagResponse:
    """RAG回答結果"""
    answer: str
    success: bool
    error_message: str = ""


def query_customer_faq(user_question: str) -> RagResponse:
    """
    顧客向けFAQに対してRAGクエリを実行して回答を生成する

    Args:
        user_question: ユーザーからの質問テキスト

    Returns:
        RagResponse: 回答テキストと成功フラグ
    """
    try:
        response = _model.generate_content(user_question)
        answer = response.text.strip()

        if not answer:
            return RagResponse(
                answer="回答の生成に失敗しました。お問い合わせフォームよりご連絡ください。",
                success=False,
            )

        return RagResponse(answer=answer, success=True)

    except Exception as e:
        logger.exception("顧客RAGクエリ実行中にエラーが発生しました: %s", e)
        return RagResponse(
            answer="現在システムに問題が発生しています。お問い合わせフォームよりご連絡ください。",
            success=False,
            error_message=str(e),
        )
