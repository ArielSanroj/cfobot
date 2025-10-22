"""Email and report templates for CFO Bot."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def build_email_html(
    current_month: str,
    outputs: Iterable[Path],
    recipient_count: int
) -> str:
    """Build professional HTML email template for CFO reports.
    
    Args:
        current_month: Current month name
        outputs: List of generated output files
        recipient_count: Number of email recipients
        
    Returns:
        HTML email content
        
    Examples:
        >>> html = build_email_html("MARZO", [Path("report.xlsx")], 2)
        >>> "Reporte Financiero Automatizado" in html
        True
    """
    outputs_list = list(outputs)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .content {{ margin: 20px 0; }}
            .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .files {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .footer {{ color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #34495e; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Reporte Financiero Automatizado</h1>
            <h2>{current_month} 2025</h2>
        </div>
        
        <div class="content">
            <div class="summary">
                <h3>📈 Resumen Ejecutivo</h3>
                <p>Se ha generado automáticamente el reporte financiero para el mes de <strong>{current_month} 2025</strong>.</p>
                <p>El sistema ha procesado los datos financieros y generado análisis detallados incluyendo:</p>
                <ul>
                    <li>✅ Métricas agregadas (EBITDA, ratios financieros)</li>
                    <li>✅ Análisis de ejecución presupuestaria</li>
                    <li>✅ Distribución de gastos por categoría</li>
                    <li>✅ Indicadores financieros clave (KPIs)</li>
                    <li>✅ Visualizaciones gráficas</li>
                    <li>✅ Informe para Junta Directiva</li>
                </ul>
            </div>
            
            <div class="files">
                <h3>📁 Archivos Generados ({len(outputs_list)} archivos)</h3>
                <ul>
    """
    
    # Add file list
    for output in outputs_list:
        file_type = "📊" if output.suffix == ".png" else "📄" if output.suffix == ".docx" else "📋"
        html_body += f"<li>{file_type} {output.name}</li>"
    
    html_body += f"""
                </ul>
            </div>
            
            <div class="footer">
                <p>Este reporte fue generado automáticamente por el Sistema CFO Bot v1.0</p>
                <p>Fecha de generación: {current_month} 2025</p>
                <p>Enviado a {recipient_count} destinatario(s)</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body


def build_ai_enhanced_email_html(
    current_month: str,
    outputs: Iterable[Path],
    recipient_count: int,
    ai_insights
) -> str:
    """Build AI-enhanced HTML email template for CFO reports.
    
    Args:
        current_month: Current month name
        outputs: List of generated output files
        recipient_count: Number of email recipients
        ai_insights: AI-generated insights
        
    Returns:
        HTML email content with AI insights
    """
    outputs_list = list(outputs)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .content {{ margin: 20px 0; }}
            .ai-summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin: 10px 0; }}
            .ai-insights {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #27ae60; }}
            .ai-recommendations {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107; }}
            .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .files {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .footer {{ color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #34495e; color: white; }}
            .ai-badge {{ background-color: #27ae60; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Reporte Financiero con IA</h1>
            <h2>{current_month} 2025 <span class="ai-badge">POTENCIADO POR IA</span></h2>
        </div>
        
        <div class="content">
            <div class="ai-summary">
                <h3>🧠 Resumen Ejecutivo con IA</h3>
                <p>{ai_insights.executive_summary}</p>
            </div>
            
            <div class="ai-insights">
                <h3>💡 Insights Clave de IA</h3>
                <ul>
    """
    
    # Add AI insights
    for insight in ai_insights.key_insights:
        html_body += f"<li>{insight}</li>"
    
    html_body += f"""
                </ul>
            </div>
            
            <div class="ai-recommendations">
                <h3>🎯 Recomendaciones Estratégicas de IA</h3>
                <ol>
    """
    
    # Add AI recommendations
    for i, recommendation in enumerate(ai_insights.recommendations, 1):
        html_body += f"<li>{recommendation}</li>"
    
    html_body += f"""
                </ol>
            </div>
            
            <div class="summary">
                <h3>📈 Análisis Financiero Detallado</h3>
                <p>El sistema ha procesado los datos financieros con análisis de IA avanzado incluyendo:</p>
                <ul>
                    <li>✅ Análisis predictivo con IA</li>
                    <li>✅ Detección automática de patrones</li>
                    <li>✅ Evaluación de riesgos inteligente</li>
                    <li>✅ Recomendaciones estratégicas personalizadas</li>
                    <li>✅ Métricas agregadas (EBITDA, ratios financieros)</li>
                    <li>✅ Análisis de ejecución presupuestaria</li>
                    <li>✅ Distribución de gastos por categoría</li>
                    <li>✅ Indicadores financieros clave (KPIs)</li>
                    <li>✅ Visualizaciones gráficas</li>
                    <li>✅ Informe para Junta Directiva con IA</li>
                </ul>
            </div>
            
            <div class="files">
                <h3>📁 Archivos Generados ({len(outputs_list)} archivos)</h3>
                <ul>
    """
    
    # Add file list
    for output in outputs_list:
        file_type = "📊" if output.suffix == ".png" else "📄" if output.suffix == ".docx" else "📋"
        ai_indicator = "🤖" if "ai" in output.name.lower() else ""
        html_body += f"<li>{file_type} {ai_indicator} {output.name}</li>"
    
    html_body += f"""
                </ul>
            </div>
            
            <div class="footer">
                <p>Este reporte fue generado automáticamente por el Sistema CFO Bot v2.0 con Ollama</p>
                <p>Fecha de generación: {current_month} 2025</p>
                <p>Enviado a {recipient_count} destinatario(s)</p>
                <p>Análisis de IA realizado con modelo Ollama</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body


def build_error_email_html(
    error_message: str,
    current_month: str
) -> str:
    """Build HTML email template for error notifications.
    
    Args:
        error_message: Error description
        current_month: Current month name
        
    Returns:
        HTML email content for error notification
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #e74c3c; color: white; padding: 20px; border-radius: 5px; }}
            .content {{ margin: 20px 0; }}
            .error {{ background-color: #fdf2f2; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #e74c3c; }}
            .footer {{ color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚠️ Error en Generación de Reporte</h1>
            <h2>{current_month} 2025</h2>
        </div>
        
        <div class="content">
            <div class="error">
                <h3>❌ Error Detectado</h3>
                <p>Se ha producido un error durante la generación del reporte financiero para el mes de <strong>{current_month} 2025</strong>.</p>
                <p><strong>Detalles del error:</strong></p>
                <pre>{error_message}</pre>
                <p>Por favor, revise la configuración y los archivos de entrada, o contacte al administrador del sistema.</p>
            </div>
            
            <div class="footer">
                <p>Este mensaje fue generado automáticamente por el Sistema CFO Bot v1.0</p>
                <p>Fecha: {current_month} 2025</p>
            </div>
        </div>
    </body>
    </html>
    """
