# Vosk 语音识别 Docker 部署

本项目提供了快速部署 [Vosk](https://alphacephei.com/vosk/) 语音识别服务的 Docker 容器化方案。Vosk 是一个开源的语音识别工具，支持多种语言，具有高效、轻量级的特点。通过 Docker，您可以轻松地在本地或云端部署 Vosk 语音识别服务。

## 功能特性

- **多语言支持**：支持中文、英语、法语、德语、西班牙语等多种语言的语音识别。（需要自行去官网下载模型替换）
- **易于部署**：通过 Docker 容器化，一键部署，无需复杂的环境配置。
- **WebSocket API**：提供标准的 WebSocket 接口，方便与其他应用集成，可流式进行识别。

### 部署步骤
1. 克隆本项目到本地：
   ```bash
   git clone https://github.com/kezbb/vosk.git
   cd vosk
   docker build -t vosk-realtime-server .
   ```

2. 启动 Docker 容器：
   ```bash
   docker run -d -p 2700:2700 --name vosk-server vosk-realtime-server
   ```

3. 等待容器启动后，测试WebSocket服务。

### 使用示例

下面是一个网页进行实时语音识别的测试：

```bash
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time Speech Recognition</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        h1 {
            color: #333;
        }
        button {
            margin: 10px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            background-color: #007BFF;
            color: white;
        }
        button:disabled {
            background-color: #cccccc;
        }
        pre {
            width: 80%;
            height: 200px;
            overflow-y: auto;
            background-color: white;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <h1>Real-time Speech Recognition</h1>
    <button id="start">Start</button>
    <button id="stop" disabled>Stop</button>
    <pre id="output"></pre>

    <script>
        const socket = io('http://localhost:2700');

        let mediaStream;
        let audioContext;
        let processor;

        // 处理服务器返回的结果
        socket.on('result', (data) => {
            document.getElementById('output').textContent += JSON.stringify(data) + '\n';
        });

        socket.on('partial_result', (data) => {
            document.getElementById('output').textContent += JSON.stringify(data) + '\n';
        });

        socket.on('final_result', (data) => {
            document.getElementById('output').textContent += JSON.stringify(data) + '\n';
        });

        socket.on('error', (data) => {
            console.error('Error:', data.message);
        });

        // 开始录音
        document.getElementById('start').addEventListener('click', async () => {
            mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioContext = new AudioContext({ sampleRate: 16000 });
            const source = audioContext.createMediaStreamSource(mediaStream);
            processor = audioContext.createScriptProcessor(4096, 1, 1);

            source.connect(processor);
            processor.connect(audioContext.destination);

            processor.onaudioprocess = (event) => {
                const audioData = event.inputBuffer.getChannelData(0);
                const pcmData = new Int16Array(audioData.length);
                for (let i = 0; i < audioData.length; i++) {
                    pcmData[i] = audioData[i] * 32768; // 转换为 16-bit PCM
                }
                socket.emit('audio_data', pcmData.buffer);
            };

            document.getElementById('start').disabled = true;
            document.getElementById('stop').disabled = false;
        });

        // 停止录音
        document.getElementById('stop').addEventListener('click', () => {
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
            }
            if (audioContext) {
                audioContext.close();
            }
            socket.emit('end_stream');
            document.getElementById('start').disabled = false;
            document.getElementById('stop').disabled = true;
        });
    </script>
</body>
</html>
```

## 配置说明

- **模型选择**：默认使用小型中文模型，您可以在 `model` 中替换为其他语言模型。
- **端口配置**：如需修改服务端口，请更改 `docker run -d -p 2700:2700 --name vosk-server vosk-realtime-server` 命令中的 `port:2700` 配置。

## 支持的语言模型

Vosk 提供了多种预训练模型，您可以根据需要下载并替换默认模型（要把文件提取出来到model文件夹下）：

- [中文模型](https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip)
- [英文模型](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
- [更多模型](https://alphacephei.com/vosk/models)

**立即部署 Vosk 语音识别服务，开启高效语音识别之旅！**
