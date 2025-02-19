from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui

class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._attributes_container = None
        self._name_label = None
        self._root = None

    def destroy(self):
        self._root = None
        self._name_label = None

    def on_build_widgets(self):
        print("DEBUG: on_build_widgets called")

        with ui.ZStack():  # Stack elements on top of each other
            # Background rectangle, now inside a Frame to auto-resize
            with ui.Frame():
                ui.Rectangle(style={
                    "background_color": cl(0.2),
                    "border_color": cl(0.7),
                    "border_width": 4,
                    "border_radius": 4,
                })

            # VStack inside the rectangle, allowing dynamic height adjustment
            with ui.VStack(spacing=5, alignment=ui.Alignment.CENTER):
                self._name_label = ui.Label("", height=20, alignment=ui.Alignment.CENTER, style={"font_size": 20})
                self._attributes_container = ui.Frame()  # Let this auto-size


    def on_build(self):
        """Called when the model is changed and rebuilds the whole slider"""
        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN):
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    # Change update_policy to ALWAYS for debugging
                    self._widget = sc.Widget(500, 200, update_policy=sc.Widget.UpdatePolicy.ALWAYS)
                    self._widget.frame.set_build_fn(self.on_build_widgets)

    def on_model_updated(self, _):
        # if not self.model or not self.model.get_item("name"):
        #     self._root.visible = False
        #     print("DEBUG: No model or no name available.")
        #     return

        position = self.model.get_as_floats(self.model.get_item("position"))
        if self._root:
            self._root.transform = sc.Matrix44.get_translation_matrix(*position)
            self._root.visible = True

        # Update the name label
        # if self._name_label:
        #     self._name_label.text = f"Prim: {self.model.get_item('name')}"
        #     print("DEBUG: Updated name label to:", self._name_label.text)

        # Get attributes and update UI
        attributes = self.model.get_item("attributes")
        print("DEBUG: Retrieved attributes:", attributes)

        # Rebuild attribute UI dynamically using set_build_fn() on our ui.Frame
        def _build_attr_ui():
            print("DEBUG: Rebuilding attribute UI")
            with ui.VStack(spacing=5, alignment=ui.Alignment.CENTER):  # Ensure labels are aligned
                for key, value in attributes.items():
                    print("DEBUG: Adding label for", key, value)
                    ui.Label(f"{key}: {value}", height=18, alignment=ui.Alignment.CENTER, style={"font_size": 24})

        if self._attributes_container:
            self._attributes_container.set_build_fn(_build_attr_ui)
            self._attributes_container.rebuild()
        else:
            print("DEBUG: _attributes_container is None")