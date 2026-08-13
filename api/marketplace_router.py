from os import getenv
from typing_extensions import Annotated
from typing import Any
from random import randint
from datetime import datetime, UTC
from fastapi import APIRouter, Query, Path, Request as faRequest, Depends, HTTPException
from tools import Request
from utils.auth import UserTokenCache
from utils.helper import dtToTimestampMs
from api.backends.marketplace import *
from api.models import Marketplace
from api.shared import limiter, get_auth

router = APIRouter(
    prefix="/market",
    tags=["marketplace"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/sell/{itemHash}",
    summary="Puts up a sell order for the given `itemHash`",
    responses={
        200: {"description": "Sell order has successfully been placed", "model": list[Marketplace.SellModel]},
        400: {"description": "Count is too high"},
        404: {"description": "Item could not be found in the inventory"}
    }
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def sell_item(
    request: faRequest,
    itemHash: Annotated[str, Path(description="The item's hash value")],
    price: Annotated[float, Query(description="The price in GJN to sell for (Includes gaijin's fee, not the value you get)", ge=0.1, le=2000)], 
    count: Annotated[int, Query(description="The amount to sell at once", gt=0)] = 1,
    anonymous: Annotated[bool, Query(description="Appear as an anonymous seller")] = False,
    user: UserTokenCache.Entry = Depends(get_auth)
):
    agree_stamp = dtToTimestampMs(datetime.now(UTC))

    itemsInInv = await item_in_inventory(user, itemHash)
    if itemsInInv is None:
        raise HTTPException(404, "Item not found in inventory")
    if len(itemsInInv.ids) < count:
        raise HTTPException(400, "Count is higher than the items in inventory")

    price = price
    gaijin_fee = price*0.15
    seller_should_get = price-gaijin_fee

    solditems = []
    for i in range(count):
        assetId = itemsInInv.ids.pop()
        resp = await Request.send_template(
            user,
            "cln_market_sell",
            body={
                "transactid": randint(10**6, 10**15),
                "reqstamp": dtToTimestampMs(datetime.now(UTC)),
                "assetid": assetId,
                "amount": 1,
                "price": int(price*10000),
                "seller_should_get": int(seller_should_get*10000),
                "agree_stamp": agree_stamp,
                "privateMode": anonymous,
                "contextid": itemsInInv.contextid
            }
        )
        solditems.append({
            "item": assetId,
            "success": "response" in resp and resp["response"].get("success", False),
            "price": price,
            "seller_gets": seller_should_get
        })
    return solditems

@router.post(
    "/buy/{itemHash}",
    summary="Puts up a buy order for the given `itemHash`",
    responses={
        200: {"description": "The buy order has successfully been placed", "model": Marketplace.GenericEmptyResponse},
        400: {"description": "Something prevented the buy order from being placed"},
        403: {"description": "Not enough funds"},
        404: {"description": "The given item doesn't exist"}
    }
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def buy_item(
    request: faRequest,
    itemHash: Annotated[str, Path(description="The item's hash value")],
    price: Annotated[float, Query(description="The price in GJN to buy for", ge=0.1, le=2000)], 
    count: Annotated[int, Query(description="The amount to buy", gt=0)] = 1,
    anonymous: Annotated[bool, Query(description="Appear as an anonymous buyer")] = False,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> Marketplace.GenericEmptyResponse:
    agree_stamp = dtToTimestampMs(datetime.now(UTC))
    resp = await Request.send_template(
        user,
        "cln_market_buy",
        body={
            "transactid": randint(10**6, 10**15),
            "reqstamp": dtToTimestampMs(datetime.now(UTC)),
            "market_name": itemHash,
            "amount": count,
            "price": int(price*10000),
            "agree_stamp": agree_stamp,
            "privateMode": anonymous,
        }
    )
    if "response" not in resp:
        raise HTTPException(500, "An unexpected error occurred")
    resp = resp["response"]
    if "error" in resp:
        if resp["error"] == "ASSET_NOT_FOUND":
            raise HTTPException(404, "Item doesn't exist")
        elif "details" in resp and resp["details"] == "NOT_ENOUGH_FUNDS":
            raise HTTPException(403, "Not enough funds")
        raise HTTPException(500, resp["error"])     
    if resp.get("success", False):
        return {
            "success": True
        }
    raise HTTPException(400, "Failed to put up buy order")

@router.get(
    "/inventory",
    summary="Gets the account's inventory contents"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def getInventory(
    request: faRequest,
    user: UserTokenCache.Entry = Depends(get_auth)
):
    inv = await get_inventory(user)
    return [i.to_json() for i in inv]

@router.get(
    "/balance",
    summary="Gets the account's balance"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_balance(
    request: faRequest,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> float:
    data = await Request.send_template(
        user,
        "GetBalance"
    )
    if data.get("status") == "OK":
        return data["balance"]/10000
    raise HTTPException(500, "Failed to get balance")

@router.get(
    "/search",
    summary="Searches the marketplace for a given item"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def searchItem(
    request: faRequest,
    name: Annotated[str, Query(title="The item to search for. Leave empty to search for ALL units")] = "",
    count: Annotated[int, Query(title="Amount to get at once")] = 25,
    page: Annotated[int, Query(title="Pagination page. Works based off of `count`")] = 0,
    user: UserTokenCache.Entry = Depends(get_auth)
):
    data = await Request.send_template(
        user,
        "cln_market_search",
        body={
            "count": count,
            "skip": count*page,
            "text": name
        }
    )
    if "response" in data:
        data:list[dict[str, Any]] = data["response"]["assets"]
    else:
        raise HTTPException(500, "Could not get item data")
    for item in data:
        item["sell_price"] = item["price"] / 100000000
        item["buy_price"] = item["buy_price"] / 100000000
        item.pop("price")

        item["sell_orders"] = item["depth"]
        item["buy_orders"] = item["buy_depth"]
        item.pop("depth")
        item.pop("buy_depth")

        item.pop("appid")
        item.pop("color")
        item.pop("asset_class")

    return data

@router.get(
    "/{vehicleHash}/orders/history",
    summary="Retrieves marketplace history data about the given vehicle"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_vehicle_history(
    request: faRequest,
    vehicleHash: Annotated[str, Path(title="The vehicle to look up")],
    user: UserTokenCache.Entry = Depends(get_auth)
):
    pairData = await Request.send_template(
        user,
        "cln_get_pair_stat",
        body={
            "market_name":vehicleHash
        }
    )
    if "response" in pairData:
        pairData = pairData["response"]
    else:
        raise HTTPException(500, "An unexpected error occurred")

    ret_data = {
        "short":[],
        "whole":[]
    }
    for i in pairData["1h"]:
        ret_data["short"].append({
            "timestamp": i[0],
            "price": i[1]/10000,
            "transactions_count": i[2]
        })
    for i in pairData["1d"]:
        ret_data["whole"].append({
            "timestamp": i[0],
            "price": i[1]/10000,
            "transactions_count": i[2]
        })
    return ret_data

@router.get(
    "/{vehicleHash}/orders",
    summary="Retrieves marketplace data about the given vehicle"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_Vehicle_orders(
    request: faRequest,
    vehicleHash: Annotated[str, Path(title="The vehicle to look up")],
    user: UserTokenCache.Entry = Depends(get_auth)
):
    books_brief = await Request.send_template(
        user,
        "cln_books_brief",
        body={
            "market_name": vehicleHash
        }
    )
    if "response" in books_brief:
        books_brief = books_brief["response"]
    else:
        raise HTTPException(500, "An unexpected error occurred")

    ret_data = {}
    ret_data["buy_orders"] = books_brief["depth"]["BUY"]
    ret_data["sell_orders"] = books_brief["depth"]["SELL"]
    ret_data["buy_prices"] = [{"price":i[0]/10000,"amount":i[1]} for i in books_brief["BUY"]]
    ret_data["sell_prices"] = [{"price":i[0]/10000,"amount":i[1]} for i in books_brief["SELL"]]
    return ret_data

@router.get(
    "/{vehicleHash}/view",
    summary="Views the vehicle ingame"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def view_vehicle(
    request: faRequest,
    vehicleHash: Annotated[str, Path(title="The vehicle's hash to view")],
    user: UserTokenCache.Entry = Depends(get_auth)
) -> bool:
    hashData = await Request.send_template(
        user,
        "cln_market_get_asset_class",
        body={
            "name":vehicleHash
        }
    )
    if "response" not in hashData or "asset_class" not in hashData["response"]:
        raise HTTPException(404, "Vehicle not found")
    hashData = hashData["response"]["asset_class"]
    if len(hashData) <= 0:
        raise HTTPException(404, "Vehicle not found")
    resp = await Request.send_template(
        user,
        "market_view_item1",
        body={
            "params":{
                "appId": "1067",
                "assetClass": [
                    {
                        "name": hashData[0]["name"],
                        "value": hashData[0]["value"]
                    }
                ]
            }
        }
    )
    await Request.send_template(
        user,
        "market_view_item2"
    )
    return resp.get("status") == "ok"

@router.get(
    "/{vehicleHash}",
    summary="Gets metadata about the given vehicle"
)
@limiter.shared_limit("trade", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_vehicle(
    request: faRequest,
    vehicleHash: Annotated[str, Path(title="The vehicle to look up")],
    user: UserTokenCache.Entry = Depends(get_auth)
):
    hashData = await Request.send_template(
        user,
        "cln_market_get_asset_class",
        body={
            "name":vehicleHash
        }
    )
    if "response" not in hashData or "asset_class" not in hashData["response"]:
        raise HTTPException(404, "Vehicle not found")
    hashData = hashData["response"]["asset_class"]
    if len(hashData) <= 0:
        raise HTTPException(404, "Vehicle not found")
    resp = await Request.send_template(
        user,
        "GetAssetClassInfo",
        body={
            "class_name0": hashData[0]["name"],
            "class_value0": hashData[0]["value"]
        }
    )
    if "result" not in resp or "asset" not in resp["result"]:
        raise HTTPException(404, "Vehicle data could not be obtained")
    resp = resp["result"]["asset"]
    ret_data = {}

    ret_data["description"] = resp["descriptions"][0]["value"]
    ret_data["tags"] = resp["tags"]
    ret_data["sellable"] = bool(resp["marketable"])
    ret_data["hash"] = resp["market_hash_name"]
    ret_data["market_name"] = resp["market_name"]
    ret_data["display_name"] = resp["name"]
    ret_data["images"] = {
        "icon": resp["icon_url"],
        "image": resp["icon_url_large"]
    }
    ret_data["type"] = resp["type"]

    return ret_data
