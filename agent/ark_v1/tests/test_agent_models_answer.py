import unittest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from ark_v1.data_models.agent_models import FinalAnswerEntityList
from ark_v1.ark_v1 import ARK_V1
from ark_v1.data_models.agent_models import (
    FinalAnswerYesNo,
    QuestionTypes,
    RuntimeState,
)


class TestFinalAnswerEntityList(unittest.TestCase):
    def test_accepts_entity_list(self):
        result = FinalAnswerEntityList(
            arisedQuestion="",
            ambigoutyOfRequest=False,
            justification="The entity was found in the retrieved triples.",
            answer=["Alzheimer's disease (Q11081)"],
        )

        self.assertEqual(
            result.answer,
            ["Alzheimer's disease (Q11081)"],
        )

    def test_accepts_none_for_unknown_answer(self):
        result = FinalAnswerEntityList(
            arisedQuestion="",
            ambigoutyOfRequest=False,
            justification="The retrieved graph information is insufficient.",
            answer=None,
        )

        self.assertIsNone(result.answer)

    def test_distinguishes_empty_list_from_none(self):
        empty_result = FinalAnswerEntityList(
            arisedQuestion="",
            ambigoutyOfRequest=False,
            justification="The query has no matching entities.",
            answer=[],
        )

        unknown_result = FinalAnswerEntityList(
            arisedQuestion="",
            ambigoutyOfRequest=False,
            justification="The answer cannot be determined.",
            answer=None,
        )

        self.assertEqual(empty_result.answer, [])
        self.assertIsNone(unknown_result.answer)

    def test_rejects_missing_answer(self):
        with self.assertRaises(ValidationError):
            FinalAnswerEntityList(
                arisedQuestion="",
                ambigoutyOfRequest=False,
                justification="No answer field was provided.",
            )

    def test_rejects_string_instead_of_list(self):
        with self.assertRaises(ValidationError):
            FinalAnswerEntityList(
                arisedQuestion="",
                ambigoutyOfRequest=False,
                justification="Incorrect answer format.",
                answer="Alzheimer's disease (Q11081)",
            )

class TestGenerateAnswer(unittest.TestCase):
    def check_answer_node(self, question_type, answer_model, value):
        agent = ARK_V1()
        agent._add_prompt_templates()
        agent._question_type = question_type

        expected = answer_model(
            ambigoutyOfRequest=False,
            justification="Simulated answer for testing.",
            answer=value,
        )

        fake_llm = Mock()
        fake_llm.with_structured_output.return_value.invoke.return_value = (
            expected
        )

        state = RuntimeState(question="Test question")

        with patch.object(agent, "_llm", fake_llm):
            result = agent.graph.nodes["generate_answer"].invoke(state)

        fake_llm.with_structured_output.assert_called_once_with(
            answer_model
        )
        self.assertEqual(result.finalAnswer.answer, value)

    def test_entity_list_uses_entity_model(self):
        self.check_answer_node(
            QuestionTypes.ENTITY_LIST,
            FinalAnswerEntityList,
            ["Example entity (Q123)"],
        )

    def test_yes_no_still_uses_boolean_model(self):
        self.check_answer_node(
            QuestionTypes.YES_NO,
            FinalAnswerYesNo,
            True,
        )

    def test_unsupported_question_type_raises(self):
        agent = ARK_V1()
        agent._question_type = QuestionTypes.OTHER

        with self.assertRaises(NotImplementedError):
            agent.graph.nodes["generate_answer"].invoke(
                RuntimeState(question="Test question")
            )

if __name__ == "__main__":
    unittest.main()