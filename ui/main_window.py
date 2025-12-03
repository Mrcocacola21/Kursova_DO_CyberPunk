"""
main_window.py — GRAPHICS-FIRST STUDIO LAYOUT (wide control panel)
"""

from __future__ import annotations
from typing import Optional

import numpy as np

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStatusBar,
    QLabel,
)

from core.iteration_result import IterationResult
from ui.control_panel import ControlPanelWidget, OptimizationConfig
from ui.table_view import IterationsTableWidget
from ui.plot_view import PlotView
from ui.dialogs import show_about
from ui.styles import apply_label_muted, MARGIN, SPACING


class MainWindow(QMainWindow):
    """
    Головне вікно GUI оптимізатора в "Studio Mode":
        - зліва: широка панель керування + картинка;
        - по центру: великий PlotView (f(k) + contour);
        - справа: таблиця ітерацій + статистика.
    """

    optimizationRequested = pyqtSignal(OptimizationConfig)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Мінімізація функцій — Studio Mode")
        # Трохи ширше загальне вікно
        self.resize(1650, 900)

        self._create_actions()
        self._create_menu()
        self._create_status_bar()
        self._create_content()
        self._connect_signals()

    # ----------------------------------------------------------------------
    # Menu + actions
    # ----------------------------------------------------------------------
    def _create_actions(self) -> None:
        self.action_exit = QAction("Вихід", self, shortcut="Ctrl+Q")
        self.action_about = QAction("Про програму", self)

    def _create_menu(self) -> None:
        menu = self.menuBar()
        menu.addMenu("Файл").addAction(self.action_exit)
        menu.addMenu("Довідка").addAction(self.action_about)

    def _create_status_bar(self) -> None:
        status = QStatusBar(self)
        self.setStatusBar(status)
        status.showMessage("Готово")

    # ----------------------------------------------------------------------
    # CONTENT LAYOUT
    # ----------------------------------------------------------------------
    def _create_content(self) -> None:
        """
        Компоновка:

         +--------------------------------------------------------------+
         |                         MENU BAR                             |
         +--------------------------------------------------------------+
         |   LEFT (wide controls)   |  CENTER (plot)  |  RIGHT (table)  |
         +--------------------------------------------------------------+
        """
        central = QWidget(self)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        root.setSpacing(SPACING)

        # LEFT PANEL – controls + image (широкий)
        left_panel = self._build_left_panel()
        # CENTER – main graphics area (one big PlotView)
        center_panel = self._build_center_panel()
        # RIGHT – table + stats
        right_panel = self._build_right_panel()

        # Пропорції: лівий 3, центр 5, правий 2
        root.addWidget(left_panel, stretch=3)
        root.addWidget(center_panel, stretch=5)
        root.addWidget(right_panel, stretch=2)

        # Початковий ресет статистики
        self.update_run_stats(None, None)

    # ------------------------------------------------------------------
    # LEFT CONTROL PANEL
    # ------------------------------------------------------------------
    def _build_left_panel(self) -> QWidget:
        widget = QWidget(self)
        # Мінімальна ширина — щоб комбобокси / поля не ламалися
        widget.setMinimumWidth(430)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING)

        self.control_panel = ControlPanelWidget(widget)
        layout.addWidget(self.control_panel)

        # Картинка під панеллю керування (необов'язкова)
        self.left_image = QLabel(widget)
        self.left_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pix = QPixmap("images/bg_main.png")
        if not pix.isNull():
            # Трошки ширше, бо панель тепер ширша
            self.left_image.setPixmap(
                pix.scaledToWidth(640, Qt.TransformationMode.SmoothTransformation)
            )
        else:
        #    self.left_image.hide()
            self.left_image.hide()

        layout.addWidget(self.left_image)
        layout.addStretch()

        return widget

    # ------------------------------------------------------------------
    # CENTER GRAPHICS AREA — один великий PlotView
    # ------------------------------------------------------------------
    def _build_center_panel(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING)

        # Один PlotView, який використовується і для contour, і для f(k)
        self.plot_view = PlotView(widget)
        layout.addWidget(self.plot_view, stretch=1)

        return widget

    # ------------------------------------------------------------------
    # RIGHT PANEL – table + stats
    # ------------------------------------------------------------------
    def _build_right_panel(self) -> QWidget:
        widget = QWidget(self)
        # Мінімальна ширина, але не жорсткий fixed
        widget.setMinimumWidth(320)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING)

        self.iterations_table = IterationsTableWidget(widget)
        layout.addWidget(self.iterations_table, stretch=1)

        layout.addLayout(self._build_stats_row())

        return widget

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING)

        self.label_func_evals = QLabel("f evals: –")
        self.label_outer_iters = QLabel("outer iters: –")
        self.label_last_step = QLabel("step: –")

        for lbl in (self.label_func_evals, self.label_outer_iters, self.label_last_step):
            apply_label_muted(lbl)
            row.addWidget(lbl)

        row.addStretch()
        return row

    # ------------------------------------------------------------------
    # Signals
    # ------------------------------------------------------------------
    def _connect_signals(self) -> None:
        self.action_exit.triggered.connect(self.close)
        self.action_about.triggered.connect(lambda: show_about(self))

        self.control_panel.exitRequested.connect(self.close)
        self.control_panel.clearRequested.connect(self._on_clear_requested)
        self.control_panel.runRequested.connect(self._on_run_requested)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def _on_run_requested(self, cfg: OptimizationConfig) -> None:
        self.clear_results()
        self.statusBar().showMessage(
            f"Запуск: {cfg.function_key}, {cfg.method_key}, x0={cfg.x0.tolist()}"
        )
        self.optimizationRequested.emit(cfg)

    def _on_clear_requested(self) -> None:
        self.clear_results()
        self.statusBar().showMessage("Очищено")

    # ------------------------------------------------------------------
    # PUBLIC API (для app.py / движка)
    # ------------------------------------------------------------------
    def clear_results(self) -> None:
        """
        Очистити таблицю, скинути графік у плейсхолдер і статистику.
        """
        self.clear_iterations_table()
        self.plot_view.show_placeholder()
        self.update_run_stats(None, None)

    def clear_iterations_table(self) -> None:
        """
        Backward compatible метод для app.py.
        """
        if hasattr(self, "iterations_table"):
            self.iterations_table.clear_table()

    def add_iteration(
        self,
        iteration: IterationResult,
        step_value=None,
    ) -> None:
        """
        Додати ітерацію в таблицю.
        """
        self.iterations_table.add_iteration(iteration, step_value)

    def add_iteration_row(
        self,
        k,
        x,
        f_val,
        step_value=None,
    ) -> None:
        """
        Сумісний з попередніми версіями метод:
        відновлює IterationResult з примітивів.
        """
        it = IterationResult(
            index=int(k),
            x=np.array(x, dtype=float),
            f=float(f_val),
            step_norm=float(step_value or 0.0),
            meta={},
        )
        self.add_iteration(it, step_value)

    def update_fk_plot(self, iterations) -> None:
        """
        Оновити графік f(k) (викликається з движка).
        """
        self.plot_view.plot_fk(iterations)

    def update_contour_trajectory(self, func, iterations) -> None:
        """
        Оновити contour plot + траєкторію (викликається з движка).
        """
        self.plot_view.plot_contour_trajectory(func, iterations)

    def update_run_stats(
        self,
        func_evals: Optional[int],
        last_step: Optional[float],
        n_outer_iters: Optional[int] = None,
    ) -> None:
        """
        Оновити підписи під таблицею:
            - кількість викликів цільової функції;
            - кількість зовнішніх ітерацій;
            - фінальний крок пошуку.
        """
        self.label_func_evals.setText(
            f"f evals: {func_evals if func_evals is not None else '–'}"
        )
        self.label_outer_iters.setText(
            f"outer iters: {n_outer_iters if n_outer_iters is not None else '–'}"
        )
        self.label_last_step.setText(
            "step: –" if last_step is None else f"step: {last_step:.3e}"
        )


# ----------------------------------------------------------------------
# MAIN (ручний запуск)
# ----------------------------------------------------------------------
def main() -> None:
    import sys

    app = QApplication(sys.argv)

    from ui.styles import apply_app_style

    apply_app_style(app)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
