# Gaijin's endpoints used ingame  
## Char server endpoints  
- These endpoints all have their root as a char server (example: https://char-lw-nl-005-5.warthunder.com/char)  
- The titles of the sections are to be used as an `action` header value to get the desired data  
- Every `POST` request must have a `token` header given for authentication  
### cln_get_users_terse_info  
- `POST` request  
- Headers  
	- `usersList` (user IDs separated by ';')  
### cln_bulk_set_gblk  
### cln_ww_global_status_short  
### cln_get_leaderboard_json  
### cln_clan_get  
### ano_get_public_userstat  
### cln_get_showcases  
### cln_get_entitlements_price_ex  
### cln_upd_entitlements_full  
### cln_get_events_leaderboard  
### cln_bq_put_batch_json  
### cln_get_short_user_info_jwt  
### cln_upgrade_crew  
### cln_clan_get_leaderboard  
### cln_set_research_clan_unit  
### cln_clan_get_log  
### cln_set_researchable  
### cln_train_aircraft  
### cln_update  
### cln_add_to_wish_list  
### cln_remove_from_wish_list  
### cln_multi_consume_inventory_item_json  
### cmn_get_bin  
### cln_set_current_booster  
### cln_bulk_train_aircraft  
### cln_buy_aircraft  
### cln_save_decals  
### cln_save_attachables  
### cln_find_users_by_nick_prefix_json  
### cln_save_profile_showcase  
### cln_save_pilot_appearance  
### cln_select_title  
### cln_recycle_items  
### cln_inventory_purchase_item  
### cln_apply_spare_item  
### ano_clan_accept_membership_request  
- `POST` request  
- Headers  
	- `userid` (Kicked user)  
	- `uidHint` (Applying user)  
	- `gameVersion`  
- Request form  
	- BLK  
- Response form  
	- "!OK"  
### ano_clan_dismiss_member  
- `POST` request  
- Headers  
	- `userid` (Kicked user)  
	- `uidHint` (Kicking officer)  
	- `gameVersion`  
- Request form  
	- HEX  
- Response form  
	- "!OK"  
### cln_clan_membership_request  
- `POST` request  
- Headers  
	- `userid` (Applying user)  
	- `gameVersion`  
- Request form  
	- HEX  
- Response form  
	- "!OK"  
### cln_get_initial_meta  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
### cln_get_price_ex  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
### cln_set_general_blk  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
	- `appId` (Game ID, WT is 1067)  
### cln_get_ugc_items_info  
### cln_accept_eula  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
	- `returnOnlyEULA`  
### cln_require_unlock  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
### cln_set_starting_info  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
### cln_get_meta_blk  
- `POST` request  
- Header  
	- `uidHint` (Account UID)  
	- `appId` (Game ID, WT is 1067)  
## Contact proxy endpoints  
- Same as before (example: https://contact-proxy-02.gaijin.net/json)  
### cln_get_allowed_to_be_added_to_contacts  
- `POST` request  
- Returns JSON  
- Request form: `Not needed`  
- Response form:  
	```json  
	{  
		"ata": true  
	}  
	```  
	- No clue what this is meant to say  
### GetContacts  
- `POST` request  
- Returns JSON  
- Request form:  
	```json  
	{  
		"groups": ["warthunder"],  
		"id": id,  
		"jsonrpc": "2.0",  
		"method": "GetContacts",  
		"satus": [statuses]  
	}  
	```  
	- Yes it is actually called `satus`  
- Response form:  
	```json  
	{  
		"warthunder": {  
			"approved": [  
				{  
					"uid": userID,  
					"nick": "nickname",  
					"time": UNIX timestamp,  
					"convNick": "nickname",  
					"isRequestor": bool  
				},  
				{...}  
			],  
			"myRequests": [...],  
			"rejectedByMe": [...],  
			"myBlacklist": [...]  
		}  
	}  
	```  
### cln_cs_login  
- `POST` Request  
- Returns JSON  
- Request body:  
	```json  
	{  
		"game":"wt"  
	}  
	```  
	- Sure i guess?  
- Response body:  
	```json  
	{  
		"chardToken": Some kind of token,  
		"user_id": user's ID,  
		"nick": "nickname",  
		"login": {  
			"first": UNIX timestamp,  
			"last": UNIX timestamp,  
		}  
	}  
	```  
## Inventory proxy endpoints  
- Same as before (example: https://inventory-proxy-01.gaijin.net/char)  
### GetItemDefsClient  
### GetInventory  
- `POST` request  
- Headers  
	- `uidHint` (User ID of person to check)  
	- `appid` (for WT it's `1067`)  
- Response form example  
	```json  
	{  
		"response": {  
			"item_json": [  
				{  
						"accountid": "126390297",  
						"appid": 1067,  
						"craftedFrom": "",  
						"expireAt": "",  
						"itemdef": 299004,  
						"itemid": "7059552941",  
						"origin": "external",  
						"quantity": 2,  
						"seenByPlayer": false,  
						"state": "none",  
						"timestamp": "2026-04-29T19:43:10.7254004Z",  
						"tradable_after_timestamp": "0"  
					},  
			]  
		}  
	}  
	```  
### GetItemPrices  
### ExchangeItems  
## User stat proxy endpoints  
- Same as before (example: https://userstat-proxy-01.gaijin.net/char)  
### GetUnlocks  
### GetStats  
### GetUserStatDescList  
## Other endpoints  
### https://auth.gaijinent.com/login.php  
- `POST` request  
- Returns JSON  
- Request form:  
	```json  
	{  
		"client":"unknown_",  
		"game":"wt",  
		"gapp_id":79,  
		"login": "<email>",  
		"meta": 1,  
		"password": "<password>",  
		"v":2  
	}  
	```  
	Optional data:  
	- `client` (Probably used for tracking logins)  
	- `gapp_id` (unsure what this does, probably used for tracking logins)  
	- `meta` (only sends metadata, such as creation location, CC URL used, registration IP, etc.)  
	- `v` (Unsure what this does)  
- Response form schema:  
	```json  
	{  
		"auth": "login",  
		"country": "country tag",  
		"gjnick": "gaijin nickname",  
		"jwt": "token",  
		"lang": "language",  
		"level": "normal",  
		"login": "email used",  
		"nick": "war thunder nickname",  
		"nickorig": "original wt nickname",  
		"status": "OK",  
		"tags": "tags associated with user (e.g. 'email_verified' or 'customer' (yes this exists))",  
		"token": "access token to most parts of the internally used API",  
		"token_exp": "expiration of the token from now in seconds (usually an hour)",  
		"user_id": "the gaijin store ID of the user"  
	}  
	```  
	- No example due to privacy issues with just copy pasting  
	- Using `meta` adds more info, which can vary a lot so I am not documenting that part  
	- The following keys have been found to have the following values that can be assigned  
		- `auth`  
			- `login` (if no 2FA)  
			- `2step` (if 2FA is set up)  
		- `level`  
			- `fastregister`  
			- `normal`  
		- `tags`  
			- `email_verified`  
			- `2step`  
			- `2step_totp`  
			- `customer` (purchased anything in the gaijin shop)  
			- `customer_wt` (purchased anything for WT in gaijin shop)  
			- `customer_el` (purchased anything for Enlisted in gaijin shop)  
			- `gjpass` (account uses gaijin pass)  
			- `google` (account uses google authenticator?)  
			- `liveclone` (account migrated from Xbox to PC)  
			- `player_wt` (has WT account)  
			- `player_wtm` (has WT Mobile account)  
			- `player_el` (has Enlisted account)  
			- `partner_unknown` (?)  
			- `partner_organic` (?)  
			- `phone_verified`  
			- `sso`  
			- `sso_allowed_post`  
			- `steam_el` (Played Enlisted on steam?)  
			- `wt_first_login` (logged in before?)  
			- `wt_quiz_success` (no clue)  
			- `infantry_cbt_requester` (probably a temporary flag, requested Infantry CBT participation)  
			- `lang_*` (computer locale on account creation?)  
- Can extend token lifetime by calling the URL but with the following data:  
	```json  
	{  
		"token": "token"  
	}  
	```  
- The game usually refreshes the token every 30 minutes  
### https://static-ggc.gaijin.net/units/*.png  
- GET request  
- the `*` must be replaced with the internal name of a vehicle you want (e.g. "https://static-ggc.gaijin.net/units/uk_churchill_avre.png")  
### https://newsfeed.gap.gaijin.net/api/patchnotes/warthunder/en/?platform=*  
- GET request  
- The `*` must be replaced with a platform (e.g. `linux64`)  
- Gets the news currently shown in the `changelog` window  
- Returns JSON  
- Request form: `Not needed`  
- Response form example:  
	```json  
	{  
		"status": 200,  
		"result": [  
			{  
				"title": "It’s fixed! №115 + Update 2.55.1.88",  
				"rev": 5,  
				"tags": [],  
				"pinned": 0,  
				"thumb": "https://patchnotes.cdn.gaijin.net/warthunder/Images/2026/Patchnotes/Fixed115_1500\.jpg",  
				"customData": {},  
				"kind": "patchnote",  
				"titleshort": "It’s fixed! №115 + Update 2.55.1.88",  
				"alwaysShowPopup": false,  
				"targets": [  
					"game"  
				],  
				"id": 376,  
				"date": "2026-04-28T17:53:39",  
				"type": "minor",  
				"version": "2.55.1.88"  
			},  
			{...}  
		]  
	}  
	```  
### https://api.gaijinent.com/item_info.php  
- `POST` request  
- Returns JSON  
- Gets premium/event vehicle data  
- Request form:  
	- `guids[]=[guid]` repeated for every single item  
		- Example guid: 009FB77B-92F8-41B7-9307-D6B834AFB345 (VL Pyorremyrsky Pack)  
	- `special=1`  
	- `jwt`  
- Response form:  
	```json  
	{  
		"status": "OK",  
		"items": {  
			"009FB77B-92F8-41B7-9307-D6B834AFB345": {  
				"item_id": "7173",  
				"title": "VL Pyorremyrsky Pack",  
				"url": "https://store.gaijin.net/story.php?id=7173",  
				"short_desc": null,  
				"multi_purch": false,  
				"status": "discard",  
				"shop_price": 19.99,  
				"shop_price_curr": "eur",  
				"can_be_bought": false,  
				"actions": [],  
				"price_usd": 19.99  
			},  
			"0108E1C9-6A59-4838-A67D-1CD8004DACA0": {  
				"item_id": "6553",  
				"title": "Semovente 105/25 Pack",  
				"url": "https://store.gaijin.net/story.php?id=6553",  
				"short_desc": null,  
				"multi_purch": false,  
				"status": "discard",  
				"shop_price": 24.99,  
				"shop_price_curr": "eur",  
				"can_be_bought": false,  
				"actions": [],  
				"price_usd": 24.99  
			},  
			{...}  
		}  
	}  
	```  
	- The following keys have been found to have the following values that can be assigned  
		- `status`  
			- `discard` (GE vehicle)  
			- `publisher` (Pack vehicle)  
### https://login.gaijin.net/en/sso/getShortToken  
## Endpoints not used ingame  
### http://newslist.gaijin.net:8080/news/warthunder/en/js  
### https://warthunder.com/en/community/getclansleaderboard/dif/_hist/page/\[pagenum\]/sort/dr_era5  
## Useful info through webscraping (no direct API)  
### https://warthunder.com/en/game/changelog/  
### https://forum.warthunder.com/t/season-schedule-for-squadron-battles/4446  
