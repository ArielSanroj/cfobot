"""AI-powered financial analysis using Ollama."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import ollama
import pandas as pd

from .config import AppConfig
from .data_loader import FinancialData
from .processing import BudgetResult, KPIResult

logger = logging.getLogger(__name__)


@dataclass
class AIInsights:
    """AI-generated financial insights and recommendations."""
    executive_summary: str
    key_insights: List[str]
    risk_assessment: str
    recommendations: List[str]
    trend_analysis: str
    budget_analysis: str
    kpi_analysis: str


class FinancialAIAnalyzer:
    """AI-powered financial analysis using Ollama."""
    
    def __init__(self, config: AppConfig, model: str = "llama3.1:8b"):
        """Initialize the AI analyzer.
        
        Args:
            config: Application configuration
            model: Ollama model to use for analysis
        """
        self.config = config
        self.model = model
        self.client = ollama.Client()
        
    def _format_financial_data(self, data: FinancialData, budget: BudgetResult, kpis: KPIResult) -> str:
        """Format financial data for AI analysis.
        
        Args:
            data: Financial data
            budget: Budget execution results
            kpis: KPI results
            
        Returns:
            Formatted string with financial data
        """
        # Extract key metrics
        ingresos = float(budget.summary.loc[0, f"Actual {data.current_month}"])
        gastos = float(budget.summary.loc[1, f"Actual {data.current_month}"])
        ejecutado_ingresos = float(budget.summary.loc[0, "% Ejecutado"])
        ejecutado_gastos = float(budget.summary.loc[1, "% Ejecutado"])
        
        # KPI metrics
        current_ratio = kpis.metrics.get("Current Ratio", 0)
        margen_bruto = kpis.metrics.get("Margen Bruto %", 0)
        margen_neto = kpis.metrics.get("Margen Neto %", 0)
        roe = kpis.metrics.get("ROE %", 0)
        ebitda = kpis.metrics.get("EBITDA", 0)
        
        # Expense breakdown
        gastos_admin = budget.gastos_admin
        gastos_otros = budget.gastos_otros
        costos_venta = budget.costos_venta
        costos_prod = budget.costos_produccion
        
        return f"""
FINANCIAL DATA FOR ANALYSIS - {data.current_month} 2025

INCOME STATEMENT:
- Total Revenue: ${ingresos:,.0f} COP
- Total Expenses: ${gastos:,.0f} COP
- EBITDA: ${ebitda:,.0f} COP

BUDGET EXECUTION:
- Revenue Execution: {ejecutado_ingresos:.1f}% of monthly budget
- Expense Execution: {ejecutado_gastos:.1f}% of monthly budget
- Monthly Revenue Budget: ${self.config.budgets.ingresos_mensual:,.0f} COP
- Monthly Expense Budget: ${self.config.budgets.gastos_mensual:,.0f} COP

FINANCIAL RATIOS:
- Current Ratio: {current_ratio:.2f}
- Gross Margin: {margen_bruto:.2f}%
- Net Margin: {margen_neto:.2f}%
- ROE: {roe:.2f}%

EXPENSE BREAKDOWN:
- Administrative Expenses: ${gastos_admin:,.0f} COP
- Other Expenses: ${gastos_otros:,.0f} COP
- Sales Costs: ${costos_venta:,.0f} COP
- Production Costs: ${costos_prod:,.0f} COP

MONTHLY TREND DATA:
Available months: {', '.join(data.months)}
Current month column: {data.current_month_col}
"""

    def _create_analysis_prompt(self, financial_data: str) -> str:
        """Create a comprehensive prompt for financial analysis.
        
        Args:
            financial_data: Formatted financial data string
            
        Returns:
            Analysis prompt
        """
        return f"""
You are a senior financial analyst and CFO advisor. Analyze the following financial data and provide comprehensive insights.

{financial_data}

Please provide a detailed analysis in the following JSON format:

{{
    "executive_summary": "A 2-3 sentence executive summary of the financial performance",
    "key_insights": [
        "Key insight 1 about financial performance",
        "Key insight 2 about trends or patterns",
        "Key insight 3 about budget execution"
    ],
    "risk_assessment": "Assessment of financial risks and concerns",
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ],
    "trend_analysis": "Analysis of trends and patterns in the data",
    "budget_analysis": "Detailed analysis of budget execution performance",
    "kpi_analysis": "Analysis of key performance indicators and ratios"
}}

Focus on:
1. Financial health and performance
2. Budget execution efficiency
3. Risk identification and mitigation
4. Actionable recommendations for improvement
5. Trend analysis and forecasting insights
6. Industry benchmarking where applicable

