# pip install pyusb,libusb,libusb-package
# pip install pyocd
# brew install hidapi
import usb.core
import libusb_package
from usb.backend import libusb1
import hid
from enum import Enum,unique,auto
import time

HID_PACKET_SIZE_MAX=64
HID_PACKET_PADLOAD_SIZE=HID_PACKET_SIZE_MAX-4
HID_RID_OFFSET=0
HID_CMD_OFFSET=1
HID_ACT_OFFSET=2
HID_RSP_OFFSET=3
HID_DATA_OFFSET=4

HID_READ_TIMEOUT=500 # unit:ms

# Format:
# HID[0]: Report ID
# HID[1]: Command Code
# HID[2]: Action Code
# HID[3]: Response Code
# HID[4...63]: Payload data
# 

@unique
class HID_REPORID_TYPE(Enum):
    RID_UNKNOWN=0
    RID_SYS    =1
    RID_FW     =2
    RID_BUSIO  =3

@unique
class HID_SYSCMD_TYPE(Enum):
    SYS_CMD_UNKNOWN                 =0
    SYS_CMD_PING                    =1
    SYS_CMD_GET_COMPONENT_ID_LIST   =2
    SYS_CMD_GET_COMPONENT_FWVER     =3
    SYS_CMD_GET_SN                  =4
    SYS_CMD_SET_SN                  =5
    SYS_CMD_GET_UID                 =6
    SYS_CMD_RESET                   =7
    SYS_CMD_RESET_TO_ROM            =8
    SYS_CMD_RESET_TO_BOOTLOAD       =9
    SYS_CMD_MAX                     =10

@unique
class HID_FWCMD_TYPE(Enum):
    FW_CMD_UNKNOWN      =0
    FW_CMD_HW_CFG       =1
    FW_CMD_PROJECT_CFG  =2
    FW_CMD_FW_UPDATE    =3
    FW_CMD_MAX          =4
    
@unique
class HID_IOBUSCMD_TYPE(Enum):
    IOBUS_CMD_UNKNOWN   =0
    IOBUS_CMD_GPIO      =1
    IOBUS_CMD_I2C       =2
    IOBUS_CMD_SPI       =3 # included spi flash command access
    IOBUS_CMD_SPI_FLASH =4 # for spi flash high level access, sector program, write
    IOBUS_CMD_PWM       =5
    IOBUS_CMD_ADC       =6
    IOBUS_CMD_UART      =7
    IOBUS_CMD_MAX       =9

@unique
class HID_FWACT_TYPE(Enum):
    FW_ACT_UNKNOWN          =0
    FW_ACT_RESET            =1 # reset state machine
    FW_ACT_START_UPDATE     =2 # start FW update
    FW_ACT_CHECK_FWCT       =3 # check fwtab
    FW_ACT_INIT             =4 # Request FW update
    FW_ACT_PREPARE_UPDATE   =5 # Request FW update
    FW_ACT_READ             =6 # Read data from buffer
    FW_ACT_WRITE            =7 # write buffer to component
    FW_ACT_RBUF             =8 # Read data from compoent to buffer
    FW_ACT_WBUF             =9 # Write data to buffer
    FW_ACT_UPDATE_FINISH    =10 # completed update
    FW_ACT_STATUS           =11 # Get status
    FW_ACT_INFO             =12        
    FW_ACT_MAX              =13  

@unique
class HID_IOBUSACT_TYPE(Enum):
    IOBUS_ACT_UNKNOWN       =0
    IOBUS_ACT_INIT          =1
    IOBUS_ACT_DEINIT        =2
    IOBUS_ACT_READ          =3
    IOBUS_ACT_WRITE         =4
    IOBUS_ACT_TOGGLE        =5
    IOBUS_ACT_MEM_READ      =6 # for I2C device memory read mode
    IOBUS_ACT_MEM_WRITE     =7 # for I2C device memory write mode
    IOBUS_ACT_PROBE         =8 # for I2C device probe
    IOBUS_ACT_DUTY          =9 # for configure pwm dutycycle
    IOBUS_ACT_FREQ          =10 # for configure pwm frequency
    IOBUS_ACT_FLASH         =11 # for SPI FLASH access through IOBUS_SPI
    IOBUS_ACT_FLASH_BWRITE  =12 # flash write from buffer (buffer -> flash)
    IOBUS_ACT_FLASH_BREAD   =13 # flash read from flash to buffer (flash -> buffer)
    IOBUS_ACT_FLASH_WBUF    =14 # flash data write to buffer (host -> buffer)
    IOBUS_ACT_FLASH_RBUF    =15 # flash data read to buffer (flash -> buffer)   
    IOBUS_ACT_MAX           =16 
    
