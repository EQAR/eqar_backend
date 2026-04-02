import os

from django.core.files.storage import FileSystemStorage

class ByteTruncatingFileSystemStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        """
        Adapted version of Django's original code, truncating filename to max 255 bytes
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        ext_bytes = len(file_ext.encode('utf-8'))
        max_root_bytes = 255 - ext_bytes
        encoded = file_root.encode('utf-8')
        if len(encoded) > max_root_bytes:
            file_root = encoded[:max_root_bytes].decode('utf-8', errors='ignore')
            name = os.path.join(dir_name, file_root + file_ext)
        return super().get_available_name(name, max_length)

    def get_alternative_name(self, file_root, file_ext):
        """
        Ensure that added random string does not exceed 255 bytes
        """
        ext_bytes = len(file_ext.encode('utf-8'))
        max_root_bytes = 247 - ext_bytes # 255 bytes - 8 bytes for random string
        encoded = file_root.encode('utf-8')
        if len(encoded) > max_root_bytes:
            file_root = encoded[:max_root_bytes].decode('utf-8', errors='ignore')
        return super().get_alternative_name(file_root, file_ext)

