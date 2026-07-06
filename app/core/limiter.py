from slowapi import Limiter
from slowapi.util import get_remote_address

# Khởi tạo bộ đếm. Dùng địa chỉ IP (remote_address) làm chìa khóa để nhận diện người dùng.
limiter = Limiter(key_func=get_remote_address)