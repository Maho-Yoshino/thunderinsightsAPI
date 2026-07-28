from utils.auth import UserTokenCache, AuthenticationError
users_cache = UserTokenCache()

from utils.vehicleParser import Vehicles # Must be after users_cache declaration, due to using users_cache
vehicle_cache = Vehicles()