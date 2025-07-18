# 🎯 Personal Content AI Agent

> AI agent that articulates your thoughts and optimizes them for different platforms while preserving your authentic voice

## 🚀 What It Does

**The Problem**: You know what you want to say, but struggle to articulate it clearly or adapt it for different platforms without losing your authentic voice.

**The Solution**: This AI agent learns your unique writing style and helps you:
- **Articulate rough ideas** into clear, compelling content
- **Optimize content** for specific platforms (Twitter, LinkedIn, Medium, Instagram)
- **Clean up drafts** while preserving your authentic voice
- **Learn from your writing** to maintain consistency

## 🎭 Key Features

- **🧠 Voice Learning**: Analyzes your writing samples to learn your unique voice
- **💬 Content Articulation**: Takes rough ideas and articulates them clearly
- **📱 Platform Optimization**: Adapts content for Twitter, LinkedIn, Medium, Instagram
- **🎨 Style Preservation**: Maintains your authentic voice throughout
- **❓ Smart Elicitation**: Asks clarifying questions to understand your needs
- **🔄 Quality Assurance**: Ensures content sounds like you, not generic AI

## 🏗️ Architecture

Built on the [MCP-Agent framework](https://github.com/lastmile-ai/mcp-agent) with:
- **Content Server**: Interactive elicitation for content processing
- **Voice Analysis**: Learns your writing patterns from samples
- **Platform Optimization**: Adapts content for specific platforms
- **Style Guardian**: Ensures authenticity throughout the process

## 🛠️ Quick Start

### 1. Setup
```bash
# Clone or create project directory
mkdir personal-content-ai-agent
cd personal-content-ai-agent

# Install dependencies
pip install mcp-agent fastmcp pydantic pyyaml rich typer textstat langdetect

# Create the project structure
mkdir -p content_samples/{social_media,articles,emails,presentations}
mkdir -p platform_configs voice_patterns output/{drafts,final}
```

### 2. Configure API Keys
```bash
# Copy and edit secrets file
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
# Add your OpenAI or Anthropic API key
```

### 3. Add Your Writing Samples
```bash
# Add your existing content to content_samples/
# - Social media posts in content_samples/social_media/
# - Articles in content_samples/articles/
# - Emails in content_samples/emails/
# - Any other writing samples
```

### 4. Start the Agent
```bash
# Learn your voice from samples
python main.py "Learn my voice from my writing samples"

# Articulate rough content
python main.py "Help me articulate my thoughts on AI trends for LinkedIn"

# Optimize existing content
python main.py "Optimize my article for Twitter"

# Clean up a draft
python main.py "Clean up this rough draft but keep my style"
```

## 📊 Usage Examples

### Example 1: Content Articulation
```bash
python main.py "I want to share my thoughts on remote work but make it professional"
```
**What happens:**
1. Agent asks clarifying questions about your thoughts
2. Analyzes your voice patterns from samples
3. Articulates your ideas clearly in your authentic style
4. Optimizes for your preferred platform

### Example 2: Platform Optimization
```bash
python main.py "Take my blog post and optimize it for LinkedIn"
```
**What happens:**
1. Agent processes your blog post
2. Extracts key points suitable for LinkedIn
3. Adapts format and tone for professional networking
4. Maintains your authentic voice throughout

### Example 3: Style Cleanup
```bash
python main.py "Clean up this rough draft: [your messy content]"
```
**What happens:**
1. Agent analyzes your rough content
2. Applies your learned voice patterns
3. Improves clarity and flow
4. Preserves your authentic tone and style

## 🔧 How It Works

### 1. **Voice Learning**
- Analyzes your writing samples in `content_samples/`
- Extracts tone, vocabulary, structure patterns
- Saves voice patterns for consistent content creation

### 2. **Content Processing**
- Uses interactive elicitation to understand your needs
- Applies learned voice patterns to new content
- Maintains authenticity while improving clarity

### 3. **Platform Optimization**
- Adapts content for specific platform requirements
- Applies platform-specific best practices
- Preserves your voice while optimizing format

### 4. **Quality Assurance**
- Style Guardian evaluates authenticity
- Ensures content sounds like you wrote it
- Provides feedback and improvements

## 📁 Project Structure

```
personal-content-ai-agent/
├── main.py                          # Main orchestrator
├── content_server.py                # Content processing with elicitation
├── mcp_agent.config.yaml            # MCP configuration
├── mcp_agent.secrets.yaml           # API keys (create from .example)
├── content_samples/                 # Your writing samples
│   ├── social_media/               # Social media posts
│   ├── articles/                   # Long-form articles
│   ├── emails/                     # Email examples
│   └── presentations/              # Presentation content
├── platform_configs/               # Platform-specific rules
│   ├── twitter.yaml                # Twitter optimization
│   ├── linkedin.yaml               # LinkedIn optimization
│   ├── medium.yaml                 # Medium optimization
│   └── instagram.yaml              # Instagram optimization
├── voice_patterns/                  # Learned voice patterns
│   └── extracted_patterns.yaml     # Your voice characteristics
└── output/                         # Generated content
    ├── drafts/                     # Draft versions
    └── final/                      # Final content
```

## 🎯 Use Cases

### **Content Creators**
- Maintain consistent voice across platforms
- Articulate complex ideas clearly
- Optimize content for different audiences

### **Business Professionals**
- Transform rough ideas into polished content
- Adapt messages for different platforms
- Maintain professional voice consistency

### **Writers & Bloggers**
- Clean up rough drafts while preserving style
- Adapt long-form content for social media
- Maintain authentic voice across formats

### **Marketing Teams**
- Ensure brand voice consistency
- Optimize content for different platforms
- Articulate campaign messages clearly

## 🔒 Privacy & Data

- **Local Processing**: All content stays on your machine
- **No Cloud Sync**: Your writing samples never leave your system
- **Full Control**: You own all your data and voice patterns
- **MCP Standard**: Uses standard Model Context Protocol for tool access

## 🤝 Contributing

This project is built on the MCP-Agent framework. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs or request features
- **Documentation**: Check the examples and configurations
- **Community**: Join discussions about content AI and voice preservation

---

**Your authentic voice, optimized for every platform. 🎭**
