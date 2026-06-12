import streamlit as st
import pandas as pd
import io 

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Calculadora Integral de Materiales - CAPECO",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Sistema Integral de Presupuestos de Construcción (Normativa CAPECO)")
st.markdown("""
Esta plataforma realiza el análisis global de materiales para una edificación, integrando **muros, acabados, estructuras de concreto y acero estructural**, aplicando las mermas y rendimientos estándar de la Cámara Peruana de la Construcción (CAPECO).
""")
st.write("---")

# 2. ENTRADAS DE DATOS EN LA BARRA LATERAL (INPUTS)
st.sidebar.header("📐 Parámetros Globales del Proyecto")
area_construccion = st.sidebar.number_input("Área Total de Construcción / Techo (m²):", min_value=1, value=60, step=5)
area_pared = st.sidebar.number_input("Área de Pared a Enchapar (m²):", min_value=0, value=20, step=5)

# MÓDULO DE LADRILLOS DE MURO (CON OPCIÓN PERSONALIZADA)
st.sidebar.write("---")
st.sidebar.subheader("🧱 Ladrillo para Muros")
tipo_ladrillo = st.sidebar.selectbox(
    "Formato de Ladrillo de Muro:",
    ["King Kong Estándar (24x13x9 cm)", "Ladrillo Pandereta (23x11x9 cm)", "Otro (Personalizado)"]
)

if tipo_ladrillo == "King Kong Estándar (24x13x9 cm)":
    L_lad, H_lad = 0.24, 0.09
elif tipo_ladrillo == "Ladrillo Pandereta (23x11x9 cm)":
    L_lad, H_lad = 0.23, 0.09
else:
    col_l1, col_l2 = st.sidebar.columns(2)
    l_cm = col_l1.number_input("Largo (cm):", min_value=1.0, value=24.0, step=0.5)
    h_cm = col_l2.number_input("Alto (cm):", min_value=1.0, value=9.0, step=0.5)
    L_lad, H_lad = l_cm / 100.0, h_cm / 100.0

# MÓDULO DE REVESTIMIENTOS Y CERÁMICOS (CON OPCIÓN PERSONALIZADA)
st.sidebar.write("---")
st.sidebar.subheader("📐 Revestimientos y Cerámicos")

tipo_cer_piso = st.sidebar.selectbox(
    "Formato Cerámica de Piso:",
    ["Cerámica de Piso (40x40 cm)", "Porcelanato de Piso (60x60 cm)", "Cerámica de Piso (30x30 cm)", "Otro (Personalizado)"]
)
if tipo_cer_piso == "Otro (Personalizado)":
    col_p1, col_p2 = st.sidebar.columns(2)
    piso_l = col_p1.number_input("Ancho Piso (cm):", min_value=1.0, value=45.0, step=1.0, key="custom_pl")
    piso_h = col_p2.number_input("Largo Piso (cm):", min_value=1.0, value=45.0, step=1.0, key="custom_ph")
    nombre_piso = f"Personalizado ({int(piso_l)}x{int(piso_h)} cm)"
else:
    nombre_piso = tipo_cer_piso

tipo_cer_pared = st.sidebar.selectbox(
    "Formato Cerámica de Pared:",
    ["Cerámica de Pared (20x30 cm)", "Cerámica de Pared (30x30 cm)", "Porcelanato de Pared (60x60 cm)", "Otro (Personalizado)"]
)
if tipo_cer_pared == "Otro (Personalizado)":
    col_w1, col_w2 = st.sidebar.columns(2)
    pared_l = col_w1.number_input("Ancho Pared (cm):", min_value=1.0, value=25.0, step=1.0, key="custom_wl")
    pared_h = col_w2.number_input("Largo Pared (cm):", min_value=1.0, value=40.0, step=1.0, key="custom_wh")
    nombre_pared = f"Personalizado ({int(pared_l)}x{int(pared_h)} cm)"
else:
    nombre_pared = tipo_cer_pared

# FACTORES LOGÍSTICOS NORMADOS CORREGIDOS
JUNTA_LADRILLO = 0.015       # 1.5 cm de junta
DESPERDECIO_LADRILLO = 0.05   # 5% merma muros
DESPERDECIO_TECHO = 0.05      # 5% merma ladrillo techo
FACTOR_CEMENTO_M2 = 2.5       # 2.5 bolsas por m²
FACTOR_ACERO_M2 = 10.0        # 10 kg de fierro por m²
PESO_VARILLA_PROMEDIO = 7.0   # Peso promedio de varilla de 9m

st.sidebar.write("---")

