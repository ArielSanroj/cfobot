#!/usr/bin/env python3
"""
MCP Server for CFO Bot - Provides conversational interface to financial analysis pipeline.
This is a simplified MCP server implementation that works with Nanobot.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the current directory to Python path to import cfobot modules
sys.path.insert(0, str(Path(__file__).parent))

from cfobot.cli import run_pipeline
from cfobot.config import AppConfig, load_config
from cfobot.data_loader import find_latest_report, load_financial_data
from cfobot.processing import compute_budget_execution, compute_kpis, consolidate_balance
from cfobot.reporting import (
    build_board_report,
    extract_caratula_difference,
    generate_all_figures,
    save_budget_execution,
    save_consolidated_balance,
    save_kpis,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cfobot-mcp")

class CFOBotMCPServer:
    """MCP Server that provides CFO analysis capabilities."""
    
    def __init__(self):
        self.config = load_config()
        self.current_data = None
        self.outputs = []
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "cfobot-mcp",
                "version": "1.0.0"
            }
        }
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return [
            {
                "name": "analyze_financial_report",
                "description": "Analyze the latest financial report and generate comprehensive CFO analysis including KPIs, budget execution, and board report",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "generate_visuals": {
                            "type": "boolean",
                            "description": "Whether to generate visual charts and graphs",
                            "default": True
                        },
                        "send_email": {
                            "type": "boolean", 
                            "description": "Whether to send analysis results via email",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "get_kpi_summary",
                "description": "Get a summary of key performance indicators from the latest analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_budget_execution",
                "description": "Get budget execution analysis showing actual vs planned performance",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_balance_summary",
                "description": "Get consolidated balance sheet summary",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "upload_excel_report",
                "description": "Upload and analyze a new Excel financial report",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Excel file to analyze"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "get_available_reports",
                "description": "List available financial reports in the downloads directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls."""
        try:
            if name == "analyze_financial_report":
                return await self._analyze_financial_report(
                    arguments.get("generate_visuals", True),
                    arguments.get("send_email", False)
                )
            elif name == "get_kpi_summary":
                return await self._get_kpi_summary()
            elif name == "get_budget_execution":
                return await self._get_budget_execution()
            elif name == "get_balance_summary":
                return await self._get_balance_summary()
            elif name == "upload_excel_report":
                return await self._upload_excel_report(arguments["file_path"])
            elif name == "get_available_reports":
                return await self._get_available_reports()
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return {"error": str(e)}
    
    async def _analyze_financial_report(self, generate_visuals: bool, send_email: bool) -> Dict[str, Any]:
        """Run the complete CFO analysis pipeline."""
        try:
            logger.info("Starting financial report analysis...")
            
            # Find and load the latest report
            report_path = find_latest_report(self.config, logger)
            self.current_data = load_financial_data(report_path, self.config, logger)
            
            # Run analysis pipeline
            consolidated = consolidate_balance(self.current_data, self.config)
            budget = compute_budget_execution(self.current_data, self.config)
            kpis = compute_kpis(self.current_data, budget)
            
            # Generate outputs
            self.outputs = [
                save_consolidated_balance(consolidated, self.current_data),
                save_budget_execution(budget, self.current_data),
                save_kpis(kpis, self.current_data),
            ]
            
            if generate_visuals and self.config.generate_visuals:
                figures_paths = generate_all_figures(budget, kpis, self.current_data)
                self.outputs.extend(figures_paths)
            
            diferencia = extract_caratula_difference(self.current_data)
            board_report = build_board_report(budget, kpis, self.current_data, diferencia)
            self.outputs.append(board_report)
            
            # Send email if requested
            if send_email and self.config.email:
                from cfobot.emailer import send_reports
                from cfobot.templates import build_email_html
                
                subject = f"Reporte CFO Automatizado - {self.current_data.current_month} 2025"
                html_body = build_email_html(
                    current_month=self.current_data.current_month,
                    outputs=self.outputs,
                    recipient_count=len(self.config.email.recipient_emails)
                )
                send_reports(self.config.email, subject, html_body, self.outputs)
            
            return {
                "success": True,
                "message": f"Analysis completed for {self.current_data.current_month}",
                "outputs": [str(path) for path in self.outputs],
                "month": self.current_data.current_month,
                "kpis_generated": len(kpis) if hasattr(kpis, '__len__') else 0,
                "budget_analysis": "completed",
                "balance_consolidated": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in financial analysis: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _get_kpi_summary(self) -> Dict[str, Any]:
        """Get KPI summary from current analysis."""
        if not self.current_data:
            return {"error": "No analysis data available. Run analyze_financial_report first."}
        
        try:
            # Re-run KPI computation
            budget = compute_budget_execution(self.current_data, self.config)
            kpis = compute_kpis(self.current_data, budget)
            
            # Extract key metrics
            kpi_summary = {}
            for kpi in kpis:
                if hasattr(kpi, 'name') and hasattr(kpi, 'value'):
                    kpi_summary[kpi.name] = kpi.value
                elif isinstance(kpi, dict):
                    kpi_summary.update(kpi)
            
            return {
                "success": True,
                "month": self.current_data.current_month,
                "kpis": kpi_summary,
                "total_kpis": len(kpis)
            }
        except Exception as e:
            return {"error": f"Failed to get KPI summary: {str(e)}"}
    
    async def _get_budget_execution(self) -> Dict[str, Any]:
        """Get budget execution analysis."""
        if not self.current_data:
            return {"error": "No analysis data available. Run analyze_financial_report first."}
        
        try:
            budget = compute_budget_execution(self.current_data, self.config)
            
            return {
                "success": True,
                "month": self.current_data.current_month,
                "budget_execution": {
                    "monthly_income_budget": self.config.budgets.ingresos_mensual,
                    "monthly_expense_budget": self.config.budgets.gastos_mensual,
                    "actual_income": getattr(budget, 'actual_income', 'N/A'),
                    "actual_expenses": getattr(budget, 'actual_expenses', 'N/A'),
                    "variance_income": getattr(budget, 'income_variance', 'N/A'),
                    "variance_expenses": getattr(budget, 'expense_variance', 'N/A')
                }
            }
        except Exception as e:
            return {"error": f"Failed to get budget execution: {str(e)}"}
    
    async def _get_balance_summary(self) -> Dict[str, Any]:
        """Get consolidated balance summary."""
        if not self.current_data:
            return {"error": "No analysis data available. Run analyze_financial_report first."}
        
        try:
            consolidated = consolidate_balance(self.current_data, self.config)
            
            return {
                "success": True,
                "month": self.current_data.current_month,
                "balance_summary": {
                    "total_assets": getattr(consolidated, 'total_assets', 'N/A'),
                    "total_liabilities": getattr(consolidated, 'total_liabilities', 'N/A'),
                    "equity": getattr(consolidated, 'equity', 'N/A'),
                    "accounts_count": len(consolidated) if hasattr(consolidated, '__len__') else 'N/A'
                }
            }
        except Exception as e:
            return {"error": f"Failed to get balance summary: {str(e)}"}
    
    async def _upload_excel_report(self, file_path: str) -> Dict[str, Any]:
        """Upload and analyze a new Excel report."""
        try:
            report_path = Path(file_path)
            if not report_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Load the new report
            self.current_data = load_financial_data(report_path, self.config, logger)
            
            return {
                "success": True,
                "message": f"Successfully loaded report: {file_path}",
                "month": self.current_data.current_month,
                "sheets_loaded": len(self.current_data.workbook.sheet_names)
            }
        except Exception as e:
            return {"error": f"Failed to upload report: {str(e)}"}
    
    async def _get_available_reports(self) -> Dict[str, Any]:
        """List available reports in downloads directory."""
        try:
            pattern = self.config.paths.expand_pattern()
            import glob
            files = glob.glob(pattern)
            
            report_files = []
            for file_path in files:
                path = Path(file_path)
                report_files.append({
                    "path": str(path),
                    "name": path.name,
                    "size": path.stat().st_size,
                    "modified": path.stat().st_mtime
                })
            
            return {
                "success": True,
                "reports": sorted(report_files, key=lambda x: x["modified"], reverse=True),
                "pattern": pattern
            }
        except Exception as e:
            return {"error": f"Failed to list reports: {str(e)}"}


async def main():
    """Main entry point for the MCP server."""
    server = CFOBotMCPServer()
    
    # Simple MCP protocol implementation for Nanobot
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            request = json.loads(line.strip())
            
            if request.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": await server.initialize()
                }
            elif request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id"),
                    "result": {"tools": await server.list_tools()}
                }
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                result = await server.call_tool(
                    params.get("name"),
                    params.get("arguments", {})
                )
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method not found: {request.get('method')}"}
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())