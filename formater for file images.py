import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from PIL import Image
from io import BytesIO

# Define the folder containing the MP3 files
root_folder = r"C:\Users\shugh\Music\deemix Music"
target_width = 400
target_height = 400

def resize_image(image_data, width, height):
    """Resize an image while maintaining aspect ratio."""
    with Image.open(BytesIO(image_data)) as img:
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format="JPEG")
        return output.getvalue()

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

                # Look for the album art
                new_cover_data = None
                for tag in audio.tags.keys():
                    if isinstance(audio.tags[tag], APIC):
                        # Resize the existing cover art
                        original_cover_data = audio.tags[tag].data
                        new_cover_data = resize_image(original_cover_data, target_width, target_height)
                        # Remove the old cover art
                        del audio.tags[tag]
                        break

                # Add the resized cover art
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
                    print(f"Updated cover for: {file_path}")
                else:
                    print(f"No album cover found in: {file_path}")

            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

print("Processing complete!")