def byteToInt(hexData):
    rulesGPS = [
        {'name': 'beggining', 'bytes': 2, 'type':'float'},
        {'name': 'length', 'bytes': 1, 'type':'float'},
        {'name': 'protocol', 'bytes': 1, 'type':'float'},
        {'name': 'timestamp', 'bytes': 6, 'type':'date'},
        {'name': 'sattelite', 'bytes': 1, 'type':'float'}, 
        {'name': 'latitude', 'bytes': 4, 'type':'cords'},
        {'name': 'longitude', 'bytes': 4, 'type':'cords'},
        {'name': 'speed', 'bytes': 1, 'type':'float'},
        {'name': 'direction', 'bytes': 2, 'type':'float'},
        {'name': 'mcc', 'bytes': 2, 'type':'float'}, 
        {'name': 'mnc', 'bytes': 1, 'type':'float'}, 
        {'name': 'lac', 'bytes': 2, 'type':'float'}, 
        {'name': 'cell-id', 'bytes': 3, 'type':'ID'},
        {'name': 'information-seq', 'bytes': 2, 'type':'float'},
        {'name': 'errors', 'bytes': 2, 'type':'float'},
        {'name': 'end', 'bytes': 2, 'type':'float'}
    ]
    
    rulesGPRS = [
        {'name': 'beggining', 'bytes': 2, 'type':'float'},
        {'name': 'length', 'bytes': 1, 'type':'float'},
        {'name': 'protocol', 'bytes': 1, 'type':'float'},
        {'name': 'term-info', 'bytes': 1, 'type':'float'}, 
        {'name': 'battery', 'bytes': 1, 'type':'float'},
        {'name': 'signal-level', 'bytes': 1, 'type':'float'},
        {'name': 'language', 'bytes': 2, 'type':'float'}, 
        {'name': 'information-seq', 'bytes': 2, 'type':'float'},
        {'name': 'errors', 'bytes': 2, 'type':'float'},
        {'name': 'end', 'bytes': 2, 'type':'float'},
    ]
    
    rulesLogin = [
        {'name': 'beggining', 'bytes': 2, 'type':'float'},       
        {'name': 'length', 'bytes': 1, 'type':'float'},         
        {'name': 'protocol', 'bytes': 1, 'type':'float'},       
        {'name': 'deviceId', 'bytes': 8, 'type':'imei'},         
        {'name': 'information-seq', 'bytes': 2, 'type':'float'}, 
        {'name': 'errors', 'bytes': 2, 'type':'float'},          
        {'name': 'end', 'bytes': 2, 'type':'float'}              
    ]

    if len(hexData) == 72:
        rules = rulesGPS
    elif len(hexData) == 30:
        rules = rulesGPRS
    elif len(hexData) == 36: 
        rules = rulesLogin
    else:
        print(f'[Translator] ERROR: Pase datos hex correctos (Largo recibido: {len(hexData)})')
        return None

    pos = 0
    results = {}
    for data in rules:
        cut = pos + (data['bytes'] * 2)
        byte_segment = hexData[pos:cut]
        
        # Validacion de seguridad por si el string viene incompleto
        if not byte_segment:
            print(f"[Translator] ERROR: Segmento vacío para '{data['name']}' en pos {pos}:{cut}")
            continue

        if data['type'] == 'date':
            year = int(byte_segment[0:2], 16)
            month = int(byte_segment[2:4], 16)
            day = int(byte_segment[4:6], 16)
            hour = int(byte_segment[6:8], 16)
            minute = int(byte_segment[8:10], 16)
            second = int(byte_segment[10:12], 16)
            value = f"{year:02d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

        elif data['type'] == 'cords':
            cords = int(byte_segment, 16)
            value = cords / 1800000
            
        elif data['type'] == 'imei':
            value = byte_segment[1:] if byte_segment.startswith('0') else byte_segment

        else:
            value = int(byte_segment, 16)
            
        results[data['name']] = value      
        pos = cut
        
    return results