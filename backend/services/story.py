from typing import Dict, Any, Optional
import os

from ..config import AppConfig


def _compose_prompt(analysis: Dict[str, Any], weather: Optional[Dict[str, Any]], location: Optional[Dict[str, float]]):
    # Extract soil analysis values for use as variables in the story
    ph = analysis.get('pH', 'unknown')
    organic_matter = analysis.get('OM') or analysis.get('organicMatter', 'unknown')
    phosphorus = analysis.get('P', 'unknown')
    electrical_conductivity = analysis.get('EC', 'unknown')
    
    # Build the detailed prompt with analysis values as variables
    prompt = f"""You are a friendly soil health expert and storyteller who makes complex soil science accessible to everyone. Your job is to analyze the uploaded soil photo and create an engaging, easy-to-understand story that explains the soil's health and provides actionable gardening advice.

**Your Analysis Should Include:**
1. **Soil Health Assessment:** Based on the photo, evaluate:
   - Soil type (sandy, clay, loamy)
   - Color indicators (dark = organic matter, light = nutrient poor, etc.)
   - Texture and structure visible in the image
   - Moisture level appearance
   - Any visible organic matter or debris

2. **Create a Friendly Story Format:**
   - Start with a warm greeting addressing the user directly
   - Use simple, non-technical language that a beginner gardener can understand
   - Make it conversational and encouraging
   - Include analogies or comparisons to everyday things when explaining soil concepts
   - Keep paragraphs short and digestible

3. **Story Structure:**
   - **Opening:** Welcome the user and acknowledge their soil sample
   - **Soil Personality:** Give the soil a "personality" - describe what you see in friendly terms
   - **Health Report:** Explain the soil's current condition in simple terms
   - **Improvement Tips:** Provide 3-4 practical, easy-to-follow recommendations
   - **Encouragement:** End with positive, motivating words about their gardening journey

4. **Writing Style Guidelines:**
   - Use "you" and "your" to make it personal
   - Avoid jargon - if you must use technical terms, explain them simply
   - Use encouraging phrases like "great news," "here's what I noticed," "you're on the right track"
   - Include seasonal or location-based advice when possible
   - Make recommendations specific and actionable

5. **Sample Tone:**
   "Hello there, fellow gardener! I've taken a close look at your soil sample, and I'm excited to share what I've discovered about your garden's foundation..."

**IMPORTANT: Use these actual analysis values in your story:**
- pH: {ph}
- Organic Matter: {organic_matter}
- Phosphorus: {phosphorus}
- Electrical Conductivity: {electrical_conductivity}

**Format the response as a cohesive, engaging story that feels like friendly advice from an experienced gardener neighbor. Aim for 200-300 words that are informative yet warm and encouraging.**

Remember: The goal is to make soil science accessible and inspire confidence in the user's gardening abilities while providing practical, actionable advice they can implement right away."""

    # Add weather and location context if available
    if weather:
        prompt += f"\n\nCurrent weather conditions: Temperature {weather.get('tempC', 'unknown')}°C, {weather.get('weather', 'unknown')} with humidity {weather.get('humidity', 'unknown')}%."
    
    if location and location.get('lat') is not None:
        prompt += f"\n\nLocation coordinates: Latitude {location.get('lat')}, Longitude {location.get('lon')}."
    
    return prompt


def generate_soil_story(analysis: Dict[str, Any], weather: Optional[Dict[str, Any]] = None, location: Optional[Dict[str, float]] = None) -> str:
    # Simple fallback deterministic template for offline use
    prompt = _compose_prompt(analysis, weather, location)
    provider = 'openai' if AppConfig().OPENAI_API_KEY else ('gemini' if AppConfig().GEMINI_API_KEY else 'none')
    try:
        if provider == 'openai':
            from openai import OpenAI
            client = OpenAI(api_key=AppConfig().OPENAI_API_KEY)
            content = [
                {"type": "text", "text": prompt}
            ]
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return (resp.choices[0].message.content or "").strip()
        if provider == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=AppConfig().GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(prompt)
            return (resp.text or "").strip()
    except Exception:
        pass

    # Fallback story using the analysis values
    ph = analysis.get('pH', 'unknown')
    moisture = analysis.get('moisture', 'unknown')
    om = analysis.get('OM') or analysis.get('organicMatter', 'unknown')
    ec = analysis.get('EC', 'unknown')
    p = analysis.get('P', 'unknown')
    
    weather_line = ''
    if weather:
        weather_line = f"Current weather: {weather.get('tempC')}°C, {weather.get('weather')} with humidity {weather.get('humidity')}%. "
    
    return (
        f"Hello there, fellow gardener! I've analyzed your soil sample and here's what I discovered about your garden's foundation.\n\n"
        f"Your soil shows pH {ph}, moisture {moisture}, organic matter {om}, phosphorus {p}, and electrical conductivity {ec}. "
        f"{weather_line}\n\n"
        f"To improve your soil health, I recommend watering early in the morning, adding compost to boost organic matter, and adjusting pH with lime (for acidic) or sulfur (for alkaline) as needed. "
        f"Mulch 5-7 cm to retain moisture and protect beneficial microbes. Check a small area weekly and re-test pH in 4-6 weeks.\n\n"
        f"You're on the right track to creating a thriving garden! Keep observing and learning from your soil - it's the foundation of everything beautiful that will grow."
    )


