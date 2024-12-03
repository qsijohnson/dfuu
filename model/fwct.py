import os
import struct
from enum import Enum

FWCT_IDENTIFY_STR="FWCT"
FWCT_DEVICE_INFO_SZIE=40
FWCT_IMAGE_INFO_SZIE=60
FWCT_SEGMENT_INFO_SZIE=8

# Device Type
class DMC_DEV_TYPE(Enum):
    DMC_DEV_TYPE_INVALID=0        # Dock controller can't recognize the device.
    DMC_DEV_TYPE_CCG3=1             # Dock device type 1 CCG3. 
    DMC_DEV_TYPE_DMC_CY7C65219=2    # Dock device type 2 CY7C65219. 
    DMC_DEV_TYPE_CCG4=3             # Dock device type 3 CCG4. 
    DMC_DEV_TYPE_CCG5=4             # Dock device type 4 CCG5.
    DMC_DEV_TYPE_HX3=5              # Dock device type 5 HX3. 
    DMC_DEV_TYPE_RESERVED_06=6      # Dock device type is reserved for future use 
    DMC_DEV_TYPE_RESERVED_07=7      # Dock device type is reserved for future use 
    DMC_DEV_TYPE_MCDP_2900=8        # Dock device type is MCDP2900. 
    DMC_DEV_TYPE_ANALOGIX_9847=9    # Dock device type is ANX9847. 
    DMC_DEV_TYPE_RESERVED_0A=10     # Dock device type is reserved for future use 
    DMC_DEV_TYPE_RESERVED_0B=11     # Dock device type is reserved for future use
    DMC_DEV_TYPE_STDP_4320=12       # Dock device type is STDP4320.     
    DMC_DEV_TYPE_CCG2=13            # Dock device type is CCG2. 
    DMC_DEV_TYPE_RESERVED_0E=14     # Dock device type is reserved for future use 
    DMC_DEV_TYPE_QSI_RTD2183=15     # Dock device type 15 RTD2183 for Realtek MST HUB by QSI 
    DMC_DEV_TYPE_QSI_VMM5320=16     # Dock device type 16 VMM5310/VMM5320/VMM5330 
    DMC_DEV_TYPE_AT32F415=17        # Dock device type 17 
    DMC_DEV_TYPE_RTD2188=18         # Dock device type 18 
    DMC_DEV_TYPE_RTD2143=19         # Dock device type 19
    DMC_DEV_TYPE_AT32F425=20        # Dock device type 20 
    DMC_DEV_TYPE_RTD2175=21         # Dock device type 21 
    DMC_DEV_TYPE_RTD2198=22         # Dock device type 22 
    DMC_DEV_TYPE_AT32F407=23        # Dock device type 23 reserved for future use 
    DMC_DEV_TYPE_MAX=24       

# Image Mode Type
class DMC_IMAGE_MODE(Enum):
    DMC_IMAGE_MODE_SINGLE=0
    DMC_IMAGE_MODE_DUAL_SYM=1
    DMC_IMAGE_MODE_DUAL_ASYM=2
    
class IMAGE_TYPE(Enum):
    IMAGE_TYPE_BOOTLOADER=0
    IMAGE_TYPE_IMAGE1=1
    IMAGE_TYPE_IMAGE2=2
    IMAGE_TYPE_INVALID=3
    IMAGE_TYPE_PROJECT_CFG=1
    IMAGE_TYPE_HARDWARE_CFG=2


# https://www.w3schools.com/python/python_datatypes.asp
class Dock_FWCT_Info: # total: 40 bytes
    identify    : str # FWCT
    table_size  : int
    checksum    : int
    fwct_version: int
    digSignAlg  : int
    cdtt_version: int
    vendor_id   : int
    product_id  : int
    device_id   : int
    reserved    : bytearray
    composite_version: int
    image_count : int
    padding     : bytearray

class Dock_FWCT_ImageInfo: # total: 60 bytes
    device_type : int
    image_type  : int
    component_id: int
    row_size_ind: int
    reserv0     : bytearray # 4 bytes
    fw_version  : int
    app_version : int
    image_offset: int
    image_size  : int
    image_digest: bytearray # 32 bytes
    num_image_segments: int
    reserv1     : bytearray # 3 bytes

class Dock_FWCT_SegmentInfo: # total: 8 bytes
    image_id    : int    
    image_type  : int
    segment_start_row:int
    segment_size: int
    reserv1     : bytearray # 2 bytes

