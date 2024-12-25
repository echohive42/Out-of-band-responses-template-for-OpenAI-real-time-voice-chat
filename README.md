# Real-Time Voice Chat Experiments

This repository contains two implementations of real-time voice chat applications using OpenAI's Realtime API with WebRTC.

## Prerequisites

- Python 3.8+
- OpenAI API key with Realtime API access
- Modern web browser with WebRTC support

## Installation

1. Clone the repository
2. Install the required packages:
```bash
pip install fastapi uvicorn requests termcolor
```

3. Set your OpenAI API key as an environment variable:
```bash
# For Linux/Mac
export OPENAI_API_KEY=your_api_key_here

# For Windows
set OPENAI_API_KEY=your_api_key_here
```

## Applications

### 1. Basic Voice & Text Chat (`1_basic_voice_text_chat.py`)

A straightforward implementation of two-way voice and text chat with the following features:

- Real-time voice communication using WebRTC
- Text chat capability
- Beautiful dark mode UI with glass-morphism effects
- Error handling and status updates
- Animated UI elements

To run:
```bash
python 1_basic_voice_text_chat.py
```

### 2. Enhanced Chat with Real-time Classification (`2_out_of_band_responses.py`)

An enhanced version that adds real-time conversation classification:

- All features from the basic version
- Real-time conversation classification into categories:
  - General
  - Philosophical
  - Math
  - Technology
- Classifications for both voice and text inputs
- Side panel showing conversation classifications with timestamps
- Color-coded classification display
- Out-of-band processing to maintain smooth chat experience

To run:
```bash
python 2_out_of_band_responses.py
```

## Technical Details

### WebRTC Implementation
- Uses OpenAI's Realtime API for WebRTC signaling
- Handles audio streams for voice communication
- Manages data channels for text and control messages
- Implements proper connection lifecycle management

### Out-of-Band Processing (Enhanced Version)
- Uses separate processing for classifications without affecting main conversation
- Analyzes entire conversation context for accurate classification
- Implements metadata-based response handling
- Maintains conversation state independently of classifications

### UI Features
- Built with Tailwind CSS and DaisyUI
- Responsive design
- Glass-morphism effects
- Smooth animations using CSS transitions
- Dark mode optimized

## Usage

1. Start either application using the commands above
2. Click "Connect & Start Chat"
3. Allow microphone access when prompted
4. Start chatting using either:
   - Voice (just speak)
   - Text (type and press Enter or click Send)
5. For the enhanced version, watch the classifications appear in real-time

## Error Handling

Both implementations include comprehensive error handling for:
- API key issues
- Connection problems
- Microphone access
- WebRTC negotiation
- Data channel communication

Errors are:
- Logged to the console
- Displayed in the UI
- Color-coded in the terminal (using termcolor)

## Security Notes

- Uses ephemeral tokens for client-side API access
- Handles API keys securely through environment variables
- Implements proper WebRTC security practices

## Limitations

- Maximum session duration: 30 minutes
- Requires modern browser with WebRTC support
- Needs stable internet connection for voice chat
- API key must have Realtime API access enabled

## Contributing

Feel free to submit issues and enhancement requests! 