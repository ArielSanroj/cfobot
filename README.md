# CFO Bot - Sistema de Análisis Financiero Automatizado

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](https://pytest.org)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)](https://codecov.io)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](https://github.com/features/actions)

## 📊 Descripción

CFO Bot es un sistema automatizado de análisis financiero que procesa reportes mensuales y genera análisis completos, visualizaciones y reportes ejecutivos para la Junta Directiva. El sistema calcula métricas agregadas, analiza la ejecución presupuestaria y genera recomendaciones estratégicas basadas en datos financieros reales.

### 🎯 Características Principales

- **Análisis Financiero Automatizado**: Procesamiento inteligente de datos contables
- **Visualizaciones Profesionales**: Gráficos y dashboards ejecutivos
- **Reportes Ejecutivos**: Documentos Word para Junta Directiva
- **Envío Automático**: Notificaciones por email con adjuntos
- **Validación de Datos**: Verificación de integridad y detección de outliers
- **Configuración Flexible**: Adaptable a diferentes estructuras contables

## 🚀 Instalación Rápida

### Opción 1: Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/your-org/cfobot.git
cd cfobot

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python cfobot.py
```

### Opción 2: Docker

```bash
# Construir imagen
docker build -t cfobot .

# Ejecutar
docker run -v $(pwd)/downloads:/home/cfobot/Downloads cfobot
```

### Opción 3: Docker Compose

```bash
# Desarrollo
docker-compose up cfobot-dev

# Producción
docker-compose up cfobot
```

## 📋 Requisitos del Sistema

- **Python**: 3.9+ (3.10+ recomendado)
- **Memoria**: 4GB RAM mínimo
- **Espacio**: 1GB de espacio libre
- **Sistema Operativo**: Windows, macOS, Linux

## 🔧 Configuración

### Variables de Entorno

```bash
# Configuración de Email (Opcional)
export CFOBOT_EMAIL_SENDER="tu-email@gmail.com"
export CFOBOT_EMAIL_PASSWORD="tu-password"
export CFOBOT_EMAIL_RECIPIENT="destinatario1@empresa.com,destinatario2@empresa.com"
export CFOBOT_EMAIL_SMTP_SERVER="smtp.gmail.com"
export CFOBOT_EMAIL_SMTP_PORT="587"
```

### Archivo de Configuración

Crear `config.yaml`:

```yaml
budgets:
  ingresos_mensual: 100_000_000
  gastos_mensual: 125_000_000

thresholds:
  current_ratio_min: 1.5
  net_margin_min: 5.0

output:
  directory: ~/Downloads
  formats: [xlsx, png, docx]
```

## 📊 Uso

### Uso Básico

```bash
# Procesar archivo Excel automáticamente
python cfobot.py

# Con opciones avanzadas
python cfobot.py --send-email --verbose

# Sin generar gráficos
python cfobot.py --skip-visuals
```

### Parámetros de Línea de Comandos

| Parámetro | Descripción |
|-----------|-------------|
| `--send-email` | Enviar reportes por correo electrónico |
| `--skip-visuals` | No generar gráficos y visualizaciones |
| `--verbose` | Habilitar logging detallado |
| `--dry-run` | Validar sin generar archivos de salida |

## 📁 Estructura del Proyecto

```
cfobot/
├── cfobot/                 # Código fuente principal
│   ├── __init__.py
│   ├── cli.py             # Interfaz de línea de comandos
│   ├── config.py          # Gestión de configuración
│   ├── constants.py       # Constantes de la aplicación
│   ├── data_loader.py     # Carga y normalización de datos
│   ├── emailer.py         # Funcionalidad de email
│   ├── processing.py      # Lógica de procesamiento financiero
│   ├── reporting.py       # Generación de reportes
│   ├── templates.py       # Plantillas de email
│   └── validators.py      # Validación de datos
├── tests/                 # Suite de pruebas
│   ├── unit/              # Pruebas unitarias
│   ├── integration/       # Pruebas de integración
│   └── fixtures/          # Datos de prueba
├── .github/               # Configuración de CI/CD
├── docs/                  # Documentación
├── requirements.txt       # Dependencias de producción
├── requirements-dev.txt   # Dependencias de desarrollo
├── pyproject.toml        # Configuración del proyecto
├── Dockerfile            # Imagen de Docker
├── docker-compose.yml    # Orquestación de contenedores
└── README.md             # Este archivo
```

## 📈 Funcionalidades Detalladas

### 🔍 Análisis Financiero

#### Métricas Calculadas
- **EBITDA**: Utilidad + Depreciación + Intereses
- **Ratios de Liquidez**: Current Ratio, Quick Ratio
- **Ratios de Rentabilidad**: Margen Bruto, Margen Neto, ROE
- **Ratios de Endeudamiento**: Deuda/Patrimonio
- **Ratios de Actividad**: Rotación de Inventarios

#### Categorización de Gastos
- **Gastos Administrativos**: Códigos 51xxxx
- **Gastos Otros**: Códigos 53xxxx
- **Costos de Venta**: Códigos 61xxxx
- **Costos de Producción**: Códigos 72xxxx, 73xxxx
- **Sueldos y Cesantías**: Detección automática por nombre

### 📊 Visualizaciones

#### Gráficos Generados
1. **Gastos Mensuales**: Barras comparativas por mes
2. **KPIs Financieros**: Dashboard de indicadores clave
3. **Distribución de Gastos**: Gráfico circular por categoría
4. **Categorías de Gastos**: Análisis detallado por tipo

#### Características de Gráficos
- **Alta Resolución**: 300 DPI para presentaciones
- **Formato Profesional**: Colores corporativos
- **Etiquetas Inteligentes**: Valores y porcentajes
- **Leyendas Detalladas**: Información contextual

### 📋 Reportes Ejecutivos

#### Informe para Junta Directiva
- **Resumen Ejecutivo**: Métricas clave y tendencias
- **Análisis Presupuestario**: Ejecución vs. presupuesto
- **Indicadores Financieros**: Tabla completa de KPIs
- **Desglose de Gastos**: Categorización detallada
- **Conciliación Bancaria**: Diferencias identificadas
- **Recomendaciones Estratégicas**: Sugerencias automáticas

#### Recomendaciones Inteligentes
- **Liquidez**: Alertas si Current Ratio < 1.5
- **Rentabilidad**: Análisis de márgenes vs. estándares
- **Presupuesto**: Control de desviaciones significativas
- **Tendencias**: Monitoreo de variaciones mensuales

## 🔧 Desarrollo

### Configuración del Entorno

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install

# Ejecutar pruebas
pytest --cov=cfobot --cov-report=html

# Formatear código
black cfobot tests
isort cfobot tests

# Verificar tipos
mypy cfobot

# Linting
flake8 cfobot tests
```

### Estructura de Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Pruebas unitarias
pytest tests/unit/

# Pruebas de integración
pytest tests/integration/

# Con cobertura
pytest --cov=cfobot --cov-report=term-missing
```

### Docker para Desarrollo

```bash
# Construir imagen de desarrollo
docker-compose build cfobot-dev

# Ejecutar pruebas
docker-compose --profile test run cfobot-test

# Linting
docker-compose --profile lint run cfobot-lint

# Type checking
docker-compose --profile typecheck run cfobot-typecheck
```

## 📊 Formato de Archivos de Entrada

### Estructura Excel Requerida

El sistema espera archivos Excel con las siguientes hojas:

#### 1. Balance General (`BALANCE [MES]`)
- **Columnas**: Nivel, Código cuenta contable, Nombre cuenta contable, Saldo inicial, Movimiento débito, Movimiento crédito, Saldo final
- **Niveles**: Clase (1, 2, 3), Grupo (11, 12, 13, 14, 21, etc.)

#### 2. Informe de Ingresos y Gastos (`INFORME-ERI`)
- **Columnas**: Código, Nombre, [Meses del año]
- **Códigos**: 51xxxx (Administrativos), 53xxxx (Otros), 61xxxx (Ventas), 72xxxx/73xxxx (Producción)

#### 3. Estado de Resultados (`ESTADO RESULTADO`)
- **Estructura**: Multi-nivel con descripciones y totales por mes
- **Elementos**: Ingresos Ordinarios, Costo de Venta, Resultado del Ejercicio

#### 4. Carátula (`CARATULA`)
- **Propósito**: Conciliación bancaria
- **Datos**: Diferencias identificadas

### Ejemplo de Archivo

```
INFORME DE MARZO APRU- 2025 .xlsx
├── BALANCE MARZO
├── INFORME-ERI
├── ESTADO RESULTADO
└── CARATULA
```

## 📁 Archivos de Salida

### Excel Reports
- `consolidated_balance_[mes]_2025.xlsx`: Balance consolidado
- `presupuesto_ejecutado_[mes]_2025.xlsx`: Análisis presupuestario
- `kpis_financieros_[mes]_2025.xlsx`: Indicadores financieros

### Visualizaciones (PNG)
- `monthly_spending_[mes]_2025.png`: Gastos mensuales
- `kpi_dashboard_[mes]_2025.png`: Dashboard de KPIs
- `distribucion_gastos_pie_[mes]_2025.png`: Distribución de gastos
- `categorias_gastos_pie_[mes]_2025.png`: Categorías de gastos

### Reporte Ejecutivo
- `informe_junta_[mes]_2025.docx`: Informe para Junta Directiva

## 🚨 Troubleshooting

### Errores Comunes

#### "No file matching pattern found"
```bash
# Verificar ubicación del archivo
ls ~/Downloads/INFORME*

# Verificar nombre del archivo
# Debe seguir el patrón: "INFORME DE [MES] APRU- 2025 .xls"
```

#### "Email configuration missing"
```bash
# Configurar variables de entorno
export CFOBOT_EMAIL_SENDER="tu-email@gmail.com"
export CFOBOT_EMAIL_PASSWORD="tu-password"

# O ejecutar sin email
python cfobot.py
```

#### "Sheet not found"
```bash
# Verificar que el archivo Excel contenga todas las hojas:
# - BALANCE [MES]
# - INFORME-ERI
# - ESTADO RESULTADO
# - CARATULA
```

### Logs y Debugging

```bash
# Ejecutar con logging detallado
python cfobot.py --verbose

# Verificar configuración
python -c "from cfobot.config import load_config; print(load_config())"
```

## 🤝 Contribución

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crear** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear** un Pull Request

### Guías de Contribución

- **Código**: Sigue las convenciones de Python (PEP 8)
- **Tests**: Mantén cobertura >80%
- **Documentación**: Actualiza README y docstrings
- **Commits**: Usa conventional commits

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### Obtener Ayuda

- **Issues**: [GitHub Issues](https://github.com/your-org/cfobot/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/your-org/cfobot/discussions)
- **Documentación**: [Wiki del Proyecto](https://github.com/your-org/cfobot/wiki)

### Reportar Bugs

Al reportar bugs, incluye:
1. **Versión** de Python y CFO Bot
2. **Sistema operativo**
3. **Pasos** para reproducir el error
4. **Logs** de error completos
5. **Archivo** de ejemplo (si aplica)

## 🗺️ Roadmap

### Versión 1.1
- [ ] Soporte para múltiples formatos de entrada (CSV, JSON)
- [ ] Dashboard web interactivo
- [ ] Integración con APIs bancarias
- [ ] Análisis predictivo con ML

### Versión 1.2
- [ ] Soporte multi-idioma
- [ ] Plantillas personalizables
- [ ] API REST para integraciones
- [ ] Notificaciones push

### Versión 2.0
- [ ] Arquitectura de microservicios
- [ ] Base de datos integrada
- [ ] Autenticación y autorización
- [ ] Escalabilidad horizontal

## 📊 Métricas del Proyecto

- **Líneas de Código**: ~2,500
- **Cobertura de Tests**: >80%
- **Dependencias**: 6 principales
- **Tiempo de Ejecución**: <30 segundos
- **Tamaño de Salida**: ~5MB por reporte

## 🏆 Reconocimientos

- **Desarrollado por**: Equipo CFO Bot
- **Inspirado en**: Mejores prácticas de análisis financiero
- **Tecnologías**: Python, Pandas, Matplotlib, Docker
- **Agradecimientos**: Comunidad open source

---

**CFO Bot** - Transformando datos financieros en insights estratégicos 🚀