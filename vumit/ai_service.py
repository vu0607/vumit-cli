import os
import json
import google.generativeai as genai

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise Exception("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=self.api_key)
        try:
            # Configure and validate the model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini model: {str(e)}")

    def analyze_commits(self, commits):
        """Analyze feature branch commits and provide recommendations"""
        commits_summary = self._format_commits_for_prompt(commits)

        prompt = f"""You are a code review expert. Analyze these feature branch commits and provide feedback in JSON format.

Commits to analyze:
{commits_summary}

Focus on:
1. A brief summary of the changes in these commits
2. Any potential issues or risks in the implementation
3. Recommendations for improvement

Respond ONLY with a JSON object in this exact format, no other text:
{{
    "summary": "Brief overview of changes in the feature branch",
    "issues": ["List of potential issues"],
    "recommendations": ["List of recommendations"]
}}"""

        try:
            response = self.model.generate_content(prompt)
            if not response.text:
                raise Exception("Empty response from Gemini API")

            # Extract JSON content
            try:
                # First try to parse the entire response
                return json.loads(response.text)
            except:
                # If that fails, try to extract JSON between { and }
                text = response.text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
                raise Exception("Could not extract valid JSON from response")

        except Exception as e:
            raise Exception(f"Failed to analyze commits: {str(e)}")

    def generate_mr_description(self, commits, context):
        """Generate a merge request description based on branch commits"""
        commits_summary = self._format_commits_for_prompt(commits)
        context_summary = json.dumps(context, indent=2)

        prompt = f"""You are a technical writer expert. Generate a merge request description for these feature branch commits.

Repository Context:
{context_summary}

Commits to analyze:
{commits_summary}

Generate a detailed merge request description following this exact format:

1. What does this MR do and why?
- Summarize the purpose and main goals
- Explain what changes were made and why
- Mention any specific problems this MR solves

2. References
- Include any relevant Jira tickets or issue numbers found in commit messages
- Link any related merge requests
- Note any documentation that needs updating

MR Acceptance Checklist:
- Code review requirements (e.g., number of approvals needed)
- Linting and formatting checks pass
- Unit tests pass
- Integration tests pass
- Documentation is updated

3. How to set up and validate locally
- List the steps needed to test these changes
- Include any new environment variables or configuration needed
- Specify test cases or scenarios to verify
- Note any potential side effects to watch for

Respond ONLY with a JSON object in this exact format, no other text:
{{
    "purpose": "Summary of what the MR does and why",
    "changes_explanation": ["List of key changes and reasons"],
    "problems_solved": ["List of problems this MR addresses"],
    "references": {{
        "jira_tickets": ["List of Jira tickets found"],
        "related_mrs": ["List of related MRs"],
        "documentation": ["List of documentation that needs updating"]
    }},
    "acceptance_checklist": ["List of items that need to be checked before merging"],
    "setup_steps": ["List of steps to test locally"],
    "validation_steps": ["List of specific test cases to verify"],
    "side_effects": ["List of potential side effects to watch for"]
}}"""

        try:
            response = self.model.generate_content(prompt)
            if not response.text:
                raise Exception("Empty response from Gemini API")

            # Extract JSON content
            try:
                # First try to parse the entire response
                return json.loads(response.text)
            except:
                # If that fails, try to extract JSON between { and }
                text = response.text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
                raise Exception("Could not extract valid JSON from response")

        except Exception as e:
            raise Exception(f"Failed to generate merge request description: {str(e)}")

    def _format_commits_for_prompt(self, commits):
        """Format commits into a readable string for the prompt"""
        formatted = []
        for commit in commits:
            formatted.append(f"Commit: {commit['hash']}")
            formatted.append(f"Author: {commit['author']}")
            formatted.append(f"Date: {commit['date']}")
            formatted.append(f"Message: {commit['message']}")
            formatted.append("Changes:")
            for change in commit['changes']:
                formatted.append(f"  File: {change['file']}")
                formatted.append(f"  Type: {change['change_type']}")
                formatted.append("  Diff:")
                formatted.append(change['diff'])
            formatted.append("-" * 40)
        return "\n".join(formatted)