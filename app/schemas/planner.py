# ZamanRah_BackEnd/app/schemas/planner.py

from pydantic import BaseModel, Field
from typing import List, Optional

class WeeklyGoalInput(BaseModel):
    """
    Represents a single weekly goal provided by the user.
    """
    goal_name: str = Field(..., min_length=1, description="Name of the weekly goal, e.g., 'Learn Python'")
    hours_per_week: int = Field(..., ge=0, description="Hours dedicated to this goal per week, e.g., 10")

class FixedRoutineInput(BaseModel):
    """
    Represents a fixed daily routine provided by the user.
    """
    activity_name: str = Field(..., min_length=1, description="Name of the fixed activity, e.g., 'Gym', 'Language Class'")
    day_of_week: str = Field(..., description="Day of the week for the routine, e.g., 'شنبه', 'یکشنبه'")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Start time of the activity in HH:mm format, e.g., '07:00'")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="End time of the activity in HH:mm format, e.g., '08:30'")

class SleepWakeTimeInput(BaseModel):
    """
    Represents the user's preferred sleep and wake times.
    """
    wake_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Wake up time in HH:mm format, e.g., '07:00'")
    sleep_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Bedtime in HH:mm format, e.g., '23:00'")

class GeneratePlanRequest(BaseModel):
    """
    Request model for generating a comprehensive weekly plan including goals, routines, and sleep times.
    """
    weekly_goals: List[WeeklyGoalInput] = Field(..., min_items=1, description="List of weekly goals provided by the user")
    fixed_routines: List[FixedRoutineInput] = Field([], description="List of fixed daily routines")
    sleep_wake_time: SleepWakeTimeInput = Field(..., description="User's preferred sleep and wake times")


# Define the Activity model first
class Activity(BaseModel):
    title: str
    start_time: str # Assuming HH:mm format, Pydantic will validate string
    end_time: str   # Assuming HH:mm format, Pydantic will validate string
    type: str       # e.g., "Routine", "FixedRoutine", "WeeklyGoal", "Sleep", "Break"

# Define the DailyPlan model, which contains a list of activities
class DailyPlan(BaseModel):
    day_of_week: str
    activities: List[Activity]

# Define the top-level response model
# This model now correctly expects a 'message' string and a 'daily_plans' list of DailyPlan objects
class GeneratePlanResponse(BaseModel):
    message: str
    daily_plans: List[DailyPlan]# حالا Pydantic این ساختار را انتظار داردily_plans: List[DailyPlanOutput] = Field(..., description="List of generated daily plans for the week")