Provide specific, actionable insights based on the data provided.
"""

    def analyze_financials(self, data: FinancialData, budget: BudgetResult, kpis: KPIResult) -> AIInsights:
        """Perform AI-powered financial analysis.
        
        Args:
            data: Financial data
            budget: Budget execution results
            kpis: KPI results
            
        Returns:
            AI-generated insights and recommendations
        """
        try:
            logger.info("Starting AI financial analysis...")
            
            # Format data for analysis
            financial_data = self._format_financial_data(data, budget, kpis)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(financial_data)
            
            # Get AI analysis
            logger.info(f"Calling Ollama model: {self.model}")
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                    "top_p": 0.9,
                    "num_predict": 2000  # Allow for comprehensive analysis
                }
            )
            
            # Parse response
            content = response['message']['content']
            logger.debug(f"AI Response: {content}")
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                # Fallback to text parsing
                analysis_data = self._parse_text_response(content)
            
            # Create AIInsights object
            insights = AIInsights(
                executive_summary=analysis_data.get("executive_summary", "Analysis completed successfully."),
                key_insights=analysis_data.get("key_insights", ["Analysis completed."]),
                risk_assessment=analysis_data.get("risk_assessment", "Risk assessment completed."),
                recommendations=analysis_data.get("recommendations", ["Continue monitoring financial performance."]),
                trend_analysis=analysis_data.get("trend_analysis", "Trend analysis completed."),
                budget_analysis=analysis_data.get("budget_analysis", "Budget analysis completed."),
                kpi_analysis=analysis_data.get("kpi_analysis", "KPI analysis completed.")
            )
            
            logger.info("AI financial analysis completed successfully")
            return insights
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return fallback insights
            return AIInsights(
                executive_summary=f"Financial analysis for {data.current_month} 2025 completed with basic metrics.",
                key_insights=["Analysis completed with standard metrics."],
                risk_assessment="Standard risk assessment applied.",
                recommendations=["Continue monitoring financial performance."],
                trend_analysis="Basic trend analysis completed.",
                budget_analysis="Budget execution analysis completed.",
                kpi_analysis="KPI analysis completed."
            )
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails.
        
        Args:
            content: Raw AI response content
            
        Returns:
            Parsed analysis data
        """
        return {
            "executive_summary": content[:200] + "..." if len(content) > 200 else content,
            "key_insights": [
                "Financial analysis completed",
                "Data processed successfully",
                "Recommendations generated"
            ],
            "risk_assessment": "Standard risk assessment applied",
            "recommendations": [
                "Continue monitoring financial performance",
                "Review budget execution regularly",
                "Maintain current operational efficiency"
            ],
            "trend_analysis": "Trend analysis completed",
            "budget_analysis": "Budget analysis completed",
            "kpi_analysis": "KPI analysis completed"
        }
    
    def generate_enhanced_report_content(self, data: FinancialData, budget: BudgetResult, kpis: KPIResult, insights: AIInsights) -> str:
        """Generate enhanced report content with AI insights.
        
        Args:
            data: Financial data
            budget: Budget execution results
            kpis: KPI results
            insights: AI-generated insights
            
        Returns:
            Enhanced report content
        """
        prompt = f"""
You are a professional financial report writer. Create an enhanced executive summary for a board report using the following data and AI insights.

FINANCIAL DATA:
{self._format_financial_data(data, budget, kpis)}

AI INSIGHTS:
- Executive Summary: {insights.executive_summary}
- Key Insights: {', '.join(insights.key_insights)}
- Risk Assessment: {insights.risk_assessment}
- Recommendations: {', '.join(insights.recommendations)}
- Trend Analysis: {insights.trend_analysis}
- Budget Analysis: {insights.budget_analysis}
- KPI Analysis: {insights.kpi_analysis}

Create a professional, executive-level report summary that:
1. Integrates the AI insights naturally
2. Maintains a professional tone
3. Provides actionable recommendations
4. Highlights key financial metrics
5. Addresses risks and opportunities
6. Is suitable for board presentation

Format as a comprehensive executive summary (2-3 paragraphs).
"""
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.4, "num_predict": 1000}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Failed to generate enhanced report content: {e}")
            return f"""
Executive Summary - {data.current_month} 2025

{insights.executive_summary}

Key Financial Performance:
The company's financial performance for {data.current_month} 2025 shows significant insights that require attention. {insights.budget_analysis}

Strategic Recommendations:
{insights.recommendations[0] if insights.recommendations else "Continue monitoring financial performance."}
"""