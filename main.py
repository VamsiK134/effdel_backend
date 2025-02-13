import logging
import traceback
import uuid
from typing import List, Optional
from datetime import datetime, timezone
import firebase_admin
from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from add_new_stock.model.add_new_stock_model import AddNewStockModel
from coupons.model.coupon_model import CouponsModelIn, CouponsModelOut
from orders.models.orders_model import OrderStatus, Refund, OrderOut, RiderInfo, BaseOrder, OrderIn
from product_requests.model.product_request_model import ProductRequestModel, ProductRequestStatus
from products.model.product_model import Product, ProductModelOut
from users.view.user_view import router as views_users_router
from user_address.view.address_view import router as views_address_router
from stores.view.store_view import router as views_store_router
# from orders.view.orders_view import router as views_orders_router
from messages.view.messages_view import router as views_messages_router
from products.view.product_view import router as views_product_router
from products.view.product_bundle_view import router as views_product_bundle_router
from categories.view.category_view import router as views_category_router
from sub_category.view.sub_category_view import router as views_sub_category_router
from store_managers.view.store_manager_view import router as views_store_manager_router
from banners.view.banner_view import router as views_banner_router
from coupons.view.coupons_view import router as views_coupon_router
from inventory.view.inventory_view import router as view_inventory_router
from riders.view.rider_view import router as views_rider_router
from product_requests.view.product_request_view import router as products_request_view
from add_new_stock.view.add_new_stock_view import router as add_new_stock_view
from inventory.view.remove_stock_view import router as remove_stock_view
from complaints.view.complaints_view import router as complaints_view

app = FastAPI()
cred = credentials.Certificate("source.json")
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()

# Include routers
app.include_router(views_users_router)
app.include_router(views_address_router)
app.include_router(views_store_router)
app.include_router(views_product_router)
# app.include_router(views_orders_router)
app.include_router(views_messages_router)
app.include_router(views_product_bundle_router)
app.include_router(views_category_router)
app.include_router(views_sub_category_router)
app.include_router(views_store_manager_router)
app.include_router(views_banner_router)
app.include_router(views_coupon_router)
app.include_router(view_inventory_router)
app.include_router(views_rider_router)
app.include_router(products_request_view)
app.include_router(add_new_stock_view)
app.include_router(remove_stock_view)
app.include_router(complaints_view)

