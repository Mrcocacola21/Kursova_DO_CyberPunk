"""
plot_view.py

Віджет для відображення графіків процесу мінімізації:

    - Графік f(k): значення цільової функції від номера ітерації.
    - Contour plot цільової функції у просторі (x1, x2) з накладеною
      траєкторією оптимізації.
    - 3D-графік поверхні f(x1, x2) з накладеною траєкторією.

Нова компоновка (за важливістю):

    [ 3D SURFACE (найбільший, вся ліва частина) |  f(k)    (маленький зверху) ]
    [                                           |  CONTOUR (середній знизу)   ]

Стилізація під кіберпанк: темний фон, неонові лінії, «голографічний» вигляд.

Використовується в MainWindow як центральний графічний блок.
"""

from __future__ import annotations

from typing import Callable, List, Optional

import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from core.iteration_result import IterationResult
from .styles import MARGIN, SPACING, apply_card_style


# Кольори кіберпанк-теми (темний фон + неонові акценти)
_BG_COLOR = "#050714"
_PANEL_BORDER = "#22d3ee"   # яскравий бірюзовий
_TEXT_MAIN = "#e0f2fe"      # світлий текст
_TEXT_MUTED = "#64748b"     # приглушений
_ACCENT_1 = "#22c55e"       # неоново-зелений
_ACCENT_2 = "#e879f9"       # рожево-фіолетовий
_ACCENT_3 = "#0ea5e9"       # синій/бірюзовий


