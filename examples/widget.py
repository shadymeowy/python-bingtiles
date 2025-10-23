from bingtiles import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from PIL.ImageQt import ImageQt
from multiprocessing.dummy import Pool


MAX_LOD = 19


class MapWidget(QWidget):
    def __init__(self, geo0=(39.89093263, 32.78269956), provider=None, cache_path=None, parent=None):
        super().__init__(parent)
        self.xy0 = list(geodetic2tile(*geo0, MAX_LOD))
        self._zoom = 1.0
        self.fetcher = CachedFetcher(cache_path=cache_path, provider=provider)
        self.pressing = False
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        self.pool = Pool(16)

    @property
    def geo0(self):
        return tile2geodetic(*self.xy0)

    @geo0.setter
    def geo0(self, value):
        self.xy0 = geodetic2tile(*value, MAX_LOD)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        size = self.size()
        center_x = size.width() / 2
        center_y = size.height() / 2
        lod = MAX_LOD
        while True:
            zoom = self.zoom * 256 / 2 ** (lod - 18)
            if zoom >= 256:
                break
            lod -= 1
        lod_start = lod
        while lod < MAX_LOD:
            zoom = self.zoom * 256 / 2 ** (lod - 18)
            result = self.draw_map(center_x, center_y, painter, lod, zoom)
            if result:
                break
            lod -= 1
            if lod_start - lod > 3:
                break
        painter.end()

    def draw_map(self, center_x, center_y, painter, lod, zoom, force=False):
        xy0 = geodetic2tile(*self.geo0[:2], lod)
        xmn = int(xy0[0] - center_x / zoom)
        xmx = int(xy0[0] + center_x / zoom)
        ymn = int(xy0[1] - center_y / zoom)
        ymx = int(xy0[1] + center_y / zoom)
        count = 0
        for x in range(xmn, xmx + 1):
            for y in range(ymn, ymx + 1):
                x1 = center_x + (x - xy0[0]) * zoom
                y1 = center_y + (y - xy0[1]) * zoom
                x2 = center_x + (x - xy0[0] + 1) * zoom
                y2 = center_y + (y - xy0[1] + 1) * zoom
                rect = [x1 - 1, y1 - 1, x2 - x1 + 1, y2 - y1 + 1]
                try:
                    image = self.fetcher((x, y, lod), only_cached=not force)
                except Exception as e:
                    print(e)
                    image = None
                if image is None:
                    # painter.drawRect(QRectF(*rect))
                    self.pool.apply_async(self.fetcher, ((x, y, lod),))
                    count += 1
                    continue
                try:
                    qimage = ImageQt(image)
                    painter.drawImage(QRectF(*rect), qimage)
                except Exception as e:
                    print(e)
                    self.pool.apply_async(self.fetcher, ((x, y, lod),))
                    count += 1
        if count > 0:
            return False
        return True

    def goto(self, geo):
        self.geo0 = geo
        self.update()

    def resizeEvent(self, event):
        self.update()

    def wheelEvent(self, event):
        self.zoom *= 1.5 ** (event.angleDelta().y() / 1200)
        self.update()

    def mousePressEvent(self, event):
        self.pressing = True
        self.mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.pressing:
            return
        dx = event.pos().x() - self.mouse_pos.x()
        dy = event.pos().y() - self.mouse_pos.y()
        self.mouse_pos = event.pos()
        self.xy0[0] -= dx / 256 / self.zoom
        self.xy0[1] -= dy / 256 / self.zoom
        self.update()

    def mouseReleaseEvent(self, event):
        self.pressing = False
        self.mouse_pos = None


if __name__ == '__main__':
    app = QApplication([])
    provider = providers['bing_aerial']
    widget = MapWidget(provider=provider, cache_path='cache')
    widget.show()
    app.exec()
