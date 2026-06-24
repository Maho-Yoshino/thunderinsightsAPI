from enum import IntEnum, Enum, auto

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