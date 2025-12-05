import pandas as pd
import os
from pathlib import Path

def filetype_validation(input_path, fn):
    """Validate file type for Excel workbooks, optimized for large files.
    
    Args:
        input_path (str): Path to the directory containing the file
        fn (str): Filename
        
    Returns:
        str: File type ('live-optics', 'rv-tools', or 'invalid')
    """
    print(f"Determining file type for {fn}")
    
    # Check file size for logging
    file_path = Path(input_path) / fn
    if file_path.exists():
        file_size = file_path.stat().st_size
        print(f"File size: {file_size / 1024 / 1024:.2f} MB")
    
    lo_sheets = ['Details', 'ESX Hosts', 'ESX Performance', 'Host Devices', 'VMs', 
                'VM Performance', 'VM Disks', 'ESX Licenses', 'Host Disks', 'Host Network Adapters']
    rv_sheets = ['vInfo', 'vCPU', 'vMemory', 'vDisk', 'vPartition', 'vNetwork', 'vCD', 
                'vUSB', 'vSnapshot', 'vTools', 'vSource', 'vRP', 'vCluster', 'vHost', 
                'vHBA', 'vNIC', 'vSwitch', 'vPort', 'dvSwitch', 'dvPort', 'vSC_VMK', 
                'vDatastore', 'vMultiPath', 'vLicense', 'vFileInfo', 'vHealth', 'vMetaData']
    
    file_type = ""
    
    try:
        # Use context manager for better memory management with large files
        with pd.ExcelFile(os.path.join(input_path, fn)) as vmfile:
            vmsheets = vmfile.sheet_names
            print(f"Found {len(vmsheets)} sheets in {fn}")
            
            if vmsheets == lo_sheets:
                print(f'{fn} is a match for LiveOptics')
                file_type = "live-optics"
            elif vmsheets == rv_sheets:
                print(f'{fn} is a match for RVTools')
                file_type = "rv-tools"
            else:
                print(f'{fn} is neither a LiveOptics file, nor an RVTools file, or is not correctly formed/complete.')
                print(f"Expected LiveOptics sheets: {len(lo_sheets)}, RVTools sheets: {len(rv_sheets)}")
                print(f"Found sheets: {vmsheets[:5]}..." if len(vmsheets) > 5 else f"Found sheets: {vmsheets}")
                file_type = "invalid"
                
    except FileNotFoundError:
        # Re-raise FileNotFoundError to be explicit about missing files
        print(f"File not found: {os.path.join(input_path, fn)}")
        raise
    except Exception as e:
        print(f"Error reading Excel file {fn}: {e}")
        file_type = "invalid"
    
    return file_type

def get_file_info(input_path, fn):
    """Get basic file information including size and sheet count.
    
    Args:
        input_path (str): Path to the directory containing the file
        fn (str): Filename
        
    Returns:
        dict: File information
    """
    file_path = Path(input_path) / fn
    info = {
        'filename': fn,
        'exists': file_path.exists(),
        'size_bytes': 0,
        'size_mb': 0,
        'sheet_count': 0
    }
    
    if file_path.exists():
        info['size_bytes'] = file_path.stat().st_size
        info['size_mb'] = info['size_bytes'] / 1024 / 1024
        
        try:
            with pd.ExcelFile(file_path) as excel_file:
                info['sheet_count'] = len(excel_file.sheet_names)
        except Exception as e:
            print(f"Could not read Excel file: {e}")
    
    return info