# CONFIGURACIÓN PRECIOS PROVEEDOR 1
st.sidebar.header("🏪 Precios - PROVEEDOR 1")
p1_lad_muro = st.sidebar.number_input("Ladrillo Muro P1 (S/. por und):", min_value=0.1, value=0.90, step=0.05, key="p1_lm")
p1_lad_techo = st.sidebar.number_input("Ladrillo Techo P1 (S/. por und):", min_value=0.1, value=2.80, step=0.10, key="p1_lt")
p1_cemento = st.sidebar.number_input("Cemento P1 (S/. por bolsa):", min_value=1.0, value=28.00, step=0.50, key="p1_cem")
p1_fierro = st.sidebar.number_input("Fierro Corrugado P1 (S/. por varilla):", min_value=1.0, value=31.00, step=1.00, key="p1_fiero")
p1_cer_piso = st.sidebar.number_input("Cerámica Piso P1 (S/. por m²):", min_value=1.0, value=35.00, step=1.00, key="p1_cp")
p1_cer_pared = st.sidebar.number_input("Cerámica Pared P1 (S/. por m²):", min_value=1.0, value=30.00, step=1.00, key="p1_cw")

st.sidebar.write("---")

# CONFIGURACIÓN PRECIOS PROVEEDOR 2
st.sidebar.header("🏪 Precios - PROVEEDOR 2")
p2_lad_muro = st.sidebar.number_input("Ladrillo Muro P2 (S/. por und):", min_value=0.1, value=0.85, step=0.05, key="p2_lm")
p2_lad_techo = st.sidebar.number_input("Ladrillo Techo P2 (S/. por und):", min_value=0.1, value=2.95, step=0.10, key="p2_lt")
p2_cemento = st.sidebar.number_input("Cemento P2 (S/. por bolsa):", min_value=1.0, value=29.50, step=0.50, key="p2_cem")
p2_fierro = st.sidebar.number_input("Fierro Corrugado P2 (S/. por varilla):", min_value=1.0, value=29.00, step=1.00, key="p2_fiero")
p2_cer_piso = st.sidebar.number_input("Cerámica Piso P2 (S/. por m²):", min_value=1.0, value=32.00, step=1.00, key="p2_cp")
p2_cer_pared = st.sidebar.number_input("Cerámica Pared P2 (S/. por m²):", min_value=1.0, value=34.00, step=1.00, key="p2_cw")


# 3. ALGORITMO CIENTÍFICO DE METRADOS
# A. Ladrillos de Muro
cant_ladrillos_m2_neto = 1 / ((L_lad + JUNTA_LADRILLO) * (H_lad + JUNTA_LADRILLO))
total_ladrillos_muro = round((cant_ladrillos_m2_neto * area_construccion) * (1 + DESPERDECIO_LADRILLO))

# B. Ladrillos de Techo (Aligerado) -> Fórmula CAPECO: 8.33 und/m²
total_ladrillos_techo = round((area_construccion * 8.33) * (1 + DESPERDECIO_TECHO))

# C. Cemento
total_bolsas_cemento = round(area_construccion * FACTOR_CEMENTO_M2, 1)

# D. Acero Estructural (Fierro en Varillas)
peso_acero_total_kg = area_construccion * FACTOR_ACERO_M2
total_varillas_fierro = round(peso_acero_total_kg / PESO_VARILLA_PROMEDIO)

# E. Acabados (Cerámicos con mermas de 5% y 10%)
total_m2_piso = round(area_construccion * 1.05, 1)
total_m2_pared = round(area_pared * 1.10, 1)


# 4. COSTOS TOTALES EN PARALELO
# Proveedor 1
c_lm_p1 = total_ladrillos_muro * p1_lad_muro
c_lt_p1 = total_ladrillos_techo * p1_lad_techo
c_cem_p1 = total_bolsas_cemento * p1_cemento
c_f_p1 = total_varillas_fierro * p1_fierro
c_cp_p1 = total_m2_piso * p1_cer_piso
c_cw_p1 = total_m2_pared * p1_cer_pared
total_p1 = c_lm_p1 + c_lt_p1 + c_cem_p1 + c_f_p1 + c_cp_p1 + c_cw_p1

# Proveedor 2
c_lm_p2 = total_ladrillos_muro * p2_lad_muro
c_lt_p2 = total_ladrillos_techo * p2_lad_techo
c_cem_p2 = total_bolsas_cemento * p2_cemento
c_f_p2 = total_varillas_fierro * p2_fierro
c_cp_p2 = total_m2_piso * p2_cer_piso
c_cw_p2 = total_m2_pared * p2_cer_pared
total_p2 = c_lm_p2 + c_lt_p2 + c_cem_p2 + c_f_p2 + c_cp_p2 + c_cw_p2


