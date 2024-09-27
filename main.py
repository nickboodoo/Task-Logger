import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
import json
import os


# A class representing a Task
class Task:
    def __init__(self, name, description, priority, logs=None):
        self.name = name
        self.description = description
        self.priority = priority
        self.logs = logs if logs else []

    def add_log(self, log, date):
        self.logs.append(f"{date}: {log}")

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'priority': self.priority,
            'logs': self.logs
        }

    @staticmethod
    def from_dict(data):
        return Task(data['name'], data['description'], data['priority'], data['logs'])


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("")
        self.tasks = {}
        self.save_file = "tasks.json"

        # Load tasks from file if it exists
        self.load_tasks()

        # Main Frame with triple padding for breathing room
        self.main_frame = tk.Frame(self.root, padx=60, pady=60)
        self.main_frame.pack(fill="both", expand=True)

        # Create the Main Menu
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Task Manager", font=("Arial", 20)).pack(pady=20)

        tk.Button(self.main_frame, text="Create Task", command=self.create_task).pack(pady=10)
        tk.Button(self.main_frame, text="View Tasks", command=self.view_tasks).pack(pady=10)
        tk.Button(self.main_frame, text="Edit Task", command=self.edit_task_menu).pack(pady=10)
        tk.Button(self.main_frame, text="Delete Task", command=self.delete_task_menu).pack(pady=10)

    def create_task(self):
        self.clear_frame()

        def submit_task():
            name = name_entry.get()
            description = desc_entry.get()
            priority = priority_combo.get()

            if name and description and priority:
                self.tasks[name] = Task(name, description, priority)
                messagebox.showinfo("Success", f"Task '{name}' created!")
                self.save_tasks()  # Save tasks after creating
                self.create_main_menu()  # Go back to main menu
            else:
                messagebox.showwarning("Error", "All fields must be filled out!")

        tk.Label(self.main_frame, text="Create Task", font=("Arial", 20)).pack(pady=10)

        tk.Label(self.main_frame, text="Task Name:").pack(pady=10)
        name_entry = tk.Entry(self.main_frame)
        name_entry.pack()

        tk.Label(self.main_frame, text="Description:").pack(pady=10)
        desc_entry = tk.Entry(self.main_frame)
        desc_entry.pack()

        tk.Label(self.main_frame, text="Priority:").pack(pady=10)
        priority_combo = ttk.Combobox(self.main_frame, values=["Low", "Medium", "High"])
        priority_combo.pack()

        tk.Button(self.main_frame, text="Create", command=submit_task).pack(pady=20)
        tk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu).pack(pady=10)

    def view_tasks(self):
        self.clear_frame()

        def view_task_details(task):
            self.clear_frame()

            # Create a frame for the task details to hold everything with a grid layout
            details_frame = tk.Frame(self.main_frame)
            details_frame.pack(padx=20, pady=20, fill="both", expand=True)

            # Left column (labels)
            tk.Label(details_frame, text="Task:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            tk.Label(details_frame, text="Description:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
            tk.Label(details_frame, text="Priority:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", padx=10, pady=10)
            tk.Label(details_frame, text="Logs:", font=("Arial", 14)).grid(row=3, column=0, sticky="nw", padx=10, pady=10)

            # Right column (content)
            tk.Label(details_frame, text=task.name, font=("Arial", 14)).grid(row=0, column=1, sticky="w", padx=10, pady=10)
            tk.Label(details_frame, text=task.description, font=("Arial", 14), wraplength=500, justify="left").grid(row=1, column=1, sticky="w", padx=10, pady=10)
            tk.Label(details_frame, text=task.priority, font=("Arial", 14)).grid(row=2, column=1, sticky="w", padx=10, pady=10)

            # Logs (if there are multiple logs, create them in a list format)
            log_frame = tk.Frame(details_frame)
            log_frame.grid(row=3, column=1, sticky="w", padx=10, pady=10)
            for log in task.logs:
                tk.Label(log_frame, text=log, font=("Arial", 12), wraplength=500, justify="left").pack(anchor="w")

            def add_log():
                log_popup = tk.Toplevel(self.root)
                log_popup.title("Add Log")
                log_popup.geometry("")  # Allow dynamic resizing
                log_frame_popup = tk.Frame(log_popup, padx=20, pady=20)
                log_frame_popup.pack(fill="both", expand=True)

                tk.Label(log_frame_popup, text="Enter log:", font=("Arial", 14)).pack(pady=10)
                log_entry = tk.Entry(log_frame_popup)
                log_entry.pack(pady=10)

                def select_date():
                    def submit_log():
                        chosen_date = cal.selection_get().strftime('%Y-%m-%d')
                        log = log_entry.get()
                        if log:
                            task.add_log(log, chosen_date)
                            self.save_tasks()  # Save tasks after adding a log
                            log_popup.destroy()
                            view_task_details(task)  # Refresh logs

                    date_popup = tk.Toplevel(log_popup)
                    date_popup.title("Select Date")
                    date_frame = tk.Frame(date_popup, padx=20, pady=20)
                    date_frame.pack(fill="both", expand=True)

                    cal = Calendar(date_frame, selectmode='day', year=2024, month=9, day=1)
                    cal.pack(pady=10)
                    tk.Button(date_frame, text="Submit Log", command=submit_log).pack(pady=10)

                tk.Button(log_frame_popup, text="Pick Date", command=select_date).pack(pady=10)

            def update_logs():
                update_popup = tk.Toplevel(self.root)
                update_popup.title("Update Logs")
                update_popup.geometry("")  # Allow dynamic resizing
                update_frame = tk.Frame(update_popup, padx=20, pady=20)
                update_frame.pack(fill="both", expand=True)

                # Display each log with Edit and Delete buttons
                for idx, log in enumerate(task.logs):
                    log_frame = tk.Frame(update_frame)
                    log_frame.pack(fill="x", pady=5)

                    # Log text
                    tk.Label(log_frame, text=log, font=("Arial", 12), wraplength=500, justify="left").pack(side="left", padx=10)

                    # Edit button
                    tk.Button(log_frame, text="Edit", command=lambda i=idx: edit_log(i)).pack(side="left", padx=5)

                    # Delete button
                    tk.Button(log_frame, text="Delete", command=lambda i=idx: delete_log(i)).pack(side="left", padx=5)

                def edit_log(index):
                    # Create popup to edit selected log
                    edit_popup = tk.Toplevel(self.root)
                    edit_popup.title("Edit Log")
                    edit_frame = tk.Frame(edit_popup, padx=20, pady=20)
                    edit_frame.pack(fill="both", expand=True)

                    tk.Label(edit_frame, text="Edit log:", font=("Arial", 14)).pack(pady=10)
                    log_entry = tk.Entry(edit_frame)
                    log_entry.insert(0, task.logs[index])  # Pre-fill with current log text
                    log_entry.pack(pady=10)

                    def save_edit():
                        new_log = log_entry.get()
                        if new_log:
                            task.logs[index] = new_log  # Update the log
                            self.save_tasks()  # Save updated log
                            edit_popup.destroy()
                            update_popup.destroy()
                            view_task_details(task)  # Refresh task details

                    tk.Button(edit_frame, text="Save", command=save_edit).pack(pady=10)

                def delete_log(index):
                    if messagebox.askyesno("Delete Log", "Are you sure you want to delete this log?"):
                        task.logs.pop(index)  # Remove the log
                        self.save_tasks()  # Save after deleting log
                        update_popup.destroy()
                        view_task_details(task)  # Refresh task details

            # Centered Buttons for "Add Log", "Update Logs", and "Back to Tasks"
            button_frame = tk.Frame(self.main_frame)
            button_frame.pack(pady=20)

            tk.Button(button_frame, text="Add Log", command=add_log).pack(side="left", padx=10)
            tk.Button(button_frame, text="Update Logs", command=update_logs).pack(side="left", padx=10)
            tk.Button(button_frame, text="Back to Tasks", command=self.view_tasks).pack(side="left", padx=10)

        tk.Label(self.main_frame, text="View Tasks", font=("Arial", 20)).pack(pady=20)

        for task_name in self.tasks:
            task_button = tk.Button(self.main_frame, text=task_name, command=lambda t=self.tasks[task_name]: view_task_details(t))
            task_button.pack(pady=5)

        tk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu).pack(pady=20)


    def edit_task_menu(self):
        self.clear_frame()

        def edit_task(task):
            def submit_edit():
                task.name = name_entry.get()
                task.description = desc_entry.get()
                task.priority = priority_combo.get()

                messagebox.showinfo("Success", f"Task '{task.name}' updated!")
                self.save_tasks()  # Save tasks after editing
                self.create_main_menu()

            self.clear_frame()

            tk.Label(self.main_frame, text=f"Edit Task: {task.name}", font=("Arial", 20)).pack(pady=10)

            tk.Label(self.main_frame, text="Task Name:").pack(pady=10)
            name_entry = tk.Entry(self.main_frame)
            name_entry.insert(0, task.name)
            name_entry.pack()

            tk.Label(self.main_frame, text="Description:").pack(pady=10)
            desc_entry = tk.Entry(self.main_frame)
            desc_entry.insert(0, task.description)
            desc_entry.pack()

            tk.Label(self.main_frame, text="Priority:").pack(pady=10)
            priority_combo = ttk.Combobox(self.main_frame, values=["Low", "Medium", "High"])
            priority_combo.set(task.priority)
            priority_combo.pack()

            tk.Button(self.main_frame, text="Update", command=submit_edit).pack(pady=20)

        tk.Label(self.main_frame, text="Edit Task", font=("Arial", 20)).pack(pady=20)

        for task_name in self.tasks:
            task_button = tk.Button(self.main_frame, text=task_name, command=lambda t=self.tasks[task_name]: edit_task(t))
            task_button.pack(pady=5)

        tk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu).pack(pady=20)

    def delete_task_menu(self):
        self.clear_frame()

        def delete_task(task_name):
            if messagebox.askyesno("Delete Task", f"Are you sure you want to delete '{task_name}'?"):
                del self.tasks[task_name]
                self.save_tasks()  # Save tasks after deletion
                messagebox.showinfo("Success", f"Task '{task_name}' deleted!")
                self.delete_task_menu()

        tk.Label(self.main_frame, text="Delete Task", font=("Arial", 20)).pack(pady=20)

        for task_name in self.tasks:
            task_button = tk.Button(self.main_frame, text=task_name, command=lambda tn=task_name: delete_task(tn))
            task_button.pack(pady=5)

        tk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu).pack(pady=20)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def save_tasks(self):
        with open(self.save_file, 'w') as file:
            json.dump([task.to_dict() for task in self.tasks.values()], file, indent=4)

    def load_tasks(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as file:
                data = json.load(file)
                for task_data in data:
                    task = Task.from_dict(task_data)
                    self.tasks[task.name] = task


# Create the Tkinter window
root = tk.Tk()
app = TaskManagerApp(root)
root.mainloop()


