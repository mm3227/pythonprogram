from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open("config_email.key", "wb") as f:
    f.write(key)

print("Clave generada correctamente")
