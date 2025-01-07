from flask import Flask, request
from flask_socketio import SocketIO, emit
from vosk import Model, KaldiRecognizer
import logging
import json
import eventlet
from threading import Lock

# 初始化 Flask 和 SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域

# 配置日志记录
logging.basicConfig(level=logging.WARNING)  # 减少日志输出
logger = logging.getLogger(__name__)

# 加载 Vosk 模型
model_path = "model/vosk-model-cn-0.22"  # 确保这是挂载后的绝对路径
try:
    model = Model(model_path)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

# 存储每个客户端的识别器
client_recognition = {}
recognition_lock = Lock()  # 用于线程安全的锁

@socketio.on('connect')
def handle_connect():
    """
    客户端连接时初始化识别器
    """
    client_id = request.sid  # 获取客户端唯一ID
    with recognition_lock:
        client_recognition[client_id] = KaldiRecognizer(model, 16000)
    logger.info(f"Client connected: {client_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """
    客户端断开连接时清理资源
    """
    client_id = request.sid
    with recognition_lock:
        if client_id in client_recognition:
            del client_recognition[client_id]
    logger.info(f"Client disconnected: {client_id}")

@socketio.on('audio_data')
def handle_audio_data(data):
    """
    处理客户端发送的音频数据
    """
    client_id = request.sid
    with recognition_lock:
        if client_id not in client_recognition:
            emit('error', {'message': 'Recognition not initialized'})
            return

        rec = client_recognition[client_id]

    try:
        # 处理音频数据
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            emit('result', result)  # 发送中间结果
        else:
            partial_result = json.loads(rec.PartialResult())
            emit('partial_result', partial_result)  # 发送部分结果

    except Exception as e:
        logger.error(f"Error processing audio data: {e}")
        emit('error', {'message': str(e)})

@socketio.on('end_stream')
def handle_end_stream():
    """
    客户端结束音频流时返回最终结果
    """
    client_id = request.sid
    with recognition_lock:
        if client_id not in client_recognition:
            emit('error', {'message': 'Recognition not initialized'})
            return

        rec = client_recognition[client_id]

    try:
        # 获取最终结果
        final_result = json.loads(rec.FinalResult())
        emit('final_result', final_result)  # 发送最终结果

        # 清理识别器
        with recognition_lock:
            del client_recognition[client_id]
            client_recognition[client_id] = KaldiRecognizer(model, 16000)

    except Exception as e:
        logger.error(f"Error finalizing stream: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    eventlet.monkey_patch()
    socketio.run(app, host='0.0.0.0', port=2700, log_output=False)  # 禁用 SocketIO 的日志输出