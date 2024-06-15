import subprocess

def install_requirements(requirements_file):
    try:
        subprocess.check_call(['pip', 'install', '-r', requirements_file])
        print("All requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")

if __name__ == "__main__":
    requirements_file = "requirements.txt"
    install_requirements(requirements_file)