# 5. VISUALIZACIÓN DE SUSTENTO TÉCNICO
st.subheader("📚 Sustento y Ratios de Ingeniería Civil")
with st.expander("Ver criterios analíticos y fórmulas de metrado estructural (Normativa CAPECO)"):
    st.markdown("### 1. Cantidad de Ladrillos de Muro por m²")
    st.latex(r"C_{muro} = \frac{1}{(L_{lad} + J) \times (H_{lad} + J)} \times (1 + \%M_{muro})")
    st.markdown(f"- **Formato seleccionado:** {tipo_ladrillo}")
    st.markdown(f"- **Rendimiento calculado:** {cant_ladrillos_m2_neto:.2f} und/m² (Con junta de {JUNTA_LADRILLO*100} cm y {DESPERDECIO_LADRILLO*100}% de merma).")
    
    st.markdown("### 2. Cantidad de Ladrillos de Techo Aligerado")
    st.latex(r"C_{techo} = \left( \text{Área de Losa} \times 8.33 \text{ und/m}^2 \right) \times (1 + \%M_{techo})")
    
    st.markdown("### 3. Acero Estructural (Fierro Corrugado)")
    st.latex(r"V_{fierro} = \frac{\text{Área Construcción} \times \text{Cuantía Estructural (10 kg/m}^2\text{)}}{\text{Peso Comercial de Varilla (7 kg/9m)}}")
    
    st.markdown("### 4. Revestimientos Cerámicos (Pisos y Paredes)")
    st.latex(r"\text{Metrado Piso} = A_{construcción} \times 1.05 \quad | \quad \text{Metrado Pared} = A_{enchape} \times 1.10")
    st.markdown(f"- **Piso:** {nombre_piso} (Añade 5% de merma por cortes).")
    st.markdown(f"- **Pared:** {nombre_pared} (Añade 10% de merma debido a esquinas y derrames).")

st.write("---")

# 6. RESUMEN DE METRADOS
st.subheader("📊 Cantidades Totales Requeridas (Lista de Materiales de Obra)")
col1, col2, col3 = st.columns(3)
col1.metric("🧱 Ladrillos de Muro", f"{total_ladrillos_muro} und")
col1.metric("🏠 Ladrillos de Techo", f"{total_ladrillos_techo} und")

col2.metric("🪨 Cemento Sol / APU", f"{total_bolsas_cemento} bolsas")
col2.metric("⛓️ Fierro de Construcción", f"{total_varillas_fierro} varillas (9m)")

col3.metric("📐 Cerámica de Piso", f"{total_m2_piso} m²")
col3.metric("🧼 Cerámica de Pared", f"{total_m2_pared} m²")

st.write("---")

# =============================================================================
# 7. ANÁLISIS COMPARATIVO DE PRESUPUESTOS (SELECCIÓN AUTOMÁTICA INTELIGENTE)
# =============================================================================
st.subheader("⚖️ Análisis Comparativo de Presupuestos")

# Evaluamos de forma automática cuál es el menor costo del proyecto
es_p1_menor = total_p1 < total_p2
es_p2_menor = total_p2 < total_p1
diferencia_absoluta = abs(total_p1 - total_p2)

# Fila superior de métricas dinámicas
cm1, cm2 = st.columns(2)

with cm1:
    st.markdown("### 🏪 Proveedor 1")
    if es_p1_menor:
        st.metric(
            label="🏆 ¡OPCIÓN MÁS ECONÓMICA!", 
            value=f"S/. {total_p1:,.2f}",
            delta=f"- S/. {diferencia_absoluta:,.2f} (Ahorro óptimo)",
            delta_color="normal" # Se pintará verde automáticamente por el beneficio
        )
    else:
        st.metric(
            label="COSTO TOTAL ESTIMADO P1", 
            value=f"S/. {total_p1:,.2f}",
            delta=f"+ S/. {diferencia_absoluta:,.2f} (Más caro)",
            delta_color="normal" # Se pintará rojo automáticamente al ser un incremento
        )

with cm2:
    st.markdown("### 🏪 Proveedor 2")
    if es_p2_menor:
        st.metric(
            label="🏆 ¡OPCIÓN MÁS ECONÓMICA!", 
            value=f"S/. {total_p2:,.2f}",
            delta=f"- S/. {diferencia_absoluta:,.2f} (Ahorro óptimo)",
            delta_color="normal" # Verde automático
        )
    else:
        st.metric(
            label="COSTO TOTAL ESTIMADO P2", 
            value=f"S/. {total_p2:,.2f}",
            delta=f"+ S/. {diferencia_absoluta:,.2f} (Más caro)",
            delta_color="normal" # Rojo automático
        )

