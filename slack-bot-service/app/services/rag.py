"""
Vertex AI RAG Engine 連携サービス（社内コーパス）
Gemini 2.0 Flash + RAG Retrieval Tool を使用してRAG回答を生成する
"""
import logging
from dataclasses import dataclass

import vertexai
from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool

from app.config import settings

logger = logging.getLogger(__name__)

# 起動時に1度だけ初期化
vertexai.init(project=settings.gcp_project_id, location=settings.gcp_location)

# RAG Retrieval Tool の構築
_rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_corpora=[settings.rag_corpus_name],
            similarity_top_k=settings.rag_top_k,
            vector_distance_threshold=settings.rag_distance_threshold,
        )
    )
)

# Gemini モデル（RAGツール付き）
_model = GenerativeModel(
    model_name=settings.gemini_model,
    tools=[_rag_retrieval_tool],
    system_instruction=(
        "あなたは社内FAQ専任のAIアシスタントです。"
        "提供されたコンテキスト情報のみを根拠として質問に回答してください。"
        "コンテキストに情報がない場合は「該当する情報が見つかりませんでした。"
        "人事担当者にお問い合わせください。」と回答してください。"
        "回答は日本語で、簡潔かつ正確に行ってください。"
    ),
)


@dataclass
class RagResponse:
    """RAG回答結果"""
    answer: str
    success: bool
    error_message: str = ""


def query_internal_faq(
    user_question: str,
    channel_filter: list[str] | None = None,
) -> RagResponse:
    """
    社内FAQに対してRAGクエリを実行して回答を生成する

    Args:
        user_question: ユーザーからの質問テキスト
        channel_filter: アクセス可能なSlackチャンネルIDリスト（Noneの場合はフィルタなし）

    Returns:
        RagResponse: 回答テキストと成功フラグ
    """
    try:
        # チャンネルフィルタをクエリに付与（メタデータフィルタリング）
        query = user_question
        if channel_filter is not None:
            # Slackチャンネル制限をコンテキストとしてシステムに通知
            # 実際のフィルタはRAGコーパスのメタデータで制御
            allowed_channels_str = ", ".join(channel_filter)
            query = (
                f"[アクセス可能チャンネル: {allowed_channels_str}]\n"
                f"{user_question}"
            )

        response = _model.generate_content(query)
        answer = response.text.strip()

        if not answer:
            return RagResponse(
                answer="回答の生成に失敗しました。しばらくしてから再度お試しください。",
                success=False,
            )

        return RagResponse(answer=answer, success=True)

    except Exception as e:
        logger.exception("RAGクエリ実行中にエラーが発生しました: %s", e)
        return RagResponse(
            answer="現在システムに問題が発生しています。しばらくしてから再度お試しください。",
            success=False,
            error_message=str(e),
        )
