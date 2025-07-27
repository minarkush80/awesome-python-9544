import logging
import json
from openai import OpenAI
from typing import List, Dict, Any
from fastapi import HTTPException, status  # Import HTTPException and status

from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_daily_plans_from_goals(plan_input: Dict[str, Any]) -> Dict[str, Any]:  # Changed return type
    client = OpenAI(base_url=settings.OPENAI_API_URL, api_key=settings.OPENAI_API_KEY)

    sleep_time = plan_input['sleep_wake_time']['sleep_time']
    wake_time = plan_input['sleep_wake_time']['wake_time']
    fixed_routines = plan_input['fixed_routines']
    weekly_goals = plan_input['weekly_goals']

    fixed_routines_str = "\n".join([
        f"- {r['activity_name']} در {r['day_of_week']} از {r['start_time']} تا {r['end_time']}"
        for r in fixed_routines
    ])
    if not fixed_routines_str:
        fixed_routines_str = "هیچ."

    weekly_goals_str = "\n".join([
        f"- {g['goal_name']}: {g['hours_per_week']} ساعت"
        for g in weekly_goals
    ])

    prompt = f"""
    شما یک برنامه‌ریز هوشمند هستید. یک برنامه‌ی **۷ روزه‌ی کامل هفتگی (شنبه تا جمعه)** ایجاد کنید.
    **تمام عنوان‌های فعالیت (title) در خروجی باید به زبان فارسی باشند.**
    هر روز شامل فعالیت‌ها با `title`, `start_time`, `end_time`, `type` (Routine, FixedRoutine, WeeklyGoal, Sleep, Break) باشد.

    ### مشخصات ورودی کاربر:
    🕒 زمان خواب و بیداری: خواب: {sleep_time}، بیداری: {wake_time}
    📅 روتین‌های ثابت: {fixed_routines_str}
    🎯 اهداف هفتگی (ساعت در هفته): {weekly_goals_str}

    ### قوانین برنامه‌ریزی:
    1. روتین‌های ثابت و زمان خواب/بیداری را رعایت کن.
    2. بین فعالیت‌های سنگین (آموزشی/کاری)، ۱ ساعت استراحت (با عنوان: "استراحت") بگذار.
    3. صبحانه (07:00-08:00 با عنوان: "بیداری و صبحانه") در همه روزها باشد، مگر تداخل.
    4. اهداف هفتگی را متوازن در روزها پخش کن (اولویت با ساعت بیشتر).
    5. زمان‌ها به فرمت "HH:mm" باشند.
    6. اگر در پایان هفته (به خصوص در روز جمعه) یا در انتهای هر روز، زمان خالی یا اهداف هفتگی برآورده نشده‌ای باقی ماند، آن زمان را به فعالیت‌های "جبرانی" (با عنوان: "زمان جبرانی" و نوع: "WeeklyGoal") اختصاص بده.

    **خروجی نهایی: فقط یک آبجکت JSON (JSON object) با کلید "daily_plans" که حاوی یک آرایه از برنامه‌های ۷ روزه (شنبه تا جمعه) است. هیچ متن اضافی، توضیح، یا آبجکت JSON والد دیگری نباید قبل یا بعد از این آبجکت JSON وجود داشته باشد. فقط آبجکت JSON را برگردانید.**

    **اطمینان حاصل کنید که آرایه‌ی "daily_plans" حتما شامل برنامه‌ی کامل برای تمام ۷ روز هفته (شنبه، یکشنبه، دوشنبه، سه‌شنبه، چهارشنبه، پنج‌شنبه، جمعه) باشد.**

    **مثال فرمت خروجی (یک آبجکت JSON در سطح بالا):**

    ```json
    {{
      "message": "Weekly plan generated successfully.",
      "daily_plans": [
        {{
          "day_of_week": "شنبه",
          "activities": [
            {{"title": "خواب", "start_time": "23:00", "end_time": "07:00", "type": "Sleep"}},
            {{"title": "بیداری و صبحانه", "start_time": "07:00", "end_time": "08:00", "type": "Routine"}},
            {{"title": "هدف هفتگی: پایتون", "start_time": "08:00", "end_time": "10:00", "type": "WeeklyGoal"}}
          ]
        }},
        {{
          "day_of_week": "یکشنبه",
          "activities": [
            {{"title": "خواب", "start_time": "23:00", "end_time": "07:00", "type": "Sleep"}},
            {{"title": "بیداری و صبحانه", "start_time": "07:00", "end_time": "08:00", "type": "Routine"}},
            {{"title": "مطالعه", "start_time": "09:00", "end_time": "12:00", "type": "WeeklyGoal"}}
          ]
        }},
        {{
          "day_of_week": "جمعه",
          "activities": [
            {{"title": "خواب", "start_time": "23:00", "end_time": "07:00", "type": "Sleep"}},
            {{"title": "بیداری و صبحانه", "start_time": "07:00", "end_time": "08:00", "type": "Routine"}},
            {{"title": "زمان جبرانی", "start_time": "14:00", "end_time": "17:00", "type": "WeeklyGoal"}}
          ]
        }}
      ]
    }}
    ```
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content.strip()

        if response_content.startswith("```json"):
            response_content = response_content.replace("```json", "").replace("```", "").strip()

        logger.info(f"AI Raw Response Content: {response_content}")

        parsed_data = json.loads(response_content)

        # Ensure the top-level structure is as expected: {"message": ..., "daily_plans": [...]}
        if not isinstance(parsed_data, dict) or "daily_plans" not in parsed_data or not isinstance(
                parsed_data["daily_plans"], list):
            raise ValueError(
                "AI response does not contain the expected 'daily_plans' key as a list, or the top-level structure is incorrect.")

        daily_plans_list: List[Dict[str, Any]] = parsed_data["daily_plans"]

        # --- POST-PROCESSING: Ensure all 7 days are present and sort them ---
        expected_days_order = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]

        existing_plans_map = {plan["day_of_week"]: plan for plan in daily_plans_list}

        complete_daily_plans = []
        for day in expected_days_order:
            if day in existing_plans_map:
                complete_daily_plans.append(existing_plans_map[day])
            else:
                logger.warning(f"AI missed generating plan for {day}. Creating a default plan.")
                default_activities = [
                    {
                        "title": "خواب",
                        "start_time": sleep_time,
                        "end_time": wake_time,
                        "type": "Sleep"
                    },
                    {
                        "title": "بیداری و صبحانه",
                        "start_time": wake_time,
                        "end_time": "08:00",
                        "type": "Routine"
                    }
                ]
                complete_daily_plans.append({
                    "day_of_week": day,
                    "activities": default_activities
                })

        final_response = {
            "message": "Weekly plan generated successfully.",
            "daily_plans": complete_daily_plans
        }
        return final_response  # Return the full dictionary

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from AI response: {e}, Response: {response_content}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI returned invalid JSON: {e}. Raw response: {response_content}"
        )
    except ValueError as e:
        logger.error(f"Error parsing AI response structure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI returned an unexpected structure: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling OpenAI API or processing response: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred with AI planning: {e}"
        )