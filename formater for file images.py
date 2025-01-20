import os
import logging
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the folder containing the MP3 files
root_folder = r"C:\Users\shugh\Music\deemix Music"
target_width = 400
target_height = 400

def resize_image(image_data, width, height):
    """Resize an image while maintaining aspect ratio."""
    try:
        with Image.open(BytesIO(image_data)) as img:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            output = BytesIO()
            img.save(output, format="JPEG")
            return output.getvalue()
    except Exception as e:
        logging.error(f"Failed to resize image: {e}")
        return None

def extract_jpeg_from_mp3(file_path):
    """Extract JPEG data from an MP3 file if present."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            start = data.find(b"\xff\xd8")  # JPEG start marker
            end = data.find(b"\xff\xd9")   # JPEG end marker
            if start != -1 and end != -1:
                return data[start:end + 2]
    except Exception as e:
        logging.error(f"Failed to extract JPEG from {file_path}: {e}")
    return None

# Process each folder and file
for folder_name, subfolders, file_names in os.walk(root_folder):
    for file_name in file_names:
        if file_name.lower().endswith('.mp3'):
            file_path = os.path.join(folder_name, file_name)
            try:
                # Load MP3 file
                audio = MP3(file_path, ID3=ID3)

                # Ensure the file has an ID3 tag
                if not audio.tags:
                    audio.add_tags()

                # Check for existing album art
                new_cover_data = None
                for tag in audio.tags.keys():
                    if isinstance(audio.tags[tag], APIC):
                        # Resize the existing cover art
                        original_cover_data = audio.tags[tag].data
                        new_cover_data = resize_image(original_cover_data, target_width, target_height)
                        # Remove the old cover art
                        del audio.tags[tag]
                        break

                # If no existing album art, extract JPEG from the MP3 file
                if not new_cover_data:
                    extracted_jpeg = extract_jpeg_from_mp3(file_path)
                    if extracted_jpeg:
                        new_cover_data = resize_image(extracted_jpeg, target_width, target_height)

                # Add the resized or extracted cover art
                if new_cover_data:
                    audio.tags.add(
                        APIC(
                            encoding=3,  # UTF-8
                            mime="image/jpeg",
                            type=3,  # Cover (front)
                            desc="Cover",
                            data=new_cover_data
                        )
                    )
                    # Save the modified MP3 file
                    audio.save()
                    logging.info(f"Updated cover for: {file_path}")
                else:
                    logging.warning(f"No album cover or embedded JPEG found in: {file_path}")

            except Exception as e:
                logging.error(f"Failed to process {file_path}: {e}")

logging.info("Processing complete!")
