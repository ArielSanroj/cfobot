"""Command-line interface for CFO bot."""

from __future__ import annotations

import argparse
import logging

from .config import AppConfig, load_config
from .data_loader import find_latest_report, load_financial_data
from .processing import compute_budget_execution, compute_kpis, consolidate_balance, compute_ai_enhanced_analysis
from .reporting import (
    build_board_report,
    build_ai_enhanced_board_report,
    extract_caratula_difference,
    generate_all_figures,
    save_budget_execution,
    save_consolidated_balance,
    save_kpis,
)
from .emailer import send_reports
from .templates import build_email_html, build_ai_enhanced_email_html


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def run_pipeline(config: AppConfig, send_email: bool, skip_visuals: bool, use_ai: bool = True) -> None:
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
    
    # Generate AI-enhanced analysis if enabled
    ai_insights = None
    if use_ai and config.ollama.enabled:
        try:
            logger.info("Generating AI-enhanced analysis...")
            ai_insights = compute_ai_enhanced_analysis(data, budget, kpis, config)
            logger.info("AI analysis completed successfully")
        except Exception as e:
            logger.warning(f"AI analysis failed, falling back to standard analysis: {e}")
            ai_insights = None
    
    # Generate appropriate board report
    if ai_insights:
        board_report = build_ai_enhanced_board_report(budget, kpis, data, ai_insights, diferencia)
        logger.info("Generated AI-enhanced board report")
    else:
        board_report = build_board_report(budget, kpis, data, diferencia)
        logger.info("Generated standard board report")
    
    outputs.append(board_report)

    logger.info("Generated outputs: %s", [str(path) for path in outputs])

    if send_email:
        if not config.email:
            logger.warning("Email configuration missing; skipping email sending")
            return

        subject = f"Reporte CFO con IA - {data.current_month} 2025" if ai_insights else f"Reporte CFO Automatizado - {data.current_month} 2025"
        
        # Use appropriate template for HTML email body
        if ai_insights:
            html_body = build_ai_enhanced_email_html(
                current_month=data.current_month,
                outputs=outputs,
                recipient_count=len(config.email.recipient_emails),
                ai_insights=ai_insights
            )
        else:
            html_body = build_email_html(
                current_month=data.current_month,
                outputs=outputs,
                recipient_count=len(config.email.recipient_emails)
            )
        
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
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Deshabilitar análisis con IA (usar análisis estándar)",
    )
    parser.add_argument(
        "--ai-model",
        type=str,
        help="Modelo de IA a usar (ej: llama3.1:8b, mistral:7b)",
    )

    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    config = load_config()
    
    # Override AI settings if specified
    if args.ai_model:
        config.ollama.model = args.ai_model
    
    use_ai = not args.no_ai and config.ollama.enabled
    
    run_pipeline(config=config, send_email=args.send_email, skip_visuals=args.skip_visuals, use_ai=use_ai)


if __name__ == "__main__":
    main()