origins = [
    "https://effdelbackendapis.el.r.appspot.com",
    "http://localhost:8080",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello EffDel"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


def generate_order_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # Current timestamp with milliseconds
    random_digits = uuid.uuid4().hex[:6]  # 6 random hexadecimal digits
    order_id = f"{timestamp}{random_digits}"
    return order_id


# create order
@app.post("/orders")
async def create_order(order: BaseOrder):
    order_id = generate_order_id()

    # Convert enum to a storable format (e.g., string)
    order_status_value = order.order_status.value

    order_dict = order.dict()
    order_dict["order_id"] = order_id
    order_dict["order_status"] = order_status_value  # Use the converted value

    firestore_db.collection('Orders').document(order_id).set(order_dict)

    return {"message": "Order created successfully", "order": order_dict}


# Endpoint to get all orders
@app.get("/orders/")
async def get_all_orders():
    orders = firestore_db.collection('Orders').stream()
    return [order.to_dict() for order in orders]


# Endpoint to get orders based on order id
@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    try:
        doc_ref = firestore_db.collection("Orders").document(order_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return HTTPException(status_code=500, detail="Internal Server Error")


# Endpoint to get orders by user ID
@app.get("/orders/user/{user_id}/")
async def get_orders_by_user_id(user_id: str):
    orders = firestore_db.collection('Orders').where("user_id", "==", user_id).stream()
    return [order.to_dict() for order in orders]


# Endpoint to update order status by order ID
@app.put("/orders/{order_id}/status/")
async def update_order_status(order_id: str, new_status: OrderStatus):
    order_ref = firestore_db.collection('Orders').document(order_id)
    order = order_ref.get()
    if order.exists:
        order_ref.update({"order_status": new_status.value, "modified_timestamp": datetime.now(timezone.utc)})
        return {"message": "Order status updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")


@app.get('/123orders/timestamp')
async def update_order_timestamp():
    order_ref = firestore_db.collection('Orders').get()

    now = datetime.now(timezone.utc)

    # order_ref.fo
    print(order_ref)
    for order in order_ref:
        order.update({"modified_timestamp": now})


# Endpoint to get orders based on orders status
@app.get("/get_orders_by_status")
async def get_orders_by_status(status: OrderStatus):
    orders_ref = firestore_db.collection('Orders').where("order_status", "==", status.value).order_by(
        'modified_timestamp', direction=firestore.Query.DESCENDING)
    orders = orders_ref.stream()
    return [order.to_dict() for order in orders]


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order_ref = firestore_db.collection("Orders").document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = order_doc.to_dict()
    if order_data["status"] != "accepted":
        raise HTTPException(status_code=400, detail="Order is not accepted")
    return order_data


def update_order(order_id: str, order_data: OrderIn):
    # Assuming `order_id` is the Firestore document ID
    order_ref = firestore_db.collection('Orders').document(order_id)
    order_data_dict = order_data.dict(exclude_unset=True)  # Convert Pydantic model to dict excluding unset fields
    order_ref.update(order_data_dict)


# FastAPI endpoint to update an order by order_id
@app.put("/orders/{order_id}")
async def update_order_by_id(
        order_id: str,
        order_data: OrderIn  # Use OrderIn model for input data
):
    try:
        update_order(order_id, order_data)
        return {"message": f"Order {order_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


# def get_orders() -> list:
#     orders_ref = firestore_db.collection('Orders').stream()
#     orders = [doc.to_dict() for doc in orders_ref]
#     return orders
#
#
#
#
# @app.get('/order_status_count', response_model=Dict[str, int])
# async def order_status_count() -> Dict[str, int]:
#     orders = get_orders()
#     status_count = Counter[[order['order_status'] for order in orders]]
#     return status_count

def get_orders() -> List[BaseOrder]:
    orders_ref = firestore_db.collection('Orders').stream()
    orders = [doc.to_dict() for doc in orders_ref]
    return [BaseOrder(**order) for order in orders]


@app.get('/order_status_count', response_model=dict)
async def order_status_count() -> dict:
    orders = get_orders()
    status_count = {status.value: sum(1 for order in orders if order.order_status == status) for status in OrderStatus}
    return status_count


@app.put("/orders/{order_id}/assign_rider")
async def assign_rider(order_id: str, rider_info: RiderInfo):
    # Check if order exists
    order_ref = firestore_db.collection("Orders").document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update rider information in the order document
    order_ref.update({
        "rider_name": rider_info.rider_name,
        "rider_id": rider_info.rider_id
    })

    return {"message": f"Rider assigned to order {order_id}"}


@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: str):
    # Retrieve order data from Firestore
    order_ref = firestore_db.collection("Orders").document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")

    order_data = order_doc.to_dict()

    # Fetch additional rider data based on rider_id
    rider_id = order_data.get("rider_id")
    if rider_id:
        rider_ref = firestore_db.collection("riders").document(rider_id)
        rider_doc = rider_ref.get()
        if rider_doc.exists:
            rider_data = rider_doc.to_dict()
            order_data["rider_name"] = rider_data.get("name")

    return order_data


@app.put("/refund/{order_id}")
async def update_refunds(order_id: str, refunds: List[Refund]):
    # Retrieve order data from Firestore
    order_ref = firestore_db.collection("Orders").document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order document with new refund data
    order_ref.update({"refunds": [refund.dict() for refund in refunds]})

    return {"message": "Refund data updated successfully"}


@app.get("/get_refund/{order_id}", response_model=List[Refund])
async def get_refunds(order_id: str):
    # Retrieve order data from Firestore
    order_ref = firestore_db.collection("Orders").document(order_id)
    order_doc = order_ref.get()

    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")

    # Extract refund data from order document
    order_data = order_doc.to_dict()
    refunds = order_data.get("refunds", [])

    return refunds


@app.put("/rider/pickup/{order_id}")
async def pickup_order(order_id: str, rider_id: str):
    try:
        # Check if order exists and is in progress
        order_ref = firestore_db.collection('Orders').document(order_id)
        order_doc = order_ref.get()
        if not order_doc.exists:
            raise HTTPException(status_code=404, detail="Order not found")
        order_data = order_doc.to_dict()
        if order_data['order_status'] != OrderStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Order is not in progress")

        # Update order status to indicate pickup by rider
        order_ref.update({'order_status': OrderStatus.DELIVERED.value, 'rider_id': rider_id})

        return {"message": "Order picked up successfully by rider"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_products_based/{sub_category_id}", response_model=List[Product])
async def get_products_by_subcategory(sub_category_id: str):
    products_ref = firestore_db.collection('Products')
    query = products_ref.where('sub_category_id', '==', sub_category_id).stream()
    matched_products = []
    for doc in query:
        product_data = doc.to_dict()
        product = Product(**product_data)
        matched_products.append(product)
    if not matched_products:
        raise HTTPException(status_code=404, detail="Products not found")
    return matched_products


ranges = {
    "0-100": (0, 100),
    "100-200": (100, 200),
    "200+": (200, float('inf'))
}


def categorize_inventory(inventory: int) -> str:
    for key, (start, end) in ranges.items():
        if start <= inventory < end:
            return key
    return "Unknown"


# async def get_products_range(inventory_range: str) -> List[ProductModelOut]:
#     products = []
#     products_ref = firestore_db.collection('Products')
#     query = products_ref.stream()
#
#     for doc in query:
#         product_data = doc.to_dict()
#
#         # Extract current_inventory from product_data dictionary
#         current_inventory = product_data.get('current_inventory')
#         if current_inventory is None:
#             continue
#
#         # Categorize current_inventory
#         inventory_range = categorize_inventory(current_inventory)
#
#         # Filter by inventory_range if provided
#         if inventory_range and inventory_range != inventory_range:
#             continue
#
#         # Create ProductModelOut instance for response
#         product_out = ProductModelOut(
#             **product_data,  # Assuming product_data contains all fields for ProductModelOut
#             product_id=doc.id,
#             timestamp=datetime.now()
#         )
#         products.append(product_out)
#
#     if not products:
#         raise HTTPException(status_code=404, detail="No products found")
#
#     return products
#
@app.get("/products_inventory_range/", )
async def get_products_range(inventory_range: str = None) -> List[dict]:
    products = []
    # Fetch products from Firestore
    products_ref = firestore_db.collection('Products')
    query = products_ref.stream()

    for doc in query:
        product = doc.to_dict()
        # Categorize current inventory
        product['inventory_range'] = categorize_inventory(product['current_inventory'])
        products.append(product)

    if inventory_range:
        # Filter products based on inventory range
        products = [product for product in products if product['inventory_range'] == inventory_range]
        if not products:
            raise HTTPException(status_code=404, detail="No products found for the specified inventory range")

    return products


# @app.get("/products_inventory_range/", response_model=List[Product])
# async def get_products_range(
#         inventory_range: Optional[str] = None,
#         page: int = Query(1, ge=1),
#         per_page: int = Query(10, ge=1)) -> List[Product]:
#     products = []
#     # Fetch products from Firestore
#     products_ref = firestore_db.collection('Products')
#     query = products_ref.stream()
#
#     for doc in query:
#         product = doc.to_dict()
#         # Categorize current inventory
#         product['inventory_range'] = categorize_inventory(product['inventory']['current_inventory'])
#         products.append(product)
#
#     if inventory_range:
#         # Filter products based on inventory range
#         products = [product for product in products if product['inventory_range'] == inventory_range]
#         if not products:
#             raise HTTPException(status_code=404, detail="No products found for the specified inventory range")
#
#     # Pagination
#     start = (page - 1) * per_page
#     end = start + per_page
#     paginated_products = products[start:end]
#
#     if not paginated_products and page > 1:
#         raise HTTPException(status_code=404, detail="Page number out of range")
#
#     return paginated_products


inventory_ref = firestore_db.collection('Products')
product_request_ref = firestore_db.collection('ProductRequest')


# Endpoints
@app.post("/add-new-stock-updation", response_model=AddNewStockModel)
async def add_new_stock(new_stock: AddNewStockModel):
    try:
        # Update current inventory
        inventory_doc = inventory_ref.document(new_stock.product_id)
        inventory_snapshot = inventory_doc.get()

        if inventory_snapshot.exists:
            current_inventory = inventory_snapshot.to_dict()['current_inventory']
            updated_inventory = current_inventory + new_stock.add_new_stock_units
        else:
            updated_inventory = new_stock.add_new_stock_units

        inventory_doc.update({'current_inventory': updated_inventory})

        # Update product unit request
        product_request_doc = product_request_ref.where("request_id", "==", new_stock.request_id).get()
        if not product_request_doc:
            raise HTTPException(status_code=404, detail="Not Found request id")
        current_request = product_request_doc[0].to_dict()

        final_status = "matched" if new_stock.add_new_stock_units == int(current_request[
                                                                             'product_unit_request']) else "unmatched"

        # updated_quantity = int(current_request['product_unit_request']) + new_stock.new_stock_units

        product_request_ref.document(product_request_doc[0].id).update(
            {'update_qty': new_stock.add_new_stock_units, 'status': final_status})
        data = {"product_id": new_stock.product_id,
                "request_id": new_stock.request_id,
                "add_new_stock_units": new_stock.add_new_stock_units,
                "timestamp": datetime.now()}
        firestore_db.collection("AddNewStock").add(data)

        return new_stock

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/product-requests/", response_model=list[ProductRequestModel])
async def get_product_requests_by_status(status: ProductRequestStatus):
    try:
        requests_ref = firestore_db.collection("ProductRequest")
        query = requests_ref.where("status", "==", status.value)
        query_result = query.stream()

        product_requests = []
        for doc in query_result:
            request_data = doc.to_dict()
            product_request = ProductRequestModel(**request_data)
            product_requests.append(product_request)

        return product_requests

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product requests: {str(e)}")


