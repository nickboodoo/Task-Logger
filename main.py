import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from tkcalendar import Calendar
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

        # Set up the style for buttons and labels
        style = ttk.Style()
        style.configure("TButton", foreground="white")
        style.configure("TLabel", foreground="white")

        # Define the styles for titles and content
        style.configure("Title.TLabel", font=("Arial", 20))  # Title font size 20
        style.configure("Content.TButton", font=("Arial", 16))  # Content button font size 16
        style.configure("Content.TLabel", font=("Arial", 16))  # Content label font size 16

        # Load tasks from file if it exists
        self.load_tasks()

        # Main Frame with triple padding for breathing room
        self.main_frame = ttk.Frame(self.root, padding=60)
        self.main_frame.pack(fill="both", expand=True)

        # Create the Main Menu
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_frame()

        ttk.Label(self.main_frame, text="Nick's Task Manager", style="Title.TLabel").pack(pady=20)

        ttk.Button(self.main_frame, text="Create Task", command=self.create_task, style="Content.TButton").pack(pady=10)
        ttk.Button(self.main_frame, text="View Tasks", command=self.view_tasks, style="Content.TButton").pack(pady=10)
        ttk.Button(self.main_frame, text="Edit Task", command=self.edit_task_menu, style="Content.TButton").pack(pady=10)
        ttk.Button(self.main_frame, text="Delete Task", command=self.delete_task_menu, style="Content.TButton").pack(pady=10)

    def create_task(self):
        self.clear_frame()

        def submit_task():
            name = name_entry.get()
            description = desc_entry.get()
            priority = priority_combo.get()

            if name and description and priority:
                self.tasks[name] = Task(name, description, priority)
                self.sort_tasks_by_priority()  # Sort tasks by priority
                messagebox.showinfo("Success", f"Task '{name}' created!")
                self.save_tasks()  # Save tasks after creating
                self.create_main_menu()  # Go back to main menu
            else:
                messagebox.showwarning("Error", "All fields must be filled out!")

        ttk.Label(self.main_frame, text="Create Task", style="Title.TLabel").pack(pady=10)

        ttk.Label(self.main_frame, text="Task Name:", style="Content.TLabel").pack(pady=10)
        name_entry = ttk.Entry(self.main_frame)
        name_entry.pack()

        ttk.Label(self.main_frame, text="Description:", style="Content.TLabel").pack(pady=10)
        desc_entry = ttk.Entry(self.main_frame)
        desc_entry.pack()

        ttk.Label(self.main_frame, text="Priority:", style="Content.TLabel").pack(pady=10)
        priority_combo = ttk.Combobox(self.main_frame, values=["Low", "Medium", "High"], state="readonly")
        priority_combo.pack()

        ttk.Button(self.main_frame, text="Create", command=submit_task, style="Content.TButton").pack(pady=20)
        ttk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu, style="Content.TButton").pack(pady=10)

    def view_tasks(self):
        self.clear_frame()

        def view_task_details(task):
            self.clear_frame()

            details_frame = ttk.Frame(self.main_frame)
            details_frame.pack(padx=20, pady=20, fill="both", expand=True)

            ttk.Label(details_frame, text="Task:", style="Content.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            ttk.Label(details_frame, text="Description:", style="Content.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=10)
            ttk.Label(details_frame, text="Priority:", style="Content.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=10)
            ttk.Label(details_frame, text="Logs:", style="Content.TLabel").grid(row=3, column=0, sticky="nw", padx=10, pady=10)

            ttk.Label(details_frame, text=task.name, style="Content.TLabel").grid(row=0, column=1, sticky="w", padx=10, pady=10)
            ttk.Label(details_frame, text=task.description, style="Content.TLabel", wraplength=500, justify="left").grid(row=1, column=1, sticky="w", padx=10, pady=10)
            ttk.Label(details_frame, text=task.priority, style="Content.TLabel").grid(row=2, column=1, sticky="w", padx=10, pady=10)

            log_frame = ttk.Frame(details_frame)
            log_frame.grid(row=3, column=1, sticky="w", padx=10, pady=10)
            for log in task.logs:
                ttk.Label(log_frame, text=log, style="Content.TLabel", wraplength=500, justify="left").pack(anchor="w")

            def add_log():
                log_popup = tk.Toplevel(self.root)
                log_popup.title("Add Log")
                log_popup.geometry("")  # Allow dynamic resizing
                log_frame_popup = ttk.Frame(log_popup, padding=20)
                log_frame_popup.pack(fill="both", expand=True)

                ttk.Label(log_frame_popup, text="Enter log:", style="Content.TLabel").pack(pady=10)
                log_entry = ttk.Entry(log_frame_popup)
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
                    date_frame = ttk.Frame(date_popup, padding=20)
                    date_frame.pack(fill="both", expand=True)

                    cal = Calendar(date_frame, selectmode='day', year=2024, month=9, day=1)
                    cal.pack(pady=10)
                    ttk.Button(date_frame, text="Submit Log", command=submit_log, style="Content.TButton").pack(pady=10)

                ttk.Button(log_frame_popup, text="Pick Date", command=select_date, style="Content.TButton").pack(pady=10)

            def update_logs():
                update_popup = tk.Toplevel(self.root)
                update_popup.title("Update Logs")
                update_popup.geometry("")  # Allow dynamic resizing
                update_frame = ttk.Frame(update_popup, padding=20)
                update_frame.pack(fill="both", expand=True)

                for idx, log in enumerate(task.logs):
                    log_frame = ttk.Frame(update_frame)
                    log_frame.pack(fill="x", pady=5)

                    ttk.Label(log_frame, text=log, style="Content.TLabel", wraplength=500, justify="left").pack(side="left", padx=10)
                    ttk.Button(log_frame, text="Edit", command=lambda i=idx: edit_log(i), style="Content.TButton").pack(side="left", padx=5)
                    ttk.Button(log_frame, text="Delete", command=lambda i=idx: delete_log(i), style="Content.TButton").pack(side="left", padx=5)

                def edit_log(index):
                    edit_popup = tk.Toplevel(self.root)
                    edit_popup.title("Edit Log")
                    edit_frame = ttk.Frame(edit_popup, padding=20)
                    edit_frame.pack(fill="both", expand=True)

                    ttk.Label(edit_frame, text="Edit log:", style="Content.TLabel").pack(pady=10)
                    log_entry = ttk.Entry(edit_frame)
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

                    ttk.Button(edit_frame, text="Save", command=save_edit, style="Content.TButton").pack(pady=10)

                def delete_log(index):
                    if messagebox.askyesno("Delete Log", "Are you sure you want to delete this log?"):
                        task.logs.pop(index)  # Remove the log
                        self.save_tasks()  # Save after deleting log
                        update_popup.destroy()
                        view_task_details(task)  # Refresh task details

            ttk.Button(self.main_frame, text="Add Log", command=add_log, style="Content.TButton").pack(side="left", padx=10)
            ttk.Button(self.main_frame, text="Update Logs", command=update_logs, style="Content.TButton").pack(side="left", padx=10)
            ttk.Button(self.main_frame, text="Back to Tasks", command=self.view_tasks, style="Content.TButton").pack(side="left", padx=10)

        sorted_tasks = self.sort_tasks_by_priority()

        ttk.Label(self.main_frame, text="View Tasks", style="Title.TLabel").pack(pady=20)

        for task in sorted_tasks:
            task_button_text = f"{task.name} (Priority: {task.priority})"
            ttk.Button(self.main_frame, text=task_button_text, command=lambda t=task: view_task_details(t), style="Content.TButton").pack(pady=5)

        ttk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu, style="Content.TButton").pack(pady=20)

    def edit_task_menu(self):
        self.clear_frame()

        ttk.Label(self.main_frame, text="Edit Task", style="Title.TLabel").pack(pady=20)

        # Create a button for each task
        for task_name, task in self.tasks.items():
            ttk.Button(self.main_frame, text=task_name, command=lambda t=task: edit_task(t), style="Content.TButton").pack(pady=5)

        ttk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu, style="Content.TButton").pack(pady=20)

        def edit_task(task):
            def submit_edit():
                new_name = name_entry.get()
                task.description = desc_entry.get()
                task.priority = priority_combo.get()

                # Handle the case if the user changes the task name
                if new_name != task.name:
                    # Update the dictionary key if the task name is changed
                    self.tasks[new_name] = self.tasks.pop(task.name)
                    task.name = new_name

                messagebox.showinfo("Success", f"Task '{task.name}' updated!")
                self.sort_tasks_by_priority()  # Re-sort tasks after editing
                self.save_tasks()  # Save tasks after editing
                self.create_main_menu()

            self.clear_frame()

            ttk.Label(self.main_frame, text=f"Edit Task: {task.name}", style="Title.TLabel").pack(pady=10)

            ttk.Label(self.main_frame, text="Task Name:", style="Content.TLabel").pack(pady=10)
            name_entry = ttk.Entry(self.main_frame)
            name_entry.insert(0, task.name)
            name_entry.pack()

            ttk.Label(self.main_frame, text="Description:", style="Content.TLabel").pack(pady=10)
            desc_entry = ttk.Entry(self.main_frame)
            desc_entry.insert(0, task.description)
            desc_entry.pack()

            ttk.Label(self.main_frame, text="Priority:", style="Content.TLabel").pack(pady=10)
            priority_combo = ttk.Combobox(self.main_frame, values=["Low", "Medium", "High"], state="readonly")
            priority_combo.set(task.priority)
            priority_combo.pack()

            ttk.Button(self.main_frame, text="Update", command=submit_edit, style="Content.TButton").pack(pady=20)
            ttk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu, style="Content.TButton").pack(pady=10)


    def delete_task_menu(self):
        self.clear_frame()

        def delete_task(task_name):
            if messagebox.askyesno("Delete Task", f"Are you sure you want to delete '{task_name}'?"):
                del self.tasks[task_name]
                self.sort_tasks_by_priority()  # Re-sort tasks after deletion
                self.save_tasks()  # Save tasks after deletion
                messagebox.showinfo("Success", f"Task '{task_name}' deleted!")
                self.delete_task_menu()

        ttk.Label(self.main_frame, text="Delete Task", style="Title.TLabel").pack(pady=20)

        for task_name in self.tasks:
            ttk.Button(self.main_frame, text=task_name, command=lambda tn=task_name: delete_task(tn), style="Content.TButton").pack(pady=5)

        ttk.Button(self.main_frame, text="Back to Menu", command=self.create_main_menu, style="Content.TButton").pack(pady=20)

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

    def sort_tasks_by_priority(self):
        # Custom sorting by priority: High > Medium > Low
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        sorted_tasks = sorted(self.tasks.values(), key=lambda task: priority_order[task.priority.title()])
        return sorted_tasks


if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = TaskManagerApp(root)
    root.mainloop()

