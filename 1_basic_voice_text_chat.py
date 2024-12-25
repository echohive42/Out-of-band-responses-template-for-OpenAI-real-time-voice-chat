#!/usr/bin/env python3
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8" />
    <title>Realtime Voice and Text Chat Demo</title>
    <!-- Load Tailwind and DaisyUI properly -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>
    <style>
        .gradient-text {
            background: linear-gradient(45deg, #6366f1, #8b5cf6, #d946ef);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            animation: gradient 6s ease infinite;
            background-size: 200% 200%;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .loading-dots::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }

        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60% { content: '...'; }
            80%, 100% { content: ''; }
        }

        .glass-morphism {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }

        #log {
            color: #e2e8f0;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 min-h-screen flex flex-col items-center p-4">
    <div class="container mx-auto p-4 max-w-2xl w-full">
        <h1 class="text-4xl font-bold mb-6 text-center gradient-text">Two-Way Voice & Text Chat</h1>

        <!-- Main Card Container -->
        <div class="glass-morphism rounded-xl p-6 space-y-6">
            <!-- Status Section -->
            <div class="space-y-4">
                <button id="btn-start" class="btn btn-primary w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 border-0 transform transition-transform duration-200 hover:scale-[1.02]">
                    Connect & Start Chat
                </button>
                <div id="status" class="text-sm text-gray-300 text-center">
                    Click "Connect & Start Chat" above to begin
                </div>
            </div>

            <!-- Text Input Section -->
            <div class="flex items-center space-x-3">
                <input type="text" id="text-input" 
                    placeholder="Type your message..." 
                    class="input input-bordered w-full bg-opacity-20 focus:ring-2 focus:ring-violet-500 transition-all duration-300"
                />
                <button id="btn-send-text" 
                    class="btn btn-accent bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 border-0">
                    Send
                </button>
            </div>

            <!-- Conversation Log -->
            <div class="mt-6">
                <h2 class="font-bold mb-3 text-violet-300">Conversation Log</h2>
                <div class="glass-morphism rounded-lg p-4 h-64 overflow-y-auto">
                    <pre id="log" class="text-sm whitespace-pre-wrap"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        let pc, dc;
        const startButton = document.getElementById("btn-start");
        const textInput = document.getElementById("text-input");
        
        // Click handler for the "Connect & Start Chat" button
        startButton.addEventListener("click", handleConnection);
        
        // Add Enter key support for text input
        textInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendTextMessage();
            }
        });

        function handleConnection() {
            if (pc && (pc.connectionState === "connected" || pc.connectionState === "connecting")) {
                // Disconnect logic
                disconnectChat();
            } else {
                // Connect logic
                startChat();
            }
        }

        function disconnectChat() {
            if (pc) {
                pc.close();
                if (dc) dc.close();
            }
            pc = null;
            dc = null;
            startButton.textContent = "Connect & Start Chat";
            startButton.classList.remove("bg-gradient-to-r", "from-red-600", "to-red-700", "hover:from-red-700", "hover:to-red-800");
            startButton.classList.add("bg-gradient-to-r", "from-violet-600", "to-indigo-600", "hover:from-violet-700", "hover:to-indigo-700");
            document.getElementById("status").textContent = "Disconnected. Click Connect to start a new chat.";
            logMessage("[INFO] Disconnected from chat.");
        }

        async function startChat() {
            startButton.textContent = "Connecting...";
            startButton.classList.remove("bg-gradient-to-r", "from-violet-600", "to-indigo-600", "hover:from-violet-700", "hover:to-indigo-700");
            startButton.classList.add("bg-gradient-to-r", "from-red-600", "to-red-700", "hover:from-red-700", "hover:to-red-800");
            
            logMessage("[INFO] Requesting ephemeral token...");
            document.getElementById("status").textContent = "Requesting ephemeral token from server...";

            // Fetch ephemeral key from our FastAPI endpoint
            const tokenResp = await fetch("/session");
            const tokenData = await tokenResp.json();
            if (tokenData.error) {
                logMessage("[ERROR] " + JSON.stringify(tokenData, null, 2));
                document.getElementById("status").textContent = "Failed to get ephemeral key.";
                return;
            }

            // Extract ephemeral key
            const EPHEMERAL_KEY = tokenData.client_secret.value;
            document.getElementById("status").textContent = "Ephemeral key acquired. Creating RTCPeerConnection...";

            // Create a new RTCPeerConnection
            pc = new RTCPeerConnection();

            // Handle remote audio track (model output)
            pc.ontrack = (event) => {
                logMessage("[INFO] Received remote audio track from model.");
                const audioEl = document.createElement("audio");
                audioEl.autoplay = true;
                audioEl.srcObject = event.streams[0];
            };

            // Add local microphone audio track
            try {
                const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaStream.getTracks().forEach((track) => pc.addTrack(track, mediaStream));
                logMessage("[INFO] Local microphone track acquired and added.");
            } catch (err) {
                logMessage("[ERROR] Unable to acquire microphone: " + err);
                document.getElementById("status").textContent = "Could not access microphone.";
                return;
            }

            // Create data channel to send/receive Realtime events
            dc = pc.createDataChannel("oai-events");
            dc.addEventListener("open", () => {
                logMessage("[INFO] Data channel opened.");
                document.getElementById("status").textContent = "Data channel open. You can chat now!";
            });

            // Listen for server -> client data channel messages (JSON events)
            dc.addEventListener("message", (e) => {
                let serverEvent;
                try {
                    serverEvent = JSON.parse(e.data);
                } catch {
                    logMessage("[WARN] Received non-JSON data from server: " + e.data);
                    return;
                }

                // Log the raw event
                logMessage("[SERVER EVENT] " + JSON.stringify(serverEvent, null, 2));
            });

            // Once ICE gathering finishes, we have a local SDP to send to the Realtime API
            pc.onicecandidate = async (evt) => {
                // We'll wait until there's no more candidates
                if (!evt.candidate && pc.iceGatheringState === "complete") {
                    document.getElementById("status").textContent = "Sending SDP offer to Realtime API...";
                    const offer = pc.localDescription;

                    const baseUrl = "https://api.openai.com/v1/realtime";
                    const model = "gpt-4o-realtime-preview-2024-12-17";

                    try {
                        const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
                            method: "POST",
                            headers: {
                                "Authorization": `Bearer ${EPHEMERAL_KEY}`,
                                "Content-Type": "application/sdp"
                            },
                            body: offer.sdp
                        });

                        if (!sdpResponse.ok) {
                            const errText = await sdpResponse.text();
                            logMessage("[ERROR] Realtime API error: " + errText);
                            document.getElementById("status").textContent = "Error from Realtime API (check console).";
                            return;
                        }

                        const answerSdp = await sdpResponse.text();
                        const answer = { type: "answer", sdp: answerSdp };
                        await pc.setRemoteDescription(answer);

                        document.getElementById("status").textContent = "Connected to Realtime API! Start chatting.";
                        logMessage("[INFO] WebRTC connection established.");
                    } catch (error) {
                        logMessage("[ERROR] " + error);
                        document.getElementById("status").textContent = "Error sending SDP offer.";
                    }
                }
            };

            // Create and set our local offer
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);

            // Update button text after successful connection
            startButton.textContent = "Disconnect";
        }

        // Send a text message from the user
        function sendTextMessage() {
            if (!dc || dc.readyState !== "open") {
                logMessage("[WARN] Data channel not open yet.");
                return;
            }

            const textVal = document.getElementById("text-input").value.trim();
            if (!textVal) return;

            // 1) Add user message to conversation
            const userEvent = {
                type: "conversation.item.create",
                item: {
                    type: "message",
                    role: "user",
                    content: [
                        {
                            type: "input_text",
                            text: textVal
                        }
                    ]
                }
            };
            dc.send(JSON.stringify(userEvent));
            logMessage("[YOU] " + textVal);

            // 2) Ask model for a response (both text and audio)
            const responseEvent = {
                type: "response.create",
                response: {
                    modalities: ["text", "audio"]  // request text + audio reply
                }
            };
            dc.send(JSON.stringify(responseEvent));
            logMessage("[INFO] Requested a model response.");

            // Clear input
            document.getElementById("text-input").value = "";
        }

        // Utility to add logs to the conversation area
        function logMessage(message) {
            const logEl = document.getElementById("log");
            logEl.textContent += "\\n" + message;
            logEl.scrollTop = logEl.scrollHeight;
            console.log(message);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    """
    Serve the single-page HTML UI.
    """
    return HTML_TEMPLATE

@app.get("/session")
async def session():
    """
    A simple endpoint to create an ephemeral Realtime key.
    Requires a standard API key (OPENAI_API_KEY) on the server side.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "No OPENAI_API_KEY found in environment variables."}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        # You can adjust the model or voice as needed
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "voice": "verse"  
    }

    resp = requests.post("https://api.openai.com/v1/realtime/sessions", headers=headers, json=data)
    if resp.status_code != 200:
        return {"error": f"Could not create ephemeral session: {resp.text}"}

    return resp.json()

if __name__ == "__main__":
    uvicorn.run("1_basic_voice_text_chat:app", host="127.0.0.1", port=8000, reload=True)
