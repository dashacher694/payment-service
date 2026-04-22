class RabbitMQSettings:
    def __init__(self, rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"):
        self.rabbitmq_url = rabbitmq_url
