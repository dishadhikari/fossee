import os
import subprocess
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QWidget,
)


class SimulationRunner:
    """Handles execution of an OpenModelica simulation."""

    def __init__(self, executable):
        self.executable = executable

    def run(self, start_time, stop_time):
        """Run the OpenModelica executable."""

        command = [
            self.executable,
            f"-startTime={start_time}",
            f"-stopTime={stop_time}",
        ]

        # OpenModelica runtime location
        env = os.environ.copy()
        openmodelica_bin = (
            r"C:\Program Files\OpenModelica1.27.0-64bit\bin"
        )
        env["PATH"] = openmodelica_bin + os.pathsep + env["PATH"]

        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(self.executable),
            env=env,
        )


class SimulationApp(QMainWindow):
    """Main GUI application for running OpenModelica simulations."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenModelica Simulation Runner")
        self.setMinimumSize(650, 500)

        self.create_ui()

    def create_ui(self):
        """Create and arrange all GUI components."""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QFormLayout()
        central_widget.setLayout(layout)

        # Application field
        self.application_input = QLineEdit()

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_application)

        layout.addRow(
            QLabel("Application:"),
            self.application_input,
        )
        layout.addRow("", browse_button)

        # Start time
        self.start_time_input = QLineEdit("0")
        layout.addRow(
            QLabel("Start Time:"),
            self.start_time_input,
        )

        # Stop time
        self.stop_time_input = QLineEdit("1")
        layout.addRow(
            QLabel("Stop Time:"),
            self.stop_time_input,
        )

        # Run button
        run_button = QPushButton("Run Simulation")
        run_button.clicked.connect(self.run_simulation)
        layout.addRow("", run_button)

        # Status
        self.status_label = QLabel("Status: Ready")
        layout.addRow(self.status_label)

        # Output box
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addRow(QLabel("Simulation Output:"))
        layout.addRow(self.output_box)

    def browse_application(self):
        """Allow the user to select the OpenModelica executable."""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenModelica Executable",
            "",
            "Executable Files (*.exe)",
        )

        if file_path:
            self.application_input.setText(file_path)

    def validate_inputs(self):
        """Validate application path and simulation times."""

        executable = self.application_input.text().strip()

        if not executable:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please select an application.",
            )
            return None

        if not os.path.isfile(executable):
            QMessageBox.warning(
                self,
                "Input Error",
                "The selected application does not exist.",
            )
            return None

        try:
            start_time = int(self.start_time_input.text())
            stop_time = int(self.stop_time_input.text())
        except ValueError:
            QMessageBox.warning(
                self,
                "Input Error",
                "Start time and stop time must be integers.",
            )
            return None

        # Required condition from the screening task
        if not (0 <= start_time < stop_time < 5):
            QMessageBox.warning(
                self,
                "Input Error",
                "Please ensure: 0 <= start time < stop time < 5.",
            )
            return None

        return executable, start_time, stop_time

    def run_simulation(self):
        """Validate inputs and execute the simulation."""

        inputs = self.validate_inputs()

        if inputs is None:
            return

        executable, start_time, stop_time = inputs

        self.status_label.setText("Status: Running...")
        self.output_box.clear()

        try:
            runner = SimulationRunner(executable)

            result = runner.run(
                start_time,
                stop_time,
            )

            output = result.stdout

            if result.stderr:
                output += "\n" + result.stderr

            self.output_box.setPlainText(output)

            if result.returncode == 0:
                self.status_label.setText(
                    "Status: Simulation completed successfully."
                )
            else:
                self.status_label.setText(
                    f"Status: Simulation failed "
                    f"(return code {result.returncode})."
                )

        except Exception as error:
            self.status_label.setText("Status: Error")
            self.output_box.setPlainText(str(error))

            QMessageBox.critical(
                self,
                "Simulation Error",
                str(error),
            )


def main():
    """Application entry point."""

    app = QApplication(sys.argv)

    window = SimulationApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()