

"""
Personal Content AI Agent MCP Server
-----------------------------------
MCP server that processes content with interactive elicitation for 
content articulation and platform optimization.
"""

import json
import os
import yaml
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.elicitation import (
    AcceptedElicitation,
    DeclinedElicitation,
    CancelledElicitation,
)
from pydantic import BaseModel, Field
import textstat
from langdetect import detect

# Initialize the MCP server
mcp = FastMCP("Personal Content AI Agent")

# Configuration
CONTENT_SAMPLES_DIR = Path("content_samples")
PLATFORM_CONFIGS_DIR = Path("platform_configs")
VOICE_PATTERNS_DIR = Path("voice_patterns")
OUTPUT_DIR = Path("output")

# Elicitation schemas for user preferences
class ContentArticulationPreferences(BaseModel):
    target_platform: str = Field(default="generic", description="Target platform: twitter, linkedin, medium, instagram, generic")
    tone_preference: str = Field(default="maintain_original", description="Tone preference: maintain_original, more_professional, more_casual, more_engaging")
    content_length: str = Field(default="optimal", description="Content length: short, optimal, long")
    include_examples: bool = Field(default=True, description="Include concrete examples?")
    include_cta: bool = Field(default=True, description="Include call-to-action?")
    audience_level: str = Field(default="general", description="Audience level: beginner, general, expert")

class PlatformOptimizationPreferences(BaseModel):
    target_platform: str = Field(..., description="Target platform: twitter, linkedin, medium, instagram")
    content_focus: str = Field(default="main_points", description="Content focus: main_points, detailed_analysis, storytelling")
    engagement_style: str = Field(default="moderate", description="Engagement style: low, moderate, high")
    hashtag_strategy: str = Field(default="relevant", description="Hashtag strategy: none, minimal, relevant, maximum")
    format_preference: str = Field(default="standard", description="Format preference: standard, bullet_points, story_format, thread")

class VoiceAnalysisPreferences(BaseModel):
    analysis_depth: str = Field(default="comprehensive", description="Analysis depth: basic, comprehensive, detailed")
    focus_areas: List[str] = Field(default=["tone", "style", "structure"], description="Focus areas: tone, style, structure, vocabulary, engagement")
    include_examples: bool = Field(default=True, description="Include examples in analysis?")
    generate_guidelines: bool = Field(default=True, description="Generate style guidelines?")


