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
