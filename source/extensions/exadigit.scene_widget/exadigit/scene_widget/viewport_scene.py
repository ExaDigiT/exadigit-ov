from omni.ui import scene as sc
import omni.ui as ui

from .object_info_model import ObjInfoModel
from .widget_info_manipulator import WidgetInfoManipulator

class ViewportSceneInfo():
    def __init__(self, viewportWindow, ext_id, display_widget) -> None:
        self.sceneView = None
        self.viewportWindow = viewportWindow

        with self.viewportWindow.get_frame(ext_id):
            self.sceneView = sc.SceneView()

            with self.sceneView.scene:
                if display_widget:
                    WidgetInfoManipulator(model=ObjInfoModel())
                else:
                    WidgetInfoManipulator(model=ObjInfoModel())

            self.viewportWindow.viewport_api.add_scene_view(self.sceneView)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.sceneView:
            self.sceneView.scene.clear()

            if self.viewportWindow:
                self.viewportWindow.viewport_api.remove_scene_view(self.sceneView)

        self.viewportWindow = None
        self.sceneView = None