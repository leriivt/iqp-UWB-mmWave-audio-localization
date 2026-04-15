"""
mmWave Point Cloud Visualizer
Companion GUI for mmWave_hardware.py
Requires: PyQt6, pyqtgraph, numpy
  pip install PyQt6 pyqtgraph numpy
"""

import sys
import time
import math
import threading
import random
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional

import os
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt6"

import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSplitter, QGroupBox, QGridLayout, QSlider,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QColor, QPalette, QFont, QPainter, QBrush, QPen, QLinearGradient

import pyqtgraph as pg
import pyqtgraph.opengl as gl

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = {
    "bg":           "#0a0e17",
    "panel":        "#0f1623",
    "border":       "#1c2a3a",
    "accent":       "#00d4ff",
    "accent2":      "#ff6b35",
    "accent3":      "#39ff14",
    "text":         "#c8d8e8",
    "text_dim":     "#4a6070",
    "warning":      "#ffaa00",
    "danger":       "#ff3355",
    "good":         "#39ff14",
}

QSS = f"""
QMainWindow, QWidget {{
    background-color: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}}
QGroupBox {{
    border: 1px solid {PALETTE['border']};
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 4px;
    font-size: 10px;
    color: {PALETTE['accent']};
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
QLabel {{
    color: {PALETTE['text']};
    background: transparent;
}}
QPushButton {{
    background-color: {PALETTE['panel']};
    color: {PALETTE['accent']};
    border: 1px solid {PALETTE['accent']};
    border-radius: 3px;
    padding: 5px 14px;
    font-family: 'Consolas', 'Courier New', monospace;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    background-color: {PALETTE['accent']};
    color: {PALETTE['bg']};
}}
QPushButton:pressed {{
    background-color: #008aaa;
}}
QPushButton#stop_btn {{
    border-color: {PALETTE['danger']};
    color: {PALETTE['danger']};
}}
QPushButton#stop_btn:hover {{
    background-color: {PALETTE['danger']};
    color: white;
}}
QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {PALETTE['panel']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['border']};
    border-radius: 3px;
    padding: 3px 6px;
}}
QComboBox::drop-down {{
    border: none;
}}
QSlider::groove:horizontal {{
    height: 4px;
    background: {PALETTE['border']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {PALETTE['accent']};
    width: 12px; height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}}
QSlider::sub-page:horizontal {{
    background: {PALETTE['accent']};
    border-radius: 2px;
}}
QTabWidget::pane {{
    border: 1px solid {PALETTE['border']};
}}
QTabBar::tab {{
    background: {PALETTE['panel']};
    color: {PALETTE['text_dim']};
    padding: 6px 16px;
    border: 1px solid {PALETTE['border']};
    border-bottom: none;
    font-size: 10px;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    color: {PALETTE['accent']};
    background: {PALETTE['bg']};
    border-bottom: 2px solid {PALETTE['accent']};
}}
QTableWidget {{
    background-color: {PALETTE['panel']};
    gridline-color: {PALETTE['border']};
    border: none;
}}
QTableWidget::item {{
    padding: 3px 6px;
}}
QTableWidget::item:selected {{
    background-color: {PALETTE['border']};
}}
QHeaderView::section {{
    background-color: {PALETTE['bg']};
    color: {PALETTE['accent']};
    border: none;
    border-bottom: 1px solid {PALETTE['border']};
    padding: 4px 6px;
    font-size: 10px;
    letter-spacing: 1px;
}}
QCheckBox {{
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 13px; height: 13px;
    border: 1px solid {PALETTE['border']};
    border-radius: 2px;
    background: {PALETTE['panel']};
}}
QCheckBox::indicator:checked {{
    background: {PALETTE['accent']};
    border-color: {PALETTE['accent']};
}}
QScrollBar:vertical {{
    background: {PALETTE['panel']};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {PALETTE['border']};
    border-radius: 4px;
    min-height: 20px;
}}
"""


# ── Data structures (mirrors mmWave_hardware.py) ──────────────────────────────
@dataclass
class mmWavePointCloudFrame:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    v: float = 0.0
    snr: float = 0.0
    id: float = 0.0
    power: float = 0.0

@dataclass
class mmWaveFrame:
    current_frame_count: int = 0
    personnel: list = field(default_factory=list)
    point_cloud: list = field(default_factory=list)


