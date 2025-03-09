import os
import glob
import json
import requests
import shutil  # Nécessaire pour copier les fichiers

# Chargement de la configuration depuis config.json
def load_config():
    config_file = "config.json"
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Le fichier de configuration '{config_file}' est introuvable.")
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

# Assurez-vous que le fichier config.json contient une clé "api_key"
API_KEY = config.get("api_key")
if not API_KEY:
    raise ValueError("La clé API n'a pas été trouvée dans le fichier de configuration.")
API_URL = "https://api.openai.com/v1/images/generations"

# Préparez l'en-tête de la requête
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def archive_current_image_copy():
    """
    Si le fichier 'IMG_XXXX.png' existe, on le copie dans le système d'archives
    en lui attribuant un numéro incrémenté.
    Les fichiers archives suivent le format 'IMG_0001.png', 'IMG_0002.png', etc.
    Le fichier 'IMG_XXXX.png' reste intact et sera écrasé par le nouveau traitement.
    """
    current_file = "IMG_XXXX.png"
    if not os.path.exists(current_file):
        return  # Rien à archiver si le fichier courant n'existe pas

    # Recherche de tous les fichiers d'archive au format IMG_0001.png (4 chiffres)
    archives = glob.glob("IMG_[0-9][0-9][0-9][0-9].png")
    max_index = 0
    for file in archives:
        try:
            index = int(os.path.splitext(os.path.basename(file))[0].split("_")[1])
            if index > max_index:
                max_index = index
        except (IndexError, ValueError):
            continue

    new_index = max_index + 1
    new_name = f"IMG_{new_index:04d}.png"
    shutil.copyfile(current_file, new_name)
    # print(f"L'image actuelle a été copiée dans l'archive sous '{new_name}'.")

def generate_image(prompt):
    print(f"En cours, avec le prompt : {prompt}")

    try:
        # Si une image courante existe, on en fait une copie pour l'archiver.
        archive_current_image_copy()

        # Préparation des données de la requête avec le prompt saisi par l'utilisateur
        data = {
            "prompt": prompt,
            "n": 1,                # nombre d'images à générer
            "size": "1024x1024",   # taille de l'image
            "model": "dall-e-3"    # utilisation du modèle DALL·E 3
        }

        # Envoi de la requête POST à l'API DALL·E
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))

        # Vérifier que la requête a réussi
        if response.status_code != 200:
            print("Erreur lors de la génération de l'image :", response.text)
        else:
            result = response.json()
            image_url = result["data"][0]["url"]
            # print("URL de l'image :", image_url)

            # Télécharger l'image et la sauvegarder localement sous le nom "IMG_XXXX.png"
            image_data = requests.get(image_url).content
            with open("IMG_XXXX.png", "wb") as img_file:
                img_file.write(image_data)
            print("L'image a été téléchargée et sauvegardée sous 'IMG_XXXX.png'.")
    except Exception as e:
        print("Une erreur s'est produite :", e)

if __name__ == "__main__":
    # Demande du prompt à l'utilisateur via le terminal
    user_prompt = input("Que voulez-vous générer ? :\n")
    generate_image(user_prompt)