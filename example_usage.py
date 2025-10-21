#!/usr/bin/env python3
"""
Example usage of CFO Bot with enhanced features
This script shows how to use the enhanced CFO Bot functionality
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from cfobot.cli import main

def run_example():
    """Run CFO Bot with example parameters"""
    
    print("🚀 CFO Bot - Sistema de Análisis Financiero Automatizado")
    print("=" * 60)
    print()
    print("Este ejemplo demuestra las funcionalidades mejoradas del CFO Bot:")
    print()
    print("📊 MÉTRICAS AGREGADAS:")
    print("   • EBITDA calculado automáticamente (utilidad + depreciación + intereses)")
    print("   • Filtrado por niveles superiores (Clase para Activo, Pasivo, Patrimonio)")
    print("   • Análisis de balance consolidado por mes")
    print()
    print("💰 ANÁLISIS PRESUPUESTARIO:")
    print("   • Comparación con presupuestos predefinidos ($100M ingresos, $125M gastos)")
    print("   • Cálculo de % ejecutado para ingresos y gastos")
    print("   • Distribución de gastos por categoría (Sueldos, Cesantías, etc.)")
    print()
    print("📈 INDICADORES FINANCIEROS (KPIs):")
    print("   • Current Ratio, Quick Ratio, Margen Bruto, Margen Neto")
    print("   • ROE, Deuda/Patrimonio, Rotación Inventarios, EBITDA")
    print()
    print("📊 VISUALIZACIONES:")
    print("   • Gráfico de barras: Gastos mensuales")
    print("   • Gráfico circular: Distribución de gastos por categoría")
    print("   • Gráfico de barras: KPIs financieros")
    print("   • Gráfico circular: Categorías de gastos")
    print()
    print("📋 REPORTE PARA JUNTA DIRECTIVA:")
    print("   • Resumen financiero ejecutivo")
    print("   • Análisis de ejecución presupuestaria")
    print("   • Tabla de indicadores financieros")
    print("   • Desglose de gastos por categoría")
    print("   • Conciliación bancaria")
    print("   • Recomendaciones estratégicas automáticas")
    print()
    print("📧 ENVÍO AUTOMÁTICO POR EMAIL:")
    print("   • Formato HTML profesional")
    print("   • Adjuntos automáticos")
    print("   • Configuración flexible de destinatarios")
    print()
    print("Para usar el sistema:")
    print("1. Coloca tu archivo Excel en la carpeta Downloads")
    print("2. Ejecuta: python cfobot.py")
    print("3. Para enviar por email: python cfobot.py --send-email")
    print("4. Para ver detalles: python cfobot.py --verbose")
    print()
    print("Archivos de salida se guardan en ~/Downloads/")
    print()

if __name__ == "__main__":
    run_example()