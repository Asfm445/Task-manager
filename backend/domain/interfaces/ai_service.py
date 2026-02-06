from abc import ABC, abstractmethod
from typing import List
from domain.models.dayplan_model import TaskAndTimeLogs, AiRecommendation


class AIService(ABC):
    @abstractmethod
    async def analyze_and_recommend(self, task: TaskAndTimeLogs) -> AiRecommendation:
        pass