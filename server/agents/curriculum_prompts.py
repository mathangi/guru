# Prompt to generate modules for a given learning goal
MODULE_GENERATION_PROMPT = """
You are an expert curriculum designer AI. Given a learning goal, create a list of modules that are relevant to the goal.

Learning Goal: {learning_goal}

Output the module IDs in a JSON list.
Example Output: ["module_id_1", "module_id_2", "module_id_3"]

Module IDs:
"""

# Prompt to suggest an initial learning path structure based on goals and assessment
INITIAL_PATH_GENERATION_PROMPT = """
You are an expert curriculum designer AI. Given the user's learning goals and their current knowledge assessment, create a structured, step-by-step learning path using the available modules.

User Goals: {user_goals}
Assessment Summary: {assessment_summary}
Available Modules (ID, Name, Prerequisites): {available_modules_summary}

Constraints:
- Ensure all prerequisites for a module are covered before the module itself.
- Prioritize modules directly related to the user's primary goal.
- Exclude modules covering topics the user already knows well (unless needed as a prerequisite for a new topic).
- Order the modules logically for effective learning.

Output the learning path as a JSON list of module IDs in the recommended sequence.
Example Output: ["module_id_1", "module_id_2", "module_id_3"]

Learning Path Module ID List:
"""

# Prompt to adapt an existing path based on recent performance
PATH_ADAPTATION_PROMPT = """
You are an AI learning assistant reviewing a student's progress on their personalized learning path. Based on their recent performance and engagement, suggest adaptations to the remaining path.

Current Learning Path (Remaining Modules): {remaining_modules}
Primary Goal: {primary_goal}
Recent Performance Summary: {performance_summary}
Engagement Issues Noted: {engagement_issues}
Available Modules: {available_modules_summary}

Consider the following adaptations:
- Adding remedial modules if the user struggled significantly with prerequisites.
- Skipping ahead if the user demonstrated mastery beyond the current module.
- Suggesting alternative content types if engagement is low.
- Reordering upcoming modules if performance indicates a different sequence might be better.
- Adding challenge modules if the user is excelling.

Suggest specific changes: Add module [ID], Remove module [ID], Reorder modules [ID1, ID2 -> ID2, ID1], Suggest alternative content for module [ID]. Provide a brief reason for each suggestion.

Suggested Adaptations:
"""
