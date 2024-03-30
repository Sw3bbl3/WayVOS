import os
import requests
import zipfile
import subprocess
import shutil
import tempfile
import urllib.request
import ctypes

def download_latest_release(repo_name):
    url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    response = requests.get(url)
    print("Response status code:", response.status_code)
    print("Response content:", response.content)
    if response.status_code == 200:
        release_info = response.json()
        assets = release_info.get('assets', [])
        if assets:
            asset = assets[0]  # Assuming the first asset is the zip file
            asset_url = asset.get('browser_download_url')
            print("Asset URL:", asset_url)
            if asset_url:
                try:
                    # Download the release file using requests
                    with requests.get(asset_url, stream=True) as r:
                        r.raise_for_status()
                        release_data = r.content
                    print("Successfully downloaded the release data.")
                    return release_data
                except Exception as e:
                    print("Failed to download the release:", e)
    else:
        print("Failed to get release information:", response.text)
    return None

def extract_zip(zip_data, target_dir):
    with tempfile.TemporaryFile() as tmp:
        tmp.write(zip_data)
        with zipfile.ZipFile(tmp) as zip_file:
            zip_file.extractall(target_dir)

def install_python_installer():
    python_installer_url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    python_installer_path = os.path.join(tempfile.gettempdir(), "python_installer.exe")
    urllib.request.urlretrieve(python_installer_url, python_installer_path)
    subprocess.run([python_installer_path, "/quiet", "InstallAllUsers=1"])

def install_requirements():
    wayvos_dir = os.path.join(os.getenv("USERPROFILE"), "Documents", "WayVOS")
    requirements_file = os.path.join(wayvos_dir, "requirements.txt")
    subprocess.run(["pip", "install", "-r", requirements_file])

def create_launcher_script():
    installer_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_script_path = os.path.join(installer_dir, "launcher_script.py")
    launcher_path = os.path.join(installer_dir, "launcher.bat")
    with open(launcher_script_path, "w") as launcher_script:
        launcher_script.write('import subprocess\n')
        launcher_script.write(f'subprocess.run(["cmd", "/c", "{launcher_path}"], shell=True)\n')
    return launcher_script_path

def main():
    repo_name = "Sw3bbl3/WayVOS"

    installer_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(installer_dir)
    
    target_dir = os.path.join(os.getenv("USERPROFILE"), "Documents", "WayVOS")
    if not os.path.exists(target_dir):
        print("Downloading the latest release...")
        release_data = download_latest_release(repo_name)
        if release_data:
            print("Extracting the release to:", target_dir)
            extract_zip(release_data, target_dir)
            
            print("Installing Python 3.10.11...")
            install_python_installer()
            
            print("Installing requirements...")
            install_requirements()
            
            if ctypes.windll.shell32.IsUserAnAdmin() != 0:
                print("Creating launcher script...")
                create_launcher_script()
            else:
                print("You need administrator privileges to create a launcher script.")

            print("Installation completed!")
        else:
            print("Failed to download the latest release.")
    else:
        print("WayVOS directory already exists. Skipping installation.")

    # Change directory to the target directory before running the launcher
    os.chdir(target_dir)

    # Automatically run the launcher.bat file after installation
    launcher = os.path.join(target_dir, "launcher.bat")
    if os.path.exists(launcher):
        subprocess.run([launcher], shell=True)
    else:
        print("launcher.bat not found. Skipping execution.")

if __name__ == "__main__":
    main()
