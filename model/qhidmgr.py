#import qhidapi
from model.hidapi_send_sys_command import hidapi_send_sys_command
from qhidapi import *
from qhidapi import HID_DATA_OFFSET
from fwct import *


def hidmgr_show_mcu_firmware_info(fw_info:list):
    # [0] RID_SYS
    # [1] SYS_CMD_GET_COMPONENT_FWVER
    # [2] Action code =0
    # [3] Response code = ACK
    # [4] Cmponent ID
    # [5] Device Type
    # [6] Active Image type
    # [7-14] BootLoader Version Info
    # [15-22] BootLoader Version Info
    # [23-30] BootLoader Version Info
    component_id=fw_info[0]
    bootload_ver=str(fw_info[10])+"."+str(fw_info[9])+"."+str(fw_info[8])+"."+str(fw_info[7])
    app_ver=str(fw_info[18])+"."+str(fw_info[17])+"."+str(fw_info[16])+"."+str(fw_info[15])

    print("Componment Device ",component_id,": DMC")
    if fw_info[6]==0 :
            print("AT32F415: (Active image:Bootloader)")
    else:
        print("AT32F415: (Active image:Application)")
    print("Bootload version: ",bootload_ver)
    print("Application version: ",app_ver)


def hidmgr_show_ccg4_firmware_info(fw_info:list):
    # [0] RID_SYS
    # [1] SYS_CMD_GET_COMPONENT_FWVER
    # [2] Action code =0
    # [3] Response code = ACK
    # [4] Cmponent ID
    # [5] Device Type
    # [6] Active Image type
    # [7-14] BootLoader Version Info
    # [15-22] FW1 Version Info
    # [23-30] FW2 Version Info
    component_id=fw_info[4]

    bl_base_ver=str(fw_info[10]>>4)+"."+str(fw_info[10]&0x0F)+"."+str(fw_info[9])+"."+str(fw_info[7]|(fw_info[8]<<8))
    bl_app_ver=chr(fw_info[12])+chr(fw_info[11])+"."+str(fw_info[16])+"."+str(fw_info[15])

    fw1_base_ver=str(fw_info[18]>>4)+"."+str(fw_info[18]&0x0F)+"."+str(fw_info[17])+"."+str(fw_info[15]|(fw_info[16]<<8))
    fw1_app_ver=chr(fw_info[20])+chr(fw_info[19])+"."+str((fw_info[22]&0xF0)>>4)+"."+str(fw_info[22]&0x0F)+"."+str(fw_info[21])

    fw2_base_ver=str(fw_info[26]>>4)+"."+str(fw_info[26]&0x0F)+"."+str(fw_info[25])+"."+str(fw_info[23]|(fw_info[24]<<8))
    fw2_app_ver=chr(fw_info[28])+chr(fw_info[27])+"."+str((fw_info[30]&0xF0)>>4)+"."+str(fw_info[30]&0x0F)+"."+str(fw_info[29])

    print("Componment Device ",component_id)
    if fw_info[6]==1 :
            print("CCG4: (Active image:Image0)")
    else:
        print("CCG4: (Active image:Image1)")
    print("Base version: ",bl_base_ver)    
    print("Application version: ",bl_app_ver)
    if (fw_info[6]&0x40 ==0 ):
        print("Image0: Valid")
    else:
         print("Image0: Invalid")
    print("Base version: ",fw1_base_ver)
    print("Application version: ",fw1_app_ver)
    if (fw_info[6]&0x80 ==0 ):
        print("Image1: Valid")
    else:
         print("Image1: Invalid")
    print("Base version: ",fw2_base_ver)
    print("Application version: ",fw2_app_ver)



def hidmgr_show_device_firmware_info(fw_info:list):
    dev_num=len(fw_info)

    print("="*8," Show Device Firmware Information ","="*8)
    print("-"*52)
    for index in range(0,dev_num):

        dev=fw_info[index]

        if dev[1] == DMC_DEV_TYPE.DMC_DEV_TYPE_AT32F415.value:
            hidmgr_show_mcu_firmware_info(dev[2])
        elif dev[1] == DMC_DEV_TYPE.DMC_DEV_TYPE_CCG4.value:
            hidmgr_show_ccg4_firmware_info(dev[2])

        print("-"*52)
    print("="*52)

def hidmgr_get_device_firmware_info(vid:int=0, pid:int=0, sn:str=None)->list:
    """_summary_

    Args:
        vid (int, optional): _description_. Defaults to 0.
        pid (int, optional): _description_. Defaults to 0.
        sn (str, optional): _description_. Defaults to None.

    Returns:
        list: _description_
        Format:
        index 0: component id (0~N)
        index 1: component type (DMC_DEV_TYPE)
        index 2: comoonent FW information (fw_version, app_version) total: 8 bytes
    """
    dev_fw_info=[]
    dev_comp_list=hidapi_send_sys_command(vid, pid,HID_SYSCMD_TYPE.SYS_CMD_GET_COMPONENT_ID_LIST)
    # SYS_CMD_GET_COMPONENT_ID_LIST:
    # HID format:
    # [0] RID_SYS
    # [1] SYS_CMD_GET_COMPONENT_ID_LIST
    # [2] Action code =0
    # [3] Response code = ACK
    # [4] TotalDevice count
    # [5] Device 0 - Component ID
    # [6] Device 0 - Device Type
    # [7] Device 1 - Component ID
    # [8] Device 2 - Device Type
    # ...

    if dev_comp_list is None:
        return None
    else:    
        component_num=dev_comp_list[HID_DATA_OFFSET]
        for index in range(0,component_num):
            component=[]
            component.append(dev_comp_list[5+2*index]) # component_id
            component.append(dev_comp_list[6+2*index]) # compoonent_type
            print(component)
            fw_info=hidapi_send_sys_command(vid, pid,HID_SYSCMD_TYPE.SYS_CMD_GET_COMPONENT_FWVER,component)
            # SYS_CMD_GET_COMPONENT_FWVER 
            # HID format:
            # [0] RID_SYS
            # [1] SYS_CMD_GET_COMPONENT_FWVER
            # [2] Action code =0
            # [3] Response code = ACK
            # [4] Cmponent ID
            # [5] Device Type
            # [6] Active Image type
            # [7-14] BootLoader Version Info
            # [15-22] BootLoader Version Info
            # [23-30] BootLoader Version Info
            # Version information structure is depending on component device type.

            if fw_info is None:
                return None
            else:
                component.append(fw_info)
                dev_fw_info.append(component)
        return dev_fw_info

if __name__ == "__main__":
    
    dev=hidapi_find_device()

    vid=0x2BEF
    pid=0x0415
    
    dev=hidapi_find_device(vid=vid,pid=pid)
    
    info=hidmgr_get_device_firmware_info(vid, pid)
    hidmgr_show_device_firmware_info(info)
    
    if(info is None):
        print("Not found device: vid=",hex(vid)," pid=",hex(pid))
    else:
        print(info)
        
    padding=[]
    #for i in range(0,60):
    #   padding.append(i)
    padding.append(0)
    padding.append(17)
    d=hidapi_send_sys_command(vid, pid,HID_SYSCMD_TYPE.SYS_CMD_GET_COMPONENT_ID_LIST)
    d1=hidapi_send_sys_command(vid, pid,HID_SYSCMD_TYPE.SYS_CMD_GET_COMPONENT_FWVER,padding)
    
    print(d)