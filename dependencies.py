import firebase_admin
from fastapi import Depends
from firebase_admin import firestore, credentials
from google.cloud import firestore as cloud_firestore

from add_new_stock.controller.add_new_stock_controller import AddNewStockController
from banners.controller.banner_controller import BannerController
from cart.controller.cart_controller import CartController
from categories.controller.category_controller import CategoryController
from complaints.controller.complaints_controller import ComplaintsController
from coupons.controller.coupons_controller import CouponController
from inventory.controller.inventory_controller import InventoryController
from inventory.controller.remove_stock_controller import RemoveStockController
from messages.controller.messages_controller import MessageController
from orders.controller.orders_controller import OrderController
from product_requests.controller.request_product_controller import RequestProductController
from products.controller.product_bundle_controller import ProductBundleController
from products.controller.product_controller import ProductController
from riders.controller.rider_controller import RiderController
from store_managers.controller.store_manager_controller import StoreManagerController
from stores.controller.store_controller import StoreController
from sub_category.controller.sub_category_controller import SubCategoryController
from user_address.controller.address_controller import AddressController
from users.controller.user_controller import UserController


def get_firestore_client() -> cloud_firestore.Client:
    return firestore.client()


def get_user_controller(firestore_client=Depends(get_firestore_client)) -> UserController:
    return UserController(firestore_db=firestore_client)


def get_user_address_controller(firestore_client=Depends(get_firestore_client)) -> AddressController:
    return AddressController(firestore_db=firestore_client)


def get_store_controller(firestore_client=Depends(get_firestore_client)) -> StoreController:
    return StoreController(firestore_db=firestore_client)


def get_order_controller(firestore_client=Depends(get_firestore_client)) -> OrderController:
    return OrderController(firestore_db=firestore_client)


def get_category_controller(firestore_client=Depends(get_firestore_client)) -> CategoryController:
    return CategoryController(firestore_db=firestore_client)


def get_address_controller(firestore_client=Depends(get_firestore_client)) -> AddressController:
    return AddressController(firestore_db=firestore_client)


def get_subcategory_controller(firestore_client=Depends(get_firestore_client)) -> SubCategoryController:
    return SubCategoryController(firestore_db=firestore_client)


def get_products_controller(firestore_client=Depends(get_firestore_client)) -> ProductController:
    return ProductController(firestore_db=firestore_client)


def get_product_bundle_controller(firestore_client=Depends(get_firestore_client)) -> ProductBundleController:
    return ProductBundleController(firestore_db=firestore_client)


def get_messages_controller(firestore_client=Depends(get_firestore_client)) -> MessageController:
    return MessageController(firestore_db=firestore_client)


def get_cart_controller(firestore_client=Depends(get_firestore_client)) -> CartController:
    return CartController(firestore_db=firestore_client)


def get_store_manager_controller(firestore_client=Depends(get_firestore_client)) -> StoreManagerController:
    return StoreManagerController(firestore_db=firestore_client)


def get_banner_controller(firestore_client=Depends(get_firestore_client)) -> BannerController:
    return BannerController(firestore_db=firestore_client)


def get_coupon_controller(firestore_client=Depends(get_firestore_client)) -> CouponController:
    return CouponController(firestore_db=firestore_client)


def inventory_controller(firestore_client=Depends(get_firestore_client)) -> InventoryController:
    return InventoryController(firestore_db=firestore_client)


def request_product_controller(firestore_client=Depends(get_firestore_client)) -> RequestProductController:
    return RequestProductController(firestore_db=firestore_client)


def get_rider_controller(firestore_client=Depends(get_firestore_client)) -> RiderController:
    return RiderController(firestore_db=firestore_client)


def get_remove_stock_controller(firestore_client=Depends(get_firestore_client)) -> RemoveStockController:
    return RemoveStockController(firestore_db=firestore_client)


def get_add_new_stock(firestore_client=Depends(get_firestore_client)) -> AddNewStockController:
    return AddNewStockController(firestore_db=firestore_client)


def get_complaints_controller(firestore_client=Depends(get_firestore_client)) -> ComplaintsController:
    return ComplaintsController(firestore_db=firestore_client)
