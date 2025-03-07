import omni.ui as ui

class DataLoaderWindow(ui.Window):
    """A simple 2-tab window showing 'Scene Management' and 'RAPS' tabs."""

    def __init__(self, title, extension, **kwargs):
        super().__init__(title, **kwargs)
        self._extension = extension  # We'll call extension methods from inside the tab content

        # Our tabs: (tab_label, method_that_builds_the_tab_ui)
        self._tabs = [
            ("Scene Management", self._build_scene_mgmt_tab),
            ("RAPS", self._build_raps_tab),
        ]
        self._active_tab = "Scene Management"

        # Called each time the window is built or rebuilt
        self.frame.set_build_fn(self._build_ui)

    def _build_ui(self):
        """Main UI, draws the tab bar + whichever tab is active."""
        with ui.VStack(spacing=5):
            # 1) Build a row of clickable tab labels
            self._build_tab_bar()

            # 2) Show only the active tab’s content
            for (tab_name, builder_fn) in self._tabs:
                if tab_name == self._active_tab:
                    builder_fn()  # call the function that actually builds the tab content
                    break

            # Some spacing at the bottom
            ui.Spacer(height=10)

    def _build_tab_bar(self):
        """A simple horizontal bar with clickable labels for each tab."""
        with ui.HStack(height=30, spacing=10):
            for (tab_name, _) in self._tabs:
                label = ui.Label(tab_name)

                # Style: highlight the active tab; grayer for inactive
                if tab_name == self._active_tab:
                    label.set_style({"color": 0xFF00FFFF, "font_size": 16})
                else:
                    label.set_style({"color": 0xFFCCCCCC, "font_size": 14})

                # When clicked, switch active tab and rebuild
                def on_click(x, y, b, m, name=tab_name):
                    self._active_tab = name
                    self.frame.rebuild()

                label.set_mouse_pressed_fn(on_click)

    #
    # TAB CONTENT BUILDERS
    #
    def _build_scene_mgmt_tab(self):
        """First tab: 'Scene Management' with Refresh and Propagate buttons."""
        with ui.VStack(spacing=5):
            ui.Label("Scene Management", height=20, style={"font_size": 16})
            with ui.HStack(spacing=10):
                ui.Button("Refresh Scene", width=140,
                          clicked_fn=self._extension.refresh_scene)
                ui.Button("Propagate Data", width=140,
                          clicked_fn=self._extension.propagate_data)

    def _build_raps_tab(self):
        """Second tab: 'RAPS' with a 'Run Simulation' button."""
        with ui.VStack(spacing=5):
            ui.Label("RAPS Panel", height=20, style={"font_size": 16})
            with ui.HStack(spacing=10):
                ui.Button("Run Simulation", width=140,
                          clicked_fn=self._extension.run_simulation_api_call)