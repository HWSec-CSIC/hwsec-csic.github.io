import os
from PIL import Image

def scale_photos_to_size(input_folder, output_folder, target_size=(520, 520)):
    """
    Resizes all images in the input_folder to the target_size and 
    saves them in the output_folder.
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # Valid image extensions to look for
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                # Open the image
                with Image.open(input_path) as img:
                    # Resize the image using Lanczos filter for high quality
                    resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                    
                    # Save the new image
                    # For JPEGs, you can specify quality (e.g., quality=95)
                    resized_img.save(output_path)
                    print(f"Successfully scaled: {filename}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # Define your folders here
    # Use '.' for the current directory, or provide full paths
    INPUT_DIR = "original_photos" 
    OUTPUT_DIR = "scaled_photos"
    
    print(f"Starting batch resize to 520x520...")
    scale_photos_to_size(INPUT_DIR, OUTPUT_DIR)
    print("Done!")