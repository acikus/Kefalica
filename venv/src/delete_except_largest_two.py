import os
import glob
def delete_except_largest_two(root_folder):
    for subdir, _, _ in os.walk(root_folder):
        images = []
        
        # Collect all image files (modify the extensions as needed)
        for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp'):
            images.extend(glob.glob(os.path.join(subdir, ext)))
        
        if len(images) > 2:
            # Sort images by file size in descending order
            images.sort(key=lambda x: os.path.getsize(x), reverse=True)
            
            # Keep the two largest and delete the rest
            for img in images[2:]:
                try:
                    os.remove(img)
                    print(f"Deleted: {img}")
                except Exception as e:
                    print(f"Error deleting {img}: {e}")

if __name__ == "__main__":
    root_directory = "E:\\Games\\Kefalica\\Kefalica\\venv\\src\\assets\\dataset\\dataset"  # Change this to your actual root folder
    delete_except_largest_two(root_directory)