# ── Mock data generator (replace with real hardware feed) ─────────────────────
class MockDataGenerator(QObject):
    frame_ready = pyqtSignal(object)

    def __init__(self, fps: float = 10.0):
        super().__init__()
        self.fps = fps
        self._running = False
        self._frame_count = 0
        self._thread: Optional[QThread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        while self._running:
            frame = self._generate_frame()
            self.frame_ready.emit(frame)
            time.sleep(1.0 / self.fps)

    def _generate_frame(self) -> mmWaveFrame:
        self._frame_count += 1
        t = time.time()
        n = random.randint(30, 120)
        points = []
        for _ in range(n):
            # Two clusters of people + noise
            cluster = random.choice([0, 1, 2])
            if cluster == 0:
                cx, cy, cz = 1.5 + 0.2 * math.sin(t * 0.7), 3.0, 0.9 + 0.05 * math.sin(t * 1.1)
            elif cluster == 1:
                cx, cy, cz = -1.0 + 0.15 * math.cos(t * 0.5), 4.5, 1.1
            else:
                cx = random.uniform(-4, 4)
                cy = random.uniform(1, 7)
                cz = random.uniform(0, 2.5)

            p = mmWavePointCloudFrame(
                x=cx + random.gauss(0, 0.15),
                y=cy + random.gauss(0, 0.15),
                z=cz + random.gauss(0, 0.10),
                v=random.gauss(0, 0.3),
                snr=random.uniform(5, 40),
                id=float(cluster),
                power=random.uniform(10, 60),
            )
            points.append(p)

        frame = mmWaveFrame(current_frame_count=self._frame_count, point_cloud=points)
        return frame


# ── Stat card widget ──────────────────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, title: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            StatCard {{
                background: {PALETTE['panel']};
                border: 1px solid {PALETTE['border']};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setSpacing(2)
        lay.setContentsMargins(8, 6, 8, 6)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 9px; letter-spacing: 1px;")

        self.value_lbl = QLabel("—")
        self.value_lbl.setStyleSheet(f"color: {PALETTE['accent']}; font-size: 18px; font-weight: bold;")

        self.unit_lbl = QLabel(unit)
        self.unit_lbl.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 9px;")

        lay.addWidget(self.title_lbl)
        lay.addWidget(self.value_lbl)
        lay.addWidget(self.unit_lbl)

    def set_value(self, v, color: Optional[str] = None):
        self.value_lbl.setText(str(v))
        if color:
            self.value_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")


# ── LED status indicator ──────────────────────────────────────────────────────
class LED(QWidget):
    def __init__(self, color=PALETTE['good'], parent=None):
        super().__init__(parent)
        self._color = color
        self._on = False
        self.setFixedSize(14, 14)

    def set_on(self, state: bool):
        self._on = state
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._on:
            p.setBrush(QBrush(QColor(self._color)))
            p.setPen(QPen(QColor(self._color).lighter(120), 1))
        else:
            p.setBrush(QBrush(QColor(PALETTE['border'])))
            p.setPen(QPen(QColor(PALETTE['border']).lighter(120), 1))
        p.drawEllipse(1, 1, 12, 12)


# ── History buffer ────────────────────────────────────────────────────────────
class PointCloudHistory:
    def __init__(self, max_frames: int = 10):
        self.max_frames = max_frames
        self._frames: deque = deque(maxlen=max_frames)
        self._counts: deque = deque(maxlen=300)  # for fps/count chart

    def add_frame(self, frame: mmWaveFrame):
        self._frames.append(frame.point_cloud or [])
        self._counts.append(len(frame.point_cloud or []))

    def get_all_points(self) -> List[mmWavePointCloudFrame]:
        pts = []
        for f in self._frames:
            pts.extend(f)
        return pts

    def get_latest_points(self) -> List[mmWavePointCloudFrame]:
        if not self._frames:
            return []
        return list(self._frames[-1])

    @property
    def count_history(self) -> List[int]:
        return list(self._counts)


# ── 3-D OpenGL scatter view ───────────────────────────────────────────────────
def _make_colormap_rgba(points: List[mmWavePointCloudFrame], mode: str) -> np.ndarray:
    """Return Nx4 float32 RGBA (0-1) based on chosen attribute."""
    n = len(points)
    rgba = np.ones((n, 4), dtype=np.float32)
    rgba[:, 3] = 0.85  # alpha

    if n == 0:
        return rgba

    if mode == "SNR":
        vals = np.array([p.snr for p in points], dtype=np.float32)
    elif mode == "Power":
        vals = np.array([p.power for p in points], dtype=np.float32)
    elif mode == "Velocity":
        vals = np.array([p.v for p in points], dtype=np.float32)
    elif mode == "Height (Z)":
        vals = np.array([p.z for p in points], dtype=np.float32)
    elif mode == "Track ID":
        vals = np.array([p.id for p in points], dtype=np.float32)
    else:  # Depth (Y)
        vals = np.array([p.y for p in points], dtype=np.float32)

    vmin, vmax = vals.min(), vals.max()
    if vmax > vmin:
        t = (vals - vmin) / (vmax - vmin)
    else:
        t = np.full(n, 0.5)

    # Cyan → accent2 gradient
    r0, g0, b0 = 0.0, 0.83, 1.0   # cyan
    r1, g1, b1 = 1.0, 0.42, 0.21  # orange
    rgba[:, 0] = r0 + (r1 - r0) * t
    rgba[:, 1] = g0 + (g1 - g0) * t
    rgba[:, 2] = b0 + (b1 - b0) * t
    return rgba


class View3D(gl.GLViewWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundColor(pg.mkColor(PALETTE['bg']))
        self.setCameraPosition(distance=12, elevation=25, azimuth=-60)

        # Grid
        gx = gl.GLGridItem()
        gx.setSize(x=12, y=12)
        gx.setSpacing(x=1, y=1)
        gx.setColor(pg.mkColor(PALETTE['border']))
        self.addItem(gx)

        # Axes
        ax = gl.GLAxisItem()
        ax.setSize(x=3, y=3, z=3)
        self.addItem(ax)

        self._scatter = gl.GLScatterPlotItem(pxMode=True)
        self._scatter.setGLOptions('translucent')
        self.addItem(self._scatter)

        self._colormap_mode = "SNR"
        self._point_size = 5

    def update_points(self, points: List[mmWavePointCloudFrame]):
        if not points:
            self._scatter.setData(pos=np.empty((0, 3)))
            return
        pos = np.array([[p.x, p.y, p.z] for p in points], dtype=np.float32)
        color = _make_colormap_rgba(points, self._colormap_mode)
        self._scatter.setData(pos=pos, color=color, size=self._point_size)

    def set_colormap(self, mode: str):
        self._colormap_mode = mode

    def set_point_size(self, s: int):
        self._point_size = s


# ── 2-D top-down scatter (XY plane) ──────────────────────────────────────────
class View2D(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setBackground(PALETTE['bg'])
        self.showGrid(x=True, y=True, alpha=0.15)
        self.setLabel('left',  'Y (depth)', units='m',
                      **{"color": PALETTE['text_dim'], "font-size": "10px"})
        self.setLabel('bottom', 'X (lateral)', units='m',
                      **{"color": PALETTE['text_dim'], "font-size": "10px"})
        self.getAxis('left').setTextPen(PALETTE['text_dim'])
        self.getAxis('bottom').setTextPen(PALETTE['text_dim'])
        self.setAspectLocked(True)

        self._scatter = pg.ScatterPlotItem(pen=None, symbol='o')
        self.addItem(self._scatter)

        # Detection range ring (e.g. 6 m)
        ring = pg.QtWidgets.QGraphicsEllipseItem(-6, 0, 12, 12)
        ring.setPen(pg.mkPen(PALETTE['border'], style=Qt.PenStyle.DashLine))
        ring.setBrush(pg.mkBrush(None))
        self.addItem(ring)

        # Sensor marker
        sensor = pg.ScatterPlotItem(
            [{'pos': (0, 0), 'symbol': 't', 'size': 14,
              'brush': pg.mkBrush(PALETTE['accent']),
              'pen': pg.mkPen(None)}]
        )
        self.addItem(sensor)

    def update_points(self, points: List[mmWavePointCloudFrame], colormap_mode: str):
        if not points:
            self._scatter.setData([])
            return
        rgba = _make_colormap_rgba(points, colormap_mode)
        spots = [
            {'pos': (p.x, p.y),
             'brush': pg.mkBrush(*[int(c * 255) for c in rgba[i]]),
             'size': 6}
            for i, p in enumerate(points)
        ]
        self._scatter.setData(spots)


# ── Point count / FPS sparkline ───────────────────────────────────────────────
class SparklineWidget(pg.PlotWidget):
    def __init__(self, title: str, color: str, parent=None):
        super().__init__(parent=parent)
        self.setBackground(PALETTE['panel'])
        self.setMaximumHeight(80)
        self.hideAxis('bottom')
        self.getAxis('left').setTextPen(color)
        self.getAxis('left').setWidth(30)
        self.showGrid(y=True, alpha=0.08)
        self.setTitle(title, color=color, size='8pt')
        self._curve = self.plot(pen=pg.mkPen(color, width=1.5))
        self._fill = pg.FillBetweenItem(
            self._curve,
            self.plot(pen=None),
            brush=pg.mkBrush(QColor(color).darker(300))
        )
        self.addItem(self._fill)

    def update_data(self, data: List[float]):
        if data:
            self._curve.setData(data)


# ── Point detail table ────────────────────────────────────────────────────────
COLS = ["X (m)", "Y (m)", "Z (m)", "Vel (m/s)", "SNR (dB)", "Track ID", "Power"]

class PointTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, len(COLS), parent)
        self.setHorizontalHeaderLabels(COLS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(self.styleSheet() + f"""
            QTableWidget {{ alternate-background-color: {PALETTE['bg']}; }}
        """)

    def load_points(self, points: List[mmWavePointCloudFrame]):
        self.setRowCount(len(points))
        for r, p in enumerate(points):
            vals = [p.x, p.y, p.z, p.v, p.snr, p.id, p.power]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(f"{v:.3f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(r, c, item)


# ── Main window ───────────────────────────────────────────────────────────────
class mmWaveVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mmWave Point Cloud Visualizer")
        self.resize(1380, 820)
        self.setStyleSheet(QSS)

        self.history = PointCloudHistory(max_frames=5)
        self.source = MockDataGenerator(fps=10.0)
        self.source.frame_ready.connect(self._on_frame)

        self._frame_times: deque = deque(maxlen=60)
        self._last_frame_time = time.time()
        self._paused = False

        self._build_ui()

        # Refresh display at 20 Hz
        self._render_timer = QTimer()
        self._render_timer.timeout.connect(self._render)
        self._render_timer.start(50)

        # Sparkline update at 2 Hz
        self._spark_timer = QTimer()
        self._spark_timer.timeout.connect(self._update_sparklines)
        self._spark_timer.start(500)

        #self.source.start()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(6)
        root.setContentsMargins(6, 6, 6, 6)

        # Left sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Main views
        main_area = QWidget()
        main_lay = QVBoxLayout(main_area)
        main_lay.setSpacing(6)
        main_lay.setContentsMargins(0, 0, 0, 0)

        # Header bar
        header = self._build_header()
        main_lay.addWidget(header)

        # Tabs: 3D / 2D top-down / data table
        self.tabs = QTabWidget()
        self.view3d = View3D()
        self.view2d = View2D()
        self.point_table = PointTable()

        self.tabs.addTab(self.view3d,      "3D SCATTER")
        self.tabs.addTab(self.view2d,      "TOP-DOWN (XY)")
        self.tabs.addTab(self.point_table, "POINT DATA")
        main_lay.addWidget(self.tabs, 1)

        # Sparklines
        sparks = self._build_sparklines()
        main_lay.addWidget(sparks)

        root.addWidget(main_area, 1)

    def _build_header(self) -> QWidget:
        w = QFrame()
        w.setStyleSheet(f"background: {PALETTE['panel']}; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        w.setMaximumHeight(48)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(12, 4, 12, 4)

        title = QLabel("mmWave  Point Cloud  Visualizer")
        title.setStyleSheet(f"color: {PALETTE['accent']}; font-size: 14px; letter-spacing: 3px; font-weight: bold;")
        lay.addWidget(title)
        lay.addStretch()

        self.status_led = LED(PALETTE['good'])
        self.status_lbl = QLabel("LIVE")
        self.status_lbl.setStyleSheet(f"color: {PALETTE['good']}; font-size: 10px; letter-spacing: 2px;")
        lay.addWidget(self.status_led)
        lay.addWidget(self.status_lbl)
        lay.addSpacing(20)

        self.frame_lbl = QLabel("Frame 0")
        self.frame_lbl.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 10px;")
        lay.addWidget(self.frame_lbl)
        return w

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        lay = QVBoxLayout(sidebar)
        lay.setSpacing(8)
        lay.setContentsMargins(0, 0, 0, 0)

        # ── Stats ──
        stats_box = QGroupBox("Live Stats")
        sg = QGridLayout(stats_box)
        sg.setSpacing(4)

        self.card_points   = StatCard("Points",  "pts")
        self.card_fps      = StatCard("Rate",    "fps")
        self.card_range    = StatCard("Max Y",   "m")
        self.card_spread   = StatCard("X Span",  "m")

        sg.addWidget(self.card_points,  0, 0)
        sg.addWidget(self.card_fps,     0, 1)
        sg.addWidget(self.card_range,   1, 0)
        sg.addWidget(self.card_spread,  1, 1)
        lay.addWidget(stats_box)

        # ── Colour coding ──
        color_box = QGroupBox("Colour Coding")
        cl = QVBoxLayout(color_box)
        self.color_combo = QComboBox()
        self.color_combo.addItems(["SNR", "Power", "Velocity", "Height (Z)", "Depth (Y)", "Track ID"])
        self.color_combo.currentTextChanged.connect(self._on_colormap_change)
        cl.addWidget(self.color_combo)

        # Colour legend
        self.legend_widget = ColorLegend()
        cl.addWidget(self.legend_widget)
        lay.addWidget(color_box)

        # ── Display options ──
        disp_box = QGroupBox("Display")
        dl = QVBoxLayout(disp_box)

        self.trail_check = QCheckBox("Show trail  (N frames)")
        self.trail_check.setChecked(True)
        dl.addWidget(self.trail_check)

        trail_row = QHBoxLayout()
        trail_row.addWidget(QLabel("Frames:"))
        self.trail_spin = QSpinBox()
        self.trail_spin.setRange(1, 30)
        self.trail_spin.setValue(5)
        self.trail_spin.valueChanged.connect(lambda v: setattr(self.history, 'max_frames', v))
        trail_row.addWidget(self.trail_spin)
        dl.addLayout(trail_row)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Point size:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(2, 16)
        self.size_slider.setValue(5)
        self.size_slider.valueChanged.connect(self._on_size_change)
        size_row.addWidget(self.size_slider)
        dl.addLayout(size_row)

        # Z-filter
        z_row = QHBoxLayout()
        z_row.addWidget(QLabel("Z min:"))
        self.z_min = QDoubleSpinBox()
        self.z_min.setRange(-5, 5); self.z_min.setValue(-0.5); self.z_min.setSingleStep(0.1)
        z_row.addWidget(self.z_min)
        dl.addLayout(z_row)
        z_row2 = QHBoxLayout()
        z_row2.addWidget(QLabel("Z max:"))
        self.z_max = QDoubleSpinBox()
        self.z_max.setRange(-5, 10); self.z_max.setValue(3.0); self.z_max.setSingleStep(0.1)
        z_row2.addWidget(self.z_max)
        dl.addLayout(z_row2)

        lay.addWidget(disp_box)

        # ── Controls ──
        ctrl_box = QGroupBox("Control")
        ctll = QVBoxLayout(ctrl_box)

        self.pause_btn = QPushButton("⏸  PAUSE")
        self.pause_btn.clicked.connect(self._toggle_pause)
        ctll.addWidget(self.pause_btn)

        self.clear_btn = QPushButton("✕  CLEAR")
        self.clear_btn.clicked.connect(self._clear)
        ctll.addWidget(self.clear_btn)

        self.demo_btn = QPushButton("⚡  DEMO MODE")
        self.demo_btn.setCheckable(True)
        self.demo_btn.setChecked(True)
        ctll.addWidget(self.demo_btn)

        lay.addWidget(ctrl_box)
        lay.addStretch()

        # Footer
        footer = QLabel("Connect mmWaveHardwareInterface\nand call set_measurement_callback\nto feed live frames.")
        footer.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 9px; padding: 6px;")
        footer.setWordWrap(True)
        lay.addWidget(footer)

        return sidebar

    def _build_sparklines(self) -> QWidget:
        w = QWidget()
        w.setMaximumHeight(85)
        lay = QHBoxLayout(w)
        lay.setSpacing(4)
        lay.setContentsMargins(0, 0, 0, 0)

        self.spark_count = SparklineWidget("POINT COUNT", PALETTE['accent'])
        self.spark_fps   = SparklineWidget("FPS",         PALETTE['accent2'])

        lay.addWidget(self.spark_count)
        lay.addWidget(self.spark_fps)
        return w

    # ── Slots & helpers ───────────────────────────────────────────────────────
    def _on_frame(self, frame: mmWaveFrame):
        if self._paused:
            return
        now = time.time()
        dt = now - self._last_frame_time
        self._last_frame_time = now
        if dt > 0:
            self._frame_times.append(1.0 / dt)
        self.history.add_frame(frame)
        self._latest_frame = frame

    def _apply_filters(self, points: List[mmWavePointCloudFrame]) -> List[mmWavePointCloudFrame]:
        zlo = self.z_min.value()
        zhi = self.z_max.value()
        return [p for p in points if zlo <= p.z <= zhi]

    def _render(self):
        if not hasattr(self, '_latest_frame'):
            return

        frame = self._latest_frame
        raw = (self.history.get_all_points() if self.trail_check.isChecked()
               else self.history.get_latest_points())
        pts = self._apply_filters(raw)

        tab = self.tabs.currentIndex()
        if tab == 0:
            self.view3d.update_points(pts)
        elif tab == 1:
            self.view2d.update_points(pts, self.color_combo.currentText())
        elif tab == 2:
            self.point_table.load_points(self.history.get_latest_points())

        # Stats
        n = len(pts)
        self.card_points.set_value(n)
        if self._frame_times:
            fps = np.mean(list(self._frame_times))
            self.card_fps.set_value(f"{fps:.1f}")

        if pts:
            max_y = max(p.y for p in pts)
            x_vals = [p.x for p in pts]
            self.card_range.set_value(f"{max_y:.1f}")
            self.card_spread.set_value(f"{max(x_vals) - min(x_vals):.1f}")

        self.status_led.set_on(not self._paused)
        self.frame_lbl.setText(f"Frame {frame.current_frame_count:06d}")

    def _update_sparklines(self):
        self.spark_count.update_data(self.history.count_history)
        fps_data = list(self._frame_times)
        self.spark_fps.update_data(fps_data)

    def _on_colormap_change(self, mode: str):
        self.view3d.set_colormap(mode)
        self.legend_widget.set_mode(mode)

    def _on_size_change(self, v: int):
        self.view3d.set_point_size(v)

    def _toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            self.pause_btn.setText("▶  RESUME")
            self.status_lbl.setText("PAUSED")
            self.status_lbl.setStyleSheet(f"color: {PALETTE['warning']}; font-size: 10px; letter-spacing: 2px;")
        else:
            self.pause_btn.setText("⏸  PAUSE")
            self.status_lbl.setText("LIVE")
            self.status_lbl.setStyleSheet(f"color: {PALETTE['good']}; font-size: 10px; letter-spacing: 2px;")

    def _clear(self):
        self.history._frames.clear()
        self.history._counts.clear()
        self._frame_times.clear()

    def feed_frame(self, frame: mmWaveFrame):
        """Public API: call this from your mmWaveHardwareInterface callback."""
        self._on_frame(frame)

    def closeEvent(self, e):
        self.source.stop()
        super().closeEvent(e)


# ── Colour legend ─────────────────────────────────────────────────────────────
class ColorLegend(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        self._mode = "SNR"

    def set_mode(self, mode: str):
        self._mode = mode
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, QColor(0, 212, 255))
        grad.setColorAt(1.0, QColor(255, 107, 53))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 4, w, 10, 5, 5)

        p.setPen(QColor(PALETTE['text_dim']))
        p.setFont(QFont("Consolas", 7))
        p.drawText(0, h, "Low")
        fm = p.fontMetrics()
        p.drawText(w - fm.horizontalAdvance("High"), h, "High")


# ── Integration example ───────────────────────────────────────────────────────
def integrate_with_hardware(app_window: mmWaveVisualizer, hw_interface):
    """
    Drop-in integration with mmWaveHardwareInterface from mmWave_hardware.py

    Usage:
        from mmWave_hardware import mmWaveHardwareInterface
        from config import mmWaveConfig

        cfg = mmWaveConfig(serial_port='/dev/ttyUSB0', baud_rate=115200)
        hw  = mmWaveHardwareInterface(cfg, mode=1)   # mode=1 for point cloud
        integrate_with_hardware(window, hw)
        hw.start()
    """
    hw_interface.set_measurement_callback(app_window.feed_frame)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark base palette so Qt chrome matches
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,        QColor(PALETTE['bg']))
    pal.setColor(QPalette.ColorRole.WindowText,    QColor(PALETTE['text']))
    pal.setColor(QPalette.ColorRole.Base,          QColor(PALETTE['panel']))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(PALETTE['bg']))
    pal.setColor(QPalette.ColorRole.Text,          QColor(PALETTE['text']))
    pal.setColor(QPalette.ColorRole.Button,        QColor(PALETTE['panel']))
    pal.setColor(QPalette.ColorRole.ButtonText,    QColor(PALETTE['text']))
    pal.setColor(QPalette.ColorRole.Highlight,     QColor(PALETTE['accent']))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(PALETTE['bg']))
    app.setPalette(pal)

    window = mmWaveVisualizer()
    window.show()
    sys.exit(app.exec())
