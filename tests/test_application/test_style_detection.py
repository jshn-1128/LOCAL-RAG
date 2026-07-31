from app.application.chat.service import ChatService
from app.application.prompt_builder import AnswerStyle


class TestStyleDetection:
    def test_explanation_what_is(self):
        assert (
            ChatService._detect_answer_style("What is RAG?") == AnswerStyle.EXPLANATION
        )

    def test_explanation_define(self):
        assert (
            ChatService._detect_answer_style("Define machine learning.")
            == AnswerStyle.EXPLANATION
        )

    def test_explanation_explain(self):
        assert (
            ChatService._detect_answer_style("Explain how Docker works.")
            == AnswerStyle.EXPLANATION
        )

    def test_explanation_describe(self):
        assert (
            ChatService._detect_answer_style("Describe neural networks.")
            == AnswerStyle.EXPLANATION
        )

    def test_summary_summarize(self):
        assert (
            ChatService._detect_answer_style("Summarize the document.")
            == AnswerStyle.SUMMARY
        )

    def test_summary_overview(self):
        assert (
            ChatService._detect_answer_style("Give me an overview of ML.")
            == AnswerStyle.SUMMARY
        )

    def test_summary_key_points(self):
        assert (
            ChatService._detect_answer_style("What are the key points?")
            == AnswerStyle.SUMMARY
        )

    def test_list_list(self):
        assert ChatService._detect_answer_style("List the topics.") == AnswerStyle.LIST

    def test_list_types(self):
        assert (
            ChatService._detect_answer_style("What types of algorithms?")
            == AnswerStyle.LIST
        )

    def test_list_examples(self):
        assert (
            ChatService._detect_answer_style("Examples of vector databases.")
            == AnswerStyle.LIST
        )

    def test_comparison_compare(self):
        assert (
            ChatService._detect_answer_style("Compare Python and JavaScript.")
            == AnswerStyle.COMPARISON
        )

    def test_comparison_difference(self):
        assert (
            ChatService._detect_answer_style(
                "What is the difference between Git and Docker?"
            )
            == AnswerStyle.COMPARISON
        )

    def test_comparison_versus(self):
        assert (
            ChatService._detect_answer_style("RAG vs fine-tuning.")
            == AnswerStyle.COMPARISON
        )

    def test_timeline(self):
        assert (
            ChatService._detect_answer_style("Timeline of RAG development.")
            == AnswerStyle.TIMELINE
        )

    def test_chronological(self):
        assert (
            ChatService._detect_answer_style("Put the events in chronological order.")
            == AnswerStyle.TIMELINE
        )

    def test_procedure_how_to(self):
        assert (
            ChatService._detect_answer_style("How to use Git rebase?")
            == AnswerStyle.PROCEDURE
        )

    def test_procedure_steps(self):
        assert (
            ChatService._detect_answer_style("Steps to set up Docker.")
            == AnswerStyle.PROCEDURE
        )

    def test_procedure_guide(self):
        assert (
            ChatService._detect_answer_style("Guide to installing FastAPI.")
            == AnswerStyle.PROCEDURE
        )

    def test_pros_cons_pros(self):
        assert (
            ChatService._detect_answer_style("What are the pros and cons of RAG?")
            == AnswerStyle.PROS_CONS
        )

    def test_pros_cons_advantages(self):
        assert (
            ChatService._detect_answer_style("Advantages and disadvantages of Python.")
            == AnswerStyle.PROS_CONS
        )

    def test_default_fallback(self):
        assert (
            ChatService._detect_answer_style("What do people say about this?")
            == AnswerStyle.DEFAULT
        )

    def test_default_tell_me(self):
        assert (
            ChatService._detect_answer_style("Tell me about the project.")
            == AnswerStyle.DEFAULT
        )


class TestStyleFormatInPrompt:
    def test_style_injected_into_system_prompt(self):
        from uuid import UUID

        from app.application.prompt_builder import _STYLE_FORMAT, PromptBuilder
        from app.domain.models.chunk import Chunk

        builder = PromptBuilder()
        chunk = Chunk(
            id=UUID(int=0), document_id=UUID(int=0), content="Test content.", index=0
        )

        for style in [
            AnswerStyle.EXPLANATION,
            AnswerStyle.COMPARISON,
            AnswerStyle.PROCEDURE,
            AnswerStyle.LIST,
            AnswerStyle.SUMMARY,
            AnswerStyle.TIMELINE,
            AnswerStyle.PROS_CONS,
        ]:
            messages = builder.build_chat_messages(
                query="Test question?",
                chunks=[chunk],
                scores=[0.9],
                style=style,
            )
            system = messages[0]["content"]
            assert "RESPONSE" in system
            assert _STYLE_FORMAT[style][:20] in system

    def test_default_style_no_format_injection(self):
        from uuid import UUID

        from app.application.prompt_builder import PromptBuilder
        from app.domain.models.chunk import Chunk

        builder = PromptBuilder()
        chunk = Chunk(
            id=UUID(int=0), document_id=UUID(int=0), content="Test content.", index=0
        )

        messages = builder.build_chat_messages(
            query="Test question?",
            chunks=[chunk],
            scores=[0.9],
            style=AnswerStyle.DEFAULT,
        )
        system = messages[0]["content"]
        assert "RESPONSE" not in system

    def test_no_style_no_injection(self):
        from uuid import UUID

        from app.application.prompt_builder import PromptBuilder
        from app.domain.models.chunk import Chunk

        builder = PromptBuilder()
        chunk = Chunk(
            id=UUID(int=0), document_id=UUID(int=0), content="Test content.", index=0
        )

        messages = builder.build_chat_messages(
            query="Test question?",
            chunks=[chunk],
            scores=[0.9],
        )
        system = messages[0]["content"]
        assert "RESPONSE" not in system
