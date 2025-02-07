import json
import shutil
import os
import base64
import hashlib
import sys
from tkinter import *
from tkinter import filedialog
from random import randint

def newarch():
    try:
        # Select the folder to archive
        file = filedialog.askdirectory(title="Select a folder to create an archive")
        if not file:
            return  # If no folder selected, exit function

        file = os.path.normpath(file)  # Normalize path
        zip_path = f"{file}.zip"

        # Create a ZIP archive for the folder
        shutil.make_archive(file, 'zip', file)

        # Prepare the SAR data structure with the content of the ZIP file
        with open(zip_path, "rb") as zip_file:
            zip_content = zip_file.read()
            # Encode the ZIP content into base64 for storage
            encoded_content = base64.b64encode(zip_content).decode('utf-8')

        # Save the encoded content in a SAR file
        sar_path = f"{file}{randint(1, 100)}.sar"
        with open(sar_path, "w", encoding="utf-8") as sar_file:
            json.dump({"content": encoded_content}, sar_file)

        os.remove(zip_path)  # Remove the temporary ZIP file

        # Open the directory containing the SAR archive
        os.system(f'start "" "{os.path.dirname(file)}"')
    except Exception as e:
        print(f"Error in newarch: {e}")

def newarchzip():
    try:
        # Select folder and create a ZIP archive
        file = filedialog.askdirectory(title="Select a folder to create an archive")
        if not file:
            return  # If no folder selected, exit function

        file = os.path.normpath(file)
        zip_path = f"{file}{randint(1, 100)}.zip"
        shutil.make_archive(zip_path.rstrip(".zip"), 'zip', file)

        # Open the folder containing the ZIP archive
        os.system(f"start {os.path.dirname(file)}")
    except Exception as e:
        print(f"Error in newarchzip: {e}")

def openarch(query):
    try:
        if query == 1:
            file = filedialog.askopenfilename(title="Select the SAR archive", filetypes=[("SAR archive", "*.sar")]).replace("/", "\\")
        else:
            file = query
        backsl = "\\"
        with open(file, "r", encoding="utf-8") as sar_file:
            data = json.load(sar_file)
        
        # Retrieve the content from SAR
        encoded_content = data["content"]
        
        # Check if the SAR archive has a password
        passbool = None
        password_hash = None
        if "password" in data:
            passbool = data["password"]
        
        # Password protection logic
        if passbool:
            # Ask for password
            pop = Tk()
            pop.title("SimpleArchive")
            Label(pop, text="This archive is password-protected. Please enter the password:").grid(row=0, column=0)
            entry = Entry(pop, width=30)
            entry.grid(row=1, column=0)

            def action():
                entered_password = entry.get()
                if entered_password:
                    entered_password_hash = hashlib.sha256(entered_password.encode('utf-8')).hexdigest()
                    if entered_password_hash == passbool:
                        # Password matches, proceed to extract and open the archive
                        zip_content = base64.b64decode(encoded_content)
                        temp_zip_file = f'{file}-tempsessionsar.zip'
                        with open(temp_zip_file, "wb") as zip_file:
                            zip_file.write(zip_content)

                        shutil.unpack_archive(temp_zip_file, f'{file.rstrip(".sar")}', "zip")
                        os.remove(temp_zip_file)
                        os.system(f"start {file.rstrip(file.split(backsl)[-1])}")
                        pop.destroy()  # Close the password prompt window
                    else:
                        Label(pop, text="Incorrect password. Please try again.").grid(row=2, column=0, pady=10)
                else:
                    Label(pop, text="You must enter a password.").grid(row=2, column=0, pady=10)

            Button(pop, text="Enter password", command=action).grid(row=3, column=0, pady=10)
            pop.mainloop()

        else:
            # No password protection, just unpack the archive
            zip_content = base64.b64decode(encoded_content)
            temp_zip_file = f'{file}-tempsessionsar.zip'
            with open(temp_zip_file, "wb") as zip_file:
                zip_file.write(zip_content)

            shutil.unpack_archive(temp_zip_file, f'{file.rstrip(".sar")}', "zip")
            os.remove(temp_zip_file)
            os.system(f"start {file.rstrip(file.split(backsl)[-1])}")

    except Exception as e:
        print(f"Error in openarch: {e}")

def openarchzip():
    try:
        file = filedialog.askopenfilename(title="Select the ZIP archive", filetypes=[("ZIP archive", "*.zip")]).replace("/", "\\")
        backsl = "\\"
        shutil.unpack_archive(file, f'{file.rstrip(".zip")}', "zip")
        os.system(f"start {file.rstrip(file.split(backsl)[-1])}")
    except Exception as e:
        print(f"Error in openarchzip: {e}")

def sarpass():
    pop = Tk()
    pop.title("SimpleArchive")
    Label(pop, text="Set your password:").grid(row=0, column=0)
    entry = Entry(pop, width=30)
    entry.grid(row=1, column=0)

    def action():
        if not entry.get():
            Label(pop, text="You must enter a password to create the SAR archive.").grid(row=3, column=0, pady=10)
        else:
            # Select the folder to create the archive
            file = filedialog.askdirectory(title="Select a folder to create an archive").replace("/", "\\")
            if not file:
                return  # If no folder selected, exit function

            # Create a ZIP archive from the folder
            zip_path = f"{file}.zip"
            shutil.make_archive(file, 'zip', file)

            # Hash the password
            password_hash = hashlib.sha256(entry.get().encode('utf-8')).hexdigest()

            # Prepare the SAR data structure with the encoded ZIP content and the password hash
            with open(zip_path, "rb") as zip_file:
                zip_content = zip_file.read()
                encoded_content = base64.b64encode(zip_content).decode('utf-8')

            sar_data = {
                "password": password_hash,
                "content": encoded_content
            }

            # Save the SAR data as a JSON file
            sar_path = f"{file}{randint(1, 100)}.sar"
            with open(sar_path, "w", encoding="utf-8") as sar_file:
                json.dump(sar_data, sar_file)

            os.remove(zip_path)  # Remove the temporary ZIP file

            # Open the folder containing the SAR archive
            os.system(f"start {os.path.dirname(file)}")

    Button(pop, text="Set the password and create the archive.", command=action).grid(row=2, column=0, pady=10)

if len(sys.argv) > 1:
    root = Tk()
    root.title("SimpleArchive")
    root.wm_state('iconic')
    path = sys.argv[1]
    openarch(path)
    root.mainloop()
else:
    root = Tk()
    PADY = 20
    FSIZE = 20
    root.title("SimpleArchive")
    Label(root, text="Simple Archive 📖", fg="red", font=("arial", 50, "normal")).grid(row=0, column=0, pady=PADY)
    arch = Frame(root)
    arch.grid(row=1, column=0, pady=PADY)
    Button(arch, text="Create a new (sar) archive ➕", font=("Lucida", FSIZE, "normal"), command=lambda: newarch()).grid(row=0, column=0)
    Button(arch, text="Open a (sar) archive 💾", font=("Lucida", FSIZE, "normal"), command=lambda: openarch(1)).grid(row=0, column=1, padx=20)

    Button(arch, text="Create a new (zip) archive ➕", font=("Lucida", FSIZE, "normal"), command=lambda: newarchzip()).grid(row=1, column=0)
    Button(arch, text="Open a (zip) archive 💾", font=("Lucida", FSIZE, "normal"), command=lambda: openarchzip()).grid(row=1, column=1, padx=20)

    Button(root, text="Create a new (sar) archive locked with password 🔐", font=("Lucida", FSIZE, "normal"), command=lambda: sarpass()).grid(row=2, column=0, pady=PADY)
    root.mainloop()
