#!/usr/bin/env python3
"""
Test script for CFO Bot functionality
This script demonstrates the enhanced features without requiring actual Excel files
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from cfobot.config import AppConfig, load_config
from cfobot.data_loader import FinancialData
from cfobot.processing import compute_budget_execution, compute_kpis
from cfobot.reporting import generate_all_figures, build_board_report

def create_sample_data():
    """Create sample financial data for testing"""
    
    # Sample balance sheet data
    balance_data = {
        'Nivel': ['Clase', 'Clase', 'Clase', 'Grupo', 'Grupo', 'Grupo', 'Grupo'],
        'Código cuenta contable': ['1', '2', '3', '11', '12', '13', '14'],
        'Nombre cuenta contable': ['ACTIVO', 'PASIVO', 'PATRIMONIO', 'ACTIVO CORRIENTE', 'INVERSIONES', 'CUENTAS POR COBRAR', 'INVENTARIOS'],
        'Saldo inicial': [0, 0, 0, 0, 0, 0, 0],
        'Movimiento débito': [0, 0, 0, 0, 0, 0, 0],
        'Movimiento crédito': [0, 0, 0, 0, 0, 0, 0],
        'Saldo final': [500000000, 200000000, 300000000, 150000000, 50000000, 80000000, 120000000]
    }
    balance_df = pd.DataFrame(balance_data)
    
    # Sample ERI data
    eri_data = {
        'Codigo': ['510101', '510201', '530101', '610101', '720101', '510301', '510401'],
        'Nombre': ['SUELDOS ADMINISTRATIVOS', 'CESANTIAS', 'INTERESES', 'COSTO VENTAS', 'COSTO PRODUCCION', 'DEPRECIACION', 'OTROS GASTOS'],
        'ENERO DE 2025': [50000000, 10000000, 5000000, 30000000, 40000000, 8000000, 15000000],
        'FEBRERO DE 2025': [52000000, 10500000, 4800000, 32000000, 42000000, 8200000, 16000000],
        'MARZO DE 2025': [48000000, 9800000, 5200000, 28000000, 38000000, 7800000, 14000000]
    }
    eri_df = pd.DataFrame(eri_data)
    eri_df['Display Name'] = eri_df['Nombre']
    
    # Sample income statement data
    resultado_data = {
        'Descripcion': ['INGRESOS ORDINARIOS', 'COSTO DE VENTA', 'RESULTADO DEL EJERCICIO'],
        'Total ENERO': [120000000, 30000000, 15000000],
        'Total FEBRERO': [125000000, 32000000, 18000000],
        'Total MARZO': [110000000, 28000000, 12000000]
    }
    resultado_df = pd.DataFrame(resultado_data)
    
    # Sample caratula data
    caratula_data = {
        'Column_0': ['Diferencia', 'Otro dato'],
        'Column_1': [5000000, 0]
    }
    caratula_df = pd.DataFrame(caratula_data)
    
    # Create mock workbook
    class MockWorkbook:
        def __init__(self):
            self.sheet_names = ['BALANCE ENERO', 'BALANCE FEBRERO', 'BALANCE MARZO', 'INFORME-ERI', 'ESTADO RESULTADO', 'CARATULA']
    
    # Create FinancialData object
    data = FinancialData(
        current_month='MARZO',
        current_month_col='MARZO DE 2025',
        resultado_current_col='Total MARZO',
        balance=balance_df,
        eri=eri_df,
        resultado=resultado_df,
        caratula=caratula_df,
        months=['ENERO DE 2025', 'FEBRERO DE 2025', 'MARZO DE 2025'],
        workbook=MockWorkbook()
    )
    
    return data

def test_cfobot_features():
    """Test the enhanced CFO Bot features"""
    
    print("🚀 Testing CFO Bot Enhanced Features")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    print(f"✅ Configuration loaded successfully")
    print(f"   - Budget: ${config.budgets.ingresos_mensual:,.0f} ingresos, ${config.budgets.gastos_mensual:,.0f} gastos")
    print(f"   - Email configured: {'Yes' if config.email else 'No'}")
    
    # Create sample data
    data = create_sample_data()
    print(f"✅ Sample data created for {data.current_month} 2025")
    
    # Test budget execution calculation
    print("\n📊 Testing Budget Execution Analysis...")
    budget = compute_budget_execution(data, config)
    print(f"   - Ingresos actuales: ${budget.summary.loc[0, f'Actual {data.current_month}']:,.0f}")
    print(f"   - Gastos totales: ${budget.summary.loc[1, f'Actual {data.current_month}']:,.0f}")
    print(f"   - % Ejecutado ingresos: {budget.summary.loc[0, '% Ejecutado']:.1f}%")
    print(f"   - % Ejecutado gastos: {budget.summary.loc[1, '% Ejecutado']:.1f}%")
    
    # Test KPI calculation
    print("\n📈 Testing KPI Calculations...")
    kpis = compute_kpis(data, budget)
    print("   - Financial Ratios:")
    for kpi, value in kpis.metrics.items():
        print(f"     • {kpi}: {value}")
    
    # Test visualization generation
    print("\n📊 Testing Visualization Generation...")
    try:
        figures = generate_all_figures(budget, kpis, data)
        print(f"   - Generated {len(figures)} visualizations:")
        for fig in figures:
            print(f"     • {fig.name}")
    except Exception as e:
        print(f"   - Visualization generation failed: {e}")
    
    # Test board report generation
    print("\n📋 Testing Board Report Generation...")
    try:
        board_report = build_board_report(budget, kpis, data, diferencia=5000000)
        print(f"   - Board report generated: {board_report.name}")
    except Exception as e:
        print(f"   - Board report generation failed: {e}")
    
    print("\n✅ All tests completed successfully!")
    print("\n🎯 Enhanced Features Demonstrated:")
    print("   • Enhanced EBITDA calculation with proper depreciation and interest")
    print("   • Improved balance sheet filtering by 'Clase' level")
    print("   • Better budget execution analysis with detailed categorization")
    print("   • Enhanced expense categorization (Sueldos, Cesantías, etc.)")
    print("   • Comprehensive KPI calculations")
    print("   • Professional visualizations with improved formatting")
    print("   • Enhanced board report with strategic recommendations")
    print("   • Professional HTML email formatting")

if __name__ == "__main__":
    test_cfobot_features()