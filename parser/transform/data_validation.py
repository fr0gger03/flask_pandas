import pandas as pd

def filetype_validation(input_path, fn):
    print("determining file type")

    lo_sheets=['Details', 'ESX Hosts', 'ESX Performance', 'Host Devices', 'VMs', 'VM Performance', 'VM Disks', 'ESX Licenses', 'Host Disks', 'Host Network Adapters']
    rv_sheets=['vInfo', 'vCPU', 'vMemory', 'vDisk', 'vPartition', 'vNetwork', 'vCD', 'vUSB', 'vSnapshot', 'vTools', 'vSource', 'vRP', 'vCluster', 'vHost', 'vHBA', 'vNIC', 'vSwitch', 'vPort', 'dvSwitch', 'dvPort', 'vSC_VMK', 'vDatastore', 'vMultiPath', 'vLicense', 'vFileInfo', 'vHealth', 'vMetaData']

    file_type=""

    vmfile = pd.ExcelFile(f'{input_path}{fn}')
    vmsheets=vmfile.sheet_names
    if vmsheets==lo_sheets:
        print(f'{fn} is a match for live optics')
        file_type="live-optics"
    elif vmsheets==rv_sheets:
        print(f'{fn} is a match for rvtools')
        file_type="rv-tools"
    else:
        print(f'{fn} is neither a LiveOptics file, nor an RV Tools file, else is not correctly formed / complete.')
        file_type="invalid"
    return file_type