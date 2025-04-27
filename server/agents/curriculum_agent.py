import logging
from typing import List, Dict, Set, Optional

AssessmentOutput = Dict
LearningModule = Dict
LearningPath = Dict

from . import knowledge_graph as kg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurriculumAgent:
    """
    Agent responsible for designing and adapting personalized learning paths.
    """

    def __init__(self, knowledge_source=kg):
        """
        Initializes the Curriculum Agent.

        Args:
            knowledge_source: Module providing access to subject structure,
                              prerequisites, etc. (defaults to knowledge_graph.py)
        """
        self.knowledge_source = knowledge_source
        logger.info("Curriculum Agent initialized.")

    def create_learning_path(self, user_id: str, assessment_output: AssessmentOutput, user_goals: List[str]) -> Optional[LearningPath]:
        """
        Designs an initial learning path based on assessment and goals.

        Args:
            user_id: The ID of the user.
            assessment_output: Output from the Assessment Agent, detailing known topics,
                               strengths, weaknesses, confidence scores.
                               Example: {'known_topics': ['variables'], 'confidence': {'variables': 0.9}, 'learning_style': 'visual'}
            user_goals: A list of learning goals provided by the user (e.g., ["learn python basics", "understand functions"]).

        Returns:
            A LearningPath dictionary/object, or None if path generation fails.
            Example LearningPath:
            {
                'user_id': user_id,
                'goal': primary_goal, # The main goal being addressed
                'modules': [
                    {'module_id': 'data_types', 'name': 'Basic Data Types', 'status': 'pending', 'estimated_time_hrs': 1},
                    {'module_id': 'operators', 'name': 'Operators', 'status': 'pending', 'estimated_time_hrs': 1},
                    # ... other modules
                ],
                'current_module_index': 0
            }
        """
        logger.info(f"Creating learning path for user {user_id} with goals: {user_goals}")
        logger.debug(f"Assessment output: {assessment_output}")

        known_topics: Set[str] = set(assessment_output.get("known_topics", []))
        primary_goal = user_goals[0] if user_goals else "Default Learning Goal" # Handle multiple goals later

        # 1. Identify Target Modules based on Goals
        target_module_ids: List[str] = self.knowledge_source.find_modules_by_goal(primary_goal)
        if not target_module_ids:
            
            logger.warning(f"Could not find relevant modules for goal: {primary_goal}")
            # Maybe default to a foundational module or use LLM to interpret goal
            target_module_ids = ["python_basics"] # Fallback example

        # 2. Determine Required Modules (including prerequisites)
        required_modules: Set[str] = set()
        modules_to_explore: List[str] = list(target_module_ids)
        processed: Set[str] = set() # To avoid infinite loops in cyclic graphs (if any)

        while modules_to_explore:
            current_module_id = modules_to_explore.pop(0)
            if current_module_id in processed:
                continue
            processed.add(current_module_id)

            # Add the module itself if it's not already known
            if current_module_id not in known_topics:
                 details = self.knowledge_source.get_module_details(current_module_id)
                 if details: # Only add if module exists in our knowledge base
                    required_modules.add(current_module_id)

                    # Add its prerequisites to the exploration list
                    prereqs = self.knowledge_source.get_prerequisites(current_module_id)
                    for prereq_id in prereqs:
                        if prereq_id not in processed and prereq_id not in known_topics:
                            modules_to_explore.append(prereq_id)
                 else:
                    logger.warning(f"Module ID '{current_module_id}' not found in knowledge source.")


        # 3. Sort Modules Topologically (based on prerequisites)
        # Basic topological sort implementation
        sorted_module_ids: List[str] = []
        modules_to_sort: Set[str] = required_modules.copy()
        satisfied_nodes: Set[str] = known_topics.copy() # Start with known topics

        while modules_to_sort:
            added_in_pass = False
            nodes_to_add_this_pass = set()

            for module_id in list(modules_to_sort): # Iterate over a copy
                prereqs = set(self.knowledge_source.get_prerequisites(module_id))
                # Check if all prerequisites are satisfied (either known or already added to sorted list)
                if prereqs.issubset(satisfied_nodes):
                    nodes_to_add_this_pass.add(module_id)
                    added_in_pass = True

            if not added_in_pass and modules_to_sort:
                # Cycle detected or missing prerequisite link! Handle error.
                logger.error(f"Could not resolve dependencies for modules: {modules_to_sort}. Cycle or missing prerequisite?")
                # For now, add remaining alphabetically to avoid infinite loop, but log error
                remaining_sorted = sorted(list(modules_to_sort))
                sorted_module_ids.extend(remaining_sorted)
                logger.warning(f"Breaking sort loop due to potential cycle/issue. Added {remaining_sorted}")
                break

            # Add the determined nodes to the sorted list and update satisfied nodes
            # Sort alphabetically within a pass for consistent ordering
            sorted_pass_nodes = sorted(list(nodes_to_add_this_pass))
            sorted_module_ids.extend(sorted_pass_nodes)
            satisfied_nodes.update(sorted_pass_nodes)
            modules_to_sort -= nodes_to_add_this_pass


        # 4. Format the Learning Path Output
        learning_path_modules: List[LearningModule] = []
        for module_id in sorted_module_ids:
            details = self.knowledge_source.get_module_details(module_id)
            if details:
                learning_path_modules.append({
                    "module_id": module_id,
                    "name": details.get("name", module_id),
                    "status": "pending", # Initial status
                    "estimated_time_hrs": details.get("estimated_time_hrs"),
                    # Add other relevant details like description if needed by frontend
                })

        if not learning_path_modules:
             logger.warning(f"No modules generated for user {user_id} and goal '{primary_goal}'. Maybe goal already met?")
             # Return an empty path or a specific message? For now return None.
             return None


        learning_path: LearningPath = {
            "user_id": user_id,
            "goal": primary_goal,
            "modules": learning_path_modules,
            "current_module_index": 0, # Start at the first module
            "assessment_snapshot": assessment_output, # Store assessment context used for this path
            "user_goals_snapshot": user_goals # Store goals used for this path
        }

        logger.info(f"Successfully created learning path for user {user_id} with {len(learning_path_modules)} modules.")
        return learning_path

    def adapt_learning_path(self, current_path: LearningPath, user_performance: Dict, engagement_data: Dict) -> Optional[LearningPath]:
        """
        Adapts the existing learning path based on user performance and engagement.
        (Placeholder - Requires more complex logic)

        Args:
            current_path: The user's current LearningPath object/dict.
            user_performance: Data from Practice/Assessment Agents (e.g., quiz scores, newly mastered topics).
            engagement_data: Data from Motivation Agent (e.g., time spent, skipped modules).

        Returns:
            An updated LearningPath object/dict, or None if no adaptation is needed.
        """
        logger.info(f"Attempting to adapt learning path for user {current_path.get('user_id')}")

        # TODO: Implement adaptation logic:
        # 1. Identify newly mastered topics from user_performance.
        # 2. Check if current module performance suggests needing remedial help or skipping ahead.
        # 3. Analyze engagement data for signs of boredom or struggle.
        # 4. Re-evaluate prerequisites based on new knowledge.
        # 5. Potentially re-run parts of the create_learning_path logic with updated known_topics.
        # 6. Consider suggesting alternative content types based on engagement/learning style.
        # 7. If using LLMs, could use prompts here to suggest adaptations.

        logger.warning("Adaptation logic is not fully implemented yet.")
        # For now, just return the original path
        return current_path

# Example Usage (for testing purposes)
if __name__ == '__main__':
    agent = CurriculumAgent()