@unique
class HID_APIRESPONE_TYPE(Enum):
    HIDAPI_UNKNOWN=0
    HIDAPI_INIT=0x55
    # Response code
    HIDAPI_ACK=0xAA     # completed
    HIDAPI_NACK=0x5A    # failed
    HIDAPI_WAIT=0xBB    #   
    HIDAPI_DEFER=0xDF   # indicate API call defer need to check it later.
    HIDAPI_REENUM=0xF0  # indicate host need to check dock reenum    

def hidapi_find_device(vid:int =0, pid:int =0)->list:
    dev_list=[]
    try:
        backend =libusb1.get_backend(find_library=libusb_package.find_library)
        #dev_list=hid.enumerate(vendor_id=vid,product_id=pid)
        
        for device_dict in hid.enumerate(vendor_id=vid,product_id=pid):
            if device_dict['bus_type']==1: # 1: USB
                dev_list.append(device_dict)
                keys = list(device_dict.keys())
                keys.sort()
                for key in keys:
                    print("%s : %s" % (key, device_dict[key]))
        print()
        return(dev_list)
    
    except IOError as ex:
        print(ex)
        return(None)

def hidapi_get_device_information(vid:int, pid:int, serial_number=None)->list:
    """_summary_

    Args:
        vid (int): _description_
        pid (int): _description_

    Returns:
        list: _description_
    """
    info=[]
    
    try:
        backend =libusb1.get_backend(find_library=libusb_package.find_library)
        
        h = hid.device()
        h.open(vid, pid)
        print("Manufacturer: %s" % h.get_manufacturer_string())
        print("Product: %s" % h.get_product_string())
        print("Serial No: %s" % h.get_serial_number_string())
        
        info.append(h.get_manufacturer_string())
        info.append(h.get_product_string())
        info.append(h.get_serial_number_string())
        
        h.close()
        
        return(info)
    
    except IOError as ex:
        print(ex)
        return(None)

def hidapi_send_raw_packet(vid:int, pid:int, packet:list=None)->list:
    """_summary_

    Args:
        vid (int): _description_
        pid (int): _description_
        packet (list, optional): _description_. Defaults to None.

    Returns:
        list: _description_
    """
    try:
        if packet is None:
            return None
        
        backend =libusb1.get_backend(find_library=libusb_package.find_library)
        h = hid.device()
        h.open(vid, pid)
        h.set_nonblocking(1)
        hid_pkt=[]
        if len(packet)>HID_PACKET_SIZE_MAX:
            hid_pkt = packet[0:HID_PACKET_SIZE_MAX]
        elif len(packet)<HID_PACKET_PADLOAD_SIZE:
            padding_len=HID_PACKET_PADLOAD_SIZE-len(packet)
            hid_pkt = packet + [0]*padding_len
        else:
            hid_pkt = packet
            
        h.write(hid_pkt)
        time.sleep(0.05)
        hid_data=h.read(HID_PACKET_SIZE_MAX,HID_READ_TIMEOUT)
        print("hid_data:",hid_data)
        
        h.close()
        return(hid_data)
    
    except IOError as ex:
        print(ex)
        return(None)


def hidapi_send_sys_command(vid:int, pid:int, cmd:HID_SYSCMD_TYPE, payload:list=None)->list:
    """_summary_

    Args:
        vid (int): _description_
        pid (int): _description_
        cmd (HID_SYSCMD_TYPE): _description_
        payload (list, optional): _description_. Defaults to None.

    Returns:
        list: _description_
    """
    try:
        backend =libusb1.get_backend(find_library=libusb_package.find_library)
        h = hid.device()
        h.open(vid, pid)
        h.set_nonblocking(1)
        
        hid_pkt=[HID_REPORID_TYPE.RID_SYS.value,cmd.value,0,0]
        if payload==None:
            hid_pkt +=[0]*HID_PACKET_PADLOAD_SIZE
        else:
            if len(payload)>HID_PACKET_PADLOAD_SIZE:
                hid_pkt += payload[0:HID_PACKET_PADLOAD_SIZE]
            elif len(payload)<HID_PACKET_PADLOAD_SIZE:
                padding_len=HID_PACKET_PADLOAD_SIZE-len(payload)
                hid_pkt +=payload
                hid_pkt +=[0]*padding_len
            else:
                hid_pkt += payload
            
        h.write(hid_pkt)
        time.sleep(0.05)
        hid_data=h.read(HID_PACKET_SIZE_MAX)
        #print("hid_data:",hid_data)
        
        if hid_data[HID_RSP_OFFSET] != HID_APIRESPONE_TYPE.HIDAPI_ACK.value:
            print("HID_CMD FAIL:",hid_data[HID_RSP_OFFSET])
        
        h.close()
        return(hid_data)
    
    except IOError as ex:
        print(ex)
        return(None)

if __name__ == "__main__":
    
    dev=hidapi_find_device()

    vid=0x2BEF
    pid=0x0415
    
    dev=hidapi_find_device(vid=vid,pid=pid)
    
    info=hidapi_get_device_information(vid, pid)
    
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