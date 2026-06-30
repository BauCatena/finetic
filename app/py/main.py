import asyncio
import translator
import crc16Calculator
import datetime
from dbHandler import saveRecentLocation

PORT = 17050

async def gpsHandler(reader, writer):
    address = writer.get_extra_info('peername')
    print(f"Conexión establecida desde {address}", flush=True)

    currentDeviceId = None 
    inactivity = 0
    TIMEOUT = 120
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                
                if not data:
                    print(f"Desconexión protocolar del dispositivo {address}")
                    break

                inactivity = 0
                hexData = data.hex().upper()
                print(f"       DEBUG para Translator -> Largo: {len(hexData)} | Contenido: {hexData}")
                loginResult = translator.byteToInt(hexData)
                if hexData.startswith('7878') and len(hexData) >= 8:
                    protocolType = hexData[6:8]
                    
                    if protocolType == '01':
                        print(f"[GT06] Paquete de Login detectado para {address}")
                        
                        loginResult = translator.byteToInt(hexData)
                        if loginResult and "deviceId" in loginResult:
                            currentDeviceId = loginResult["deviceId"]
                            print(f"[GT06] Dispositivo autenticado exitosamente: {currentDeviceId}")
                        
                        serialNumber = hexData[24:28] if len(hexData) >= 28 else '0001'
                        baseResponseHex = f"0501{serialNumber}"
                        
                        bytesToCalculate = bytes.fromhex(baseResponseHex)
                        crcCalculated = crc16Calculator.calculateCrc16Gt06(bytesToCalculate)
                        
                        response_hex = f"7878{baseResponseHex}{crcCalculated}0D0A"
                        writer.write(bytes.fromhex(response_hex))
                        await writer.drain()
                    
                    elif protocolType == '13':
                        print(f"[GT06] Paquete de Heartbeat detectado para {address}")
                        
                        heartbeatResult = translator.byteToInt(hexData)
                        if heartbeatResult:
                            print(f"[Status] Batería (1 al 5): {heartbeatResult.get('battery')} - Señal: {heartbeatResult.get('signal-level')}")

                        # 🚀 TRUCO DINÁMICO: Extrae el número de serie contando desde el final
                        serialNumber = hexData[-12:-8] if len(hexData) >= 12 else '0001'
                        baseResponseHex = f"0513{serialNumber}"
                        
                        bytesToCalculate = bytes.fromhex(baseResponseHex)
                        crcCalculated = crc16Calculator.calculateCrc16Gt06(bytesToCalculate)
                        
                        response_hex = f"7878{baseResponseHex}{crcCalculated}0D0A"
                        writer.write(bytes.fromhex(response_hex))
                        await writer.drain()

                    elif protocolType == '12':
                        print(f"[GT06] Coordenadas recibidas de {address}")
                        
                        if not currentDeviceId:
                            print(f"[Warning] Coordenadas ignoradas: {address} no envió paquete de Login previo.")
                            continue

                        gpsResult = translator.byteToInt(hexData)
                        
                        if gpsResult:
                            print(f'Traducción de coordenadas: {gpsResult}')
                        raw_date = gpsResult.get("timestamp") # '26/06/30 15:38:30'
                        dt_object = datetime.strptime(raw_date, '%y/%m/%d %H:%M:%S')

                        await saveRecentLocation(
                            deviceId=currentDeviceId, 
                            latitude=gpsResult.get("latitude"),
                            longitude=gpsResult.get("longitude"),
                            trackerTimestamp=dt_object, # 🚀 Ahora enviás el objeto datetime
                            signalType="GPS", 
                            rawHex=hexData
                        )
            except asyncio.TimeoutError:
                inactivity += 1
                if inactivity >= TIMEOUT:
                    print(f"TIMEOUT: {address} superó los {TIMEOUT}s de inactividad. Desconectando.")
                    break

    except (ConnectionResetError, BrokenPipeError):
        print(f"Conexión perdida abruptamente con {address} (Corte de señal/energía).")
    except Exception as e:
        print(f"Error inesperado en el handler de {address}: {e}")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        print(f"Socket liberado y cerrado para {address}")

async def startServer():
    server = await asyncio.start_server(gpsHandler, '0.0.0.0', PORT)
    print(f"Servidor activo y escuchando en el puerto {PORT}...")

    async with server:
        await server.serve_forever()

asyncio.run(startServer())