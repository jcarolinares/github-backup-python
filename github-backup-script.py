import requests
import datetime
import os
import shutil
import urllib.request # why requests and urlib request? you only need one
import time
import configparser

# Modify these parameters with your own.
private_repository_url = " "
public_repository_url = " "
private_backup_folder = r" "   
public_backup_folder = r" "


# Global variables
connected = False

# Downloading repositories function
# It is important to keep your token safe and don't share it with anyone.

def download_repo(repo_url, dest_folder, branch="main", token="your_token"):
    # Make a GET request to the GitHub API to download the repository as a zip file
    headers = {"Authorization": f"token {token}"}
    zip_url = f"{repo_url}/archive/{branch}.zip"
    response = requests.get(zip_url, headers=headers, stream=True)

    # If the response status code is not 200, raise an error
    if response.status_code != 200:
        raise ValueError(f"Failed to download repository. Status code: {response.status_code}")

    # Create the destination folder if it does not exist
    os.makedirs(dest_folder, exist_ok=True)

    # Save the contents of the zip file to a local file with the current date in the filename
    repo_name = repo_url.split("/")[-1]
    now = datetime.datetime.now()
    filename = f"{repo_name}-{branch}_{now.strftime('%Y-%m-%d_%Hh_%Mm')}_backup.zip"
    filepath = os.path.join(dest_folder, filename)

    with open(filepath, "wb") as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)

    # Close the response to free up resources
    response.close()

    print(f"Repository downloaded to {filepath}")

# Removing older backups function
def delete_old_files(folder_path, hours_del):
    # Get the current time
    now = datetime.datetime.now()

    # Calculate the time threshold for deleting files
    threshold = now - datetime.timedelta(hours=hours_del)

    # Loop over all files in the folder
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        # Check if the file is a zip file and is older than the threshold
        if filename.endswith(".zip") and os.path.getmtime(filepath) < threshold.timestamp():
            # Delete the file
            os.remove(filepath)
            print(f"Deleted old file: {filename}")


# Check if the device is connected to the internet
def check_internet_connection():
    try:
        urllib.request.urlopen("https://www.google.com")
        return True
    except:
        return False



if __name__ == '__main__':
    # Read credentials file and put it the data on the global variables
    config_file = "setup_credentials.ini"
    config = configparser.ConfigParser()
    config.read(config_file)

    if (config.get("github-backup", "api_token") == "<THINGIVERSE_API_TOKEN>"):
        print("ERROR-YOU HAVE TO PUT YOUR THINGIVERSE API TOKEN AT: api_credentials.ini")
        sys.exit()
    else:
        api_token = config.get("ThingiverseAPI", "api_token")


    # Internet connection check and program execution
    while not connected:
        if check_internet_connection():

            #Uncomment the next line to start after an user confirmation:
            #input('Press any button to start..')

            print(f"Downloading private repository...")
            download_repo(config.get("private_repository_url"), config.get("api_token"), config.get("private_backup_folder") )
            print(f"Private repository downloaded successfully...") # FIXME or not, you can have errors

            print(f"Downloading public repository..")
            download_repo(config.get("public_repository_url"), config.get("public_backup_folder"))
            print(f"Public repository downloaded successfully..") # FIXME or not, you can have errors

            # Execute the backup-cleaner function
            # Change the second parameter on the next functions to change the deleting frequency. Defalut: 48h
            print(f"Deleting old repositories..")
            delete_old_files(private_backup_folder, 48)
            delete_old_files(public_backup_folder, 48)
            print(f"Old backups deleted successfully..")
            print(f"All work done here!!!") 

            connected = True

        #If not connected to the internet, returns error message
        else:
            print("Device is not connected to the internet. Retrying in 10 seconds...")
            time.sleep(10)