# FWCT Structure
# +-------------------+
# | FWCT Head         | Dock_FWCT_Info
# +-------------------+
# | FWCT Tables       | Dock_FWCT_ImageInfo
# | ...               | Dock_FWCT_SegmentInfo
# +-------------------+
# | Digital signature | (2 + Signature_Data)
# | content appended  | Signature_Length: 2 Bytes
# +-------------------+
# | Dev 1 FW Seg0 BIN |
# | Dev 1 FW Seg1 BIN |
# +-------------------+
# | Dev 2 FW Seg0 BIN |
# | Dev 2 FW Seg1 BIN |
# +-------------------+
# | Dev 3 FW Seg0 BIN |
# | Dev 3 FW Seg1 BIN |
# +-------------------+
# | Dev N ...         |
# +-------------------+

def parser_fwct_info(imageFile) -> Dock_FWCT_Info:
    # https://docs.python.org/3/library/struct.html
    struct_fwctInfo_fmt = ('<') +( # Little-endian, 40Bytes
        '4s'    # identify, 'F','W','C','T'
        'H'     # Table size
        'B'     # Checksum
        'B'     # FWCT Version
        'B'     # Digital signalture algorithm
        'B'     # CDTT Version
        'H'     # Vendor ID
        'H'     # Product ID
        'H'     # Device ID
        '16s'   # Reserved, 16 bytes
        'I'     # Composite FW Version
        'B'     # count of images
        '3s'    # Padding, 3 bytes
    )
    
    struct_len = struct.calcsize(struct_fwctInfo_fmt)
    struct_unpack = struct.Struct(struct_fwctInfo_fmt).unpack_from
    fw_fwctInfo=Dock_FWCT_Info()
    
    with open(imageFile, "rb") as f:
        data = f.read(struct_len)
        if not data: return(None)
        
        s = struct_unpack(data)
        # Mapping list to class object
        fw_fwctInfo.identify     = s[0]
        fw_fwctInfo.table_size   = s[1]
        fw_fwctInfo.checksum     = s[2]
        fw_fwctInfo.fwct_version = s[3]
        fw_fwctInfo.digSignAlg   = s[4]
        fw_fwctInfo.cdtt_version = s[5]
        fw_fwctInfo.vendor_id    = s[6]
        fw_fwctInfo.product_id   = s[7]
        fw_fwctInfo.device_id    = s[8]
        fw_fwctInfo.reserved     = s[9]
        fw_fwctInfo.composite_version = s[10]
        fw_fwctInfo.image_count  = s[11]
        fw_fwctInfo.padding      = s[12]
    if(fw_fwctInfo.identify.decode('ascii') == FWCT_IDENTIFY_STR):
        return(fw_fwctInfo)
    else:
        return(None)
        
def parser_image_info(imageFile, offset) -> Dock_FWCT_ImageInfo: 
    struct_fwctImageInfo_fmt = ('<') +( # Little-endian, 60Bytes
        'B'     # Device Type
        'B'     # Device Image Type
        'B'     # Component ID
        'B'     # Row Size indicator
        '4s'    # Rserved, 4 bytes
        'I'     # FW Version
        'I'     # APP Version
        'I'     # Image fffset
        'I'     # Image size
        '32s'   # Image Digest, 32 bytes
        'B'     # Number of image segments
        '3s'    # Padding, 3 bytes
    )
    
    struct_len = struct.calcsize(struct_fwctImageInfo_fmt)
    struct_unpack = struct.Struct(struct_fwctImageInfo_fmt).unpack_from
    fw_imageInfo=Dock_FWCT_ImageInfo()  
    
    with open(imageFile, "rb") as f:
        f.seek(offset)
        data = f.read(struct_len)
        if not data: return(None)
        
        s = struct_unpack(data)
        # Mapping list to class object
        fw_imageInfo.device_type  = s[0]
        fw_imageInfo.image_type   = s[1]
        fw_imageInfo.component_id = s[2]
        fw_imageInfo.row_size_ind = s[3]
        fw_imageInfo.reserv0      = s[4]
        fw_imageInfo.fw_version   = s[5]
        fw_imageInfo.app_version  = s[6]
        fw_imageInfo.image_offset = s[7]
        fw_imageInfo.image_size   = s[8]
        fw_imageInfo.image_digest = s[9]
        fw_imageInfo.num_image_segments = s[10]
        fw_imageInfo.reserv1      = s[11]
    return(fw_imageInfo)
   
