# Gemini Integration for SoilStory

This document explains how to use the new Gemini AI integration to generate engaging soil health stories based on your soil analysis values.

## What's New

The story service has been enhanced to use your specific Gemini prompt that creates friendly, accessible soil health narratives. The system now:

1. **Uses your exact prompt** - The friendly soil health expert and storyteller prompt you provided
2. **Incorporates soil analysis values** - pH, Organic Matter (OM), Phosphorus (P), Electrical Conductivity (EC), and moisture
3. **Creates engaging stories** - 200-300 word narratives that feel like advice from an experienced gardener neighbor
4. **Provides actionable advice** - Practical gardening tips based on the soil analysis

## Setup

### 1. Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

### 2. Set Environment Variables

Create a `.env` file in your project root and add:

```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Install Dependencies

The required package is already in your `requirements.txt`:
```bash
pip install google-generativeai
```

## How It Works

### Story Generation Flow

1. **Image Upload** → User uploads soil photo
2. **ML Analysis** → Your models analyze the image and extract:
   - pH value
   - Organic Matter (OM) percentage
   - Phosphorus (P) content
   - Electrical Conductivity (EC)
   - Moisture level
3. **Gemini Prompt** → The system sends your specific prompt + analysis values to Gemini
4. **Story Creation** → Gemini generates a friendly, educational story
5. **User Experience** → User receives an engaging narrative about their soil

### Example Analysis Values

```python
sample_analysis = {
    'pH': 6.8,           # Slightly acidic
    'OM': 2.5,           # 2.5% organic matter
    'P': 15.2,           # 15.2 mg/kg phosphorus
    'EC': 0.8,           # 0.8 dS/m electrical conductivity
    'moisture': 0.65     # 65% moisture level
}
```

### Example Generated Story

The system will generate stories like:

> "Hello there, fellow gardener! I've taken a close look at your soil sample, and I'm excited to share what I've discovered about your garden's foundation. Your soil has a pH of 6.8, which is actually quite good for most plants - it's slightly acidic but in the sweet spot that many vegetables love..."

## Testing the Integration

Run the test script to verify everything works:

```bash
python test_gemini_story.py
```

This will test the story generation with sample data and show you the output.

## Customization

### Modifying the Prompt

The prompt is defined in `backend/services/story.py` in the `_compose_gemini_prompt()` function. You can modify:

- Story structure and format
- Writing style guidelines
- Specific instructions for Gemini
- Length requirements

### Adding More Context

The system automatically includes:
- Weather data (if available)
- Location coordinates (if provided)
- All soil analysis values

You can extend this by adding more context variables to the prompt.

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set"**
   - Make sure you have a `.env` file with your API key
   - Restart your application after adding the key

2. **"AI story generation failed"**
   - Check your internet connection
   - Verify your API key is valid
   - Check the console for detailed error messages

3. **Stories not generating**
   - Ensure Gemini API key is set
   - Check if you have sufficient API quota
   - Verify the `google-generativeai` package is installed

### Fallback Behavior

If Gemini fails, the system will:
1. Try OpenAI (if configured)
2. Use a deterministic template with the analysis values
3. Always provide useful information to the user

## API Usage

The story generation is automatically called when:
- A user uploads a soil image
- The ML analysis completes
- The `/api/analyze` endpoint is called

The generated story is stored with the analysis and can be retrieved later.

## Next Steps

1. **Set your Gemini API key** in the `.env` file
2. **Test the integration** with the test script
3. **Upload a soil image** through your web interface
4. **Enjoy the engaging stories** that explain soil health in friendly terms!

## Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify your API key and internet connection
3. Test with the provided test script
4. Check the fallback template output

The system is designed to be robust and will always provide useful information to users, even if the AI service is temporarily unavailable.
