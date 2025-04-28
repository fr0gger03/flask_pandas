import pandas as pd
import sys

def rvtools_conversion(**kwargs):
    input_path = kwargs['input_path']
    file_name = kwargs['file_name'] 

    print()
    print("Parsing RVTools file(s) locally.")

    vmdata_df = pd.read_excel(f'{input_path}/{file_name}', sheet_name = 'vInfo')

    # specify columns to KEEP - all others will be dropped
    keep_columns = ['VM ID','Cluster', 'Datacenter','Primary IP Address','OS according to the VMware Tools', 'DNS Name','Powerstate','CPUs','VM','Memory']
    if 'Provisioned MiB' in vmdata_df:
        keep_columns.extend(['Provisioned MiB','In Use MiB'])
    else:
        keep_columns.extend(['Provisioned MB','In Use MB'])
    vmdata_df = vmdata_df.filter(items= keep_columns, axis= 1)

    # rename remaining columns
    vmdata_df.rename(columns = {
        'VM ID':'vmId', 
        'VM':'vmName',
        'OS according to the VMware Tools':'os',
        'DNS Name':'os_name',
        'Powerstate':'vmState',
        'CPUs':'vCpu',
        'Memory':'vRam', 
        'Primary IP Address':'ip_addresses',
        'Folder':'vmFolder',
        'Resource pool':'resourcePool',
        'Cluster':'cluster', 
        'Datacenter':'virtualDatacenter'
        }, inplace = True)
    
    if 'Provisioned MiB' in vmdata_df:
        vmdata_df.rename(columns = {
            'Provisioned MiB':'vinfo_provisioned', 
            'In Use MiB':'vinfo_used'
            }, inplace = True)
    else:
        vmdata_df.rename(columns = {
            'Provisioned MB':'vinfo_provisioned', 
            'In Use MB':'vinfo_used'
            }, inplace = True)

    fillna_values = {"ip_addresses": "no ip", "os": "none specified"}
    vmdata_df.fillna(value=fillna_values, inplace = True)

    # pull in rows from vDisk for allocated storage
    vdisk_df = pd.read_excel(f'{input_path}/{file_name}', sheet_name = 'vDisk')

    vdisk_columns = ['VM ID']
    # Different versions of RVTools use either "MB" or "MiB" for storage; check for presence and include appropriate columns
    if 'Capacity MiB' in vdisk_df:
        vdisk_columns.extend(['Capacity MiB'])
    else:
        vdisk_columns.extend(['Capacity MB'])
    vdisk_df = vdisk_df.filter(items= vdisk_columns, axis= 1)

    if 'Capacity MiB' in vdisk_df:
        vdisk_df.rename(columns ={'Capacity MiB':'vmdkTotal'}, inplace = True)
    else:
        vdisk_df.rename(columns ={'Capacity MB':'vmdkTotal'}, inplace = True)
    vdisk_df.rename(columns ={'VM ID':'vmId'}, inplace = True)

    vdisk_df = vdisk_df.groupby(['vmId'])['vmdkTotal'].sum().reset_index()

    # pull in rows from vPartition for consumed storage
    vpart_df = pd.read_excel(f'{input_path}/{file_name}', sheet_name = 'vPartition')
    
    part_list = ['VM ID']
    if 'Consumed MiB' in vpart_df:
        part_list.extend(['Consumed MiB'])
    else:
        part_list.extend(['Consumed MB'])
    vpart_df = vpart_df.filter(items= part_list, axis= 1)

    if 'Consumed MiB' in vpart_df:
        vpart_df.rename(columns ={'Consumed MiB':'vmdkUsed'}, inplace = True)
    else:
        vpart_df.rename(columns ={'Consumed MB':'vmdkUsed'}, inplace = True)
    vpart_df.rename(columns ={'VM ID':'vmId'}, inplace = True)

    vpart_df = vpart_df.groupby(['vmId'])['vmdkUsed'].sum().reset_index()

    vm_consolidated = pd.merge(vmdata_df, vdisk_df, on = "vmId", how = "left")
    vm_consolidated = pd.merge(vm_consolidated, vpart_df, on = "vmId", how = "left")

    # convert RAM and storage numbers into GB
    vm_consolidated['vinfo_provisioned'] = vm_consolidated['vinfo_provisioned']/1024
    vm_consolidated['vinfo_used'] = vm_consolidated['vinfo_used']/1024
    vm_consolidated['vmdkTotal'] = vm_consolidated['vmdkTotal']/1024
    vm_consolidated['vmdkUsed'] = vm_consolidated['vmdkUsed']/1024
    vm_consolidated['vRam'] = vm_consolidated['vRam']/1024

    # Replace NA values for used VMDK and total VMDK with 0 GB
    storage_na_values = {"vmdkTotal": 0, "vmdkUsed": 0}
    vm_consolidated.fillna(value=storage_na_values, inplace = True)

    # replace missing values from vDisk or vPartition with values from vInfo
    vm_consolidated.loc[vm_consolidated.vmdkTotal == 0, 'vmdkTotal'] = vm_consolidated.vinfo_provisioned
    vm_consolidated.loc[vm_consolidated.vmdkUsed == 0, 'vmdkUsed'] = vm_consolidated.vinfo_used

    return vm_consolidated