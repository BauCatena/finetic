def calculateCrc16Gt06(data_bytes: bytes) -> str:
    crc = 0xFFFF
    for byte in data_bytes:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                # 0x1021 reflejado es 0x8408
                crc = (crc >> 1) ^ 0x8408  
            else:
                crc >>= 1
    final_crc = crc ^ 0xFFFF 

    return f"{final_crc:04X}"