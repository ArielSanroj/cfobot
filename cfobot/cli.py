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
from .templates import build_email_html


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
        
        # Use template for HTML email body
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

    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    config = load_config()
    run_pipeline(config=config, send_email=args.send_email, skip_visuals=args.skip_visuals)


if __name__ == "__main__":
    main()
