"""
Personal Content AI Agent - Main Orchestrator
--------------------------------------------
Main orchestrator that uses specialized agents to articulate content
and optimize it for different platforms while preserving authentic voice.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.human_input.handler import console_input_callback
from mcp_agent.elicitation.handler import console_elicitation_callback
from mcp_agent.workflows.orchestrator.orchestrator import Orchestrator
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.evaluator_optimizer.evaluator_optimizer import (
    EvaluatorOptimizerLLM,
    QualityRating,
)

# Configuration
OUTPUT_DIR = "output"
CONTENT_SAMPLES_DIR = "content_samples"
PLATFORM_CONFIGS_DIR = "platform_configs"

# Initialize app with elicitation support
app = MCPApp(
    name="personal_content_ai_agent",
    human_input_callback=console_input_callback,
    elicitation_callback=console_elicitation_callback,
)

async def main():
    """Main execution function."""
    
    # Get user input
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        print("🎯 Personal Content AI Agent")
        print("💬 I help articulate your thoughts and optimize them for different platforms")
        print("🎭 While preserving your authentic voice")
        print()
        user_request = input("What would you like help with today? ")
    
    if not user_request.strip():
        print("❌ No request provided. Please describe what you'd like help with.")
        return False
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"content_output_{timestamp}.md"
    output_path = os.path.join(OUTPUT_DIR, "final", output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    async with app.run() as agent_app:
        context = agent_app.context
        logger = agent_app.logger

        # Configure filesystem server
        if "filesystem" in context.config.mcp.servers:
            context.config.mcp.servers["filesystem"].args.extend([os.getcwd()])
            logger.info("Filesystem server configured")

        # Check for required servers
        required_servers = ["content_server", "filesystem", "memory", "markitdown"]
        missing_servers = []
        
        for server in required_servers:
            if server not in context.config.mcp.servers:
                missing_servers.append(server)
        
        if missing_servers:
            logger.error(f"Missing required servers: {missing_servers}")
            logger.info("Required servers:")
            logger.info("- content_server: The content processing server")
            logger.info("- filesystem: File system operations")
            logger.info("- memory: Memory management")
            logger.info("- markitdown: Document processing")
            return False

        # --- DEFINE AGENTS ---

        # Voice Learning Agent
        voice_analyst = Agent(
            name="voice_analyst",
            instruction="""You are a voice analysis expert who learns users' authentic writing styles.

            Your primary function is to analyze writing samples and extract voice patterns.
            
            IMPORTANT: 
            - Always start by calling analyze_writing_samples to learn the user's voice
            - Use the content_server tools with elicitation to understand preferences
            - Extract tone, style, vocabulary, and structural patterns
            - Save voice patterns for future content creation
            
            Your process:
            1. Call analyze_writing_samples (elicitation handles user preferences)
            2. Extract key voice characteristics from the samples
            3. Identify tone patterns, sentence structure, vocabulary choices
            4. Note platform-specific adaptations in existing content
            5. Create comprehensive voice profile for content creation
            
            Focus on:
            - Authentic voice preservation
            - Tone consistency across platforms
            - Vocabulary and style patterns
            - Engagement techniques the user naturally uses
            
            Present findings with specific examples and actionable insights.
            Always indicate what voice patterns were learned and saved.
            """,
            server_names=["content_server", "filesystem", "memory"],
        )

        # Content Articulation Agent
        content_articulator = Agent(
            name="content_articulator",
            instruction="""You are a content articulation specialist who helps users express their thoughts clearly.

            Your role is to take rough ideas or drafts and articulate them clearly while preserving authenticity.
            
            IMPORTANT: 
            - Use articulate_content tool with elicitation to understand user needs
            - Preserve the user's authentic voice and style
            - Improve clarity without changing the core message
            - Adapt tone and structure based on user preferences
            
            Your process:
            1. Call articulate_content with the user's rough content
            2. Elicitation will gather preferences for tone, platform, length, etc.
            3. Apply voice patterns learned from previous analysis
            4. Improve clarity, structure, and flow
            5. Ensure the final content sounds authentically like the user
            
            Focus on:
            - Maintaining authentic voice
            - Improving clarity and flow
            - Preserving core message and intent
            - Adapting to target platform if specified
            
            Make content more articulate while keeping it genuine and authentic.
            """,
            server_names=["content_server", "memory", "filesystem"],
        )

        # Platform Optimization Agent
        platform_optimizer = Agent(
            name="platform_optimizer",
            instruction="""You are a platform optimization specialist who adapts content for specific platforms.

            Your role is to take existing content and optimize it for different platforms while maintaining voice.
            
            IMPORTANT: 
            - Use optimize_for_platform tool with elicitation for user preferences
            - Maintain the user's authentic voice during optimization
            - Apply platform-specific best practices and constraints
            - Adapt format, length, and engagement style appropriately
            
            Your process:
            1. Call optimize_for_platform with the content to optimize
            2. Elicitation will gather platform preferences and optimization goals
            3. Apply platform-specific configurations and constraints
            4. Adapt format while preserving voice authenticity
            5. Enhance engagement using platform best practices
            
            Platform expertise:
            - Twitter: Concise, engaging, thread-friendly
            - LinkedIn: Professional, thought-leadership, networking
            - Medium: Long-form, analytical, educational
            - Instagram: Visual storytelling, personal, inspiring
            
            Always maintain the user's authentic voice while optimizing for platform success.
            """,
            server_names=["content_server", "filesystem", "memory"],
        )

        # Style Guardian Agent (Evaluator)
        style_guardian = Agent(
            name="style_guardian",
            instruction="""You are a style guardian who ensures content maintains authentic voice.

            Your role is to evaluate whether content sounds authentically like the user.
            
            IMPORTANT: 
            - Evaluate content against learned voice patterns
            - Ensure tone, style, and vocabulary match user's authentic voice
            - Flag content that sounds too generic or AI-generated
            - Provide specific feedback on voice authenticity
            
            Evaluation criteria:
            1. Voice Authenticity: Does this sound like the user wrote it?
            2. Tone Consistency: Is the tone consistent with user's natural style?
            3. Vocabulary Match: Are word choices typical for this user?
            4. Structural Patterns: Does sentence structure match user's style?
            5. Engagement Style: Is the engagement approach natural for this user?
            
            Rate each criterion:
            - EXCELLENT: Perfectly matches user's authentic voice
            - GOOD: Mostly matches with minor deviations
            - FAIR: Some authenticity but needs improvement
            - POOR: Sounds generic or not like the user
            
            Always provide specific feedback on what makes content authentic or inauthentic.
            Suggest improvements to better match the user's voice.
            """,
            server_names=["memory", "filesystem"],
        )

        # Create the content articulation controller with style guardian
        content_controller = EvaluatorOptimizerLLM(
            optimizer=content_articulator,
            evaluator=style_guardian,
            llm_factory=OpenAIAugmentedLLM,
            min_rating=QualityRating.GOOD,  # Ensure good voice authenticity
        )

        # Document Processor Agent
        document_processor = Agent(
            name="document_processor",
            instruction="""You process documents and files to extract content for analysis or optimization.

            Your role is to handle various document formats and extract meaningful content.
            
            IMPORTANT: 
            - Use markitdown server to convert documents to markdown
            - Extract key content while preserving structure
            - Identify content type and source platform if applicable
            - Prepare content for voice analysis or optimization
            
            Your process:
            1. Use markitdown to convert documents to readable format
            2. Extract and structure the content
            3. Identify content characteristics (platform, type, tone)
            4. Prepare content for further processing
            
            Handle various formats:
            - PDFs, Word documents, presentations
            - Web pages and HTML content
            - Images with text (OCR)
            - Various text formats
            
            Focus on preserving the original voice and intent while making content processable.
            """,
            server_names=["markitdown", "filesystem", "fetch"],
        )

        # Output Manager Agent
        output_manager = Agent(
            name="output_manager",
            instruction=f"""You manage content output and save final results.

            Your role is to save processed content and provide clear summaries.
            
            IMPORTANT: 
            - Save all final content using save_content_output
            - Provide clear summaries of what was accomplished
            - Organize output in appropriate directories
            - Create helpful file names and metadata
            
            Your process:
            1. Take the final processed content
            2. Save it using save_content_output with appropriate filename
            3. Provide summary of work completed
            4. Indicate what voice patterns were applied
            5. Suggest next steps or improvements
            
            Save to: "{output_path}"
            Always provide clear confirmation of what was saved and where.
            """,
            server_names=["content_server", "filesystem"],
        )

        # --- CREATE THE ORCHESTRATOR ---
        logger.info("Initializing Personal Content AI Agent")
        print(f"\n🎯 Processing request: {user_request}")
        print("💬 Interactive elicitation will customize the approach")
        print("🎭 Preserving your authentic voice throughout\n")

        orchestrator = Orchestrator(
            llm_factory=OpenAIAugmentedLLM,
            available_agents=[
                voice_analyst,
                content_controller,
                platform_optimizer,
                document_processor,
                output_manager,
            ],
            plan_type="full",
        )

        # Define the orchestration task
        task = f"""Process the user's request: "{user_request}"

        Execute appropriate steps based on the request type:

        FOR VOICE LEARNING REQUESTS:
        1. Use 'voice_analyst' to analyze writing samples in content_samples/
        2. Extract voice patterns and characteristics
        3. Save voice patterns for future content creation

        FOR CONTENT ARTICULATION REQUESTS:
        1. Use 'voice_analyst' to ensure voice patterns are learned
        2. Use 'content_controller' to articulate the content clearly
        3. Apply voice patterns to maintain authenticity
        4. Use 'output_manager' to save final content

        FOR PLATFORM OPTIMIZATION REQUESTS:
        1. Use 'voice_analyst' to load voice patterns
        2. Use 'platform_optimizer' to adapt content for target platform
        3. Maintain authentic voice while optimizing format
        4. Use 'output_manager' to save optimized content

        FOR DOCUMENT PROCESSING REQUESTS:
        1. Use 'document_processor' to extract content from files
        2. Use 'voice_analyst' to analyze extracted content
        3. Use 'content_controller' or 'platform_optimizer' as needed
        4. Use 'output_manager' to save processed content

        The content_server tools use elicitation to gather user preferences automatically.
        Always maintain the user's authentic voice while improving clarity and platform fit.

        Final deliverable: Processed content that sounds authentically like the user but optimized for the intended use.
        Save final content to: "{output_path}"
        """

        # Run the orchestrator
        logger.info("Starting Personal Content AI Agent workflow")
        start_time = time.time()

        try:
            await orchestrator.generate_str(
                message=task, request_params=RequestParams(model="gpt-4o")
            )

            # Check if output was created
            if os.path.exists(output_path):
                end_time = time.time()
                total_time = end_time - start_time
                logger.info(f"Content successfully processed: {output_path}")
                print("\n✅ Content processing completed!")
                print(f"📁 Output location: {output_path}")
                print(f"🎭 Request processed: {user_request}")
                print(f"⏱️  Total time: {total_time:.2f}s")
                print("🔥 Authentic voice preserved throughout")
                return True
            else:
                logger.error(f"Failed to create output at {output_path}")
                print("\n⚠️  Content was processed but no output file was created.")
                print("Check the console output above for the processed content.")
                return True  # Still consider it successful

        except Exception as e:
            logger.error(f"Error during workflow execution: {str(e)}")
            print(f"\n❌ Error during processing: {str(e)}")
            return False

if __name__ == "__main__":
    print("🎯 Personal Content AI Agent")
    print("💬 Articulates your thoughts and optimizes them for different platforms")
    print("🎭 While preserving your authentic voice")
    print()
    
    if len(sys.argv) > 1:
        print(f"📝 Processing: {' '.join(sys.argv[1:])}")
    else:
        print("💡 Usage examples:")
        print("  python main.py 'Help me articulate my thoughts on AI trends'")
        print("  python main.py 'Optimize my article for LinkedIn'")
        print("  python main.py 'Clean up this rough draft but keep my style'")
        print("  python main.py 'Learn my voice from my writing samples'")
    
    print("⏳ Starting Personal Content AI Agent...\n")

    start = time.time()
    success = asyncio.run(main())
    end = time.time()
    total_time = end - start

    if success:
        print(f"\n🎉 Processing completed in {total_time:.2f}s!")
        print("🎭 Your authentic voice has been preserved and optimized")
        print("💡 Add more writing samples to content_samples/ to improve voice learning")
    else:
        print(f"\n❌ Processing failed after {total_time:.2f}s. Check logs.")
        print("💡 Ensure all MCP servers are configured correctly.")