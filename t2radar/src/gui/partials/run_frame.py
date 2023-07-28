from datetime import datetime
from tkinter import *
from tkinter.ttk import *
from gui.logger import Logger
from gui.state import get_state, set_state
from lib.config import write_config_file
from lib.commanager import commanager
from lib.trimdata import trim_data
from lib.save_data import save_data
from lib.util import range_to_ps, ps_to_range

comm = commanager()


class RunFrame(Frame):
    statusLog = Logger(maxLen=10)
    log = statusLog.log
    run_dynamic = True
    snapshot_count = 1

    def __init__(self, root: Tk, update_status: callable):
        Frame.__init__(self, root)
        self.update_status = update_status
        self.root = root

        self.log("App Booted!")

        root = Frame(root)

        # title
        title = Label(root, text="Scan Panel", font=("Helvetica", 16))
        title.pack()

        # create a button to upload the config
        upload_config_button = Button(
            root, text="Upload Config", command=self.upload_config_handler)
        upload_config_button.pack()

        # create a button to download the config
        download_config_button = Button(
            root, text="Download Config", command=self.download_config_handler)
        download_config_button.pack()

        # create a button to start the scan
        start_scan_button = Button(
            root, text="Start Scan", command=self.start_scan_handler)
        start_scan_button.pack()

        # create a button to end the scan
        end_scan_button = Button(
            root, text="End Scan", command=self.end_scan_handler)
        end_scan_button.pack()

        # create a button to take a snapshot
        take_snapshot_button = Button(
            root, text="Take Snapshot", command=self.__snapshot_scan)
        take_snapshot_button.pack()

        # create a button to save the data
        save_snapshot_button = Button(
            root, text="Save Snapshots", command=self.__dump_snapshots)
        save_snapshot_button.pack()

        # create a button to clear the log
        clear_log_button = Button(
            root, text="Clear Log", command=self.clear_log_handler)
        clear_log_button.pack()

        # create a small space
        space = Label(root, text="")
        space.pack()

        # title
        title = Label(root, text="Log", font=("Helvetica", 16))
        title.pack()

        # create a box of status messages
        self.logItems = Variable(value=self.statusLog.get())
        status_box = Listbox(root, height=10, width=70,
                             listvariable=self.logItems)
        status_box.pack()

        # fill any extra space
        root.pack(fill=Y, expand=True)

        self.update_log_box()

    def upload_config_handler(self):
        """ Uploads the config to the radar """

        self.log("Uploading Config")
        self.update_log_box()

        # grab latest config
        config = get_state("config")["radar"]

        integration_index = config["integrationIndex"]
        scan_start = config["scanStart"]
        scan_end = config["scanEnd"]

        try:
            resp = comm.send_sync("MRM_SET_CONFIG_REQUEST", False, baseIntegrationIndex=integration_index,
                                  scanStart=scan_start, scanEnd=scan_end, persistFlag=1)
        except TimeoutError:
            self.log("FAILED: Did not receive confirm.")
            self.update_log_box()
            return

        # check if all went well
        if resp["status"] == 0:
            self.log("Config Uploaded")
        else:
            self.log(f"FAILED. Error code: {resp['status']}")

        # download config from radar to sync settings
        self.download_config_handler()
        set_state("data_ready", True)

        self.update_log_box()

    def download_config_handler(self):
        """ Downloads the config from the radar """
        self.log("Downloading Config")
        self.update_log_box()

        # grab latest config
        config = get_state("config")

        try:
            resp = comm.send_sync("MRM_GET_CONFIG_REQUEST", False)

        except TimeoutError:
            self.log("FAILED: Did not receive confirm.")
            self.update_log_box()
            return

        # check if all went well
        if resp["status"] == 0:
            self.log("Config Downloaded")
        else:
            self.log(f"FAILED. Error code: {resp['status']}")
            self.update_log_box()
            return

        # update config
        config["radar"]["integrationIndex"] = resp["baseIntegrationIndex"]
        config["radar"]["scanStart"] = resp["scanStart"]
        config["radar"]["scanEnd"] = resp["scanEnd"]

        # add it to the log
        self.log(f"New Integration: {resp['baseIntegrationIndex']}")
        self.log(f"Scan start (ps): {resp['scanStart']}")
        self.log(f"Scan End (ps): {resp['scanEnd']}")

        set_state("config", config)
        write_config_file(config)

        # update the status
        self.update_status()

        self.log("Config Updated")
        self.update_log_box()

    def start_scan_handler(self):

        # get the current settings
        config = get_state("config")["radar"]

        # if scan_count is not 0, then we are doing a static scan
        if config["scanCount"] != 65535:

            self.root.after(1, self.__static_scan)
            self.update_log_box()
        else:
            self.run_dynamic = True
            success = self.__start_dynamic_scan()
            if not success:
                self.update_log_box()
                return

            self.__run_dynamic_scan()

    def end_scan_handler(self):
        self.log("Ending Scan")
        self.update_log_box()

        try:
            comm.send_sync("MRM_CONTROL_REQUEST", True,
                           scanCount=0, scanIntervalTime=0)
        except TimeoutError:
            self.log("FAILED: Did not receive confirm.")
            return False
        except Exception as e:
            self.log(f"FAILED: {e}")
            return False

        self.update_log_box()

    def clear_log_handler(self):
        self.statusLog.clear()
        self.log("Log Cleared")
        self.update_log_box()

    def update_log_box(self):
        """Updates the log box"""

        contents = self.statusLog.get()
        self.logItems.set(contents)

    def __dump_data_buffers(self):
        data = comm.databuffer
        self.log("Scan Complete")
        self.log(f"Data Length: {len(data)}")

        # there are 0-pads, so get rid of them
        data = trim_data(data)

        # grab range settings
        config = get_state("config")["radar"]
        start_range = ps_to_range(
            config["scanStart"]) + config["distanceCorrection"]
        end_range = ps_to_range(
            config["scanEnd"]) + config["distanceCorrection"]

        print(config["scanStart"], config["distanceCorrection"])

        # get current date and time string
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_data(data, start_range, end_range, f"./data/{now}.pkl")
        self.log(f"File saved to {now}.pkl")

    def __static_scan(self):

        # get the current settings
        config = get_state("config")["radar"]

        scan_count = config["scanCount"]
        scan_interval = config["scanInterval"]

        self.log("Starting Static Scan")
        self.log(f"Scan Count: {scan_count}")
        self.log(f"Scan Interval: {scan_interval}")

        try:
            comm.exec_scan(scan_count, scan_interval)
        except Exception as e:
            self.log(f"FAILED: {e}")
            return

        self.__dump_data_buffers()

        comm.__reset__()
        self.update_log_box()

    def __start_dynamic_scan(self) -> bool:
        # get the current settings
        config = get_state("config")["radar"]

        scan_interval = config["scanInterval"]

        self.log("Starting Dynamic Scan")
        self.log(f"Scan Interval: {scan_interval}")

        try:
            resp = comm.send_sync("MRM_CONTROL_REQUEST", False,
                                  scanCount=65535, scanIntervalTime=scan_interval)
        except TimeoutError:
            self.log("FAILED: Did not receive confirm.")
            return False
        except Exception as e:
            self.log(f"FAILED: {e}")
            return False

        # check if all went well
        if resp["status"] != 0:
            self.log(f"FAILED. Error code: {resp['status']}")
            return False

        self.log("Dynamic Scan Started")

        # also set comm to async mode
        comm.mode = "async"

        self.update_log_box()
        return True

    def __run_dynamic_scan(self):

        # run these in batches of 70 to avoid keeping the thread busy 100% of the time
        # FIXME: Find a sweet spot for this number
        for _ in range(70):
            run_next = comm.get_data()

            if (not run_next):
                self.log(f"Stopping Dynamic Scan")
                self.update_log_box()
                self.run_dynamic = False

                # we need to use up the rest of the sent packets.
                # we are aiming for the timeout here
                while comm.get_data():
                    pass

                self.__dump_data_buffers()
                comm.__reset__()

                break

        self.log(f"Saved {len(comm.databuffer)} scans")
        self.update_log_box()

        # add self to root with a delay of 1 ms
        if (self.run_dynamic):
            self.root.after(1, self.__run_dynamic_scan)

    def __snapshot_scan(self):
        comm.exec_scan(self.snapshot_count, 0)
        self.snapshot_count += 1
        self.log("Took a snapshot!")

        self.update_log_box()

    def __dump_snapshots(self):
        self.__dump_data_buffers()
        self.log("Dumped snapshots")
        comm.__reset__()
        self.snapshot_count = 1

        self.update_log_box()