def parser_segment_info(imageFile, offset) -> Dock_FWCT_SegmentInfo: 
    struct_fwctSegmentInfo_fmt = ('<') +( # Little-endian, 8Bytes
        'B'     # Image ID
        'B'     # Segment Type
        'H'     # Segment Start Row
        'H'     # Segment size, number of row
        '2s'    # Rserved, 2 bytes
    )
    
    struct_len = struct.calcsize(struct_fwctSegmentInfo_fmt)
    struct_unpack = struct.Struct(struct_fwctSegmentInfo_fmt).unpack_from
    fw_segmentInfo=Dock_FWCT_SegmentInfo()  
    
    with open(imageFile, "rb") as f:
        f.seek(offset)
        data = f.read(struct_len)
        if not data: return(None)
        
        s = struct_unpack(data)
        # Mapping list to class object
        fw_segmentInfo.image_id     = s[0]
        fw_segmentInfo.image_type   = s[1]
        fw_segmentInfo.segment_start_row = s[2]
        fw_segmentInfo.segment_size = s[3]
        fw_segmentInfo.reserv1      = s[4]
    return(fw_segmentInfo)
            
        
def load_fwct_image(imageFile):
    print("[INFO] Image:",imageFile)
    composite_image=[]
    image_offset=0
    devInfo=parser_fwct_info(imageFile)
    if ( devInfo is not None ):
        composite_image.append(devInfo)
    else:
        return(None)    
    
    print("FWCT size:",devInfo.table_size)
    print("identify:",devInfo.identify)
    print("checksum:",devInfo.checksum)
    print("fwct_version:",devInfo.fwct_version)
    print("cdtt_version:",devInfo.cdtt_version)
    print("vendor_id:",hex(devInfo.vendor_id))
    print("product_id:",hex(devInfo.product_id))
    print("device_id:",hex(devInfo.device_id))
    print("composite_version:",hex(devInfo.composite_version))
    print("Image count:",devInfo.image_count)
    
    struct_signature_size_fmt = ('<') +( # Little-endian, 2Bytes
        'H'     # Sigature Size, 2 bytes
    )
    
    struct_len = struct.calcsize(struct_signature_size_fmt)
    struct_unpack = struct.Struct(struct_signature_size_fmt).unpack_from
    
    with open(imageFile, "rb") as f:
        f.seek(devInfo.table_size)
        data = f.read(struct_len)
        if not data: return(None)
        s = struct_unpack(data)

        Signature_size=s[0]
    
    bincode_offset=devInfo.table_size +  Signature_size + 2
    
    image_offset +=FWCT_DEVICE_INFO_SZIE
    for imgNum in range(0,devInfo.image_count):
        imageInfo=parser_image_info(imageFile,image_offset)
        if(imageInfo is not None):
            composite_image.append(imageInfo)
            print("IMAGE NUM:",imgNum,"\n","="*30)
            image_offset +=FWCT_IMAGE_INFO_SZIE
            print("device_type:",imageInfo.device_type)
            print("image_type:",imageInfo.image_type)
            print("component_id:",imageInfo.component_id)
            print("row_size_ind:",imageInfo.row_size_ind)
            print("fw_version:",hex(imageInfo.fw_version))
            print("app_version:",hex(imageInfo.app_version))
            print("image_offset:",hex(imageInfo.image_offset))
            print("image_size:",hex(imageInfo.image_size))
            print("image_digest:",imageInfo.image_digest)
            print("num_image_segments:",imageInfo.num_image_segments)
            
            for segNum in range(0,imageInfo.num_image_segments):
                segInfo=parser_segment_info(imageFile,image_offset)
                if(segInfo is not None):
                    composite_image.append(segInfo)
                    print("SEGMENT NUM:",segNum,"\n","-"*30)
                    image_offset +=FWCT_SEGMENT_INFO_SZIE
                    print("image_id:",segInfo.image_id)
                    print("image_type:",segInfo.image_type)
                    print("segment_start_row:",segInfo.segment_start_row)
                    print("segment_size:",segInfo.segment_size)
                    
                    # load bin code
                    with open(imageFile, "rb") as f:
                        f.seek(bincode_offset)
                        binCodeSize=segInfo.segment_size * imageInfo.row_size_ind * 64
                        binCode = f.read(binCodeSize)
                        composite_image.append(binCode)
                else:
                    return(None)    
            
        else:
            return(None) 
        
    return(composite_image)
    

        
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        imageFile=sys.argv[1]
        if(os.path.isfile(imageFile)==False):
            print("<ERROR> Image File:", imageFile ,"isn't existing.")
            sys.exit(2)
        composite=load_fwct_image(imageFile)    
        sys.exit(0)
    else:
        print("<ERROR> Wrong input.")
        print("Help:\n\t %s <image>" % os.path.basename(__file__))
        sys.exit(1)