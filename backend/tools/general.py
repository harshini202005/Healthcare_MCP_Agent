import os
from mistralai import Mistral

def is_health_related(question):
    """Check if the question is health-related"""
    health_keywords = [
        'health', 'medical', 'symptom', 'disease', 'treatment', 'medicine', 'doctor',
        'pain', 'sick', 'illness', 'condition', 'diagnosis', 'therapy', 'cure',
        'hospital', 'clinic', 'patient', 'healthcare', 'wellness', 'fitness',
        'diet', 'nutrition', 'mental health', 'anxiety', 'depression', 'stress',
        'appointment', 'prescription', 'vaccine', 'surgery', 'injury', 'infection',
        'fever', 'cough', 'headache', 'allergy', 'diabetes', 'blood pressure',
        'heart', 'lung', 'kidney', 'liver', 'brain', 'skin', 'bone', 'muscle',
        'vitamin', 'exercise', 'sleep', 'water', 'weight', 'yoga', 'meditation',
        'food', 'eat', 'drink', 'calories', 'protein', 'carb', 'fat', 'fiber',
        'sugar', 'cholesterol', 'hydration', 'meal', 'snack', 'breakfast', 'lunch', 'dinner',
        'vegetarian', 'vegan', 'keto', 'paleo', 'gluten', 'lactose', 'dairy',
        'running', 'walking', 'gym', 'workout', 'cardio', 'strength', 'stretch',
        'breath', 'relax', 'tired', 'energy', 'fatigue', 'insomnia', 'rest',
        'benefit', 'healthy', 'unhealthy', 'habit', 'lifestyle', 'prevent',
        'immune', 'body', 'physical', 'mental', 'emotional', 'wellbeing'
    ]
    
    question_lower = question.lower()
    
    # If question contains health keywords, it's health-related
    if any(keyword in question_lower for keyword in health_keywords):
        return True
    
    # Check for common health question patterns
    health_patterns = [
        'how to', 'what is', 'why is', 'should i', 'can i', 'is it good', 'is it bad',
        'how much', 'how many', 'what are', 'benefits of', 'effects of', 'causes of'
    ]
    
    # If it's a "how to" or "what is" type question, be more lenient
    # Many health questions don't explicitly mention health keywords
    if any(pattern in question_lower for pattern in health_patterns):
        return True
    
    return False

def answer(question, context=None):
    """
    Answer general health and wellness questions.
    Only responds to health-related queries.
    
    Args:
        question: The health question to answer
        context: Additional context or patient information (optional)
    """
    print(f"\n🔧 TOOL CALLED: general_query")
    print(f"   Question: {question}")
    print(f"   Context: {context or 'None'}")
    
    # Validate that query is health-related
    if not is_health_related(question):
        print(f"   ⚠️ Non-health question detected")
        return {
            "error": True,
            "message": "I can only answer health-related questions.",
            "suggestion": "Please ask about health topics like:\n• Medical conditions and symptoms\n• Treatments and medications\n• Diet and nutrition\n• Exercise and fitness\n• Mental health and wellness\n• Healthcare appointments and services"
        }
    
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key or api_key == "your-mistral-api-key-here":
        print(f"   ⚠️ Mistral API key not configured, using template response")
        
        # Common health topics with responses
        health_knowledge = {
            "exercise": "Regular exercise is crucial for health. Aim for 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity per week, plus strength training twice weekly.",
            "sleep": "Adults need 7-9 hours of quality sleep per night. Maintain a consistent sleep schedule and create a relaxing bedtime routine.",
            "water": "Stay hydrated by drinking 8-10 glasses (about 2 liters) of water daily. Increase intake during exercise or hot weather.",
            "diet": "A balanced diet includes fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit processed foods, sugar, and sodium.",
            "stress": "Manage stress through exercise, meditation, deep breathing, adequate sleep, and connecting with others. Seek professional help if needed.",
            "vitamins": "A balanced diet usually provides necessary vitamins. Consult a doctor before taking supplements."
        }
        
        answer = "I'm a healthcare assistant. "
        for topic, info in health_knowledge.items():
            if topic in question.lower():
                answer = info
                break
        else:
            answer = "I can help with health questions. Could you please be more specific about your health concern?"
        
        return {
            "answer": answer,
            "source": "template",
            "disclaimer": "⚕️ This is general information. Please consult a healthcare professional for medical advice."
        }
    
    # Use Mistral AI for response
    client = Mistral(api_key=api_key)
    
    try:
        messages = [
            {
                "role": "system",
                "content": """You are a helpful healthcare assistant. 
                
IMPORTANT: You ONLY answer health-related questions about:
- Medical conditions, symptoms, and diseases
- Treatments, medications, and therapies
- Diet, nutrition, and meal planning
- Exercise, fitness, and wellness
- Mental health and stress management
- Healthcare appointments and services

If asked about non-health topics (weather, sports, politics, general knowledge, etc.), politely decline and redirect to health topics.

Provide accurate, helpful health information. Always remind users to consult healthcare professionals for medical advice."""
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        if context:
            messages.insert(1, {
                "role": "system",
                "content": f"Additional context: {context}"
            })
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages
        )
        
        answer = response.choices[0].message.content
        
        print(f"   ✅ Response generated successfully")
        
        return {
            "answer": answer,
            "source": "mistral_ai",
            "disclaimer": "⚕️ This information is for educational purposes. Please consult a healthcare professional for personalized medical advice."
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {error_msg}")
        return {
            "error": True,
            "message": f"Unable to process your question: {error_msg}",
            "suggestion": "Please try again or rephrase your health question."
        }
