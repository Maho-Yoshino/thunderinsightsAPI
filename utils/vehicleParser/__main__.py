# This file is purely used for debugging the units database unit
from asyncio import new_event_loop, set_event_loop

async def runtime():
	from . import Vehicles
	vehicles = Vehicles()
	#await vehicles.setup()
	await vehicles._write_vehicles("saab_jas39e")
	result = await vehicles.get("saab_jas39e")
	pass # Used for breakpoint
	...
def main():
	loop = new_event_loop()
	set_event_loop(loop)
	loop.run_until_complete(runtime())
	pass # Used for breakpoint

if __name__ == '__main__':
	main()
