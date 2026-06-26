import asyncio
from datetime import datetime
import translator

PORT = 17050
DATA_FILE = "telemetria_temporal.jsonl"  # Archivo temporal donde se guardará todo

def guardar_en_jsonl(address, tipo_paquete, hex_data):
    """
    Función encargada de estructurar el JSON.
    En el futuro, esta lógica vivirá en la capa de 'infrastructure'.
    """
    # Estructuramos un diccionario limpio con lo que nos interesa trackear
    registro = {
        "fecha_servidor": datetime.now().isoformat(),
        "dispositivo_ip": address[0],
        "dispositivo_puerto": address[1],
        "protocolo": "GT06 (Jessica)",
        "tipo_paquete": tipo_paquete,  # '01' para Login, '12' para Ubicación, etc.
        "raw_hex": hex_data
    }
    


async def gpsHandler(reader, writer):
    address = writer.get_extra_info('peername')
    print(f" Conexión establecida desde {address}")

    inactivity = 0
    TIMEOUT = 120

    while True:
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
            
            if not data:
                print(f" Desconexión limpia del dispositivo {address}")
                break

            inactivity = 0
            hexData = data.hex().upper()
            
            if hexData.startswith('7878'):
                protocolType = hexData[6:8]
                
                # 1. Paquete de Login
                if protocolType == '01':
                    print(f"[GT06] Paquete de Login detectado para {address}")
                    
                    
                    serialNumber = hexData[24:28] if len(hexData) >= 28 else '0001'
                    response_hex = f"78780501{serialNumber}51280D0A"
                    
                    writer.write(bytes.fromhex(response_hex))
                    await writer.drain()
                    print(f"[GT06] Respuesta de Login enviada: {response_hex}")
                
                # 2. Paquete de Ubicación
                elif protocolType == '12':
                    response_hex = f"78780513{serialNumber}51280D0A"  
                    writer.write(bytes.fromhex(response_hex))

                    print(f"[GT06] Coordenadas recibidas de {address}")
            resultado = translator.byteToInt(hexData)
            print(f'Traduccion de datos: {resultado}')

        except asyncio.TimeoutError:
            inactivity += 1

            if inactivity >= TIMEOUT:
                print(f" TIMEOUT: Desconectando a {address}")
                break


async def startServer():
    server = await asyncio.start_server(gpsHandler, '0.0.0.0', PORT)
    print(f"Servidor activo y escuchando en el puerto {PORT}...")

    async with server:
        await server.serve_forever()

asyncio.run(startServer())