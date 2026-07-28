from enum import IntEnum, Enum, auto
from re import search as re_search
from fastapi import HTTPException
from typing import Any

class ServerPool(IntEnum):
	CHAR = 0
	INVENTORY = 1
	USERSTAT = 2
	CONTACTS = 3
	UGC = 4
class Action(Enum): # Filtered actions, only leaving those that do not affect the account directly
	#region Char
	cln_get_users_terse_info = auto(), ServerPool.CHAR
	cln_get_leaderboard_json = auto(), ServerPool.CHAR  
	cln_clan_get = auto(), ServerPool.CHAR  
	ano_get_public_userstat = auto(), ServerPool.CHAR  
	cln_get_showcases = auto(), ServerPool.CHAR  
	cln_get_entitlements_price_ex = auto(), ServerPool.CHAR  
	cln_upd_entitlements_full = auto(), ServerPool.CHAR  
	cln_get_events_leaderboard = auto(), ServerPool.CHAR  
	cln_clan_get_leaderboard = auto(), ServerPool.CHAR  
	cln_clan_get_log = auto(), ServerPool.CHAR  
	cln_clan_find_by_prefix = auto(), ServerPool.CHAR  
	cln_get_price_ex = auto(), ServerPool.CHAR
	cln_require_unlock = auto(), ServerPool.CHAR
	cln_get_news_ex = auto(), ServerPool.CHAR
	ano_get_wishlist_json = auto(), ServerPool.CHAR
	#endregion
	#region Contact proxy
	cln_find_users_by_nick_prefix_json = auto(), ServerPool.CONTACTS
	#endregion
	#region User stat
	GetUnlocks = auto(), ServerPool.USERSTAT
	GetStats = auto(), ServerPool.USERSTAT
	GetUserStatDescList = auto(), ServerPool.USERSTAT
	#endregion
	#region UGC
	cln_get_ugc_items_info = auto(), ServerPool.UGC
	#endregion
class UserAction(Enum):
	#region Char
	cln_upgrade_crew = auto(), ServerPool.CHAR
	cln_set_research_clan_unit = auto(), ServerPool.CHAR
	cln_set_researchable = auto(), ServerPool.CHAR
	cln_train_aircraft = auto(), ServerPool.CHAR
	cln_add_to_wish_list = auto(), ServerPool.CHAR
	cln_remove_from_wish_list = auto(), ServerPool.CHAR
	cln_multi_consume_inventory_item_json = auto(), ServerPool.CHAR
	cln_set_current_booster = auto(), ServerPool.CHAR
	cln_bulk_train_aircraft = auto(), ServerPool.CHAR
	cln_buy_aircraft = auto(), ServerPool.CHAR
	cln_save_profile_showcase = auto(), ServerPool.CHAR
	cln_save_pilot_appearance = auto(), ServerPool.CHAR
	cln_select_title = auto(), ServerPool.CHAR
	cln_recycle_items = auto(), ServerPool.CHAR
	cln_inventory_purchase_item = auto(), ServerPool.CHAR
	cln_apply_spare_item = auto(), ServerPool.CHAR
	cln_clan_membership_request = auto(), ServerPool.CHAR
	ano_clan_accept_membership_request = auto(), ServerPool.CHAR
	ano_clan_dismiss_member = auto(), ServerPool.CHAR
	ano_clan_change_member_role = auto(), ServerPool.CHAR
	ano_clan_reject_membership_request = auto(), ServerPool.CHAR
	cln_clan_leave = auto(), ServerPool.CHAR
	cln_flush_clan_exp_to_unit = auto(), ServerPool.CHAR
	#endregion
	#region Contacts proxy
	GetContacts = auto(), ServerPool.CONTACTS
	cln_cs_login = auto(), ServerPool.CONTACTS
	#endregion
	#region Inventory Proxy
	GetItemDefsClient = auto(), ServerPool.INVENTORY
	GetInventory = auto(), ServerPool.INVENTORY
	GetItemPrices = auto(), ServerPool.INVENTORY
	ExchangeItems = auto(), ServerPool.INVENTORY
	#endregion

class GaijinErrorCodes(Enum): # TODO: Finish documenting gaijin error codes
	# Will require a lot of testing to finish
	"""Enum for Gaijin's error codes."""
	# HTTP code, error details
	CLAN_NOT_MEMBER = {
		"code": 403, 
		"detail":"You are not a member of the given clan"
	} 
	CLAN_CANDIDATE_TIMEOUT = {
		"code": 400, 
		"detail":"You are already a candidate for this clan"
	}
	CLAN_YOU_HAVE_NO_RIGHT = {
		"code": 403,
		"detail": "You do not have permission to do this action"
	}
	CLAN_USER_IS_NOT_CANDIDATE = {
		"code": 404,
		"detail": "The given user is not an applicant"
	}
	DECLINE_TO_CREATE_NEW_PROFILE = {
		"code": 403,
		"detail": "User doesn't exist"
	}
	CLAN_IS_NOT_EXISTS = {
		"code": 404,
		"detail": "Searched clan doesn't exist"
	}
	@staticmethod
	def parse(response: bytes) -> None:
		"""Parse a Gaijin error code string into a properly formatted `HTTPException`. Returns early if error is not found or not given"""
		code: str = response.decode("utf-8")

		try:
			match = re_search(r"!ERROR:(.*)", code.upper())
			if match is None: return

			err = GaijinErrorCodes[ match.group(1).strip() ]
			raise HTTPException(
				status_code=err.value["code"], 
				detail=err.value["detail"]
			)
		except ValueError:
			raise HTTPException(500, detail=code)