
import os
from mistralai import Mistral

def generate(preferences, calories=None, allergies=None):
    """
    Generate a personalized diet plan based on preferences.
    
    Args:
        preferences: Dietary preference (vegetarian, vegan, keto, etc.)
        calories: Target daily calorie intake (optional)
        allergies: List of food allergies or restrictions (optional)
    """
    print(f"\n🔧 TOOL CALLED: generate_diet")
    print(f"   Preferences: {preferences}")
    print(f"   Calories: {calories or 'Not specified'}")
    print(f"   Allergies: {allergies or 'None'}")
    
    if allergies is None:
        allergies = []
    
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key or api_key == "your-mistral-api-key-here":
        print(f"   ⚠️ Mistral API key not configured, using template response")
        diet_plan = {
            "error": False,
            "message": "🥗 Here's your personalized diet plan",
            "preference": preferences,
            "daily_calories": calories or 2000,
            "allergies": allergies or ["None"],
            "meals": {
                "Breakfast": f"Healthy {preferences} breakfast - oatmeal with berries (400 cal)",
                "Morning Snack": "Greek yogurt with honey (150 cal)",
                "Lunch": f"Nutritious {preferences} lunch - quinoa bowl with vegetables (500 cal)",
                "Afternoon Snack": "Fresh fruits and nuts (200 cal)",
                "Dinner": f"Balanced {preferences} dinner with protein and veggies (600 cal)",
                "Evening": "Herbal tea (0 cal)"
            },
            "tips": [
                "💧 Stay hydrated - drink 8-10 glasses of water daily",
                "🥗 Include variety of colorful vegetables",
                "🍽️ Practice portion control",
                "🧘 Eat mindfully and avoid distractions",
                "🏃 Combine with 30 minutes of daily exercise"
            ],
            "note": "⚠️ Configure Mistral API key in .env for AI-powered recommendations"
        }
        return diet_plan
    
    try:
        client = Mistral(api_key=api_key)
        
        prompt = f"""Create a detailed, personalized diet plan:
- Dietary preference: {preferences}
- Target calories: {calories or '2000 (standard)'} per day
- Allergies/restrictions: {', '.join(allergies) if allergies else 'None'}

Provide a complete day's meal plan with breakfast, lunch, dinner, and 2 snacks. 
Include approximate calories and practical nutrition tips."""
        
        response = client.chat.complete(
            model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            messages=[
                {"role": "system", "content": "You are a professional nutritionist. Provide specific, practical diet plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        diet_content = response.choices[0].message.content
        print(f"   ✅ Result: AI diet plan generated with Mistral")
        
        return {
            "error": False,
            "message": "🥗 Your AI-Powered Personalized Diet Plan (Mistral AI)",
            "plan": diet_content,
            "preference": preferences,
            "daily_calories": calories or 2000,
            "allergies": allergies or ["None"]
        }
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {
            "error": True,
            "message": f"Failed to generate diet plan: {str(e)}",
            "fallback": "Please check your Mistral API key configuration in .env file"
        }
