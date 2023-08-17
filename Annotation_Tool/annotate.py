import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageGrab
import json
from tkinter import ttk
import os
from tkinter.simpledialog import askstring

script_directory = os.path.dirname(os.path.abspath(__file__))

class CategoryDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Category")
        self.geometry("250x100")
        
        self.var = tk.StringVar()
        
        ball_rb = tk.Radiobutton(self, text="Ball", variable=self.var, value="ball")
        ball_rb.pack(pady=5)
        
        player_rb = tk.Radiobutton(self, text="Player", variable=self.var, value="player")
        player_rb.pack(pady=5)
        
        submit_button = tk.Button(self, text="Submit", command=self.destroy)
        submit_button.pack(pady=10)
        
    def show(self):
        self.wait_window()  # This will wait until the dialog is closed
        return self.var.get()  # Return the selected category



class AnnotationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Soccer Annotation Tool")
        self.root.geometry("800x600")  # This will set the initial size to 800x600
        # UI Elements
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas.bind("<ButtonPress-1>", self.start_rect)
        self.canvas.bind("<B1-Motion>", self.dragging)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)

        # Key bindings for undo and redo
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-s>', lambda e: self.save_annotations())


        self.annotations = []


        self.classes = ['ball', 'player']  # Add this line back

        self.category_colors = {
            'ball': 'blue',
            'player': 'red'
        }


        self.current_image_path = None
        self.current_ball_coords = []
        self.frame_number = 111  # adjust this as needed
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        self.undone_annotations = []
        self.rectangles = []  # Stores rectangle IDs for undo/redo


        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder...", command=self.open_folder)
        file_menu.add_command(label="Save Annotations...", command=self.save_annotations, accelerator="Ctrl+S")

        edit_menu = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")

        # Progress bar and label setup
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.progress_label = ttk.Label(self.bottom_frame, text="")
        self.progress_label.pack(side=tk.LEFT)

        self.progressbar = ttk.Progressbar(self.bottom_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progressbar.pack(side=tk.RIGHT, fill=tk.X, expand=True)




    def open_folder(self):
        folder_path = filedialog.askdirectory(initialdir="/home/mehdi/YOLO_Train")
        print(f"Selected folder path: {folder_path}")

        if not folder_path:
            return

        self.image_paths = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.jpg') or f.lower().endswith('.png')])
        print(f"Total images found: {len(self.image_paths)}")  # Debugging line
        self.current_image_index = 0  # Ensure it's initialized to 0
        print(f"Selected folder path: {folder_path}")

        self.load_image()

    def load_image(self):
        if self.current_image_index >= len(self.image_paths):
            print("All images have been annotated.")
            return

        self.current_image_path = self.image_paths[self.current_image_index]
        image_name = os.path.basename(self.current_image_path)  # This gets the image name from its path

        self.root.title(f"Soccer Annotation Tool - {image_name}")  # Set the title to include the image name

        image = Image.open(self.current_image_path)
        self.tk_image = ImageTk.PhotoImage(image)

        self.root.geometry(f"{image.width}x{image.height}")
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.frame_number = int(os.path.basename(self.current_image_path).split('.')[0])
        # Update the progress bar and label
        self.update_progress()
        
    def update_progress(self):
        completed = self.current_image_index
        total = len(self.image_paths)
        self.progressbar['value'] = (completed / total) * 100
        self.progress_label.config(text=f"{completed} out of {total} images annotated")



    def start_rect(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if not self.rect_id:
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y, 
                outline='red',  width=3)


    def dragging(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, curX, curY)

    def release_mouse(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        if self.start_x and self.start_y:
            category_dialog = CategoryDialog(self.root)
            category = category_dialog.show()

            if category in self.classes:
                image = Image.open(self.current_image_path)

                x_center = ((self.start_x + end_x) / 2.0) / image.width
                y_center = ((self.start_y + end_y) / 2.0) / image.height
                width = abs(end_x - self.start_x) / image.width
                height = abs(end_y - self.start_y) / image.height

                class_id = self.classes.index(category)

                # Update rectangle color based on the category
                color = self.category_colors.get(category, 'red')
                self.canvas.itemconfig(self.rect_id, outline=color,  width=3)
                
                annotation = {
                    "class_id": class_id,
                    "x_center": x_center,
                    "y_center": y_center,
                    "width": width,
                    "height": height
                }
                self.annotations.append(annotation)
                self.rectangles.append(self.rect_id)  

        self.start_x = None
        self.start_y = None
        self.rect_id = None   # Reset the rectangle ID

    def undo(self):
        if self.annotations:
            last_annotation = self.annotations.pop()
            self.undone_annotations.append(last_annotation)

            # Remove the rectangle from the canvas
            last_rectangle = self.rectangles.pop()
            self.canvas.delete(last_rectangle)

    def redo(self):
        if self.undone_annotations:
            last_undone_annotation = self.undone_annotations.pop()
            self.annotations.append(last_undone_annotation)

            # Draw the rectangle on the canvas
            annotation = self.annotations[-1]
            x1 = annotation['x_center'] - annotation['width'] / 2.0
            y1 = annotation['y_center'] - annotation['height'] / 2.0
            x2 = annotation['x_center'] + annotation['width'] / 2.0
            y2 = annotation['y_center'] + annotation['height'] / 2.0
            image = Image.open(self.current_image_path)
            x1 *= image.width
            y1 *= image.height
            x2 *= image.width
            y2 *= image.height
            color = self.category_colors.get(self.classes[annotation['class_id']], 'red')
            rectangle = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color,  width=3)
            self.rectangles.append(rectangle)
    
    def save_overlay_image(self):
        overlay_folder = os.path.join(script_directory, 'overlays')
        
        # Create the overlays folder if it doesn't exist
        if not os.path.exists(overlay_folder):
            os.makedirs(overlay_folder)
            
        # Generate filename and path for the overlay image
        overlay_image_name = os.path.basename(self.current_image_path)
        overlay_image_path = os.path.join(overlay_folder, overlay_image_name)

        # Capture the canvas content using ImageGrab
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, x1, y1))

        img.save(overlay_image_path)
    

    def save_annotations(self):
        if not self.current_image_path:
            return
        
        # Save overlay image (moved this up before the potential destruction of the app)
        self.save_overlay_image()
        
        # Define the annotations folder path
        annotations_folder = os.path.join(script_directory, 'annotations')
        
        # Create the annotations folder if it doesn't exist
        if not os.path.exists(annotations_folder):
            os.makedirs(annotations_folder)
        
        # Get the filename without the extension and add '.txt'
        txt_filename = os.path.splitext(os.path.basename(self.current_image_path))[0] + '.txt'
        txt_filepath = os.path.join(annotations_folder, txt_filename)
        
        with open(txt_filepath, 'w') as txt_file:
            for annotation in self.annotations:
                line = f"{annotation['class_id']} {annotation['x_center']} {annotation['y_center']} {annotation['width']} {annotation['height']}\n"
                txt_file.write(line)
        
        # Clear the annotations and move to the next image
        self.annotations.clear()
        self.current_image_index += 1
        self.update_progress()

        if self.current_image_index < len(self.image_paths):
            self.load_image()
        else:
            print("All images have been annotated.")
            self.root.destroy()  # Close the main window after saving the overlay

        self.undone_annotations.clear()  # Clear the undone annotations list after saving

if __name__ == "__main__":
    root = tk.Tk()
    app = AnnotationTool(root)
    root.mainloop()