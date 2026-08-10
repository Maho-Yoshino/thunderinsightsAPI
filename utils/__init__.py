
from utils.network import NetworkManager, NetworkError
networkManager = NetworkManager()

from utils.auth import UserTokenCache, AuthenticationError
users_cache = UserTokenCache(networkManager)

from utils.vehicleParser import Vehicles # Must be after users_cache declaration, due to using users_cache
vehicle_cache = Vehicles()