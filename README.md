# OneDrive Ransomware


## Description
OneDriveRansomware is a proof-of-concept tool that is designed to allow simulating ransomware capabilities against OneDrive in Microsoft 365.  

### Disclaimer
This tool was created as a simulation tool to increase awareness around ransomware threats and to help in improving the security posture of organizations. This tool should be used solely for authorized security research purposes. This tool is provided “as is” and Hunters.secuity disclaims any and all warranties and liabilities regarding the use/misuse of this tool. Use responsibly.


## <b> How It works </b>
### Starting a ransomware attack
1. When the tool is set to start a ransomware attack, it will use the access token to set a session to OneDrive.
2. If the tool is set to generate a new key, it will generate a key and write it to the key path that is set by ```--key-path``` (default file path: ```./config/key.txt```). 
3. The tool will enumerate all files that are stored in the token's user private drive. The tool will not encrypt file that are not stored in the user's private drive.
4. After having a list of all the files to encrypt, the tool will iteratively:
   1. Read the file content
   2. Encrypt the content using the key stored at ```--key-path```
   3. Permanently delete the original file
   4. Upload the new encrypted file with the original name with an encrypted extension suffix
5. The default encrypted file extension is set to ```.enc``` and be configured by using the ```--encrypted-file-extension``` option.

### Reverting a ransomware attack
1. When the tool is set to revert a ransomware attack, it will use the access token to set a session to OneDrive.
2. The tool will user the key set to generate a new key, it will generate a key and write it to the key path that is set by ```--key-path``` (default file path: ```./config/key.txt```). 
3. The tool will enumerate all files that are stored in the token's user private drive. The tool will not encrypt file that are not stored in the user's private drive.
4. After having a list of all the files to encrypt, the tool will iteratively:
   1. Read the file content
   2. Decrypt the content using the key stored at ```--key-path```
   3. Permanently delete the encrypted file from OneDrive
   4. Upload the new decrypted file with the original name without the encrypted extension suffix
5. The default decrypted file extension is set to ```.enc``` and be configured by using the ```--encrypted-file-extension``` option.

### Hunting Queries
After simulating the ransomware, it is recommended to perform an analysis of the activities made during the simulation.
Threat hunting queries are available <a href="https://github.com/axon-git/threat-hunting/tree/main/OneDrive%20Ransomware">here</a>

## How to use
OneDriveRansomware uses Poetry to allow easy and fast dependency installation. 
### Installation
- Set up relevant packages and dependencies using Poetry. 
```
git clone git@github.com:axon-git/OneDriveRansomware.git
poetry install
poetry shell
```

- Set the Azure access token in the `./config/token.txt` file.
- Set the Encryption key in the `./config/key.txt` file.<br>It is possible to let the tool generate a new encryption key by specifying ```--generate-key```  

### Usage
```
usage: main.py [-h] [--start-ransomware] [--revert-ransomware]
               [--key-path KEY_PATH] [--token-path TOKEN_PATH]
               [--encrypted-file-extension ENCRYPTED_FILE_EXTENSION]
               [--generate-key]

Proof-of-concept of running ransomware in OneDrive

optional arguments:
  -h, --help            show this help message and exit
  --start-ransomware    Start a ransomware attack by encrypting all the remote
                        files
  --revert-ransomware   Revert a ransomware attack by decrypting all the
                        remote files
  --generate-key        When specified, a new key will be generated.
                        Otherwise, a key will be read from the key path
  --key-path KEY_PATH   Path to symmetric encryption/decryption key./default:
                        ./config/key.txt
  --token-path TOKEN_PATH
                        Path to the JWT token. default: ./config/token.txt
  --encrypted-file-extension ENCRYPTED_FILE_EXTENSION
                        The extension of the encrypted files. default: .enc
```

## Examples
Execute a ransomware attack, take the token from the default location ```./config/token.txt``` and generate a new encryption key and store it in the default location ```./config/key.txt```
```commandline
python /OneDriveRansomware/main.py --start-ransomware --generate-key
```
<br>

Execute a ransomware attack, take the token from ```/Downloads/access_token.txt```, generate a new encryption key and store it in ```./config/key.txt```
```commandline
python /OneDriveRansomware/main.py --start-ransomware --token-path /Downloads/access_token.txt --generate-key
```

<br>

Revert the ransomware attack, take the token from the default location ```./config/token.txt``` and use the decryption key stored in ```./config/key.txt```
```commandline
python /OneDriveRansomware/main.py --revert-ransomware
```

#### Credits
OneDrive's objects and API utilization were inspired from <a href="https://github.com/SafeBreach-Labs/DoubleDrive">DoubleDrive</a> by <a href="https://safebreach.com/">SafeBreach</a>   
