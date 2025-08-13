import os
import requests
import json
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

class AIService:
    """Service for interacting with AI providers for soil analysis and story generation"""
    
    def __init__(self):
        """Initialize the AI service based on configuration"""
        self.provider = settings.AI_SERVICE_PROVIDER.lower()
        
        if self.provider == "openai":
            self.api_key = settings.OPENAI_API_KEY
            if not self.api_key:
                print("Warning: OpenAI API key not set")
        elif self.provider == "gemini":
            self.api_key = settings.GEMINI_API_KEY
            if not self.api_key:
                print("Warning: Gemini API key not set")
        else:
            print(f"Warning: Unknown AI provider {self.provider}, defaulting to OpenAI")
            self.provider = "openai"
            self.api_key = settings.OPENAI_API_KEY
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_soil_image(self, image_url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze soil image and return soil health metrics
        
        Args:
            image_url: URL to the soil image
            metadata: Additional metadata about the image (location, date, etc.)
            
        Returns:
            Dict containing soil analysis results
        """
        try:
            # For now, we'll simulate the analysis with basic metrics
            # In a real implementation, this would call the AI service with the image
            
            if self.provider == "openai":
                return await self._analyze_with_openai(image_url, metadata)
            elif self.provider == "gemini":
                return await self._analyze_with_gemini(image_url, metadata)
            else:
                # Fallback to simulated results
                return self._simulate_soil_analysis(metadata)
                
        except Exception as e:
            print(f"Error in soil analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_story(self, analysis_results: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Generate a personalized story based on soil analysis results
        
        Args:
            analysis_results: Results from soil analysis
            user_preferences: Optional user preferences for story generation
            
        Returns:
            Generated story text
        """
        try:
            if self.provider == "openai":
                return await self._generate_story_with_openai(analysis_results, user_preferences)
            elif self.provider == "gemini":
                return await self._generate_story_with_gemini(analysis_results, user_preferences)
            else:
                # Fallback to simulated results
                return self._simulate_story_generation(analysis_results, user_preferences)
                
        except Exception as e:
            print(f"Error in story generation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    async def _analyze_with_openai(self, image_url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze soil image using OpenAI's API"""
        if not self.api_key:
            return self._simulate_soil_analysis(metadata)
        
        try:
            # This is a simplified example - in production, you would:
            # 1. Download the image or use a direct URL if OpenAI supports it
            # 2. Use OpenAI's vision capabilities to analyze the image
            # 3. Process the response to extract soil metrics
            
            # Example using GPT-4 Vision API (simplified)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this soil image and provide detailed soil health metrics including pH, nutrient levels, organic matter content, and any visible issues. Also suggest plants that would grow well in this soil."},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            # In a real implementation, you would make the API call
            # response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            # response_data = response.json()
            
            # For now, return simulated results
            return self._simulate_soil_analysis(metadata)
            
        except Exception as e:
            print(f"OpenAI analysis error: {str(e)}")
            return self._simulate_soil_analysis(metadata)
    
    async def _analyze_with_gemini(self, image_url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze soil image using Google's Gemini API"""
        if not self.api_key:
            return self._simulate_soil_analysis(metadata)
        
        try:
            # This is a simplified example - in production, you would:
            # 1. Download the image or use a direct URL if Gemini supports it
            # 2. Use Gemini's vision capabilities to analyze the image
            # 3. Process the response to extract soil metrics
            
            # For now, return simulated results
            return self._simulate_soil_analysis(metadata)
            
        except Exception as e:
            print(f"Gemini analysis error: {str(e)}")
            return self._simulate_soil_analysis(metadata)
    
    def _simulate_soil_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate soil analysis results for development and testing"""
        # Generate realistic-looking soil analysis results
        return {
            "soil_type": "Loamy",
            "ph_level": round(6.0 + (metadata.get("random_seed", 0) % 20) / 10, 1),  # pH between 6.0 and 8.0
            "nutrients": {
                "nitrogen": "Medium",
                "phosphorus": "High",
                "potassium": "Medium",
                "calcium": "Medium",
                "magnesium": "Low"
            },
            "organic_matter": f"{3 + (metadata.get('random_seed', 0) % 7)}%",  # Between 3% and 10%
            "moisture": f"{20 + (metadata.get('random_seed', 0) % 40)}%",  # Between 20% and 60%
            "health_score": round(60 + (metadata.get("random_seed", 0) % 40), 1),  # Between 60 and 100
            "recommendations": [
                "Add compost to increase organic matter",
                "Consider adding magnesium supplements",
                "Maintain current watering schedule"
            ],
            "suitable_plants": [
                "Tomatoes",
                "Peppers",
                "Zucchini",
                "Marigolds",
                "Sunflowers"
            ],
            "analysis_confidence": "85%"
        }
    
    async def _generate_story_with_openai(self, analysis_results: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Generate story using OpenAI's API"""
        if not self.api_key:
            return self._simulate_story_generation(analysis_results, user_preferences)
        
        try:
            # Prepare the prompt based on analysis results and user preferences
            soil_type = analysis_results.get("soil_type", "unknown")
            health_score = analysis_results.get("health_score", 50)
            nutrients = analysis_results.get("nutrients", {})
            suitable_plants = analysis_results.get("suitable_plants", [])
            
            # Consider user preferences if available
            tone = "informative"
            audience = "gardener"
            if user_preferences:
                tone = user_preferences.get("tone", tone)
                audience = user_preferences.get("audience", audience)
            
            prompt = f"""Create an engaging and personalized story about a garden's soil. Here are the details:
            
            Soil Type: {soil_type}
            Health Score: {health_score}/100
            Key Nutrients: {', '.join([f'{k}: {v}' for k, v in nutrients.items()])}
            Plants that would thrive: {', '.join(suitable_plants)}
            
            The story should be {tone} in tone and written for a {audience}. 
            Personify the soil and its microorganisms as characters in the story.
            Include practical gardening advice based on the soil analysis.
            Keep the story under 500 words.
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a creative writer specializing in environmental storytelling that educates and inspires gardeners."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            # In a real implementation, you would make the API call
            # response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            # response_data = response.json()
            # story = response_data['choices'][0]['message']['content']
            
            # For now, return simulated results
            return self._simulate_story_generation(analysis_results, user_preferences)
            
        except Exception as e:
            print(f"OpenAI story generation error: {str(e)}")
            return self._simulate_story_generation(analysis_results, user_preferences)
    
    async def _generate_story_with_gemini(self, analysis_results: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Generate story using Google's Gemini API"""
        if not self.api_key:
            return self._simulate_story_generation(analysis_results, user_preferences)
        
        try:
            # Similar implementation to OpenAI but using Gemini API
            # For now, return simulated results
            return self._simulate_story_generation(analysis_results, user_preferences)
            
        except Exception as e:
            print(f"Gemini story generation error: {str(e)}")
            return self._simulate_story_generation(analysis_results, user_preferences)
    
    def _simulate_story_generation(self, analysis_results: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Simulate story generation for development and testing"""
        soil_type = analysis_results.get("soil_type", "rich loamy")
        health_score = analysis_results.get("health_score", 75)
        suitable_plants = ", ".join(analysis_results.get("suitable_plants", ["tomatoes", "peppers", "flowers"]))
        
        # Generate a simple story based on the analysis results
        if health_score >= 80:
            quality = "thriving"
            mood = "vibrant"
        elif health_score >= 60:
            quality = "healthy"
            mood = "content"
        else:
            quality = "struggling"
            mood = "tired"
        
        story = f"""# The Secret Life of Your Garden Soil

Beneath your garden lies a {mood} world of {soil_type} soil, home to billions of tiny organisms working in harmony. Your soil is currently {quality}, with a health score of {health_score}/100.

Meet Terra, the soil particle who has lived in your garden for decades. Terra remembers when this land was wild and untamed, but has grown to appreciate the care you've shown as a gardener. Terra works with her friends - the nitrogen-fixing bacteria, the industrious earthworms, and the decomposing fungi - to create a welcoming home for plant roots.

"We've created quite a community here," Terra tells the newly arrived compost particles. "Our pH levels are balanced, and we've got a good mix of nutrients flowing through our networks."

The earthworm named Wiggle tunnels by, creating channels for water and air. "The humans above have been watering consistently," Wiggle reports. "And that last application of compost really brought in some wonderful new neighbors!"

Your soil community would especially welcome plants like {suitable_plants}. These plants would thrive in the current conditions, their roots forming beneficial relationships with the mycorrhizal fungi network that helps distribute resources throughout the soil ecosystem.

To keep your soil community happy, consider these tips from Terra and friends:

1. Add a thin layer of compost every season to introduce new beneficial organisms
2. Avoid over-tilling, which disrupts the delicate networks formed underground
3. Mulch during hot periods to maintain moisture and protect soil life
4. Plant a diverse range of species to encourage different types of soil interactions

Remember, healthy soil means healthy plants, and your garden's soil has stories to tell if you listen closely enough!
"""
        
        return story

# Create a singleton instance
ai_service = AIService()