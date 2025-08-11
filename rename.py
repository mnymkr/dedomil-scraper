import os
import zipfile

JAR_DIR = "jar"

import re

def smart_split(s):
    # Replace underscores and hyphens with space
    s = s.replace('_', ' ').replace('-', ' ')

    # Avoid splitting digit-uppercase combos (e.g., 3D should stay 3D)
    # So we block this rule: (?<=\d)(?=[A-Z]) ← we do NOT allow this one

    # Insert space between lowercase and uppercase (but NOT if the uppercase is followed by another uppercase)
    s = re.sub(r'(?<=[a-z])(?=[A-Z](?![A-Z]))', ' ', s)

    # Insert space between uppercase followed by uppercase + lowercase (e.g. HTMLParser → HTML Parser)
    s = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)

    # Insert space between letters and digits
    s = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', s)

    # Insert space between digits and letters (but NOT if the letter is uppercase — so skip 3D)
    s = re.sub(r'(?<=\d)(?=[a-z])', ' ', s)

    # Collapse multiple spaces and strip
    return re.sub(r'\s+', ' ', s).strip()


def parse_manifest(manifest_content):
    props = {}
    for line in manifest_content.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            props[key.strip()] = value.strip()
    return props

def sanitize_filename(name):
    # Remove or replace invalid characters for filenames
    return "".join(c if c.isalnum() or c in " ._-()" else "_" for c in name)

def rename_jar_files():
    if not os.path.exists(JAR_DIR):
        print(f"Directory '{JAR_DIR}' does not exist.")
        return

    jar_files = [f for f in os.listdir(JAR_DIR) if f.lower().endswith(".jar")]
    total = len(jar_files)

    if total == 0:
        print("No .jar files found.")
        return

    print(f"Renaming {total} .jar files...")

    for i, filename in enumerate(jar_files, start=1):
        jar_path = os.path.join(JAR_DIR, filename)

        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                if "META-INF/MANIFEST.MF" not in jar.namelist():
                    print(f"\nSkipping {filename} (no MANIFEST.MF)")
                    continue

                with jar.open("META-INF/MANIFEST.MF") as manifest_file:
                    manifest_bytes = manifest_file.read()
                    manifest_text = manifest_bytes.decode("utf-8", errors="ignore")
                    props = parse_manifest(manifest_text)

                name = props.get("MIDlet-Name", "UnknownApp")
                vendor = props.get("MIDlet-Vendor", "UnknownVendor")
                version = props.get("MIDlet-Version", "0.0")

                name = smart_split(name)
                vendor = smart_split(vendor)
                version = smart_split(version)

                new_filename = sanitize_filename(f"{name} {vendor} {version}.jar")
                new_path = os.path.join(JAR_DIR, new_filename)

                if os.path.abspath(new_path) == os.path.abspath(jar_path):
                    pass  # already correctly named
                elif os.path.exists(new_path):
                    print(f"\nFile {new_filename} already exists. Skipping.")
                else:
                    os.rename(jar_path, new_path)

        except Exception as e:
            print(f"\nError processing {filename}: {e}")

        # Print progress inline
        percent = (i / total) * 100
        print(f"\rProgress: {i}/{total} files ({percent:.1f}%)", end="", flush=True)

    print("\nDone.")


if __name__ == "__main__":
    rename_jar_files()
