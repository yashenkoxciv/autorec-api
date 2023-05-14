import json
import pika
import uuid


class RecognitionRpcClient:
    def __init__(self, mq_host: str, queue_name: str = ''):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
        self.channel = self.connection.channel()
        
        result = self.channel.queue_declare(queue=queue_name, exclusive=True)
        self.callback_queue = result.method.queue
        
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.correlation_id = None
    
    def on_response(self, ch, method, props, body):
        if self.correlation_id == props.correlation_id:
            self.response = body
    
    def call(self, image_id: str, image_url: str):
        self.response = None
        self.correlation_id = str(uuid.uuid4())
        message = json.dumps({'image_id': image_id, 'image_url': image_url})
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id
            ),
            body=message
        )
        self.connection.process_data_events(time_limit=None)
        str_response = self.response.decode('utf-8')
        response = json.loads(str_response)
        return response


