import base64
import json
import websockets
import asyncio
import audioop
import pywav
from pyngrok import ngrok
import os
from dotenv import load_dotenv
load_dotenv()

async def hello(websocket):
    inboundAudio = []
    outboundAudio = []
    saveInbound = True
    saveOutbound = True
    try:
        async for message in websocket:
            msg = json.loads(message)
            if msg['event'] == 'start':
                callId = msg['start']['callSid']
                streamSid = msg['start']['streamSid']

                file_path = 'sample.wav'

                with open(file_path, 'rb') as audio_file:
                    audio_file.seek(44)  # Skip the header (44 bytes)
                    while True:
                        chunk = audio_file.read(1024)
                        if not chunk:
                            break
                        decoded_chunk = audioop.lin2ulaw(chunk, 2)  # Convert to mu-law
                        payload = base64.b64encode(decoded_chunk).decode()
                        data = {
                            "event": "media",
                            "streamSid": streamSid,
                            "media": {
                                "payload": payload
                            }
                        }
                        await websocket.send(json.dumps(data))

            if msg['event'] == 'media':
                media = msg['media']
                if media['track'] == 'inbound':
                    inboundAudio.append(base64.b64decode(media['payload']))
                if media['track'] == 'outbound':
                    outboundAudio.append(base64.b64decode(media['payload']))

            if msg['event'] == 'stop':
                print('received stop, writing audio')

                if saveInbound:
                    inbound_bytes = b"".join(inboundAudio)
                    wave_write = pywav.WavWrite("recordings/Inbound-" + callId + ".wav", 1, 8000, 8, 7)
                    wave_write.write(inbound_bytes)
                    wave_write.close()

                if saveOutbound:
                    outbound_bytes = b"".join(outboundAudio)
                    wave_write = pywav.WavWrite("recordings/Outbound-" + callId + ".wav", 1, 8000, 8, 7)
                    wave_write.write(outbound_bytes)
                    wave_write.close()

    except websockets.ConnectionClosed:
        print('connection ended')

async def main():
    ngrok.set_auth_token(os.getenv('NGROK_AUTH_TOKEN'))
    http_tunnel = ngrok.connect(addr=5000)
    wss_url = http_tunnel.public_url.replace('http://', 'wss://')

    text = (
        "\nConnect a Phone Number with a SignalWire/Twilio Bin with the following XML:\n\n"
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<Response>\n"
        "  <Connect>\n"
        f'    <Stream url="{wss_url}" />\n'
        "  </Connect>\n"
        "</Response>\n"
    )

    print(text)

    async with websockets.serve(hello, 'localhost', 5000):
        await asyncio.Future()

asyncio.run(main())