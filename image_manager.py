import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import uuid
from config import Config

class ImageManager:
    def __init__(self):
        self.images_dir = "images"
        self.property_images_dir = os.path.join(self.images_dir, "properties")
        self.thumbnails_dir = os.path.join(self.images_dir, "thumbnails")
        
        # Create directories if they don't exist
        os.makedirs(self.property_images_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
    
    def save_property_image(self, image_path, property_id=None):
        """Save property image and create thumbnail"""
        try:
            if not os.path.exists(image_path):
                return None
            
            # Generate unique filename
            file_extension = os.path.splitext(image_path)[1].lower()
            if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                raise ValueError("Unsupported image format")
            
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Copy original image
            dest_path = os.path.join(self.property_images_dir, unique_filename)
            shutil.copy2(image_path, dest_path)
            
            # Create thumbnail
            self.create_thumbnail(dest_path, unique_filename)
            
            return unique_filename
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def create_thumbnail(self, image_path, filename):
        """Create thumbnail for image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(Config.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumb_path = os.path.join(self.thumbnails_dir, filename)
                img.save(thumb_path, 'JPEG', quality=85)
                
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
    
    def get_image_path(self, filename, thumbnail=False):
        """Get full path to image or thumbnail"""
        if not filename:
            return None
        
        if thumbnail:
            return os.path.join(self.thumbnails_dir, filename)
        else:
            return os.path.join(self.property_images_dir, filename)
    
    def delete_image(self, filename):
        """Delete image and its thumbnail"""
        try:
            # Delete original image
            image_path = os.path.join(self.property_images_dir, filename)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Delete thumbnail
            thumb_path = os.path.join(self.thumbnails_dir, filename)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
                
            return True
            
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    def load_image_for_display(self, filename, size=None, thumbnail=False):
        """Load image for Tkinter display"""
        try:
            image_path = self.get_image_path(filename, thumbnail)
            
            if not image_path or not os.path.exists(image_path):
                return self.get_placeholder_image(size)
            
            # Open and resize image
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                
                return ImageTk.PhotoImage(img)
                
        except Exception as e:
            print(f"Error loading image: {e}")
            return self.get_placeholder_image(size)
    
    def get_placeholder_image(self, size=None):
        """Create placeholder image"""
        try:
            if not size:
                size = Config.PROPERTY_IMAGE_SIZE
            
            # Create a simple placeholder
            img = Image.new('RGB', size, color='#E1E8ED')
            
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            return None

class ImageUploadWidget(tk.Frame):
    def __init__(self, parent, on_image_selected=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_image_selected = on_image_selected
        self.image_manager = ImageManager()
        self.current_image = None
        self.current_filename = None
        
        self.create_widgets()
    
    def create_widgets(self):
        self.configure(bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        
        # Image display area
        self.image_label = tk.Label(
            self,
            text="📷\nClick to upload image",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BORDER_COLOR,
            fg=Config.TEXT_SECONDARY,
            width=30,
            height=10,
            cursor="hand2"
        )
        self.image_label.pack(padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(self, bg=Config.CARD_COLOR)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        upload_btn = tk.Button(
            button_frame,
            text="Upload Image",
            command=self.upload_image,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.PRIMARY_COLOR,
            fg="white",
            relief="flat",
            cursor="hand2"
        )
        upload_btn.pack(side="left", padx=(0, 5))
        
        self.remove_btn = tk.Button(
            button_frame,
            text="Remove",
            command=self.remove_image,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.ERROR_COLOR,
            fg="white",
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.remove_btn.pack(side="left")
        
        # Bind click event to image label
        self.image_label.bind("<Button-1>", lambda e: self.upload_image())
    
    def upload_image(self):
        """Handle image upload"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Property Image",
            filetypes=file_types
        )
        
        if filename:
            # Save image using ImageManager
            saved_filename = self.image_manager.save_property_image(filename)
            
            if saved_filename:
                self.current_filename = saved_filename
                self.display_image(saved_filename)
                self.remove_btn.configure(state="normal")
                
                if self.on_image_selected:
                    self.on_image_selected(saved_filename)
            else:
                messagebox.showerror("Error", "Failed to upload image")
    
    def display_image(self, filename):
        """Display uploaded image"""
        try:
            self.current_image = self.image_manager.load_image_for_display(
                filename, 
                size=(250, 150)
            )
            
            if self.current_image:
                self.image_label.configure(
                    image=self.current_image,
                    text="",
                    bg="white"
                )
                
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def remove_image(self):
        """Remove current image"""
        if self.current_filename:
            self.image_manager.delete_image(self.current_filename)
            self.current_filename = None
            self.current_image = None
            
            self.image_label.configure(
                image="",
                text="📷\nClick to upload image",
                bg=Config.BORDER_COLOR
            )
            
            self.remove_btn.configure(state="disabled")
            
            if self.on_image_selected:
                self.on_image_selected(None)
    
    def set_image(self, filename):
        """Set image from filename"""
        if filename:
            self.current_filename = filename
            self.display_image(filename)
            self.remove_btn.configure(state="normal")
    
    def get_image_filename(self):
        """Get current image filename"""
        return self.current_filename

