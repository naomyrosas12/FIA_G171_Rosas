"""S1 · Infografía comparativa de 3 casos de IA (salud, industria/logística, movilidad).

Todas las cifras provienen de las fuentes citadas en el informe (consultadas el 9-oct-2026):
· IDx-DR   -> ensayo pivotal (Abràmoff et al., 2018) vía News-Medical (2018)
· UPS ORION -> Henschen (2013), InformationWeek
· Waymo    -> Waymo (2026), página "Safety Impact" (datos a junio de 2026)

Ejecutar: python s1_infografia.py   (genera figuras/infografia_casos.png)
"""
import os
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


# ---- estilo visual (antes estaba en el módulo externo "estilo"; ahora va incluido)
class estilo:
    AZUL = "#2A7BD8"
    NARANJA = "#EE6A35"
    AQUA = "#1DB383"
    INDIGO = "#2B1B5E"
    TINTA = "#1B1B1F"
    TINTA2 = "#5A5A66"

    @staticmethod
    def aplicar():
        plt.rcParams.update({
            "font.family": "DejaVu Sans",
            "figure.facecolor": "white",
            "axes.facecolor": "#F6F7FB",
            "axes.edgecolor": "#D9DCE6",
            "axes.grid": True,
            "grid.color": "#E3E6EE",
            "savefig.dpi": 200,
            "savefig.facecolor": "white",
        })


estilo.aplicar()

AQUI = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(AQUI, "figuras")
os.makedirs(FIG, exist_ok=True)

# ---- datos de cada caso (tomados de las fuentes)
CASOS = [
    {"sector": "SALUD · EE. UU.", "nombre": "IDx-DR", "sub": "Detección autónoma de retinopatía diabética",
     "color": estilo.AZUL, "grande": "87 % / 90 %", "grande_et": "sensibilidad / especificidad",
     "barras": [("Sensibilidad", 87), ("Especificidad", 90), ("Imageabilidad", 96)],
     "tit_graf": "Desempeño en ensayo clínico (%)", "n": "900 participantes · 10 consultorios de atención primaria",
     "tecnica": "Aprendizaje profundo sobre imágenes de fondo de ojo", "anio": "FDA, abril 2018"},
    {"sector": "LOGÍSTICA · EE. UU.", "nombre": "UPS ORION", "sub": "Optimización de rutas de reparto",
     "color": estilo.NARANJA, "grande": "1.5 M gal", "grande_et": "de combustible ahorrados (≈14,000 t CO₂)",
     "barras": [("2009 (beta)", 1), ("2010", 9), ("2013 (plan)", 82)],
     "tit_graf": "Centros de distribución con ORION", "n": "55,000 rutas objetivo para 2017",
     "tecnica": "Optimización combinatoria + telemática (algoritmo propietario)", "anio": "Cifras de 2013"},
    {"sector": "MOVILIDAD · EE. UU.", "nombre": "Waymo", "sub": "Conducción autónoma (sin conductor humano)",
     "color": estilo.AQUA, "grande": "−95 %", "grande_et": "choques con lesiones graves vs. humanos",
     "barras": [("Lesión grave", 95), ("Peatón herido", 93), ("Con lesión", 82), ("Airbag", 82)],
     "tit_graf": "Reducción de choques vs. conductor humano (%)",
     "n": "271.3 M millas sin conductor · datos a junio 2026",
     "tecnica": "Aprendizaje automático: percepción, predicción y planeación", "anio": "Datos de la empresa"},
]


def tarjeta(fig, i, caso):
    ancho, gap, x0 = 0.30, 0.025, 0.04
    x = x0 + i * (ancho + gap)
    # fondo de tarjeta
    fondo = fig.add_axes([x, 0.04, ancho, 0.80]); fondo.axis("off")
    fondo.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03", fc="#F6F7FB",
                                   ec="#D9DCE6", lw=1, transform=fondo.transAxes))
    # encabezado
    enc = fig.add_axes([x, 0.74, ancho, 0.10]); enc.axis("off")
    enc.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.12", fc=caso["color"],
                                 ec="none", transform=enc.transAxes))
    enc.text(0.05, 0.70, caso["sector"], color="white", fontsize=8, fontweight="bold", va="center")
    enc.text(0.05, 0.30, caso["nombre"], color="white", fontsize=15, fontweight="bold", va="center")
    # subtítulo, cifra grande
    fig.text(x + 0.015, 0.705, caso["sub"], fontsize=8.2, color=estilo.TINTA2, va="center")
    fig.text(x + 0.015, 0.625, caso["grande"], fontsize=26, fontweight="bold", color=estilo.TINTA, va="center")
    fig.text(x + 0.015, 0.575, caso["grande_et"], fontsize=8, color=estilo.TINTA2, va="center")
    # mini gráfica de barras horizontales
    ax = fig.add_axes([x + 0.10, 0.275, ancho - 0.12, 0.25])
    nombres = [b[0] for b in caso["barras"]][::-1]
    valores = [b[1] for b in caso["barras"]][::-1]
    barras = ax.barh(nombres, valores, color=caso["color"], height=0.58)
    if caso["nombre"] == "UPS ORION":
        barras[0].set_hatch("////"); barras[0].set_edgecolor("white")  # 2013 = plan, no medición
        ax.set_xlim(0, 100)
    else:
        ax.set_xlim(0, 112)
    for b, v in zip(barras, valores):
        ax.text(v + 1.5, b.get_y() + b.get_height() / 2, f"{v}", va="center", fontsize=8, color=estilo.TINTA)
    ax.set_title(caso["tit_graf"], fontsize=8, fontweight="bold", loc="left", x=-0.55)
    ax.tick_params(axis="y", labelsize=8, length=0); ax.tick_params(axis="x", labelsize=7)
    ax.spines["left"].set_visible(False); ax.grid(axis="y", visible=False)
    # pie de tarjeta
    fig.text(x + 0.015, 0.205, caso["n"], fontsize=7.6, color=estilo.TINTA2, va="center")
    fig.text(x + 0.015, 0.152, "Técnica", fontsize=7.6, fontweight="bold", color=caso["color"], va="center")
    fig.text(x + 0.015, 0.108, "\n".join(textwrap.wrap(caso["tecnica"], 44)), fontsize=7.6, color=estilo.TINTA,
             va="center", linespacing=1.35)
    fig.text(x + 0.015, 0.060, caso["anio"], fontsize=7.4, style="italic", color=estilo.TINTA2, va="center")


def main():
    fig = plt.figure(figsize=(11, 6.3))
    fig.text(0.04, 0.945, "Tres casos de IA con impacto medible", fontsize=17, fontweight="bold", color=estilo.INDIGO)
    fig.text(0.04, 0.895, "Salud · logística · movilidad: cada indicador es propio del caso y no es comparable "
             "entre columnas", fontsize=9, color=estilo.TINTA2)
    for i, c in enumerate(CASOS):
        tarjeta(fig, i, c)
    fig.text(0.04, 0.012, "Fuentes: Abràmoff et al. (2018); News-Medical (2018); Henschen (2013); Waymo (2026). "
             "Rayado = valor planeado, no medido.", fontsize=7, color=estilo.TINTA2)
    fig.savefig(os.path.join(FIG, "infografia_casos.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()