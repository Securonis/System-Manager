#!/usr/bin/env python3
import sys
import os
import subprocess
import psutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTextEdit,
                           QMessageBox, QTabWidget, QFrame, QScrollArea, QDialog,
                           QGridLayout, QProgressBar, QTextBrowser)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QLinearGradient

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

class SystemMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)  # 
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 
        progress_style = """
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #42d4d4;
            }
        """
        
        # Only CPU and RAM, removed DISK
        for name in ["CPU", "RAM"]:
            item_layout = QHBoxLayout()
            label = QLabel(f"{name}:")
            label.setStyleSheet("color: white; font-weight: bold;")
            progress = QProgressBar()
            progress.setStyleSheet(progress_style)
            item_layout.addWidget(label)
            item_layout.addWidget(progress)
            layout.addLayout(item_layout)
            setattr(self, f"{name.lower()}_bar", progress)
        
        self.setLayout(layout)
        
    def update_stats(self):
        # CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_bar.setValue(int(cpu_percent))
        self.cpu_bar.setFormat(f"CPU: {cpu_percent}%")
        
        # RAM usage
        ram = psutil.virtual_memory()
        self.ram_bar.setValue(int(ram.percent))
        self.ram_bar.setFormat(f"RAM: {ram.percent}%")
        
        # Disk usage indicator removed

class SystemManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Securonis Linux System Manager")
        self.setGeometry(100, 100, 800, 600)
        
        # main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Logo
        self.logo_label = QLabel()
        logo_pixmap = QPixmap("/usr/share/icons/securonis/newlogo.png")
        if not logo_pixmap.isNull():
            self.logo_pixmap = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.logo_label)
        
        # 
        self.system_monitor = SystemMonitor()
        left_layout.addWidget(self.system_monitor)
        
      
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        # 
        button_style = """
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
            QPushButton:disabled {
                background-color: #1d1d1d;
                color: #666666;
            }
        """
        
        # Menu - removed Disk Info, Packages, Memory, CPU Info, Drivers
        menu_buttons = [
            ("Update System", lambda: self.safe_execute(self.update_system)),
            ("Firmware Update", lambda: self.safe_execute(self.update_firmware)),
            ("System Info", lambda: self.safe_execute(self.system_info)),
            ("Internet Test", lambda: self.safe_execute(self.internet_test)),
            ("Network", lambda: self.safe_execute(self.network_connections)),
            ("Clear Cache", lambda: self.safe_execute(self.clear_cache)),
            ("About", lambda: self.safe_execute(self.show_about)),
            ("Help", lambda: self.safe_execute(self.show_help)),
            ("Exit", self.close)
        ]
        
        self.buttons = {}
        
     
        for text, callback in menu_buttons:
            button = ModernButton(text)
            button.clicked.connect(callback)
            button_layout.addWidget(button)
            self.buttons[text] = button
        
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # 
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 
        logs_label = QLabel("Logs:")
        logs_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; padding: 5px;")
        right_layout.addWidget(logs_label)
        
        # 
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #42d4d4; font-weight: bold; font-size: 12px; padding: 5px;")
        right_layout.addWidget(self.status_label)
        
        # frame
        output_frame = QFrame()
        output_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #3d3d3d; border-radius: 4px;")
        output_frame_layout = QVBoxLayout(output_frame)
        output_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.6;
                selection-background-color: #3d3d3d;
                selection-color: #ffffff;
            }
            QTextEdit:focus { border: none; }
            QScrollBar:vertical {
                border: none;
                background-color: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background-color: #4d4d4d; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        output_frame_layout.addWidget(self.output_text)
        
        right_layout.addWidget(output_frame)
        main_layout.addWidget(right_panel)
        
        # theme dark
        self.set_dark_theme()
        
    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))         
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(12, 12, 12))           
        palette.setColor(QPalette.AlternateBase, QColor(24, 24, 24))  
        palette.setColor(QPalette.ToolTipBase, QColor(18, 18, 18))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(32, 32, 32))       
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(0, 120, 212))     
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        
    def safe_execute(self, function):
        """Error handling wrapper for button functions"""
        try:
            function()
        except Exception as e:
            self.status_label.setText("Error occurred!")
            self.output_text.clear()
            self.output_text.append(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            import traceback
            self.output_text.append("\nDetailed error info:")
            self.output_text.append(traceback.format_exc())
            
    def run_command(self, command, button_text=None):
        try:
            # 
            if button_text and button_text in self.buttons:
                self.buttons[button_text].setEnabled(False)
            
            # 
            self.output_text.setText("Processing...")
            QApplication.processEvents()  # Update interface
            
            # run the command
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # update 
            self.output_text.setText(result.stdout)
            if result.stderr:
                self.output_text.append("\nErrors:\n" + result.stderr)
            
        except Exception as e:
            self.output_text.setText(f"Error: {str(e)}")
        finally:
            # 
            if button_text and button_text in self.buttons:
                self.buttons[button_text].setEnabled(True)
            
    def update_system(self):
        self.status_label.setText("Updating system...")
        self.output_text.clear()
        self.output_text.append("Starting system update process...")
        
        try:
            # Update repositories
            self.output_text.append("\n[1/2] Updating package repositories...")
            update_process = subprocess.Popen(['sudo', 'apt-get', 'update'], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True)
            
            # Process output in batches to reduce UI updates
            output_buffer = []
            while True:
                output = update_process.stdout.readline()
                if output == '' and update_process.poll() is not None:
                    break
                if output:
                    output_buffer.append(output.strip())
                    # Update UI less frequently to improve performance
                    if len(output_buffer) >= 5:
                        self.output_text.append("\n".join(output_buffer))
                        output_buffer = []
                        QApplication.processEvents()
            
            # Display any remaining output
            if output_buffer:
                self.output_text.append("\n".join(output_buffer))
            
            # Upgrade packages
            self.output_text.append("\n[2/2] Upgrading packages...")
            upgrade_process = subprocess.Popen(['sudo', 'apt-get', 'upgrade', '-y'],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            universal_newlines=True)
            
            # Process output in batches to reduce UI updates
            output_buffer = []
            while True:
                output = upgrade_process.stdout.readline()
                if output == '' and upgrade_process.poll() is not None:
                    break
                if output:
                    output_buffer.append(output.strip())
                    # Update UI less frequently to improve performance
                    if len(output_buffer) >= 5:
                        self.output_text.append("\n".join(output_buffer))
                        output_buffer = []
                        QApplication.processEvents()
            
            # Display any remaining output
            if output_buffer:
                self.output_text.append("\n".join(output_buffer))
                
            # Only show the success message at the end of the entire process
            self.status_label.setText("System update completed!")
            QMessageBox.information(self, "Success", "System has been successfully updated!")
            
        except Exception as e:
            self.status_label.setText("Error occurred!")
            self.output_text.append(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while updating the system: {str(e)}")
        
    def system_info(self):
        self.output_text.clear()
        try:
            # Kernel version
            kernel = subprocess.check_output(['uname', '-r']).decode().strip()
            self.output_text.append(f"Kernel: {kernel}")
            
            # Read from /etc/os-release instead of lsb_release
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    os_release = f.readlines()
                
                os_info = {}
                for line in os_release:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        # Remove quotes if present
                        os_info[key] = value.strip('"')
                
                self.output_text.append("\nOperating System:")
                if 'NAME' in os_info:
                    self.output_text.append(f"Name: {os_info['NAME']}")
                if 'VERSION' in os_info:
                    self.output_text.append(f"Version: {os_info['VERSION']}")
                if 'ID' in os_info:
                    self.output_text.append(f"ID: {os_info['ID']}")
                if 'PRETTY_NAME' in os_info:
                    self.output_text.append(f"Description: {os_info['PRETTY_NAME']}")
            else:
                # Fallback to lsb_release if os-release doesn't exist
                os_info = subprocess.check_output(['lsb_release', '-a']).decode()
                self.output_text.append("\nOperating System Information:")
                self.output_text.append(os_info)
                
            # Additional hardware info
            self.output_text.append("\nCPU Information:")
            cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -1", shell=True).decode().strip()
            self.output_text.append(cpu_info)
            
            # Memory information
            mem_info = psutil.virtual_memory()
            self.output_text.append(f"\nMemory Total: {self.format_bytes(mem_info.total)}")
            self.output_text.append(f"Memory Available: {self.format_bytes(mem_info.available)}")
            
        except Exception as e:
            self.output_text.append(f"Error: {str(e)}")
        

    def internet_test(self):
        try:
            # Disable button while testing
            if "Internet Test" in self.buttons:
                self.buttons["Internet Test"].setEnabled(False)
            
            # Show testing message
            self.output_text.setText("Testing internet connection...")
            QApplication.processEvents()
            
            # Run ping command with appropriate parameters for platform
            if sys.platform == 'win32':
                result = subprocess.run("ping -n 1 google.com", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run("ping -c 1 google.com", shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.output_text.setText("Internet connection is working!")
            else:
                self.output_text.setText("No internet connection!")
            
        except Exception as e:
            self.output_text.setText(f"Error checking internet connection: {str(e)}")
        finally:
            # Re-enable button
            if "Internet Test" in self.buttons:
                self.buttons["Internet Test"].setEnabled(True)
        
    def list_packages(self):
        self.run_command("dpkg -l", "Packages")
        
    def memory_usage(self):
        self.run_command("free -h", "Memory")
        
    def cpu_info(self):
        self.run_command("lscpu", "CPU Info")
        
    def network_connections(self):
        self.run_command("ip a", "Network")
        
    def clear_cache(self):
        self.run_command("sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches && sudo apt clean && sudo apt autoremove -y", "Clear Cache")
        
    def check_drivers(self):
        try:
            self.run_command("sudo lshw -C display", "Drivers")
        except Exception as e:
            self.output_text.setText(f"Error checking drivers: {str(e)}")
    def show_about(self):
        try:
            about_dialog = QDialog(self)
            about_dialog.setWindowTitle("About")
            about_dialog.setFixedSize(400, 280)
            about_dialog.setStyleSheet("background-color: #121212; color: white;")
            
            about_dialog.setWindowFlags(about_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            
            layout = QVBoxLayout()
            
            icon_label = QLabel()
            icon = QPixmap("/usr/share/icons/securonis/newlogo.png")
            if not icon.isNull():
                icon_label.setPixmap(icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignCenter)
            
            title = QLabel("Securonis Linux System Manager")
            title.setStyleSheet("font-weight: bold; font-size: 16px; color: white; margin-top: 10px;")
            title.setAlignment(Qt.AlignCenter)
            
            info = QLabel("Version: 2.5\n\nDeveloper: root0emir\n\n" +
                         "Website: https://securonis.github.io\n" +
                         "Github: https://github.com/securonis/system-manager")
            info.setStyleSheet("color: white; margin: 10px;")
            info.setAlignment(Qt.AlignCenter)
            
            close_button = QPushButton("OK")
            close_button.clicked.connect(about_dialog.accept)
            close_button.setFixedWidth(100)
            close_button.setStyleSheet(
                "QPushButton {background-color: #1a1a1a; color: white; border: 1px solid #333; padding: 5px;}"
                "QPushButton:hover {background-color: #292929;}"
                "QPushButton:pressed {background-color: #0f0f0f;}"
            )
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            button_layout.addStretch()
            
         
            layout.addWidget(icon_label)
            layout.addWidget(title)
            layout.addWidget(info)
            layout.addStretch()
            layout.addLayout(button_layout)
            
            about_dialog.setLayout(layout)
            about_dialog.exec_()
            
        except Exception as e:
            self.status_label.setText(f"About dialog error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def show_help(self):
        try:
            help_dialog = QDialog(self)
            help_dialog.setWindowTitle("Help")
            help_dialog.setFixedSize(400, 300)
            help_dialog.setStyleSheet("background-color: #121212; color: white;")
            
            help_dialog.setWindowFlags(help_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            
            layout = QVBoxLayout()
            
            icon_label = QLabel()
            icon = QPixmap("icons/info.png")
            if not icon.isNull():
                icon_label.setPixmap(icon.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setStyleSheet("font-size: 40px; color: white;")
            icon_label.setAlignment(Qt.AlignCenter)
            
            title_label = QLabel("Securonis Linux System Manager:")
            title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
            title_label.setAlignment(Qt.AlignCenter)
            
            description = QLabel("This application provides the following system management tools:")
            description.setWordWrap(True)
            description.setStyleSheet("color: white;")
            
            features = QLabel(
                "1. Update System: Updates system packages\n"
                "2. Firmware Update: Updates system firmware\n"
                "3. System Info: Shows operating system and kernel information\n"
                "4. Internet Test: Tests your internet connection\n"
                "5. Network: Displays network interfaces\n"
                "6. Clear Cache: Cleans system cache\n"
                "7. About: Shows application information\n"
                "8. Help: Displays this help message\n"
                "9. Exit: Closes the application"
            )
            features.setWordWrap(True)
            features.setStyleSheet("color: white;")
            
            close_button = QPushButton("OK")
            close_button.clicked.connect(help_dialog.accept)
            close_button.setFixedWidth(100)
            close_button.setStyleSheet(
                "QPushButton {background-color: #1a1a1a; color: white; border: 1px solid #333; padding: 5px;}"
                "QPushButton:hover {background-color: #292929;}"
                "QPushButton:pressed {background-color: #0f0f0f;}"
            )
            
            layout.addWidget(icon_label)
            layout.addWidget(title_label)
            layout.addWidget(description)
            layout.addWidget(features)
            layout.addStretch()
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            
            help_dialog.setLayout(layout)
            help_dialog.exec_()
            
        except Exception as e:
            self.status_label.setText(f"Help dialog error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        
    def update_firmware(self):
        self.status_label.setText("Updating firmware...")
        self.output_text.clear()
        
        try:
            update_process = subprocess.Popen(
                'sudo apt update && sudo apt install -y fwupd && sudo fwupdmgr refresh --force && sudo fwupdmgr get-updates && sudo fwupdmgr update -y',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while True:
                output = update_process.stdout.readline()
                if output == '' and update_process.poll() is not None:
                    break
                if output:
                    self.output_text.append(output.strip())
                    QApplication.processEvents()
                
            self.status_label.setText("Firmware update completed")
        except Exception as e:
            self.output_text.append(f"Error updating firmware: {str(e)}")
            self.status_label.setText("Firmware update failed")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SystemManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
