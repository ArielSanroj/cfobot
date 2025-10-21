"""Command-line interface for CFO bot."""

from __future__ import annotations

import argparse
import logging

from .config import AppConfig, load_config
from .data_loader import find_latest_report, load_financial_data
from .processing import compute_budget_execution, compute_kpis, consolidate_balance
from .reporting import (
    build_board_report,
    extract_caratula_difference,
    generate_all_figures,
    save_budget_execution,
    save_consolidated_balance,
    save_kpis,
)
from .emailer import send_reports


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def run_pipeline(config: AppConfig, send_email: bool, skip_visuals: bool) -> None:
    logger = logging.getLogger("cfobot")

    report_path = find_latest_report(config, logger)
    data = load_financial_data(report_path, config, logger)

    consolidated = consolidate_balance(data, config)
    budget = compute_budget_execution(data, config)
    kpis = compute_kpis(data, budget)

    outputs = [
        save_consolidated_balance(consolidated, data),
        save_budget_execution(budget, data),
        save_kpis(kpis, data),
    ]

    if not skip_visuals and config.generate_visuals:
        figures_paths = generate_all_figures(budget, kpis, data)
        outputs.extend(figures_paths)

    diferencia = extract_caratula_difference(data)
    board_report = build_board_report(budget, kpis, data, diferencia)
    outputs.append(board_report)

    logger.info("Generated outputs: %s", [str(path) for path in outputs])

    if send_email:
        if not config.email:
            logger.warning("Email configuration missing; skipping email sending")
            return

        subject = f"Reporte CFO Automatizado - {data.current_month} 2025"
        
        # Enhanced HTML email body
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
                <h2>{data.current_month} 2025</h2>
            </div>
            
            <div class="content">
                <div class="summary">
                    <h3>📈 Resumen Ejecutivo</h3>
                    <p>Se ha generado automáticamente el reporte financiero para el mes de <strong>{data.current_month} 2025</strong>.</p>
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
                    <h3>📁 Archivos Generados ({len(outputs)} archivos)</h3>
                    <ul>
        """
        
        # Add file list
        for output in outputs:
            file_type = "📊" if output.suffix == ".png" else "📄" if output.suffix == ".docx" else "📋"
            html_body += f"<li>{file_type} {output.name}</li>"
        
        html_body += f"""
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Este reporte fue generado automáticamente por el Sistema CFO Bot v1.0</p>
                    <p>Fecha de generación: {data.current_month} 2025</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_reports(config.email, subject, html_body, outputs)
        logger.info("Email sent to %s", config.email.recipient_emails)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="CFO Bot CLI")
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Enviar los reportes generados por correo",
    )
    parser.add_argument(
        "--skip-visuals",
        action="store_true",
        help="No generar gráficos",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Habilitar logging detallado",
    )

    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    config = load_config()
    run_pipeline(config=config, send_email=args.send_email, skip_visuals=args.skip_visuals)


if __name__ == "__main__":
    main()
