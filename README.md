# CFO Bot - Sistema de Análisis Financiero Automatizado

## Descripción

CFO Bot es un sistema automatizado que procesa reportes financieros mensuales y genera análisis completos, visualizaciones y reportes para la Junta Directiva. El sistema calcula métricas agregadas, analiza la ejecución presupuestaria y genera recomendaciones estratégicas.

## Características Principales

### 📊 Métricas Agregadas
- **EBITDA**: Cálculo automático (utilidad + depreciación + intereses)
- **Filtrado por niveles superiores**: Activo, Pasivo, Patrimonio a nivel 'Clase'
- **Análisis de balance consolidado** por mes

### 💰 Análisis Presupuestario
- **Comparación con presupuestos predefinidos** ($100M ingresos, $125M gastos)
- **Cálculo de % ejecutado** para ingresos y gastos
- **Distribución de gastos por categoría**:
  - Gastos Administrativos
  - Gastos Otros
  - Costos de Venta
  - Costos de Producción
  - Sueldos y Cesantías (categorización específica)

### 📈 Indicadores Financieros (KPIs)
- **Current Ratio**: Activos corrientes / Pasivos corrientes
- **Quick Ratio**: (Activos corrientes - Inventarios) / Pasivos corrientes
- **Margen Bruto**: ((Ingresos - Costos) / Ingresos) × 100
- **Margen Neto**: (Utilidad / Ingresos) × 100
- **ROE**: (Utilidad / Patrimonio) × 100
- **Deuda/Patrimonio**: Pasivos corrientes / Patrimonio
- **Rotación de Inventarios**: Costos / Inventarios
- **EBITDA**: Utilidad + Depreciación + Intereses

### 📊 Visualizaciones
- **Gráfico de barras**: Gastos mensuales (Enero a mes actual)
- **Gráfico circular**: Distribución de gastos por categoría con porcentajes
- **Gráfico de barras**: KPIs financieros del mes
- **Gráfico circular**: Categorías de gastos (Administrativos, Otros, etc.)

### 📋 Reporte para Junta Directiva
- **Resumen financiero ejecutivo** con métricas clave
- **Análisis de ejecución presupuestaria**
- **Tabla de indicadores financieros**
- **Desglose de gastos por categoría**
- **Conciliación bancaria** (desde CARATULA)
- **Recomendaciones estratégicas** basadas en análisis automático

### 📧 Envío Automático por Email
- **Formato HTML profesional** con resumen ejecutivo
- **Adjuntos automáticos** de todos los archivos generados
- **Configuración flexible** de destinatarios

## Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd CFO
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno** (opcional para email):
```bash
export CFOBOT_EMAIL_SENDER="tu-email@gmail.com"
export CFOBOT_EMAIL_PASSWORD="tu-password"
export CFOBOT_EMAIL_RECIPIENT="destinatario1@empresa.com,destinatario2@empresa.com"
export CFOBOT_EMAIL_SMTP_SERVER="smtp.gmail.com"
export CFOBOT_EMAIL_SMTP_PORT="587"
```

## Uso

### Uso Básico
```bash
python cfobot.py
```

### Opciones Avanzadas
```bash
# Generar reportes sin gráficos
python cfobot.py --skip-visuals

# Enviar reportes por email
python cfobot.py --send-email

# Habilitar logging detallado
python cfobot.py --verbose

# Combinar opciones
python cfobot.py --send-email --verbose
```

## Estructura de Archivos

```
CFO/
├── cfobot/
│   ├── __init__.py
│   ├── cli.py              # Interfaz de línea de comandos
│   ├── config.py           # Configuración de la aplicación
│   ├── data_loader.py      # Carga y normalización de datos
│   ├── processing.py       # Lógica de procesamiento financiero
│   ├── reporting.py        # Generación de reportes y visualizaciones
│   └── emailer.py          # Funcionalidad de envío de emails
├── tests/
│   ├── test_config.py
│   └── test_data_loader.py
├── cfobot.py              # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
└── README.md              # Este archivo
```

## Formato de Archivos de Entrada

El sistema espera archivos Excel con las siguientes hojas:
- **BALANCE [MES]**: Balance general del mes
- **INFORME-ERI**: Informe de ingresos y gastos por cuenta
- **ESTADO RESULTADO**: Estado de resultados
- **CARATULA**: Información de conciliación bancaria

## Archivos de Salida

### Excel
- `consolidated_balance_[mes]_2025.xlsx`: Balance consolidado
- `presupuesto_ejecutado_[mes]_2025.xlsx`: Análisis presupuestario
- `kpis_financieros_[mes]_2025.xlsx`: Indicadores financieros

### Visualizaciones (PNG)
- `monthly_spending_[mes]_2025.png`: Gastos mensuales
- `kpi_dashboard_[mes]_2025.png`: KPIs financieros
- `distribucion_gastos_pie_[mes]_2025.png`: Distribución de gastos
- `categorias_gastos_pie_[mes]_2025.png`: Categorías de gastos

### Reporte Word
- `informe_junta_[mes]_2025.docx`: Informe para Junta Directiva

## Configuración

### Presupuestos
Los presupuestos se configuran en `config.py`:
```python
@dataclass
class BudgetConfig:
    ingresos_mensual: float = 100_000_000  # $100M
    gastos_mensual: float = 125_000_000    # $125M
```

### Orden de Meses
```python
DEFAULT_MONTH_ORDER = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]
```

## Análisis Automático

### Recomendaciones Inteligentes
El sistema genera recomendaciones automáticas basadas en:
- **Liquidez**: Alerta si Current Ratio < 1.5
- **Rentabilidad**: Analiza margen neto vs estándares
- **Ejecución presupuestaria**: Controla desviaciones significativas
- **Tendencias**: Monitorea variaciones mes a mes

### Categorización Inteligente
- **Sueldos**: Detecta cuentas con "SUELDO" o "SALARIO"
- **Cesantías**: Identifica cuentas de "CESANTIA"
- **Gastos Administrativos**: Cuentas 51xxxx
- **Gastos Otros**: Cuentas 53xxxx
- **Costos de Venta**: Cuentas 61xxxx
- **Costos de Producción**: Cuentas 72xxxx y 73xxxx

## Troubleshooting

### Error: "No file matching pattern found"
- Verificar que el archivo esté en la carpeta Downloads
- Confirmar que el nombre siga el patrón: "INFORME DE [MES] APRU- 2025 .xls"

### Error: "Email configuration missing"
- Configurar las variables de entorno para email
- O ejecutar sin la opción `--send-email`

### Error: "Sheet not found"
- Verificar que el archivo Excel contenga todas las hojas requeridas
- Confirmar que los nombres de las hojas coincidan con el formato esperado

## Contribuciones

Para contribuir al proyecto:
1. Fork el repositorio
2. Crear una rama para tu feature
3. Hacer commit de los cambios
4. Push a la rama
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo
- Revisar la documentación en línea