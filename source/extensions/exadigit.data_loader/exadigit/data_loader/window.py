import omni.ui as ui


class DataLoaderWindow(ui.Window):
    """A simple 2-tab window showing 'Propagation', 'Run Simulation', and 'Simulation List' tabs."""
    def __init__(self, title, extension, **kwargs):
        super().__init__(title, **kwargs)
        self._extension = extension  # We'll call extension methods from inside the tab content

        # Our tabs: (tab_label, method_that_builds_the_tab_ui)
        self._tabs = [
            ("Propagation", self._build_propagation_tab),
            ("Run Simulation", self._build_run_simulation_tab),
            ("Simulation List", self._build_simulation_list_tab)
        ]
        self._active_tab = "Propagation"

        # Called each time the window is built or rebuilt
        self.frame.set_build_fn(self._build_ui)

    def _build_ui(self):
        """Main UI, draws the tab bar + whichever tab is active."""
        with ui.VStack(spacing=5):
            # Build a row of clickable tab labels
            self._build_tab_bar()

            # Show only the active tab’s content
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

    ### TAB CONTENT BUILDERS ###
    def _build_propagation_tab(self):
        """First tab: 'Scene Management' with Refresh and Propagate buttons."""
        with ui.VStack(spacing=5):
            with ui.VStack(spacing=10):
                ui.Button("Generate Lookup Map", width=140,
                          clicked_fn=self._extension.generate_lookup)
                ui.Button("Propagate Data", width=140,
                          clicked_fn=self._extension.propagate_data)

    def _build_run_simulation_tab(self):
        """Creates the 'Run Simulation' panel with user-configurable fields."""

        self.simulation_params = {
            "start": "2025-03-10T12:00:00Z",  # Default values, user can change them
            "end": "2025-03-10T14:00:00Z",
            "system": "frontier",
            "scheduler": {
                "enabled": True,
                "jobs_mode": "random",
                "seed": 12345,
                "num_jobs": 10
            },
            "cooling": {
                "enabled": False
            }
        }

        def update_param(param_path, value):
            """Helper function to update simulation parameters dynamically."""
            keys = param_path.split(".")
            param_ref = self.simulation_params
            for key in keys[:-1]:
                param_ref = param_ref[key]
            param_ref[keys[-1]] = value
            print(f"[DEBUG] Updated {param_path} to {value}")  # Debugging line

        with ui.ScrollingFrame(height=400):
            with ui.VStack(spacing=5):
                # Start Time Input
                ui.Label("Start Time (ISO 8601)")
                self.start_input = ui.StringField()
                self.start_input.model.set_value(self.simulation_params["start"])
                self.start_input.model.add_value_changed_fn(lambda m: update_param("start", m.get_value_as_string()))

                # End Time Input
                ui.Label("End Time (ISO 8601)")
                self.end_input = ui.StringField()
                self.end_input.model.set_value(self.simulation_params["end"])
                self.end_input.model.add_value_changed_fn(lambda m: update_param("end", m.get_value_as_string()))

                # Define available systems
                systems = ["frontier", "fugaku", "lassen", "marconi100"]

                # System Selection Dropdown
                ui.Label("Select System")
                self.system_dropdown = ui.ComboBox(0, *systems)

                # Correctly track selection changes
                self.system_dropdown.model.get_item_value_model().add_value_changed_fn(
                    lambda m: update_param("system", systems[m.as_int] if m.as_int is not None else "frontier")
                )

                # Jobs Mode Selection Dropdown
                ui.Label("Jobs Mode")
                self.jobs_mode_dropdown = ui.ComboBox(0, "replay", "custom", "random", "test")
                self.jobs_mode_dropdown.model.add_item_changed_fn(lambda m, idx: update_param("scheduler.jobs_mode", self.jobs_mode_dropdown.model.get_item_value_model(idx).as_string()))

                # Random Seed (for random jobs mode)
                ui.Label("Random Seed")
                self.seed_input = ui.IntField()
                self.seed_input.model.set_value(self.simulation_params["scheduler"]["seed"])
                self.seed_input.model.add_value_changed_fn(lambda m: update_param("scheduler.seed", m.get_value_as_int()))

                # Number of Jobs (for random jobs mode)
                ui.Label("Number of Jobs")
                self.num_jobs_input = ui.IntField()
                self.num_jobs_input.model.set_value(self.simulation_params["scheduler"]["num_jobs"])
                self.num_jobs_input.model.add_value_changed_fn(lambda m: update_param("scheduler.num_jobs", m.get_value_as_int()))

                # Cooling Enabled Toggle
                ui.Label("Enable Cooling")
                self.cooling_toggle = ui.CheckBox()
                self.cooling_toggle.model.set_value(self.simulation_params["cooling"]["enabled"])
                self.cooling_toggle.model.add_value_changed_fn(lambda m: update_param("cooling.enabled", m.get_value_as_bool()))

                # Run Simulation Button
                ui.Button("Run", width=140, clicked_fn=lambda: self._extension.run_simulation(self.simulation_params))

    def _build_simulation_list_tab(self):
        """Creates the 'Simulation List' panel with selectable simulations."""

        with ui.VStack(spacing=5):
            if not self._extension.sim_list:
                ui.Label("Please start simulationserver container.", height=30, style={"color": "red"})
            else:
                # Column headers
                with ui.HStack(spacing=10):
                    ui.Label("Simulation ID", width=150)
                    ui.Label("System", width=100)
                    ui.Label("Start", width=150)
                    ui.Spacer(width=10)  # Space for "Select" button
                # Scrollable list of simulations
                with ui.ScrollingFrame(height=300):
                    with ui.VStack(spacing=5):
                        for sim in self._extension.sim_list:
                            with ui.HStack(spacing=10):
                                ui.Label(sim.id[:15] + "...", width=150)  # Shorten ID
                                ui.Label(sim.system, width=100)
                                ui.Label(sim.start, width=150)

                                # Select button
                                def select_simulation(sim=sim):
                                    self._extension.selected_sim = sim
                                    print("[window] Selected Simulation: " + str(self._extension.selected_sim))
                                    self.frame.rebuild()  # Rebuild to reflect selection

                                # Highlight if selected
                                is_selected = self._extension.selected_sim and self._extension.selected_sim.id == sim.id
                                btn_label = "Selected" if is_selected else "Select"
                                btn_style = {"color": 0xFF00FF00} if is_selected else {}

                                ui.Button(btn_label, width=80, clicked_fn=select_simulation, style=btn_style)