def load_platform_config(platform: str) -> Dict[str, Any]:
    """Load platform-specific configuration."""
    config_path = PLATFORM_CONFIGS_DIR / f"{platform}.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def load_voice_patterns() -> Dict[str, Any]:
    """Load existing voice patterns."""
    patterns_path = VOICE_PATTERNS_DIR / "extracted_patterns.yaml"
    if patterns_path.exists():
        with open(patterns_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def save_voice_patterns(patterns: Dict[str, Any]) -> None:
    """Save voice patterns to file."""
    VOICE_PATTERNS_DIR.mkdir(exist_ok=True)
    patterns_path = VOICE_PATTERNS_DIR / "extracted_patterns.yaml"
    with open(patterns_path, 'w') as f:
        yaml.safe_dump(patterns, f, default_flow_style=False)

def analyze_text_metrics(text: str) -> Dict[str, Any]:
    """Analyze text for basic metrics."""
    try:
        language = detect(text)
    except:
        language = "unknown"
    
    return {
        "word_count": len(text.split()),
        "character_count": len(text),
        "sentence_count": len([s for s in text.split('.') if s.strip()]),
        "readability_score": textstat.flesch_reading_ease(text),
        "grade_level": textstat.flesch_kincaid_grade(text),
        "language": language,
        "avg_sentence_length": len(text.split()) / max(len([s for s in text.split('.') if s.strip()]), 1)
    }

def extract_voice_characteristics(text: str) -> Dict[str, Any]:
    """Extract voice characteristics from text."""
    metrics = analyze_text_metrics(text)
    
    # Determine tone indicators
    tone_indicators = {
        "contractions": len([word for word in text.split() if "'" in word]),
        "questions": text.count('?'),
        "exclamations": text.count('!'),
        "first_person": len([word for word in text.lower().split() if word in ['i', 'me', 'my', 'mine']]),
        "second_person": len([word for word in text.lower().split() if word in ['you', 'your', 'yours']]),
    }
    
    # Determine formality level
    if metrics["avg_sentence_length"] > 20 and tone_indicators["contractions"] < 3:
        formality = "formal"
    elif metrics["avg_sentence_length"] < 12 and tone_indicators["contractions"] > 5:
        formality = "casual"
    else:
        formality = "conversational"
    
    return {
        "formality_level": formality,
        "tone_indicators": tone_indicators,
        "sentence_structure": "complex" if metrics["avg_sentence_length"] > 18 else "simple",
        "engagement_style": "high" if tone_indicators["questions"] > 0 else "moderate",
        "metrics": metrics
    }

@mcp.tool()
async def analyze_writing_samples(ctx: Context) -> str:
    """
    Analyze user's writing samples to extract voice patterns and style characteristics.
    Interactive elicitation customizes the analysis scope and detail level.
    """
    
    # Check if samples directory exists and has content
    if not CONTENT_SAMPLES_DIR.exists():
        return "Error: content_samples directory not found. Please create it and add your writing samples."
    
    sample_files = list(CONTENT_SAMPLES_DIR.rglob("*.md")) + list(CONTENT_SAMPLES_DIR.rglob("*.txt"))
    if not sample_files:
        return "Error: No writing samples found. Please add .md or .txt files to the content_samples directory."
    
    # Elicit analysis preferences
    result = await ctx.elicit(
        message="Let's analyze your writing samples to learn your unique voice. Please specify your preferences:",
        schema=VoiceAnalysisPreferences
    )
    
    match result:
        case AcceptedElicitation(data=prefs):
            analysis_results = {
                "analysis_config": {
                    "depth": prefs.analysis_depth,
                    "focus_areas": prefs.focus_areas,
                    "include_examples": prefs.include_examples,
                    "generate_guidelines": prefs.generate_guidelines
                },
                "samples_analyzed": len(sample_files),
                "voice_patterns": {},
                "style_characteristics": {},
                "recommendations": []
            }
            
            # Analyze each sample
            all_text = ""
            sample_analyses = []
            
            for sample_file in sample_files:
                try:
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        all_text += content + "\n"
                        
                        if prefs.analysis_depth in ["comprehensive", "detailed"]:
                            sample_analysis = {
                                "file": str(sample_file),
                                "characteristics": extract_voice_characteristics(content),
                                "platform": sample_file.parent.name
                            }
                            sample_analyses.append(sample_analysis)
                except Exception as e:
                    continue
            
            if not all_text:
                return "Error: Could not read any writing samples. Please check file permissions and formats."
            
            # Extract overall voice characteristics
            overall_characteristics = extract_voice_characteristics(all_text)
            
            # Build voice patterns
            voice_patterns = {
                "user_voice_characteristics": {
                    "tone_analysis": {
                        "primary_tone": overall_characteristics["formality_level"],
                        "engagement_style": overall_characteristics["engagement_style"],
                        "sentence_structure": overall_characteristics["sentence_structure"]
                    },
                    "writing_metrics": overall_characteristics["metrics"],
                    "tone_indicators": overall_characteristics["tone_indicators"]
                },
                "sample_breakdown": sample_analyses if prefs.analysis_depth == "detailed" else [],
                "analyzed_at": str(asyncio.get_event_loop().time())
            }
            
            # Save voice patterns if requested
            if prefs.generate_guidelines:
                save_voice_patterns(voice_patterns)
                analysis_results["voice_patterns_saved"] = True
            
            analysis_results["voice_patterns"] = voice_patterns
            analysis_results["recommendations"] = [
                f"Your writing style is {overall_characteristics['formality_level']}",
                f"You use {overall_characteristics['engagement_style']} engagement",
                f"Your sentences are {overall_characteristics['sentence_structure']}",
                "Voice patterns have been learned and saved for future content creation"
            ]
            
            return json.dumps(analysis_results, indent=2)
            
        case DeclinedElicitation():
            return "Writing sample analysis declined by user."
            
        case CancelledElicitation():
            return "Writing sample analysis was cancelled."

@mcp.tool()
async def articulate_content(content: str, ctx: Context) -> str:
    """
    Take rough content and articulate it clearly while preserving the user's authentic voice.
    Interactive elicitation customizes the articulation approach.
    
    Args:
        content: The rough content to be articulated and improved
    """
    
    if not content.strip():
        return "Error: No content provided to articulate."
    
    # Elicit articulation preferences
    result = await ctx.elicit(
        message="Let's articulate your content. How would you like it improved?",
        schema=ContentArticulationPreferences
    )
    
    match result:
        case AcceptedElicitation(data=prefs):
            # Load voice patterns and platform config
            voice_patterns = load_voice_patterns()
            platform_config = load_platform_config(prefs.target_platform)
            
            # Analyze the input content
            input_analysis = extract_voice_characteristics(content)
            
            # Build articulation instructions
            articulation_request = {
                "original_content": content,
                "target_platform": prefs.target_platform,
                "preferences": {
                    "tone_preference": prefs.tone_preference,
                    "content_length": prefs.content_length,
                    "include_examples": prefs.include_examples,
                    "include_cta": prefs.include_cta,
                    "audience_level": prefs.audience_level
                },
                "voice_patterns": voice_patterns,
                "platform_config": platform_config,
                "input_analysis": input_analysis,
                "articulation_instructions": {
                    "preserve_voice": True,
                    "improve_clarity": True,
                    "maintain_authenticity": True,
                    "optimize_for_platform": prefs.target_platform != "generic"
                }
            }
            
            return json.dumps(articulation_request, indent=2)
            
        case DeclinedElicitation():
            return "Content articulation declined by user."
            
        case CancelledElicitation():
            return "Content articulation was cancelled."

@mcp.tool()
async def optimize_for_platform(content: str, ctx: Context) -> str:
    """
    Optimize existing content for a specific platform while maintaining the user's voice.
    Interactive elicitation customizes the optimization approach.
    
    Args:
        content: The content to be optimized for a specific platform
    """
    
    if not content.strip():
        return "Error: No content provided to optimize."
    
    # Elicit optimization preferences
    result = await ctx.elicit(
        message="Let's optimize your content for a specific platform. What are your preferences?",
        schema=PlatformOptimizationPreferences
    )
    
    match result:
        case AcceptedElicitation(data=prefs):
            # Load configuration and patterns
            platform_config = load_platform_config(prefs.target_platform)
            voice_patterns = load_voice_patterns()
            
            # Analyze the content
            content_analysis = extract_voice_characteristics(content)
            
            # Build optimization request
            optimization_request = {
                "original_content": content,
                "target_platform": prefs.target_platform,
                "platform_config": platform_config,
                "optimization_preferences": {
                    "content_focus": prefs.content_focus,
                    "engagement_style": prefs.engagement_style,
                    "hashtag_strategy": prefs.hashtag_strategy,
                    "format_preference": prefs.format_preference
                },
                "voice_patterns": voice_patterns,
                "content_analysis": content_analysis,
                "optimization_instructions": {
                    "maintain_voice": True,
                    "adapt_format": True,
                    "optimize_length": True,
                    "enhance_engagement": True
                }
            }
            
            return json.dumps(optimization_request, indent=2)
            
        case DeclinedElicitation():
            return "Platform optimization declined by user."
            
        case CancelledElicitation():
            return "Platform optimization was cancelled."

@mcp.tool()
async def extract_voice_patterns(sample_text: str) -> str:
    """
    Extract voice patterns from a specific text sample.
    
    Args:
        sample_text: The text sample to analyze for voice patterns
    """
    
    if not sample_text.strip():
        return "Error: No text provided for voice pattern extraction."
    
    # Extract characteristics
    characteristics = extract_voice_characteristics(sample_text)
    
    # Build structured response
    response = {
        "sample_analysis": {
            "text_length": len(sample_text),
            "word_count": len(sample_text.split()),
            "voice_characteristics": characteristics,
            "style_indicators": {
                "uses_contractions": characteristics["tone_indicators"]["contractions"] > 0,
                "asks_questions": characteristics["tone_indicators"]["questions"] > 0,
                "uses_exclamations": characteristics["tone_indicators"]["exclamations"] > 0,
                "personal_pronouns": characteristics["tone_indicators"]["first_person"] > 0,
                "direct_address": characteristics["tone_indicators"]["second_person"] > 0
            }
        },
        "recommendations": [
            f"This text shows {characteristics['formality_level']} formality",
            f"Sentence structure is {characteristics['sentence_structure']}",
            f"Engagement style is {characteristics['engagement_style']}",
            "Use these patterns to maintain voice consistency"
        ]
    }
    
    return json.dumps(response, indent=2)

@mcp.tool()
async def save_content_output(content: str, filename: str, content_type: str = "final") -> str:
    """
    Save generated content to the output directory.
    
    Args:
        content: The content to save
        filename: The filename to save as
        content_type: Type of content (draft, final)
    """
    
    if not content.strip():
        return "Error: No content provided to save."
    
    # Determine output directory
    output_subdir = OUTPUT_DIR / content_type
    output_subdir.mkdir(parents=True, exist_ok=True)
    
    # Save the content
    output_path = output_subdir / filename
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Content saved successfully to: {output_path}"
    except Exception as e:
        return f"Error saving content: {str(e)}"

def main():
    """Main entry point for the Personal Content AI Agent MCP server."""
    print("🎯 Personal Content AI Agent MCP Server")
    print("💬 Interactive content articulation and platform optimization")
    print("🔥 Preserving your authentic voice across platforms")
    
    # Create necessary directories
    CONTENT_SAMPLES_DIR.mkdir(exist_ok=True)
    PLATFORM_CONFIGS_DIR.mkdir(exist_ok=True)
    VOICE_PATTERNS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    mcp.run()

if __name__ == "__main__":
    main()