from datetime import datetime
from lib.commanager import commanager
from lib.util import range_to_ps, ps_to_range
from lib.trimdata import trim_data
from lib.save_data import save_data
from lib.config import get_config

cmm = commanager()

config = get_config()
radar_config = config["radar"]

# these are in meters
start_range = range_to_ps(radar_config["scanStart"])
end_range = range_to_ps(radar_config["scanEnd"])

actual_config = cmm.init_radar(baseIntegrationIndex=radar_config["integrationIndex"], persistFlag=1,
                               scanStart=start_range, scanEnd=end_range, nodeID=6)

# figure out what the actual ranges are
startRange = ps_to_range(actual_config["scanStart"])
endRange = ps_to_range(actual_config["scanEnd"])

# start the scan
data = cmm.exec_scan(
    scanCount=radar_config["scanCount"], scanInterval=radar_config["scanInterval"])

# turn off the radar
cmm.sleep_radar()

# there are 0-pads, so get rid of them
data = trim_data(data)

# write data to file

# get current date and time string
now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_data(data, startRange, endRange, f"./data/{now}.pkl")
