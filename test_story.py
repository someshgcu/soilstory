#!/usr/bin/env python3
"""
Test script for the updated story generation service
"""

import sys
import os
sys.path.append('backend')

from services.story import generate_soil_story

def test_story_generation():
    """Test the story generation with sample soil analysis data"""
    
    # Sample soil analysis data
    sample_analysis = {
        'pH': 6.5,
        'OM': 3.2,
        'P': 25.0,
        'EC': 1.8,
        'moisture': 'moderate'
    }
    
    # Sample weather data
    sample_weather = {
        'tempC': 22,
        'weather': 'partly cloudy',
        'humidity': 65
    }
    
    # Sample location
    sample_location = {
        'lat': 40.7128,
        'lon': -74.0060
    }
    
    print("Testing Story Generation Service")
    print("=" * 50)
    
    print(f"\nSample Analysis Data:")
    for key, value in sample_analysis.items():
        print(f"  {key}: {value}")
    
    print(f"\nSample Weather: {sample_weather['tempC']}°C, {sample_weather['weather']}, {sample_weather['humidity']}% humidity")
    print(f"Sample Location: {sample_location['lat']}, {sample_location['lon']}")
    
    print("\n" + "=" * 50)
    print("Generating Story...")
    print("=" * 50)
    
    try:
        # Generate story with the new detailed prompt
        story = generate_soil_story(
            analysis=sample_analysis,
            weather=sample_weather,
            location=sample_location
        )
        
        print("\nGenerated Story:")
        print("-" * 30)
        print(story)
        print("-" * 30)
        
        # Check if the analysis values are included in the story
        story_lower = story.lower()
        analysis_values_found = []
        
        if str(sample_analysis['pH']) in story:
            analysis_values_found.append(f"pH: {sample_analysis['pH']}")
        if str(sample_analysis['OM']) in story:
            analysis_values_found.append(f"OM: {sample_analysis['OM']}")
        if str(sample_analysis['P']) in story:
            analysis_values_found.append(f"P: {sample_analysis['P']}")
        if str(sample_analysis['EC']) in story:
            analysis_values_found.append(f"EC: {sample_analysis['EC']}")
        
        print(f"\nAnalysis Values Found in Story: {len(analysis_values_found)}/4")
        for value in analysis_values_found:
            print(f"  ✓ {value}")
        
        if len(analysis_values_found) < 4:
            missing = []
            if str(sample_analysis['pH']) not in story:
                missing.append(f"pH: {sample_analysis['pH']}")
            if str(sample_analysis['OM']) not in story:
                missing.append(f"OM: {sample_analysis['OM']}")
            if str(sample_analysis['P']) not in story:
                missing.append(f"P: {sample_analysis['P']}")
            if str(sample_analysis['EC']) not in story:
                missing.append(f"EC: {sample_analysis['EC']}")
            print(f"\nMissing Values:")
            for value in missing:
                print(f"  ✗ {value}")
        
        print(f"\nStory Length: {len(story)} characters")
        print(f"Story Word Count: {len(story.split())} words")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error generating story: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_story_generation()
    if success:
        print("\n✅ Story generation test completed successfully!")
    else:
        print("\n❌ Story generation test failed!")
        sys.exit(1)
