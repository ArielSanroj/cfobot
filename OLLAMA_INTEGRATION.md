# CFO Bot with Ollama AI Integration

This document explains how to use the enhanced CFO Bot with Ollama AI integration for advanced financial analysis and report generation.

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Or use the setup script
python setup_ollama.py
```

### 2. Start Ollama Service

```bash
# Start Ollama service
ollama serve
```

### 3. Pull AI Model

```bash
# Pull the recommended model
ollama pull llama3.1:8b

# Or try other models
ollama pull mistral:7b
ollama pull codellama:7b
```

### 4. Run CFO Bot with AI

```bash
# Run with AI analysis (default)
python -m cfobot --verbose

# Run with specific AI model
python -m cfobot --ai-model mistral:7b

# Run without AI (fallback to standard analysis)
python -m cfobot --no-ai
```

## 🤖 AI Features

### Enhanced Financial Analysis

The AI integration provides:

- **Intelligent Executive Summaries**: AI-generated executive summaries that highlight key financial insights
- **Risk Assessment**: Automated identification of financial risks and concerns
- **Strategic Recommendations**: Actionable recommendations based on financial data patterns
- **Trend Analysis**: Advanced analysis of financial trends and patterns
- **Budget Analysis**: Intelligent budget execution analysis with insights
- **KPI Analysis**: Enhanced analysis of key performance indicators

### AI-Enhanced Reports

- **Board Reports**: AI-powered board reports with intelligent insights
- **Email Templates**: Enhanced email templates with AI-generated content
- **Visualizations**: AI-enhanced chart descriptions and analysis

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Enable/disable AI analysis
CFOBOT_OLLAMA_ENABLED=true

# AI model to use
CFOBOT_OLLAMA_MODEL=llama3.1:8b

# Ollama server URL
CFOBOT_OLLAMA_BASE_URL=http://localhost:11434

# AI response temperature (0.0-1.0)
CFOBOT_OLLAMA_TEMPERATURE=0.3

# Maximum tokens for AI response
CFOBOT_OLLAMA_MAX_TOKENS=2000
```

### Supported Models

| Model | Size | Recommended For | Description |
|-------|------|----------------|-------------|
| `llama3.1:8b` | ~4.7GB | General analysis | Balanced performance and quality |
| `llama3.1:70b` | ~40GB | Advanced analysis | Highest quality, requires more resources |
| `mistral:7b` | ~4.1GB | Fast analysis | Good balance of speed and quality |
| `codellama:7b` | ~3.8GB | Technical analysis | Specialized for code and technical content |
| `phi3:medium` | ~7.2GB | Efficient analysis | Good performance with lower resource usage |

## 📊 AI Analysis Examples

### Executive Summary
```
"During March 2025, the company demonstrated strong financial performance with revenue execution at 95.2% of budget and expense control at 98.1%. The EBITDA of $2.3M reflects healthy operational efficiency, though the current ratio of 1.2 indicates potential liquidity concerns that require attention."
```

### Key Insights
- Revenue execution is 5.2% below budget, primarily due to delayed Q1 contracts
- Administrative expenses increased 12% month-over-month, requiring cost control measures
- Gross margin improved to 34.2%, indicating effective pricing strategies

### Strategic Recommendations
- Implement immediate cost control measures for administrative expenses
- Accelerate Q1 contract closures to improve revenue execution
- Consider short-term financing to address liquidity concerns

## 🔧 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Restart Ollama service
   ollama serve
   ```

2. **Model Not Found**
   ```bash
   # List available models
   ollama list
   
   # Pull the required model
   ollama pull llama3.1:8b
   ```

3. **AI Analysis Fails**
   - Check Ollama service status
   - Verify model is available
   - Check system resources (RAM/CPU)
   - Review logs for specific error messages

### Performance Optimization

1. **Model Selection**: Choose smaller models for faster processing
2. **Resource Management**: Ensure adequate RAM for the selected model
3. **Temperature Settings**: Lower temperature (0.1-0.3) for more consistent results
4. **Token Limits**: Adjust max_tokens based on your needs

## 📈 Usage Examples

### Basic AI Analysis
```bash
# Run with default AI settings
python -m cfobot --verbose
```

### Custom AI Model
```bash
# Use a different model
python -m cfobot --ai-model mistral:7b --verbose
```

### Disable AI
```bash
# Run without AI (standard analysis)
python -m cfobot --no-ai --verbose
```

### Email with AI
```bash
# Send AI-enhanced reports via email
python -m cfobot --send-email --verbose
```

## 🛠️ Development

### Adding New AI Features

1. **Extend AIInsights class** in `cfobot/ai_analyzer.py`
2. **Add new analysis methods** to `FinancialAIAnalyzer`
3. **Update report templates** to include new insights
4. **Test with different models** for compatibility

### Custom Prompts

Modify the analysis prompts in `cfobot/ai_analyzer.py`:

```python
def _create_analysis_prompt(self, financial_data: str) -> str:
    # Customize the prompt for your specific needs
    return f"""
    Your custom prompt here...
    {financial_data}
    """
```

## 📝 Logs and Monitoring

### Enable Detailed Logging
```bash
python -m cfobot --verbose
```

### Check AI Analysis Logs
Look for these log messages:
- `Starting AI financial analysis...`
- `AI analysis completed successfully`
- `AI analysis failed, falling back to standard analysis`

## 🔒 Security Considerations

- Ollama runs locally, keeping your financial data private
- No data is sent to external AI services
- All analysis is performed on your local machine
- Consider network security if using remote Ollama instances

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Model Library](https://ollama.ai/library)
- [CFO Bot Documentation](README.md)
- [Financial Analysis Best Practices](https://example.com)

## 🤝 Support

For issues related to:
- **Ollama**: Check [Ollama GitHub](https://github.com/ollama/ollama)
- **CFO Bot AI Integration**: Check this repository's issues
- **Financial Analysis**: Consult with your financial team