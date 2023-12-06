import os
from dataclasses import dataclass


@dataclass
class OneDriveItem:
    id: str

    def __init__(self, full_path: str, parent_id: str, id: str) -> None:
        self.full_path = full_path
        if "/" == full_path:
            self.name = "/"
        else:
            self.name = os.path.basename(full_path)
        self.id = id
        self.parent_id = parent_id


@dataclass
class OneDriveFolderItem(OneDriveItem):
    def __init__(self, full_path: str, parent_id: str, id: str) -> None:
        OneDriveItem.__init__(self, full_path, parent_id, id)


@dataclass
class OneDriveFileItem(OneDriveItem):
    def __init__(self, full_path: str, parent_id: str, id: str) -> None:
        OneDriveItem.__init__(self, full_path, parent_id, id)


@dataclass
class OneDrivePackageItem(OneDriveItem):
    def __init__(self, full_path: str, parent_id: str, id: str) -> None:
        OneDriveItem.__init__(self, full_path, parent_id, id)
