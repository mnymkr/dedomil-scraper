import os
import zipfile
import re

JAR_DIR = "jar"

def parse_manifest(manifest_content):
    props = {}
    for line in manifest_content.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            props[key.strip()] = value.strip()
    return props

def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in " ._-()" else "_" for c in name)

def smart_split(s):
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    s = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', s)
    s = re.sub(r'(?<=\d)(?=[A-Za-z])', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def rename_jars_with_prettified_names():
    if not os.path.isdir(JAR_DIR):
        print(f"Folder '{JAR_DIR}' does not exist.")
        return

    for filename in os.listdir(JAR_DIR):
        if not filename.lower().endswith(".jar"):
            continue

        filepath = os.path.join(JAR_DIR, filename)

        try:
            with zipfile.ZipFile(filepath, 'r') as jar:
                if "META-INF/MANIFEST.MF" not in jar.namelist():
                    print(f"Skipping {filename} (no MANIFEST.MF)")
                    continue

                with jar.open("META-INF/MANIFEST.MF") as manifest_file:
                    content = manifest_file.read().decode("utf-8", errors="ignore")
                    props = parse_manifest(content)

                name = smart_split(props.get("MIDlet-Name", "UnknownApp"))
                vendor = smart_split(props.get("MIDlet-Vendor", "UnknownVendor"))
                version = smart_split(props.get("MIDlet-Version", "0.0"))

                new_name = f"{name} {vendor} {version}.jar"
                new_path = os.path.join(JAR_DIR, sanitize_filename(new_name))

                if os.path.abspath(new_path) == os.path.abspath(filepath):
                    continue  # Already correctly named
                if os.path.exists(new_path):
                    print(f"Skipped {filename} → {new_name} (already exists)")
                    continue

                os.rename(filepath, new_path)
                print(f"Renamed: {filename} → {new_name}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    rename_jars_with_prettified_names()
