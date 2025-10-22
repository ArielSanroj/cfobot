# CFO Bot MCP Agent Integration

This document describes how to use the CFO Bot with Nanobot MCP for conversational financial analysis.

## Overview

The CFO Bot has been integrated with Nanobot MCP to provide a conversational interface for financial analysis. Users can now interact with the CFO system through a web-based chat interface, making it accessible to non-technical users.

## Features

The MCP-enabled CFO Agent provides the following capabilities:

- **Automated Financial Analysis**: Analyze Excel financial reports with a simple command
- **KPI Generation**: Generate comprehensive key performance indicators
- **Budget Execution Analysis**: Compare actual vs planned performance
- **Balance Sheet Consolidation**: Create consolidated balance summaries
- **Report Management**: Upload new reports and list available ones
- **Email Integration**: Send analysis results via email
- **Visual Reports**: Generate charts and graphs automatically

## Setup

### Prerequisites

1. **API Key**: You need either an OpenAI or Anthropic API key
   ```bash
   # For OpenAI (recommended)
   export OPENAI_API_KEY=sk-...
   
   # For Anthropic
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

2. **Dependencies**: All required packages are already installed

### Starting the CFO Agent

1. **Quick Start**:
   ```bash
   python start_cfo_agent.py
   ```

2. **Manual Start**:
   ```bash
   nanobot run nanobot.yaml
   ```

3. **Access the Web Interface**:
   - Open your browser to `http://localhost:8080`
   - Start chatting with the CFO Financial Analyst

## Usage Examples

### Basic Analysis
```
User: "Analyze the latest financial report"
Agent: "I'll analyze the latest financial report for you. Let me process the Excel file and generate comprehensive KPIs, budget execution analysis, and board report..."
```

### KPI Summary
```
User: "Show me the KPI summary"
Agent: "Here's the KPI summary for [month]: [detailed KPI breakdown]"
```

### Budget Analysis
```
User: "How is our budget execution looking?"
Agent: "Let me check the budget execution analysis... [detailed budget vs actual comparison]"
```

### Upload New Report
```
User: "Upload and analyze this Excel file: /path/to/report.xlsx"
Agent: "I'll upload and analyze the new Excel report for you..."
```

## Configuration

The agent configuration is in `nanobot.yaml`:

```yaml
agents:
  cfo_analyst:
    name: "CFO Financial Analyst"
    model: "gpt-4o"  # or "claude-3"
    mcpServers: 
      - cfobot_mcp

mcpServers:
  cfobot_mcp:
    command: "python"
    args: ["cfo_mcp_server.py"]
    env:
      PYTHONPATH: "."
```

## Available Tools

The MCP server provides these tools:

1. **analyze_financial_report**: Complete financial analysis pipeline
2. **get_kpi_summary**: Get KPI summary from latest analysis
3. **get_budget_execution**: Get budget execution analysis
4. **get_balance_summary**: Get consolidated balance summary
5. **upload_excel_report**: Upload and analyze new Excel report
6. **get_available_reports**: List available financial reports

## File Structure

```
CFO/
├── cfo_mcp_server.py          # MCP server implementation
├── nanobot.yaml              # Nanobot configuration
├── start_cfo_agent.py        # Startup script
├── README_MCP.md            # This documentation
└── cfobot/                  # Original CFO bot modules
    ├── cli.py
    ├── config.py
    ├── data_loader.py
    └── ...
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**:
   ```
   Error: No API key found
   Solution: Set OPENAI_API_KEY or ANTHROPIC_API_KEY
   ```

2. **Port Already in Use**:
   ```
   Error: Port 8080 already in use
   Solution: Kill the process using port 8080 or change the port in nanobot.yaml
   ```

3. **Excel File Not Found**:
   ```
   Error: No file matching pattern found
   Solution: Ensure Excel files are in ~/Downloads/ with .xls* extension
   ```

### Logs

Check the console output for detailed logs. The MCP server logs all operations and errors.

## Advanced Usage

### Custom Model Configuration

Edit `nanobot.yaml` to use different models:

```yaml
agents:
  cfo_analyst:
    model: "gpt-4o-mini"  # Faster, cheaper
    # or
    model: "claude-3-sonnet"  # Alternative model
```

### Environment Variables

Set additional environment variables in `nanobot.yaml`:

```yaml
mcpServers:
  cfobot_mcp:
    command: "python"
    args: ["cfo_mcp_server.py"]
    env:
      PYTHONPATH: "."
      CFOBOT_EMAIL_SENDER: "your-email@company.com"
      CFOBOT_EMAIL_PASSWORD: "your-password"
      CFOBOT_EMAIL_RECIPIENT: "recipient@company.com"
```

## Integration with Existing Workflow

The MCP agent integrates seamlessly with your existing CFO pipeline:

1. **Same Data Sources**: Uses the same Excel file detection and processing
2. **Same Analysis**: Generates identical reports and KPIs
3. **Same Outputs**: Creates the same files in the same locations
4. **Enhanced Access**: Adds conversational interface on top

## Support

For issues or questions:
1. Check the console logs for error messages
2. Verify API keys are correctly set
3. Ensure Excel files are in the correct location
4. Check that all dependencies are installed

The CFO MCP Agent provides a powerful, user-friendly interface to your financial analysis pipeline while maintaining all the robust functionality of the original system.