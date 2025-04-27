import unittest
from unittest.mock import Mock, patch
from ..agents.curriculum_agent import CurriculumAgent

class TestCurriculumAgent(unittest.TestCase):
    def setUp(self):
        self.mock_kg = Mock()
        self.agent = CurriculumAgent(knowledge_source=self.mock_kg)

    def test_create_learning_path_with_some_knowledge(self):
        """Test creating a path when user already knows some topics"""
        mock_assessment = {
            'known_topics': ['variables'],
            'confidence': {'variables': 0.9},
            'learning_style': 'visual'
        }
        mock_goals = ["learn python basics"]

        # Mock knowledge graph responses
        self.mock_kg.get_module_details.return_value = {
            "name": "Test Module",
            "estimated_time_hrs": 1
        }
        self.mock_kg.get_prerequisites.return_value = []

        path = self.agent.create_learning_path("user123", mock_assessment, mock_goals)

        self.assertIsNotNone(path)
        self.assertEqual(path["user_id"], "user123")
        self.assertEqual(path["goal"], "learn python basics")
        self.assertIn("modules", path)

    def test_create_learning_path_no_prerequisites(self):
        """Test creating a path when user has no prior knowledge"""
        mock_assessment = {
            'known_topics': [],
            'learning_style': 'kinesthetic'
        }
        mock_goals = ["learn control flow"]

        # Mock knowledge graph responses
        self.mock_kg.get_module_details.return_value = {
            "name": "Control Flow",
            "estimated_time_hrs": 2
        }
        self.mock_kg.get_prerequisites.return_value = ["variables", "operators"]

        path = self.agent.create_learning_path("user456", mock_assessment, mock_goals)

        self.assertIsNotNone(path)
        self.assertEqual(path["user_id"], "user456")
        self.assertTrue(len(path["modules"]) > 1)  # Should include prerequisites

    def test_create_learning_path_with_prerequisites_met(self):
        """Test creating a path when prerequisites are already known"""
        mock_assessment = {
            'known_topics': ['variables', 'data_types', 'operators'],
            'learning_style': 'textual'
        }
        mock_goals = ["learn control flow"]

        # Mock knowledge graph responses
        self.mock_kg.get_module_details.return_value = {
            "name": "Control Flow",
            "estimated_time_hrs": 2
        }
        self.mock_kg.get_prerequisites.return_value = ["variables", "operators"]

        path = self.agent.create_learning_path("user789", mock_assessment, mock_goals)

        self.assertIsNotNone(path)
        self.assertEqual(path["user_id"], "user789")
        # Should only include new modules, not prerequisites
        self.assertTrue(all(m["module_id"] not in mock_assessment["known_topics"] 
                          for m in path["modules"]))

if __name__ == '__main__':
    unittest.main()