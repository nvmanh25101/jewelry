APP_VALUE_LAYOUT_DEFAULT = "list"
APP_VALUE_STATUS_DEFAULT = 1
APP_VALUE_LAYOUT_CHOICES = (
    ("list", "List"),
    ("grid", "Grid"),
)
APP_VALUE_STATUS_CHOICES = (
    (0, "Ngừng hoạt động"),
    (1, "Hoạt động"),
)

APP_VALUE_STATUS_ORDER_CHOICES = (
    (0, "Người bán đã hủy"),
    (1, "Chưa duyệt"),
    (2, "Đang chuẩn bị hàng"),
    (3, "Đang giao hàng"),
    (4, "Hoàn thành"),
    (5, "Người đặt đã hủy"),
)
ADMIN_SRC_CSS = {"all": ("my_admin/css/custom.css",)}
ADMIN_SRC_JS = (
    "my_admin/js/jquery-3.6.4.min.js",
    "my_admin/js/slugify.js",
    "my_admin/js/general.js",
)

ADMIN_SITE_HEADER = "Admin"
