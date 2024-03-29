import logging
import json
import pika

from settings import settings

settings.load([
    "/etc/app/config.json", 
    "/etc/app/secrets.json"
])

import hookup

def consume_handler(ch, method, properties, body):
    """
    Callback for the message queue. 

    This function handles the synchroneous message handling and informs the MQ once a 
    message has been successfully handled. 
    """
    try:
        resolved_any_author = hookup.run(method.routing_key, json.loads(body))
        ch.basic_ack(method.delivery_tag)

        if resolved_any_author:
            ch.basic_publish(exchange=settings.MQ_EXCHANGE, routing_key="importer.person", body=body)
    except:
        logging.getLogger("ad_resolver").exception('An unexpected error occured while resolving authors.')
        ch.basic_nack(method.delivery_tag)


def main():
    logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
    logger = logging.getLogger("ad_resolver")

    while True:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.MQ_HOST,
                heartbeat=settings.MQ_HEARTBEAT,
                blocked_connection_timeout=settings.MQ_TIMEOUT,
                credentials=pika.PlainCredentials(settings.MQ_USER, settings.MQ_PASS)
            )
        )

        channel = connection.channel()

        for binding_key in settings.MQ_BINDKEYS:
            channel.queue_bind(
                exchange=settings.MQ_EXCHANGE,
                queue=settings.MQ_QUEUE,
                routing_key=binding_key
            )

        # switch message round-robin assignment to ready processes first
        # Force service to handle one message at the time!
        channel.basic_qos(prefetch_count=1)

        # register consuming function as callback
        channel.basic_consume(
            queue=settings.MQ_QUEUE,
            on_message_callback=consume_handler
        )

        try:
            channel.start_consuming()
        # Don't recover if connection was closed by broker
        except pika.exceptions.ConnectionClosedByBroker:
            break
        # Don't recover on channel errors
        except pika.exceptions.AMQPChannelError:
            break
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            continue

    connection.close()


if __name__ == "__main__":
    main()
