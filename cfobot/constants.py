"""Constants and configuration values for CFO Bot."""

# Account code patterns for expense categorization
ADMIN_EXPENSES_PATTERN = r"^51[0-9]{4,}"
OTHER_EXPENSES_PATTERN = r"^53[0-9]{4,}"
SALES_COSTS_PATTERN = r"^61[0-9]{4,}"
PRODUCTION_COSTS_PATTERN = r"^(72|73)[0-9]{4,}"

# Financial thresholds and limits
MIN_CURRENT_RATIO = 1.5
MIN_NET_MARGIN = 5.0
BUDGET_WARNING_THRESHOLD = 80.0
BUDGET_CRITICAL_THRESHOLD = 100.0

# Default budget values (in COP)
DEFAULT_MONTHLY_INCOME = 100_000_000
DEFAULT_MONTHLY_EXPENSES = 125_000_000

# Email configuration defaults
DEFAULT_SMTP_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587
EMAIL_TIMEOUT = 30

# File patterns and paths
DEFAULT_DOWNLOADS_DIR = "~/Downloads"
REPORT_PATTERN = "INFORME DE * APRU- 2025 .xls"

# Excel sheet names
BALANCE_SHEET_PREFIX = "BALANCE"
ERI_SHEET_NAME = "INFORME-ERI"
INCOME_STATEMENT_SHEET = "ESTADO RESULTADO"
CARATULA_SHEET_NAME = "CARATULA"

# Chart configuration
CHART_DPI = 300
CHART_FIGSIZE = (14, 8)
PIE_CHART_FIGSIZE = (14, 10)

# Account name patterns for specific calculations
DEPRECIATION_PATTERNS = ["DEPRECIACION", "AMORTIZACION"]
INTEREST_PATTERNS = ["INTERES"]
SALARY_PATTERNS = ["SUELDO", "SALARIO"]
SEVERANCE_PATTERNS = ["CESANTIA"]

# Month order for processing
DEFAULT_MONTH_ORDER = [
    "ENERO",
    "FEBRERO", 
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]

# Month aliases for flexible matching
MONTH_ALIASES = {
    "ENERO": {"ENERO", "ENE"},
    "FEBRERO": {"FEBRERO", "FEB"},
    "MARZO": {"MARZO", "MAR"},
    "ABRIL": {"ABRIL", "ABR"},
    "MAYO": {"MAYO", "MAY"},
    "JUNIO": {"JUNIO", "JUN"},
    "JULIO": {"JULIO", "JUL"},
    "AGOSTO": {"AGOSTO", "AGO"},
    "SEPTIEMBRE": {"SEPTIEMBRE", "SEP"},
    "OCTUBRE": {"OCTUBRE", "OCT"},
    "NOVIEMBRE": {"NOVIEMBRE", "NOV"},
    "DICIEMBRE": {"DICIEMBRE", "DIC"},
}

# Balance sheet account codes
ASSET_CLASS_CODE = "1"
LIABILITY_CLASS_CODE = "2"
EQUITY_CLASS_CODE = "3"

# Current asset group codes
CURRENT_ASSET_GROUPS = ["11", "12", "13", "14"]
INVENTORY_GROUP_CODE = "14"

# Income statement descriptions
INCOME_DESCRIPTION = "INGRESOS ORDINARIOS"
COST_DESCRIPTION = "COSTO DE VENTA"
PROFIT_DESCRIPTION = "RESULTADO DEL EJERCICIO"

# Output file prefixes
CONSOLIDATED_BALANCE_PREFIX = "consolidated_balance"
BUDGET_EXECUTION_PREFIX = "presupuesto_ejecutado"
KPIS_PREFIX = "kpis_financieros"
MONTHLY_SPENDING_PREFIX = "monthly_spending"
KPI_DASHBOARD_PREFIX = "kpi_dashboard"
DISTRIBUTION_PIE_PREFIX = "distribucion_gastos_pie"
CATEGORIES_PIE_PREFIX = "categorias_gastos_pie"
BOARD_REPORT_PREFIX = "informe_junta"

# File extensions
EXCEL_EXTENSION = ".xlsx"
PNG_EXTENSION = ".png"
DOCX_EXTENSION = ".docx"
