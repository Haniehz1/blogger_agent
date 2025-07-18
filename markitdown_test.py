#!/usr/bin/env python3
"""
Simple test script for the markitdown MCP server
Tests if we can connect to and use the markitdown server to convert files.
"""

import asyncio
import os
from pathlib import Path
from mcp_agent.mcp.gen_client import gen_client

async def test_markitdown():
    """Test the markitdown MCP server functionality."""
    
    print("🧪 Testing markitdown MCP server...")
    print("-" * 50)
    
    try:
        # Connect to markitdown server
        print("📡 Connecting to markitdown server...")
        async with gen_client("markitdown") as client:
            print("✅ Connected to markitdown server!")
            
            # List available tools
            print("\n🔧 Available tools:")
            tools = await client.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Check content_samples directory
            content_samples_dir = Path("content_samples")
            if not content_samples_dir.exists():
                print(f"\n❌ Directory {content_samples_dir} doesn't exist")
                print("💡 Create it and add some files to test")
                return
            
            # Find files to convert
            print(f"\n📁 Looking for files in {content_samples_dir}...")
            files_found = []
            
            # Common file extensions that markitdown can handle
            supported_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.html', '.htm']
            
            for ext in supported_extensions:
                files = list(content_samples_dir.rglob(f"*{ext}"))
                files_found.extend(files)
            
            if not files_found:
                print("❌ No supported files found in content_samples/")
                print(f"💡 Supported formats: {', '.join(supported_extensions)}")
                print("💡 Add some files to content_samples/ and try again")
                return
            
            print(f"📄 Found {len(files_found)} files to convert:")
            for file in files_found:
                print(f"  - {file}")
            
            # Test conversion on the first file
            test_file = files_found[0]
            print(f"\n🔄 Testing conversion of: {test_file}")
            
            try:
                # Convert file to markdown
                # Check what tools are available first
                tool_names = [tool.name for tool in tools.tools]
                print(f"Available tool names: {tool_names}")
                
                # Try to find the right tool name
                convert_tool = None
                for tool in tools.tools:
                    if 'convert' in tool.name.lower() or 'markdown' in tool.name.lower():
                        convert_tool = tool.name
                        break
                
                if not convert_tool:
                    print("❌ Could not find conversion tool")
                    print("Available tools:")
                    for tool in tools.tools:
                        print(f"  - {tool.name}")
                    return
                
                print(f"🔧 Using tool: {convert_tool}")
                
                # Call the conversion tool
                result = await client.call_tool(
                    name=convert_tool,
                    arguments={"uri": f"file://{test_file.absolute()}"}
                )
                
                print("✅ Conversion successful!")
                print("\n📝 Converted content preview (first 500 chars):")
                print("-" * 50)
                content = result.content[0].text if result.content else "No content returned"
                print(content[:500] + ("..." if len(content) > 500 else ""))
                print("-" * 50)
                
                # Save converted content
                output_file = test_file.with_suffix('.md')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"\n💾 Saved converted content to: {output_file}")
                
            except Exception as e:
                print(f"❌ Conversion failed: {str(e)}")
                print("💡 Check if the file path is correct and accessible")
            
    except Exception as e:
        print(f"❌ Failed to connect to markitdown server: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure markitdown server is configured in mcp_agent.config.yaml")
        print("2. Install markitdown server: npm install -g @modelcontextprotocol/server-markitdown")
        print("3. Check if the server is running")


async def test_server_availability():
    """Test if markitdown server is available."""
    print("🔍 Checking server availability...")
    
    try:
        async with gen_client("markitdown") as client:
            print("✅ markitdown server is available")
            return True
    except Exception as e:
        print(f"❌ markitdown server not available: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🎯 markitdown MCP Server Test")
    print("=" * 50)
    
    # Test server availability first
    if not await test_server_availability():
        print("\n💡 Setup Instructions:")
        print("1. Install markitdown server:")
        print("   npm install -g @modelcontextprotocol/server-markitdown")
        print("\n2. Add to mcp_agent.config.yaml:")
        print("   mcp:")
        print("     servers:")
        print("       markitdown:")
        print("         command: \"npx\"")
        print("         args: [\"-y\", \"@modelcontextprotocol/server-markitdown\"]")
        return
    
    # Run full test
    await test_markitdown()
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())