class ImageGalleryWidget(tk.Frame):
    def __init__(self, parent, property_id, db_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.property_id = property_id
        self.db_manager = db_manager
        self.image_manager = ImageManager()
        self.images = []
        
        self.create_widgets()
        self.load_images()
    
    def create_widgets(self):
        self.configure(bg=Config.CARD_COLOR)
        
        # Header
        header_frame = tk.Frame(self, bg=Config.CARD_COLOR)
        header_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            header_frame,
            text="Property Images",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        ).pack(side="left")
        
        add_btn = tk.Button(
            header_frame,
            text="+ Add Image",
            command=self.add_image,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.SUCCESS_COLOR,
            fg="white",
            relief="flat",
            cursor="hand2"
        )
        add_btn.pack(side="right")
        
        # Images container with scrollbar
        self.create_scrollable_gallery()
    
    def create_scrollable_gallery(self):
        """Create scrollable image gallery"""
        # Canvas and scrollbar
        canvas = tk.Canvas(self, bg=Config.CARD_COLOR, height=200)
        scrollbar = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        
        self.gallery_frame = tk.Frame(canvas, bg=Config.CARD_COLOR)
        
        canvas.configure(xscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.gallery_frame, anchor="nw")
        
        canvas.pack(fill="both", expand=True)
        scrollbar.pack(fill="x")
        
        # Update scroll region when frame changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.gallery_frame.bind("<Configure>", configure_scroll_region)
        
        self.canvas = canvas
    
    def load_images(self):
        """Load property images from database"""
        try:
            self.images = self.db_manager.get_property_images(self.property_id)
            self.display_images()
        except Exception as e:
            print(f"Error loading images: {e}")
    
    def display_images(self):
        """Display images in gallery"""
        # Clear existing images
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        
        for i, image_data in enumerate(self.images):
            image_frame = tk.Frame(self.gallery_frame, bg=Config.CARD_COLOR)
            image_frame.pack(side="left", padx=5, pady=5)
            
            # Load and display image
            try:
                img = self.image_manager.load_image_for_display(
                    image_data['image_path'],
                    size=(150, 100),
                    thumbnail=True
                )
                
                image_label = tk.Label(
                    image_frame,
                    image=img,
                    bg="white",
                    relief="solid",
                    borderwidth=1
                )
                image_label.pack()
                
                # Keep reference to prevent garbage collection
                image_label.image = img
                
                # Primary indicator
                if image_data.get('is_primary'):
                    primary_label = tk.Label(
                        image_frame,
                        text="PRIMARY",
                        font=(Config.FONT_FAMILY, 8, "bold"),
                        bg=Config.SUCCESS_COLOR,
                        fg="white"
                    )
                    primary_label.pack(fill="x")
                
                # Action buttons
                btn_frame = tk.Frame(image_frame, bg=Config.CARD_COLOR)
                btn_frame.pack(fill="x", pady=(2, 0))
                
                if not image_data.get('is_primary'):
                    primary_btn = tk.Button(
                        btn_frame,
                        text="Set Primary",
                        command=lambda img_id=image_data['id']: self.set_primary(img_id),
                        font=(Config.FONT_FAMILY, 8),
                        bg=Config.ACCENT_COLOR,
                        fg="white",
                        relief="flat"
                    )
                    primary_btn.pack(side="left", padx=(0, 2))
                
                delete_btn = tk.Button(
                    btn_frame,
                    text="Delete",
                    command=lambda img_id=image_data['id'], path=image_data['image_path']: self.delete_image(img_id, path),
                    font=(Config.FONT_FAMILY, 8),
                    bg=Config.ERROR_COLOR,
                    fg="white",
                    relief="flat"
                )
                delete_btn.pack(side="left")
                
            except Exception as e:
                print(f"Error displaying image: {e}")
        
        # Update canvas scroll region
        self.gallery_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def add_image(self):
        """Add new image to property"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Property Image",
            filetypes=file_types
        )
        
        if filename:
            saved_filename = self.image_manager.save_property_image(filename)
            
            if saved_filename:
                # Add to database
                is_primary = len(self.images) == 0  # First image is primary
                success = self.db_manager.add_property_image(
                    self.property_id, 
                    saved_filename, 
                    is_primary
                )
                
                if success:
                    self.load_images()  # Refresh gallery
                else:
                    messagebox.showerror("Error", "Failed to save image to database")
            else:
                messagebox.showerror("Error", "Failed to upload image")
    
    def set_primary(self, image_id):
        """Set image as primary"""
        success = self.db_manager.set_primary_image(self.property_id, image_id)
        if success:
            self.load_images()  # Refresh gallery
        else:
            messagebox.showerror("Error", "Failed to set primary image")
    
    def delete_image(self, image_id, image_path):
        """Delete image"""
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this image?")
        
        if result:
            # Delete from database
            success = self.db_manager.delete_property_image(image_id)
            
            if success:
                # Delete file
                self.image_manager.delete_image(image_path)
                self.load_images()  # Refresh gallery
            else:
                messagebox.showerror("Error", "Failed to delete image")