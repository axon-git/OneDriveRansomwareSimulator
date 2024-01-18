# OneDrive Ransomware Simulator


## Description
OneDriveRansomwareSimulator is a proof-of-concept tool that is designed to allow simulating ransomware capabilities against OneDrive in Microsoft 365.  

### Disclaimer
This tool was created as a simulation tool to increase awareness around ransomware threats and to help improve the security posture of organizations. This tool should be used solely for authorized security research purposes. This tool is provided “as is” and Hunters.secuity disclaims any and all warranties and liabilities regarding the use/misuse of this tool. Use responsibly.


## <b> How It works </b>
### Starting a ransomware attack
1. When the tool is set to start a ransomware attack, it will use the access token to set a session to OneDrive. The access token should be set in ```./config/token.txt``` (or elsewhere by specifying the optional ```--key-path``` argument).
2. If the tool is set to generate an encryption new key (using the optional flag ```--generate-key``` to create a symmetric key), it will generate a key and write it to a default file location at ```./config/key.txt``` (can be customized by the optional ```--key-path``` argument). 
3. The tool will enumerate all files that are stored in the user's (that the token belongs to) private drive. As a security measure, the tool will not encrypt files that are stored in drives shared with the user.
4. After having a list of all the files to encrypt, the tool will iteratively:
   1. Read a file's content
   2. Encrypt the content using the specified encryption key
   3. Permanently delete the original file
   4. Upload the new encrypted file with the original name with an encrypted extension suffix
5. The default encrypted file extension is set to ```.enc``` and be configured by using the optional ```--encrypted-file-extension``` argument.

### Reverting a ransomware attack

1. Similarly to the encryption flow, when the tool is set to revert a ransomware attack, it will use the access token to set a session to OneDrive. The access token should be set in ```./config/token.txt``` (or elsewhere by specifying the optional ```--key-path``` argument).
2. The tool will use the key  that is set in ```./config/key.txt``` (or elsewhere set by the optional ```--key-path``` argument) as the decryption key 
3. The tool will enumerate all files that are stored in the user's (that the token belongs to) private drive. As mentioned before, the tool will not encrypt files that are stored in drives shared with the user.
4. After having a list of all the files to decrypt, the tool will iteratively:
   1. Read the file content
   2. Decrypt the content using the decryption key
   3. Permanently delete the encrypted file from OneDrive
   4. Upload the new decrypted file with the original name without the encrypted extension suffix
5. Same as before, the default file extension of the encrypted files is set to ```.enc``` and be configured by using the ```--encrypted-file-extension``` option.

### Hunting Queries
After simulating the ransomware, it is recommended to perform an analysis of the activities made during the simulation.<br>
Threat hunting queries are available <a href="https://github.com/axon-git/threat-hunting/tree/main/OneDrive%20Ransomware">here</a>

## How to use
OneDriveRansomwareSimulator uses Poetry to allow easy and fast dependency installation. 

### Installation
- Set up relevant packages and dependencies using Poetry. 
```
git clone git@github.com:axon-git/OneDriveRansomwareSimulator.git
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
### Start a Ransomware Attack 
#### Case #1
Execute a ransomware attack, take the token from the default location ```./config/token.txt```, generate a new encryption key, and store it in the default location ```./config/key.txt```
```commandline
python /OneDriveRansomwareSimulator/main.py --start-ransomware --generate-key
```

#### Case #2
Execute a ransomware attack, take the token from ```/Downloads/access_token.txt```, generate a new encryption key and store it in ```./config/key.txt```
```commandline
python /OneDriveRansomwareSimulator/main.py --start-ransomware --token-path /Downloads/access_token.txt --generate-key
```
<br>

### Start a Ransomware Attack

Revert the ransomware attack, take the token from the default location ```./config/token.txt``` and use the decryption key stored in ```./config/key.txt```
```commandline
python /OneDriveRansomwareSimulator/main.py --revert-ransomware
```

### Credits
OneDrive's objects and API utilization were inspired from <a href="https://github.com/SafeBreach-Labs/DoubleDrive">DoubleDrive</a> by <a href="https://safebreach.com/">SafeBreach</a>   
