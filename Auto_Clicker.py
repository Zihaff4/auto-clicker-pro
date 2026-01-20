import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Controller, Button
from pynput.keyboard import Key, Listener
import threading
import time

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Pro")
        self.root.geometry("350x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#2b2b2b")
        
        # Variables
        self.is_running = False
        self.click_interval = 1.0
        self.clicking_thread = None
        self.mouse = Controller()
        self.total_clicks = 0
        
        # Style configuration
        self.setup_styles()
        
        # Create GUI
        self.create_gui()
        
        # Start keyboard listener
        self.start_keyboard_listener()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure modern styling for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#4a9eff')
        style.configure('Status.TLabel', font=('Segoe UI', 11))
        style.configure('TEntry', fieldbackground='#3c3c3c', foreground='#ffffff', font=('Segoe UI', 10))
        
        # Button styles
        style.configure('Start.TButton', font=('Segoe UI', 11, 'bold'), background='#4CAF50', foreground='white')
        style.configure('Stop.TButton', font=('Segoe UI', 11, 'bold'), background='#f44336', foreground='white')
        style.map('Start.TButton', background=[('active', '#45a049')])
        style.map('Stop.TButton', background=[('active', '#da190b')])
    
    def create_gui(self):
        """Create the modern GUI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="⚡ AutoClicker Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Interval section
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill=tk.X, pady=10)
        
        interval_label = ttk.Label(interval_frame, text="Click Interval (seconds):")
        interval_label.pack(anchor=tk.W)
        
        # Entry with validation
        self.interval_entry = ttk.Entry(interval_frame, width=25, font=('Segoe UI', 11))
        self.interval_entry.pack(fill=tk.X, pady=(5, 0))
        self.interval_entry.insert(0, "1.0")
        
        # Bind real-time validation
        self.interval_entry.bind('<KeyRelease>', self.validate_interval_realtime)
        
        # Validation message
        self.validation_label = ttk.Label(interval_frame, text="", foreground="#ffa726", font=('Segoe UI', 9))
        self.validation_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Click counter
        counter_frame = ttk.Frame(main_frame)
        counter_frame.pack(fill=tk.X, pady=10)
        
        counter_label = ttk.Label(counter_frame, text="Total Clicks:")
        counter_label.pack(anchor=tk.W)
        
        self.counter_display = ttk.Label(counter_frame, text="0", font=('Segoe UI', 20, 'bold'), foreground='#4a9eff')
        self.counter_display.pack(pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        self.start_button = tk.Button(
            button_frame, 
            text="▶ START", 
            command=self.start_clicking,
            bg='#4CAF50',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.stop_button = tk.Button(
            button_frame,
            text="■ STOP",
            command=self.stop_clicking,
            bg='#f44336',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Reset button
        reset_button = tk.Button(
            main_frame,
            text="Reset Counter",
            command=self.reset_counter,
            bg='#3c3c3c',
            fg='white',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            cursor='hand2',
            padx=10,
            pady=5
        )
        reset_button.pack(pady=5)
        
        # Status section
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=15)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="● STOPPED", 
            style='Status.TLabel',
            foreground='#f44336',
            font=('Segoe UI', 11, 'bold')
        )
        self.status_label.pack()
        
        # Hotkey info
        hotkey_frame = tk.Frame(main_frame, bg='#3c3c3c', relief=tk.RIDGE, bd=1)
        hotkey_frame.pack(fill=tk.X, pady=(10, 0))
        
        hotkey_label = ttk.Label(
            hotkey_frame, 
            text="⌨ Hotkey: Press F6 to toggle",
            font=('Segoe UI', 9),
            foreground='#9e9e9e',
            background='#3c3c3c'
        )
        hotkey_label.pack(pady=8)
    
    def validate_interval_realtime(self, event=None):
        """Real-time validation of interval input"""
        value = self.interval_entry.get()
        
        if not value:
            self.validation_label.config(text="⚠ Interval cannot be empty", foreground="#ff9800")
            return False
        
        try:
            interval = float(value)
            
            if interval < 0.01:
                self.validation_label.config(text="⚠ Minimum interval: 0.01 seconds", foreground="#ff9800")
                return False
            elif interval > 3600:
                self.validation_label.config(text="⚠ Maximum interval: 3600 seconds", foreground="#ff9800")
                return False
            else:
                self.validation_label.config(text="✓ Valid interval", foreground="#4CAF50")
                return True
                
        except ValueError:
            self.validation_label.config(text="⚠ Must be a valid number", foreground="#ff5722")
            return False
    
    def clicking_loop(self):
        """Main clicking loop with error handling"""
        try:
            while self.is_running:
                try:
                    # Perform click
                    self.mouse.click(Button.left, 1)
                    
                    # Update counter safely
                    self.total_clicks += 1
                    self.root.after(0, self.update_counter_display)
                    
                    # Sleep for interval
                    time.sleep(self.click_interval)
                    
                except Exception as e:
                    print(f"Click error: {e}")
                    # Continue clicking even if one click fails
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Critical error in clicking loop: {e}")
            self.root.after(0, self.emergency_stop)
    
    def update_counter_display(self):
        """Safely update the counter display from any thread"""
        self.counter_display.config(text=str(self.total_clicks))
    
    def start_clicking(self):
        """Start the autoclicker with full validation"""
        # Check if already running
        if self.is_running:
            messagebox.showwarning("Already Running", "AutoClicker is already running!")
            return
        
        # Validate interval
        if not self.validate_interval_realtime():
            messagebox.showerror("Invalid Input", "Please enter a valid click interval (0.01 - 3600 seconds)")
            return
        
        try:
            # Get and validate interval
            interval_value = float(self.interval_entry.get())
            
            if interval_value < 0.01:
                messagebox.showerror("Invalid Interval", "Minimum interval is 0.01 seconds for system safety.")
                return
            
            if interval_value > 3600:
                messagebox.showerror("Invalid Interval", "Maximum interval is 3600 seconds (1 hour).")
                return
            
            self.click_interval = interval_value
            
            # Start clicking
            self.is_running = True
            
            # Update UI
            self.status_label.config(text="● RUNNING", foreground="#4CAF50")
            self.start_button.config(state=tk.DISABLED, bg='#2e7d32')
            self.stop_button.config(state=tk.NORMAL, bg='#f44336')
            self.interval_entry.config(state=tk.DISABLED)
            
            # Create and start thread
            self.clicking_thread = threading.Thread(target=self.clicking_loop, daemon=True)
            self.clicking_thread.start()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the interval.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start autoclicker: {str(e)}")
            self.emergency_stop()
    
    def stop_clicking(self):
        """Stop the autoclicker safely"""
        try:
            # Set flag to stop
            self.is_running = False
            
            # Update UI
            self.status_label.config(text="● STOPPED", foreground="#f44336")
            self.start_button.config(state=tk.NORMAL, bg='#4CAF50')
            self.stop_button.config(state=tk.DISABLED, bg='#9e9e9e')
            self.interval_entry.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error while stopping: {str(e)}")
    
    def emergency_stop(self):
        """Emergency stop in case of errors"""
        self.is_running = False
        self.status_label.config(text="● ERROR - STOPPED", foreground="#ff5722")
        self.start_button.config(state=tk.NORMAL, bg='#4CAF50')
        self.stop_button.config(state=tk.DISABLED, bg='#9e9e9e')
        self.interval_entry.config(state=tk.NORMAL)
        messagebox.showerror("Error", "AutoClicker stopped due to an error. Please restart.")
    
    def reset_counter(self):
        """Reset the click counter"""
        self.total_clicks = 0
        self.counter_display.config(text="0")
    
    def on_press(self, key):
        """Keyboard hotkey handler"""
        try:
            if key == Key.f6:
                if self.is_running:
                    self.root.after(0, self.stop_clicking)
                else:
                    self.root.after(0, self.start_clicking)
        except AttributeError:
            pass
        except Exception as e:
            print(f"Hotkey error: {e}")
    
    def start_keyboard_listener(self):
        """Start the keyboard listener in background"""
        try:
            self.keyboard_listener = Listener(on_press=self.on_press)
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Failed to start keyboard listener: {e}")
            messagebox.showwarning("Warning", "Hotkey (F6) may not work properly.")
    
    def on_closing(self):
        """Handle window close event"""
        try:
            # Stop clicking if running
            self.is_running = False
            
            # Wait a moment for thread to finish
            if self.clicking_thread and self.clicking_thread.is_alive():
                time.sleep(0.2)
            
            # Stop keyboard listener
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()
            
            # Destroy window
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during closing: {e}")
            self.root.destroy()

# Main execution
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AutoClicker(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")