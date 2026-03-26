import google.generativeai as genai
from domain.interfaces.ai_service import AIService
from domain.models.dayplan_model import TaskAndTimeLogs, AiRecommendation


class AIServiceImpl(AIService):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def analyze_and_recommend(self, task: TaskAndTimeLogs) -> AiRecommendation:
        # 1. Format the list of time logs into a readable string

        print(f"+++++++++++++++++++++++++++++++++++++++++++++ asking ai for task {task.task_description} ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        def display_times(times):
            ans=[]
            for time in times:
                ans.append(f"- Start Time: {time.start_time}, End Time: {time.end_time}, Note: {time.description or 'N/A'}")
            return "\n".join(ans)

        logs_summary = "\n".join([
            f"- Date: {log.date}, Time Logs:\n{display_times(log.times)}"
            for log in task.time_logs
        ])

        # 2. Build a data-rich prompt
        prompt = f"""
        Analyze the following task and its specific time logs to identify productivity patterns.
        
        TASK DETAILS:
        - Description: {task.task_description}
        - Period: {task.task_start_date} to {task.task_end_date}
        - Hours: {task.task_done_hr} done / {task.task_estimated_hr} estimated
        - Completion: {task.task_completion_rate}% 
        
        DETAILED TIME LOGS:
        {logs_summary}
        
        Return a JSON object with exactly the following keys:
        1. "feedback": A string containing analysis of whether the time spent per session is effective and how it compares to the completion rate.
        2. "recommendations": A string suggesting changes in work habits or schedule based on the log patterns.
        """

        # 3. Requesting JSON for easier parsing
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            print(f"RAW AI RESPONSE: {response.text}")

            import json
            res_data = json.loads(response.text)

            return AiRecommendation(
                feedback=res_data.get("feedback", "No feedback available."),
                recommendations=res_data.get("recommendations", "No recommendations available.")
            )
        except Exception as e:
            print(f"AI Service Error: {str(e)}")
            return AiRecommendation(
                feedback=f"Error during AI analysis: {str(e)}",
                recommendations="Please try again later."
            )