class PlotView(QWidget):
    """
    Віджет, що інкапсулює Matplotlib-графік з трьома зонами в кіберпанк-стилі:

        - великий 3D-графік поверхні f(x1, x2) + траєкторія;
        - contour plot + траєкторія (праворуч знизу);
        - маленький графік f(k) (праворуч зверху).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("plotView")
        self._build_ui()

    # ------------------------------------------------------------------
    # Побудова UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        layout.setSpacing(SPACING)

        # Базова "картка" + свій кіберпанк-стиль
        apply_card_style(self)
        self.setStyleSheet(
            """
            #plotView {
                background-color: %s;
                border: 1px solid %s;
                border-radius: 8px;
            }
            """
            % (_BG_COLOR, _PANEL_BORDER)
        )

        # Темна фігура для matplotlib
        self.figure = Figure(figsize=(7, 6), facecolor=_BG_COLOR)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")

        # GridSpec з пріоритетом 3D-графіку
        gs = self.figure.add_gridspec(
            2,
            2,
            width_ratios=[1.7, 1.0],   # ліва частина (3D) більша
            height_ratios=[0.6, 1.4],  # нижній ряд вищий за верхній
        )

        # 3D surface — обидва рядки зліва
        self.ax_surface = self.figure.add_subplot(gs[:, 0], projection="3d")

        # f(k) — маленький зверху праворуч
        self.ax_fk = self.figure.add_subplot(gs[0, 1])

        # contour — праворуч знизу
        self.ax_contour = self.figure.add_subplot(gs[1, 1])

        # Застосовуємо кіберпанк-стиль до всіх осей
        self._apply_cyberpunk_style_all()

        self.figure.tight_layout(pad=2.0)
        layout.addWidget(self.canvas)

        # Початковий плейсхолдер
        self.show_placeholder()

    # ------------------------------------------------------------------
    # Стилізація
    # ------------------------------------------------------------------

    def _style_2d_axes(self, ax) -> None:
        ax.set_facecolor("#020617")
        ax.tick_params(colors=_TEXT_MUTED, which="both", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(_PANEL_BORDER)
            spine.set_linewidth(0.8)
        ax.grid(
            True,
            color="#1f2937",
            linestyle="--",
            linewidth=0.6,
            alpha=0.7,
        )
        ax.xaxis.label.set_color(_TEXT_MAIN)
        ax.yaxis.label.set_color(_TEXT_MAIN)
        ax.title.set_color(_ACCENT_2)
        ax.title.set_fontsize(10)

    def _style_3d_axes(self, ax) -> None:
        ax.set_facecolor("#020617")
        ax.tick_params(colors=_TEXT_MUTED, which="both", labelsize=7)

        # Осьові підписи / колір
        ax.xaxis.label.set_color(_TEXT_MAIN)
        ax.yaxis.label.set_color(_TEXT_MAIN)
        ax.zaxis.label.set_color(_TEXT_MAIN)

        ax.title.set_color(_ACCENT_1)
        ax.title.set_fontsize(10)

    def _apply_cyberpunk_style_all(self) -> None:
        self._style_3d_axes(self.ax_surface)
        self._style_2d_axes(self.ax_fk)
        self._style_2d_axes(self.ax_contour)

    def _clear_all_axes(self) -> None:
        self.ax_fk.clear()
        self.ax_contour.clear()
        self.ax_surface.clear()

    def _redraw(self) -> None:
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Публічні методи
    # ------------------------------------------------------------------

    def show_placeholder(self) -> None:
        """
        Показати простий плейсхолдер замість поточних графіків.
        Очищає всі осі та виводить текст в осі f(k).
        """
        self._clear_all_axes()
        self._apply_cyberpunk_style_all()

        self.ax_fk.text(
            0.5,
            0.5,
            "Графіки процесу мінімізації\nз'являться після запуску",
            ha="center",
            va="center",
            transform=self.ax_fk.transAxes,
            color=_ACCENT_3,
            fontsize=10,
        )
        self.ax_fk.set_xticks([])
        self.ax_fk.set_yticks([])
        self.ax_fk.set_title("")

        self.ax_contour.set_xticks([])
        self.ax_contour.set_yticks([])
        self.ax_contour.set_title("")

        self.ax_surface.set_xticks([])
        self.ax_surface.set_yticks([])
        self.ax_surface.set_zticks([])
        self.ax_surface.set_title("")

        self._redraw()

    def plot_fk(self, iterations: List[IterationResult]) -> None:
        """
        Побудувати графік f(k) (верхній правий).

        Якщо iterations порожній — показує плейсхолдер.
        """
        if not iterations:
            self.show_placeholder()
            return

        self.ax_fk.clear()
        self._style_2d_axes(self.ax_fk)

        ks = [it.index for it in iterations]
        fs = [float(it.f) for it in iterations]

        self.ax_fk.plot(
            ks,
            fs,
            marker="o",
            linestyle="-",
            linewidth=1.5,
            markersize=4,
            color=_ACCENT_3,
        )
        self.ax_fk.set_xlabel("k (номер ітерації)")
        self.ax_fk.set_ylabel("f(xₖ)")
        self.ax_fk.set_title("Графік f(k)")

        self._redraw()

    def plot_contour_trajectory(
        self,
        func: Callable[[np.ndarray], float],
        iterations: List[IterationResult],
        levels: int = 20,
        padding: float = 0.5,
        grid_size: int = 100,
    ) -> None:
        """
        Побудувати:
            - contour plot в площині (x1, x2) + траєкторія (низ праворуч);
            - 3D-поверхню f(x1, x2) + траєкторія (велика ліва частина).
        """
        self.ax_contour.clear()
        self.ax_surface.clear()

        if not iterations:
            self.show_placeholder()
            return

        xs = np.array([it.x for it in iterations], dtype=float)
        if xs.ndim != 2 or xs.shape[1] != 2:
            # Фолбек для задач не в R²
            self._style_2d_axes(self.ax_contour)
            self._style_3d_axes(self.ax_surface)

            self.ax_contour.text(
                0.5,
                0.5,
                "Contour / поверхня доступні\nлише для задачі в R²",
                ha="center",
                va="center",
                transform=self.ax_contour.transAxes,
                color=_ACCENT_2,
            )
            self.ax_surface.text(
                0.5,
                0.5,
                "Неможливо побудувати\n3D-поверхню",
                ha="center",
                va="center",
                transform=self.ax_surface.transAxes,
                color=_ACCENT_2,
            )
            self._redraw()
            return

        # Область побудови: по траєкторії + невеликий запас
        x1_min, x1_max = xs[:, 0].min(), xs[:, 0].max()
        x2_min, x2_max = xs[:, 1].min(), xs[:, 1].max()

        if abs(x1_max - x1_min) < 1e-9:
            x1_min -= 1.0
            x1_max += 1.0
        if abs(x2_max - x2_min) < 1e-9:
            x2_min -= 1.0
            x2_max += 1.0

        x1_min -= padding
        x1_max += padding
        x2_min -= padding
        x2_max += padding

        x1_vals = np.linspace(x1_min, x1_max, grid_size)
        x2_vals = np.linspace(x2_min, x2_max, grid_size)
        X1, X2 = np.meshgrid(x1_vals, x2_vals)

        # Обчислюємо f на сітці
        Z = np.zeros_like(X1)
        for i in range(grid_size):
            for j in range(grid_size):
                x_vec = np.array([X1[i, j], X2[i, j]], dtype=float)
                Z[i, j] = func(x_vec)

        # -------- Contour plot (праворуч знизу, середній) --------
        self._style_2d_axes(self.ax_contour)
        contour = self.ax_contour.contour(
            X1,
            X2,
            Z,
            levels=levels,
            cmap="plasma",
        )
        self.ax_contour.clabel(
            contour,
            inline=True,
            fontsize=7,
            fmt="%.2f",
            colors=_TEXT_MUTED,
        )

        x1_traj = xs[:, 0]
        x2_traj = xs[:, 1]

        # Траєкторія на contour
        self.ax_contour.plot(
            x1_traj,
            x2_traj,
            marker="o",
            linestyle="-",
            linewidth=1.4,
            markersize=4,
            color=_ACCENT_3,
            label="Траєкторія",
        )
        self.ax_contour.scatter(
            x1_traj[0],
            x2_traj[0],
            marker="s",
            s=50,
            color=_ACCENT_1,
            label="Старт",
            zorder=5,
        )
        self.ax_contour.scatter(
            x1_traj[-1],
            x2_traj[-1],
            marker="*",
            s=120,
            color=_ACCENT_2,
            label="Мінімум",
            zorder=5,
        )

        self.ax_contour.set_xlabel("x₁")
        self.ax_contour.set_ylabel("x₂")
        self.ax_contour.set_title("Рівні функції та траєкторія")
        self.ax_contour.legend(
            loc="best",
            fontsize=7,
            facecolor="#020617",
            edgecolor=_PANEL_BORDER,
        )

        # -------- 3D surface (ліва частина, найбільша) --------
        self._style_3d_axes(self.ax_surface)

        self.ax_surface.plot_surface(
            X1,
            X2,
            Z,
            rstride=1,
            cstride=1,
            cmap="plasma",
            edgecolor="#020617",
            linewidth=0.2,
            alpha=0.9,
        )

        z_traj = np.array([func(x) for x in xs], dtype=float)

        # Темний контур під лінією (аура), щоб не губилась на поверхні
        self.ax_surface.plot(
            x1_traj,
            x2_traj,
            z_traj,
            color="#020617",
            linewidth=4.0,
            alpha=0.9,
            zorder=9,
        )

        # Неонова лінія поверх
        self.ax_surface.plot(
            x1_traj,
            x2_traj,
            z_traj,
            color=_ACCENT_1,
            marker="o",
            linestyle="-",
            linewidth=2.2,
            markersize=5,
            markerfacecolor=_ACCENT_1,
            markeredgecolor="#020617",
            markeredgewidth=0.8,
            zorder=10,
            label="Траєкторія",
        )

        # Старт / фініш — яскраві маркери
        self.ax_surface.scatter(
            [x1_traj[0]],
            [x2_traj[0]],
            [z_traj[0]],
            color=_ACCENT_1,
            marker="s",
            s=60,
            edgecolor="#020617",
            linewidths=1.0,
            label="Старт",
            zorder=11,
        )
        self.ax_surface.scatter(
            [x1_traj[-1]],
            [x2_traj[-1]],
            [z_traj[-1]],
            color=_ACCENT_2,
            marker="*",
            s=110,
            edgecolor="#020617",
            linewidths=1.0,
            label="Мінімум",
            zorder=12,
        )

        self.ax_surface.set_xlabel("x₁")
        self.ax_surface.set_ylabel("x₂")
        self.ax_surface.set_zlabel("f(x₁, x₂)")
        self.ax_surface.set_title("Поверхня f(x₁, x₂) + траєкторія")

        self._redraw()