st.write("##") # Espacio estético

# Tabla única consolidada para comparar precios unitarios y subtotales lado a lado
st.markdown("#### 📊 Desglose de Costos Estructurado")

df_comparativo = pd.DataFrame({
    "Material de Construcción": [
        "🧱 Ladrillo Muro", 
        "🏠 Ladrillo Techo", 
        "🪨 Cemento Sol / APU", 
        "⛓️ Fierro (Varillas)", 
        f"📐 Piso ({nombre_piso})", 
        f"🧼 Pared ({nombre_pared})"
    ],
    "Cantidad Requerida": [
        f"{total_ladrillos_muro} und", 
        f"{total_ladrillos_techo} und", 
        f"{total_bolsas_cemento} bolsas", 
        f"{total_varillas_fierro} var", 
        f"{total_m2_piso} m²", 
        f"{total_m2_pared} m²"
    ],
    "P1: P. Unitario": [f"S/. {p1_lad_muro:.2f}", f"S/. {p1_lad_techo:.2f}", f"S/. {p1_cemento:.2f}", f"S/. {p1_fierro:.2f}", f"S/. {p1_cer_piso:.2f}", f"S/. {p1_cer_pared:.2f}"],
    "P1: Subtotal": [f"S/. {c_lm_p1:,.2f}", f"S/. {c_lt_p1:,.2f}", f"S/. {c_cem_p1:,.2f}", f"S/. {c_f_p1:,.2f}", f"S/. {c_cp_p1:,.2f}", f"S/. {c_cw_p1:,.2f}"],
    "P2: P. Unitario": [f"S/. {p2_lad_muro:.2f}", f"S/. {p2_lad_techo:.2f}", f"S/. {p2_cemento:.2f}", f"S/. {p2_fierro:.2f}", f"S/. {p2_cer_piso:.2f}", f"S/. {p2_cer_pared:.2f}"],
    "P2: Subtotal": [f"S/. {c_lm_p2:,.2f}", f"S/. {c_lt_p2:,.2f}", f"S/. {c_cem_p2:,.2f}", f"S/. {c_f_p2:,.2f}", f"S/. {c_cp_p2:,.2f}", f"S/. {c_cw_p2:,.2f}"]
})

# Mostrar la tabla ocupando todo el ancho disponible para una lectura cómoda
st.dataframe(df_comparativo, use_container_width=True, hide_index=True)

# 8. RECOMENDACIÓN DE COMPRA
st.subheader("💡 Recomendación de Optimización Financiera")
if total_p1 < total_p2:
    ahorro = total_p2 - total_p1
    st.success(f"✔️ **Estrategia de Suministro:** Se recomienda realizar la compra con el **Proveedor 1**. Ahorro neto de **S/. {ahorro:,.2f}**.")
elif total_p2 < total_p1:
    ahorro = total_p1 - total_p2
    st.success(f"✔️ **Estrategia de Suministro:** Se recomienda realizar la compra con el **Proveedor 2**. Ahorro neto de **S/. {ahorro:,.2f}**.")
else:
    st.info("📊 Ambos proveedores presentan un empate técnico.")
st.write("---")

st.write("---")

# GRÁFICO COMPARATIVO
st.subheader("📊 Comparativa Visual por Material")

import plotly.express as px

df_grafico = pd.DataFrame({
    "Material": ["Ladrillo Muro", "Ladrillo Techo", "Cemento", "Fierro", "Piso", "Pared"],
    "Proveedor 1": [c_lm_p1, c_lt_p1, c_cem_p1, c_f_p1, c_cp_p1, c_cw_p1],
    "Proveedor 2": [c_lm_p2, c_lt_p2, c_cem_p2, c_f_p2, c_cp_p2, c_cw_p2]
})

df_melted = df_grafico.melt(id_vars="Material", var_name="Proveedor", value_name="Costo (S/.)")

fig = px.bar(df_melted, x="Material", y="Costo (S/.)", color="Proveedor",
             barmode="group", title="Costo por Material - P1 vs P2")
st.plotly_chart(fig, use_container_width=True)

# 9. EXPORTAR A EXCEL
st.subheader("📥 Exportar Presupuesto")

def exportar_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_comparativo.to_excel(writer, index=False, sheet_name='Presupuesto')
    return output.getvalue()

excel_data = exportar_excel()
st.download_button(
    label="⬇️ Descargar Excel",
    data=excel_data,
    file_name="presupuesto_capeco.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
